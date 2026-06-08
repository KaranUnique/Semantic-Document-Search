"""
Lightweight static file server for the HTML/CSS/JS frontend.
Serves files from ./static on port 8501 (same port as the old Streamlit app).
"""
import http.server
import os

PORT = 8501
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def log_message(self, fmt, *args):
        print(f"[server] {fmt % args}")


if __name__ == "__main__":
    print(f"Serving frontend at http://localhost:{PORT}")
    with http.server.HTTPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
