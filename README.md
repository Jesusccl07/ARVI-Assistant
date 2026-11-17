# ARVI — web de documentación

Sitio estático (GitHub Pages) con la memoria, el diario, las pruebas y la arquitectura de ARVI.

## Reconstruir la web

```bash
pip install beautifulsoup4 lxml
python3 build.py
```

- `src/content/**` — contenido de cada página (fragmentos HTML).
- `src/pages.json` — títulos y descripciones.
- `src/static/` — CSS, JS (esfera, búsqueda, portada) e imágenes; se copia a `assets/`.
- `build.py` — genera todas las páginas, la portada, el 404, `search-index.json` y `sitemap.xml` en la raíz.

Para verla en local: `python3 -m http.server 8000` y abrir <http://localhost:8000>.
