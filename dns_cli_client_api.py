# dns_cli_client_api.py
import requests

BASE = "http://127.0.0.1:8080"

def resolve(hostname):
    r = requests.get(f"{BASE}/resolve", params={"hostname": hostname}, timeout=5)
    r.raise_for_status()
    print(r.json())

def show_cache():
    r = requests.get(f"{BASE}/cache", timeout=5)
    r.raise_for_status()
    data = r.json()
    if not data:
        print("Cache is empty")
        return
    print("Current cache:")
    for e in data:
        print(f"{e['hostname']:30} {', '.join(e['addresses']):30} TTL: {e['ttl']}s")

def stats():
    r = requests.get(f"{BASE}/stats", timeout=5)
    r.raise_for_status()
    print("Stats:", r.json())

if __name__ == "__main__":
    print("Type a hostname to resolve, 'cache' to view cache, 'stats' for analytics, 'exit' to quit")
    while True:
        cmd = input("> ").strip()
        if not cmd:
            continue
        if cmd == "exit":
            break
        if cmd == "cache":
            show_cache()
            continue
        if cmd == "stats":
            stats()
            continue
        try:
            resolve(cmd)
        except Exception as e:
            print("Error:", e)
