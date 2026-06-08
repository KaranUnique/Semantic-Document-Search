"""
Static file server for the HTML/CSS/JS frontend.
Reads BACKEND_URL from frontend/static/.env and injects it into config.js at startup.
Serves files from ./static on port 8501.
"""
import http.server
import os

PORT = 8501
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
ENV_FILE   = os.path.join(STATIC_DIR, ".env")
CONFIG_JS  = os.path.join(STATIC_DIR, "config.js")

def load_env(path):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            env[key.strip()] = val.strip()
    return env

def write_config(env):
    backend_url = env.get("BACKEND_URL", "http://127.0.0.1:8000")
    js = f'// Auto-generated from .env — do not edit manually\nwindow.__ENV__ = {{\n  BACKEND_URL: "{backend_url}"\n}};\n'
    with open(CONFIG_JS, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"[config] BACKEND_URL = {backend_url}")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def log_message(self, fmt, *args):
        print(f"[server] {fmt % args}")

if __name__ == "__main__":
    env = load_env(ENV_FILE)
    write_config(env)
    print(f"Serving frontend at http://localhost:{PORT}")
    with http.server.HTTPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
