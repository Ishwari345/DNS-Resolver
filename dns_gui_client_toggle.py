# dns_gui_dashboard.py
# Final professional GUI: resizable, live cache + stats, export to CSV

import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import threading

API_BASE = "http://127.0.0.1:8080"  # backend API

# ---------- API helpers ----------
def api_resolve(hostname):
    r = requests.get(f"{API_BASE}/resolve", params={"hostname": hostname}, timeout=5)
    r.raise_for_status()
    return r.json()

def api_cache():
    r = requests.get(f"{API_BASE}/cache", timeout=5)
    r.raise_for_status()
    return r.json()

def api_stats():
    r = requests.get(f"{API_BASE}/stats", timeout=5)
    r.raise_for_status()
    return r.json()

# ---------- Actions ----------
def do_resolve():
    hostname = hostname_var.get().strip()
    if not hostname:
        messagebox.showwarning("Input Error", "Please enter a hostname.")
        return
    resolve_btn.config(state="disabled")
    result_label.config(text="Resolving...", fg=theme['accent_fg'])

    t = threading.Thread(target=_resolve_background, args=(hostname,), daemon=True)
    t.start()

def _resolve_background(hostname):
    try:
        data = api_resolve(hostname)
        addrs = data.get("addresses") or []
        ip_text = ", ".join(addrs) if addrs else data.get("error", "No IP found")
        from_cache = data.get("from_cache", False)
        ttl = data.get("ttl", "N/A")

        text = (f"Hostname: {hostname}\n"
                f"Address(es): {ip_text}\n"
                f"From Cache: {from_cache}\n"
                f"TTL (s): {ttl}")
        _set_result(text, ok=True)
    except Exception as e:
        _set_result(f"Error: {e}", ok=False)
    finally:
        root.after(0, lambda: resolve_btn.config(state="normal"))

def _set_result(text, ok=True):
    def update():
        result_label.config(text=text,
                            fg=theme['result_fg'] if ok else theme['error_fg'])
    root.after(0, update)

def refresh_cache_once():
    try:
        data = api_cache()
    except Exception:
        return
    def update():
        cache_tree.delete(*cache_tree.get_children())
        for item in data:
            cache_tree.insert(
                "", "end",
                values=(item["hostname"],
                        ", ".join(item["addresses"]),
                        f"{item['ttl']}s")
            )
    root.after(0, update)

def loop_cache_refresh():
    refresh_cache_once()
    root.after(1000, loop_cache_refresh)  # 1 second

def loop_stats_refresh():
    try:
        s = api_stats()
    except Exception:
        root.after(2000, loop_stats_refresh)
        return
    def update():
        total_var.set(str(s.get("total_queries", 0)))
        hits_var.set(str(s.get("cache_hits", 0)))
        misses_var.set(str(s.get("cache_misses", 0)))
        hitrate_var.set(f"{s.get('hit_rate_percent', 0)}%")
    root.after(0, update)
    root.after(2000, loop_stats_refresh)  # 2 seconds

def export_cache_csv():
    try:
        data = api_cache()
    except Exception as e:
        messagebox.showerror("Export Error", f"Could not fetch cache: {e}")
        return
    if not data:
        messagebox.showinfo("Export", "Cache is empty, nothing to export.")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Save Cache as CSV"
    )
    if not path:
        return

    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["hostname", "addresses", "ttl_seconds"])
            for item in data:
                w.writerow([
                    item["hostname"],
                    ";".join(item["addresses"]),
                    item["ttl"],
                ])
        messagebox.showinfo("Export", f"Cache exported to {path}")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))

# ---------- Theme ----------
def set_dark():
    global theme
    theme = {
        "bg": "#0f1721",
        "panel_bg": "#0b1220",
        "fg": "#e5e7eb",
        "muted": "#9ca3af",
        "accent_fg": "#60a5fa",
        "accent_bg": "#1d4ed8",
        "btn_bg": "#1d4ed8",
        "btn_fg": "#f9fafb",
        "result_fg": "#e5e7eb",
        "error_fg": "#f97373",
        "tree_bg": "#020617",
    }
    apply_theme()

def set_light():
    global theme
    theme = {
        "bg": "#f3f4f6",
        "panel_bg": "#ffffff",
        "fg": "#111827",
        "muted": "#6b7280",
        "accent_fg": "#1d4ed8",
        "accent_bg": "#e0ecff",
        "btn_bg": "#1d4ed8",
        "btn_fg": "#f9fafb",
        "result_fg": "#111827",
        "error_fg": "#b91c1c",
        "tree_bg": "#ffffff",
    }
    apply_theme()

def apply_theme():
    root.configure(bg=theme["bg"])
    for frame in (main_frame, header_frame, top_frame, result_frame,
                  lower_frame, cache_panel, stats_panel, footer_frame):
        frame.configure(bg=theme["bg"] if frame is main_frame else theme["panel_bg"])

    title_label.configure(bg=theme["bg"], fg=theme["accent_fg"])
    subtitle_label.configure(bg=theme["bg"], fg=theme["muted"])

    hostname_label.configure(bg=theme["bg"], fg=theme["fg"])
    entry.configure(bg=theme["panel_bg"], fg=theme["fg"],
                    insertbackground=theme["fg"], relief="flat")

    resolve_btn.configure(bg=theme["btn_bg"], fg=theme["btn_fg"],
                          activebackground=theme["accent_bg"], relief="flat")
    theme_btn.configure(bg=theme["panel_bg"], fg=theme["muted"], relief="flat")

    result_label.configure(bg=theme["panel_bg"], fg=theme["result_fg"])

    cache_title.configure(bg=theme["panel_bg"], fg=theme["fg"])
    stats_title.configure(bg=theme["panel_bg"], fg=theme["fg"])

    for lbl in (total_lbl, hits_lbl, misses_lbl, hitrate_lbl,
                total_val, hits_val, misses_val, hitrate_val):
        lbl.configure(bg=theme["panel_bg"], fg=theme["fg"])

    export_btn.configure(bg=theme["panel_bg"], fg=theme["muted"], relief="flat")

    style.configure(
        "Custom.Treeview",
        background=theme["tree_bg"],
        fieldbackground=theme["tree_bg"],
        foreground=theme["fg"],
        rowheight=26,
        bordercolor=theme["bg"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Custom.Treeview.Heading",
        background=theme["accent_bg"],
        foreground=theme["fg"],
        font=("Segoe UI", 10, "bold"),
    )

def toggle_theme():
    global current_theme
    if current_theme == "dark":
        current_theme = "light"
        set_light()
        theme_btn.config(text="Dark Mode")
    else:
        current_theme = "dark"
        set_dark()
        theme_btn.config(text="Light Mode")

# ---------- Build GUI ----------
root = tk.Tk()
root.title("DNS Resolver – Dashboard")
root.geometry("960x620")
root.minsize(900, 600)           # allow maximize and resizing
root.resizable(True, True)       # you can now maximize!

style = ttk.Style()
style.theme_use("default")

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=12, pady=10)

# Header
header_frame = tk.Frame(main_frame)
header_frame.pack(fill="x")
title_label = tk.Label(header_frame, text="DNS Resolver & Caching — Dashboard",
                       font=("Segoe UI", 18, "bold"))
title_label.pack(anchor="w")
subtitle_label = tk.Label(header_frame, text="Resolve hostnames, view server cache and live stats",
                          font=("Segoe UI", 10))
subtitle_label.pack(anchor="w", pady=(2, 8))

# Top controls
top_frame = tk.Frame(main_frame)
top_frame.pack(fill="x", pady=(4, 8))

hostname_var = tk.StringVar()
hostname_label = tk.Label(top_frame, text="Hostname", font=("Segoe UI", 10))
hostname_label.pack(anchor="w")
entry = tk.Entry(top_frame, textvariable=hostname_var, font=("Consolas", 12), width=40)
entry.pack(side="left", pady=4, ipady=4)

resolve_btn = tk.Button(top_frame, text="Resolve", command=do_resolve)
resolve_btn.pack(side="left", padx=10, ipadx=10, ipady=4)

theme_btn = tk.Button(top_frame, text="Light Mode", command=toggle_theme)
theme_btn.pack(side="right", padx=4, ipadx=6, ipady=2)

# Result
result_frame = tk.Frame(main_frame)
result_frame.pack(fill="x")
result_label = tk.Label(result_frame, text="No query yet.",
                        font=("Consolas", 11), anchor="w", justify="left",
                        padx=10, pady=8)
result_label.pack(fill="x")

# Lower layout (cache + stats)
lower_frame = tk.Frame(main_frame)
lower_frame.pack(fill="both", expand=True, pady=(8, 4))

# Cache panel
cache_panel = tk.Frame(lower_frame)
cache_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

cache_title = tk.Label(cache_panel, text="Server Cache (live)",
                        font=("Segoe UI", 12, "bold"))
cache_title.pack(anchor="w", padx=6, pady=(4, 0))

columns = ("Hostname", "Address(es)", "TTL")
cache_tree = ttk.Treeview(cache_panel, columns=columns,
                           show="headings", style="Custom.Treeview")
for col in columns:
    cache_tree.heading(col, text=col)
    cache_tree.column(col, anchor="center")
cache_tree.pack(fill="both", expand=True, padx=6, pady=6)

export_btn = tk.Button(cache_panel, text="Export Cache to CSV",
                       command=export_cache_csv)
export_btn.pack(anchor="e", padx=8, pady=(0, 8))

# Stats panel
stats_panel = tk.Frame(lower_frame, width=220)
stats_panel.pack(side="right", fill="y")

stats_title = tk.Label(stats_panel, text="Live Stats",
                       font=("Segoe UI", 12, "bold"))
stats_title.pack(anchor="w", padx=8, pady=(6, 0))

total_var = tk.StringVar(value="0")
hits_var = tk.StringVar(value="0")
misses_var = tk.StringVar(value="0")
hitrate_var = tk.StringVar(value="0%")

total_lbl = tk.Label(stats_panel, text="Total Queries", font=("Segoe UI", 10))
total_lbl.pack(anchor="w", padx=8, pady=(10, 0))
total_val = tk.Label(stats_panel, textvariable=total_var,
                     font=("Segoe UI", 12, "bold"))
total_val.pack(anchor="w", padx=8)

hits_lbl = tk.Label(stats_panel, text="Cache Hits", font=("Segoe UI", 10))
hits_lbl.pack(anchor="w", padx=8, pady=(10, 0))
hits_val = tk.Label(stats_panel, textvariable=hits_var,
                    font=("Segoe UI", 12, "bold"))
hits_val.pack(anchor="w", padx=8)

misses_lbl = tk.Label(stats_panel, text="Cache Misses", font=("Segoe UI", 10))
misses_lbl.pack(anchor="w", padx=8, pady=(10, 0))
misses_val = tk.Label(stats_panel, textvariable=misses_var,
                      font=("Segoe UI", 12, "bold"))
misses_val.pack(anchor="w", padx=8)

hitrate_lbl = tk.Label(stats_panel, text="Hit Rate", font=("Segoe UI", 10))
hitrate_lbl.pack(anchor="w", padx=8, pady=(10, 0))
hitrate_val = tk.Label(stats_panel, textvariable=hitrate_var,
                       font=("Segoe UI", 12, "bold"))
hitrate_val.pack(anchor="w", padx=8)

# Footer
footer_frame = tk.Frame(main_frame)
footer_frame.pack(fill="x", pady=(4, 0))
tk.Label(footer_frame,
         text=f"Backend API: {API_BASE}  (ensure dns_api_server.py is running)",
         font=("Segoe UI", 8)).pack(anchor="w", padx=4)

# ---- Init theme + loops ----
current_theme = "dark"
set_dark()
theme_btn.config(text="Light Mode")

entry.focus_set()

loop_cache_refresh()
loop_stats_refresh()

root.mainloop()
