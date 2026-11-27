import ast
import io
import json
import random
from contextlib import redirect_stdout
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
last_website_html = None


class NeedInput(Exception):
    def __init__(self, prompt):
        self.prompt = prompt


class MontyTranslator(ast.NodeTransformer):
    def visit_Call(self, node):
        self.generic_visit(node)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "vachange"
            and len(node.args) == 2
            and isinstance(node.args[0], ast.Name)
            and isinstance(node.args[1], ast.Name)
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="__vachange__", ctx=ast.Load()),
                    args=[
                        ast.Constant(node.args[0].id),
                        ast.Constant(node.args[1].id),
                    ],
                    keywords=[],
                ),
                node,
            )
        return node


class Website:
    """A small Monty website builder that generates a standalone HTML page."""

    def __init__(self, title="My Monty Website"):
        self.title = str(title)
        self.html = None
        self.elements = []
        self.custom_css_rules = []
        self.background = "#ffffff"
        self.foreground = "#202033"
        self.accent = "#7657e8"
        self.font_family = "Arial, sans-serif"
        self._nav_added = False

    def _add(self, markup):
        self.elements.append(markup)
        return self

    def heading(self, content, level=1):
        level = max(1, min(6, int(level)))
        return self._add(f"<h{level}>{escape(str(content))}</h{level}>")

    def text(self, content):
        return self._add(f"<p class='monty-text'>{escape(str(content))}</p>")

    def button(self, label, message="Button clicked!"):
        msg = json.dumps(str(message))
        return self._add(
            f"<button class='monty-button' "
            f"onclick='alert({escape(msg, quote=True)})'>"
            f"{escape(str(label))}</button>"
        )

    def image(self, url, alt="Website image"):
        url = str(url).strip()
        if not url.startswith(("https://", "http://")):
            raise ValueError("Images must use an http:// or https:// URL.")
        return self._add(
            f"<img class='monty-image' src='{escape(url, quote=True)}' "
            f"alt='{escape(str(alt), quote=True)}'>"
        )

    def link(self, label, url):
        url = str(url).strip()
        if not url.startswith(("https://", "http://", "mailto:")):
            raise ValueError("Links must start with https://, http://, or mailto:.")
        return self._add(
            f"<a class='monty-link' href='{escape(url, quote=True)}' "
            f"target='_blank' rel='noopener noreferrer'>"
            f"{escape(str(label))}</a>"
        )

    def card(self, title, content):
        return self._add(
            "<section class='monty-card'>"
            f"<h2>{escape(str(title))}</h2>"
            f"<p>{escape(str(content))}</p>"
            "</section>"
        )

    def navbar(self, brand, links=None):
        links = links or []
        link_html = []
        for item in links:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise ValueError("Navbar links must look like [('Home', 'https://...')].")
            label, url = map(str, item)
            if not url.startswith(("https://", "http://", "#")):
                raise ValueError("Navbar links must use http://, https://, or #.")
            link_html.append(
                f"<a href='{escape(url, quote=True)}'>{escape(label)}</a>"
            )
        self._nav_added = True
        return self._add(
            "<nav class='monty-navbar'>"
            f"<strong>{escape(str(brand))}</strong>"
            f"<div>{''.join(link_html)}</div></nav>"
        )

    def footer(self, content):
        return self._add(
            f"<footer class='monty-footer'>{escape(str(content))}</footer>"
        )

    def input(self, label, placeholder="Type here"):
        safe_label = escape(str(label))
        safe_placeholder = escape(str(placeholder), quote=True)
        field_id = f"field-{len(self.elements)}"
        return self._add(
            "<label class='monty-field' "
            f"for='{field_id}'>{safe_label}"
            f"<input id='{field_id}' placeholder='{safe_placeholder}'>"
            "</label>"
        )

    def form(self, fields, button_label="Submit"):
        if not isinstance(fields, (list, tuple)):
            raise ValueError("form() expects a list of field names.")
        field_markup = []
        for index, field in enumerate(fields):
            label = escape(str(field))
            field_markup.append(
                f"<label class='monty-field'>{label}"
                f"<input name='field{index}' placeholder='Enter {label}' required>"
                "</label>"
            )
        return self._add(
            "<form class='monty-form' "
            "onsubmit=\"event.preventDefault(); "
            "alert('Your form was submitted!');\">"
            + "".join(field_markup)
            + f"<button class='monty-button' type='submit'>"
              f"{escape(str(button_label))}</button></form>"
        )

    def columns(self, *items):
        cells = "".join(
            f"<div class='monty-column'><p>{escape(str(item))}</p></div>"
            for item in items
        )
        return self._add(f"<div class='monty-columns'>{cells}</div>")

    def divider(self):
        return self._add("<hr class='monty-divider'>")

    def spacer(self, size=24):
        size = max(0, min(300, int(size)))
        return self._add(f"<div style='height:{size}px'></div>")

    def background_color(self, color):
        self.background = str(color)
        return self

    def color(self, color):
        self.foreground = str(color)
        return self

    def accent_color(self, color):
        self.accent = str(color)
        return self

    def font(self, family):
        self.font_family = str(family)
        return self

    def custom_css(self, css):
        # Custom CSS is intentionally supported for the website creator.
        self.custom_css_rules.append(str(css))
        return self

    def animate(self, content, effect="fade"):
        allowed = {"fade", "slide", "pop"}
        if effect not in allowed:
            raise ValueError("Animation must be fade, slide, or pop.")
        return self._add(
            f"<div class='monty-animate {effect}'>"
            f"{escape(str(content))}</div>"
        )

    def run(self):
        global last_website_html
        body = "\n".join(self.elements)
        custom_css = "\n".join(self.custom_css_rules)
        self.html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(self.title)}</title>
<style>
:root {{ --accent: {self.accent}; }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; padding: 32px;
  background: {self.background}; color: {self.foreground};
  font-family: {self.font_family}; line-height: 1.6;
}}
main {{ max-width: 1050px; margin: 0 auto; }}
h1, h2, h3 {{ line-height: 1.2; }}
.monty-navbar {{
  display:flex; justify-content:space-between; align-items:center;
  gap:18px; padding:16px 20px; margin:-32px -32px 30px;
  background:#171827; color:white; flex-wrap:wrap;
}}
.monty-navbar div {{ display:flex; gap:16px; flex-wrap:wrap; }}
.monty-navbar a {{ color:white; text-decoration:none; }}
.monty-button {{
  display:inline-block; border:0; border-radius:9px; padding:12px 20px;
  margin:8px 8px 8px 0; background:var(--accent); color:white;
  font-size:15px; cursor:pointer; transition:transform .2s, filter .2s;
}}
.monty-button:hover {{ transform:translateY(-2px); filter:brightness(1.1); }}
.monty-link {{ color:var(--accent); margin:8px; }}
.monty-image {{
  display:block; max-width:100%; height:auto; max-height:420px;
  object-fit:cover; border-radius:14px; margin:18px 0;
}}
.monty-card {{
  padding:22px; margin:14px 0; border-radius:14px;
  background:rgba(127,127,127,.10); box-shadow:0 5px 20px rgba(0,0,0,.08);
}}
.monty-columns {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
  gap:16px; margin:18px 0;
}}
.monty-column {{ padding:16px; border-radius:12px; background:rgba(127,127,127,.10); }}
.monty-field {{ display:block; margin:12px 0; font-weight:600; }}
.monty-field input {{
  display:block; width:100%; max-width:440px; padding:12px;
  margin-top:6px; border:1px solid #aaa; border-radius:8px; font:inherit;
}}
.monty-form {{ padding:18px; border:1px solid #aaa5; border-radius:12px; }}
.monty-divider {{ border:0; border-top:1px solid #8887; margin:24px 0; }}
.monty-footer {{ margin:35px -32px -32px; padding:22px; text-align:center; background:#171827; color:white; }}
.monty-animate.fade {{ animation:fadeIn .8s ease both; }}
.monty-animate.slide {{ animation:slideIn .8s ease both; }}
.monty-animate.pop {{ animation:popIn .5s ease both; }}
@keyframes fadeIn {{ from {{opacity:0}} to {{opacity:1}} }}
@keyframes slideIn {{ from {{opacity:0;transform:translateY(18px)}} to {{opacity:1;transform:none}} }}
@keyframes popIn {{ from {{opacity:0;transform:scale(.85)}} to {{opacity:1;transform:scale(1)}} }}
{custom_css}
@media (max-width:600px) {{
  body {{ padding:20px; }}
  .monty-navbar {{ margin:-20px -20px 24px; }}
  .monty-footer {{ margin:28px -20px -20px; }}
}}
</style>
</head>
<body><main>{body}</main></body>
</html>"""
        return "Website created! Check the Website Preview."


def run_monty(code, inputs):
    from monty_engine import run_monty as run_safe_monty

    return run_safe_monty(
        code,
        inputs,
        max_output=20_000,
        website_factory=Website
    )


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, content, content_type):
        data = content if isinstance(content, bytes) else content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = unquote(self.path.split("?", 1)[0])
        if path == "/":
            path = "/index.html"
        target = (WEB_DIR / path.lstrip("/")).resolve()
        if WEB_DIR.resolve() not in target.parents and target != WEB_DIR.resolve():
            self.send_error(403)
            return
        if not target.is_file():
            self.send_error(404)
            return
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
        }.get(target.suffix, "application/octet-stream")
        self._send(200, target.read_bytes(), content_type)

    def do_POST(self):
        if self.path != "/run":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length))
            result = run_monty(data.get("code", ""), data.get("inputs", []))
            self._send(200, json.dumps(result), "application/json; charset=utf-8")
        except Exception as error:
            self._send(500, json.dumps({"output": f"Server error: {error}"}),
                       "application/json; charset=utf-8")

    def log_message(self, format, *args):
        print("[Monty server] " + (format % args))


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Monty Playground is running.")
    print("Open Chrome: http://127.0.0.1:8000")
    print("Press CTRL+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMonty stopped.")
        server.server_close()
 
def application(environ, start_response):
    """PythonAnywhere WSGI entry point."""

    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")

    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin",
         "https://ariomoshfeqi-cell.github.io"),
        ("Access-Control-Allow-Methods", "POST, OPTIONS, GET"),
        ("Access-Control-Allow-Headers", "Content-Type"),
        ("X-Content-Type-Options", "nosniff"),
    ]

    def respond(status, body):
        data = body.encode("utf-8")
        start_response(
            status,
            headers + [("Content-Length", str(len(data)))]
        )
        return [data]

    if method == "OPTIONS":
        return respond("200 OK", "")

    if method == "GET" and path == "/":
        return respond("200 OK", '{"status":"Monty backend online"}')

    if method != "POST" or path != "/run":
        return respond("404 Not Found", '{"error":"Not found"}')

    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)

        if length <= 0 or length > 65536:
            return respond(
                "413 Payload Too Large",
                '{"error":"Invalid request size"}'
            )

        raw_data = environ["wsgi.input"].read(length)
        data = json.loads(raw_data.decode("utf-8"))

        code = data.get("code", "")
        inputs = data.get("inputs", [])

        if not isinstance(code, str) or not isinstance(inputs, list):
            return respond("400 Bad Request", '{"error":"Invalid data"}')

        result = run_monty(code, inputs)

        return respond("200 OK", json.dumps(result))

    except Exception:
        return respond("500 Internal Server Error",
                       '{"error":"Backend error"}')
