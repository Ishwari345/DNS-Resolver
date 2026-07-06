# dns_api_server.py
"""
Flask-based DNS Resolver API with caching, TTL, and analytics.
Endpoints:
 - GET /resolve?hostname=<host>    -> resolve hostname (returns addresses list and from_cache)
 - GET /cache                      -> current cache table (hostname, addresses, ttl_remaining)
 - GET /stats                      -> hit/miss stats
 - POST /clear_cache               -> clears server cache (optional admin)
"""
from flask import Flask, request, jsonify
import socket
import time
import threading

app = Flask(__name__)

# shared data
_cache = {}      # hostname -> {"addresses": [...], "expires_at": float}
_cache_lock = threading.Lock()

_hits = 0
_misses = 0
_stats_lock = threading.Lock()

# TTL seconds for cached entries
TTL = 30

def resolve_system(hostname):
    """Return list of IP addresses for hostname using system resolver."""
    addrs = []
    try:
        infos = socket.getaddrinfo(hostname, None)
        for info in infos:
            ip = info[4][0]
            if ip not in addrs:
                addrs.append(ip)
    except Exception as e:
        raise

    # if still empty, try gethostbyname as fallback (rare)
    if not addrs:
        try:
            ip = socket.gethostbyname(hostname)
            addrs.append(ip)
        except Exception:
            pass
    return addrs

def get_cache_snapshot():
    """Return list of cache entries with TTL remaining (thread-safe)."""
    now = time.time()
    out = []
    with _cache_lock:
        # remove expired entries first
        expired = [k for k, v in _cache.items() if v["expires_at"] <= now]
        for k in expired:
            _cache.pop(k, None)
        # now build snapshot
        for hostname, v in _cache.items():
            ttl_rem = max(0, int(v["expires_at"] - now))
            out.append({"hostname": hostname, "addresses": v["addresses"], "ttl": ttl_rem})
    return out

@app.route("/resolve", methods=["GET"])
def api_resolve():
    global _hits, _misses
    hostname = request.args.get("hostname", "").strip()
    if not hostname:
        return jsonify({"error": "missing hostname"}), 400

    now = time.time()
    # check cache
    with _cache_lock:
        entry = _cache.get(hostname)
        if entry and entry["expires_at"] > now:
            with _stats_lock:
                _hits += 1
            return jsonify({
                "hostname": hostname,
                "addresses": entry["addresses"],
                "from_cache": True,
                "ttl": int(entry["expires_at"] - now)
            })

    # not in cache or expired -> resolve using system resolver
    try:
        addrs = resolve_system(hostname)
    except Exception as e:
        with _stats_lock:
            _misses += 1
        return jsonify({"hostname": hostname, "addresses": [], "from_cache": False, "error": str(e)}), 502

    if not addrs:
        with _stats_lock:
            _misses += 1
        return jsonify({"hostname": hostname, "addresses": [], "from_cache": False, "error": "no addresses found"}), 404

    # store in cache
    with _cache_lock:
        _cache[hostname] = {"addresses": addrs, "expires_at": now + TTL}
    with _stats_lock:
        _misses += 1

    return jsonify({"hostname": hostname, "addresses": addrs, "from_cache": False, "ttl": TTL})

@app.route("/cache", methods=["GET"])
def api_cache():
    return jsonify(get_cache_snapshot())

@app.route("/stats", methods=["GET"])
def api_stats():
    with _stats_lock:
        total = _hits + _misses
        hit_rate = (100.0 * _hits / total) if total > 0 else 0.0
        return jsonify({
            "total_queries": total,
            "cache_hits": _hits,
            "cache_misses": _misses,
            "hit_rate_percent": round(hit_rate, 2),
            "ttl_seconds": TTL
        })

@app.route("/clear_cache", methods=["POST"])
def api_clear_cache():
    with _cache_lock:
        _cache.clear()
    return jsonify({"status": "ok", "cleared": True})

if __name__ == "__main__":
    # run Flask on localhost:8080
    app.run(host="0.0.0.0", port=8080, debug=False)
