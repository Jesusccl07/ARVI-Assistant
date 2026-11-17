"""Extrae el contenido de las páginas HTML generadas con MkDocs (commit original)
a fragmentos limpios en src/content/<ruta>.html. Se ejecuta una sola vez: el
resto del flujo trabaja con src/ y build.py."""
import subprocess, json, re, pathlib
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent
REV = "5191e38"
files = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", REV], cwd=ROOT, text=True).split("\n")
pages = [f for f in files if f.endswith("index.html")]
out = ROOT / "src" / "content"
meta = {}
for f in pages:
    if f == "404.html":
        continue
    html = subprocess.check_output(["git", "show", f"{REV}:{f}"], cwd=ROOT, text=True)
    soup = BeautifulSoup(html, "lxml")
    art = soup.select_one("article.md-content__inner")
    for a in art.select("a.headerlink"):
        a.decompose()
    for pre in art.select("pre.mermaid"):
        code = pre.get_text()
        pre.clear(); pre.string = code
    h1 = art.find("h1")
    title = h1.get_text(strip=True) if h1 else "ARVI"
    desc = ""
    p = art.find("p")
    if p: desc = re.sub(r"\s+", " ", p.get_text(" ", strip=True))[:180]
    route = f[:-len("index.html")].rstrip("/")
    dest = out / (route or "_home") / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if h1: h1.decompose()  # el título lo pinta la plantilla
    dest.write_text(art.decode_contents().strip() + "\n", encoding="utf-8")
    meta[route] = {"title": title, "description": desc}
(ROOT / "src" / "pages.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(meta), "páginas")
