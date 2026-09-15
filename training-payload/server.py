#!/usr/bin/env python3
"""
server.py — Kali-side host + collector for a ClickFix phishing simulation.

Does two benign things on one port:
  1. Serves files from this directory (so the victim can fetch payload.zip).
  2. Logs GET /callback?host=..&user=..&ts=.. requests from the beacon binary,
     printing each check-in and appending it to callbacks.log.

Run:  python3 server.py
Stop: Ctrl+C
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import datetime
import os

HOST = "0.0.0.0"
PORT = 8000
SERVE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SERVE_DIR, "callbacks.log")

GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/callback":
            self._handle_callback(parse_qs(parsed.query))
            return

        self._serve_file(parsed.path)

    def _handle_callback(self, qs):
        host = qs.get("host", ["?"])[0]
        user = qs.get("user", ["?"])[0]
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        line = (f"[{ts}] CALLBACK from {self.client_address[0]} "
                f"host={host} user={user}")

        print(GREEN + ">>> " + line + RESET)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def _serve_file(self, path):
        rel = path.lstrip("/")
        full = os.path.normpath(os.path.join(SERVE_DIR, rel))

        # Keep serving confined to SERVE_DIR.
        if not full.startswith(SERVE_DIR) or not os.path.isfile(full):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        print(CYAN + f"--- served {rel} to {self.client_address[0]}" + RESET)
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()
        with open(full, "rb") as f:
            self.wfile.write(f.read())

    # Silence the default one-line-per-request logging; we print our own.
    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"Training server listening on {HOST}:{PORT}")
    print(f"Serving files from: {SERVE_DIR}")
    print(f"Callbacks logged to: {LOG_FILE}\n")
    try:
        HTTPServer((HOST, PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
