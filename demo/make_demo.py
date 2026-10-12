"""Renderuje demo/queue.html (widok kolejki z panelu) i zrzut screenshots/kolejka.png.

Uruchom: python demo/make_demo.py   (zrzut wymaga: playwright install chromium)
"""
import html
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import approval, simulation  # noqa: E402

DNI = ["pon", "wt", "śr", "czw", "pt", "sob", "ndz"]
STATUS = {"opublikowany": ("ok", "Opublikowany"), "wstrzymany": ("wh", "Wstrzymany"),
          "blad": ("er", "Błąd publikacji"), "zaplanowany": ("pl", "Zaplanowany")}


def powod_wstrzymania(w, zgody):
    z = zgody.get(w["id"], {})
    if z.get("werdykt") == "odrzucony":
        kto = z.get("kto", "")
        if kto == "wlasciciel":
            return "Sprzeciw właściciela (weto)"
        return "Sędzia odrzucił: " + "; ".join(w["ocena"]["powody"])
    if z.get("odcisk") != approval.odcisk(w["obraz"], w["tresc"]):
        return "Treść zmieniona po zatwierdzeniu: odcisk się nie zgadza"
    return ""


def karta(w, zgody, zdarzenia):
    kl, nazwa = STATUS[w["status"]]
    d = datetime.fromisoformat(w["kiedy"])
    tresc = html.escape(w["tresc"].replace("\N{EM DASH}", "[znak zakazany]"))
    notka = next((n for i, s, n in zdarzenia if i == w["id"]), "")
    if w["status"] == "wstrzymany":
        notka = powod_wstrzymania(w, zgody)
    odc = zgody.get(w["id"], {}).get("odcisk", "")[:10] or "brak"
    return f"""<article class="c {kl}">
<div class="im"><span>{html.escape(w['temat'])}</span></div>
<div class="tx"><div class="top"><b>{DNI[d.weekday()]} {d:%d.%m} · {d:%H:%M}</b><span class="b {kl}">{nazwa}</span></div>
<p>{tresc}</p>
<small>odcisk zgody: <code>{odc}</code></small>
<small class="n">{html.escape(notka)}</small></div></article>"""


def strona():
    kolejka, zgody, zdarzenia, decyzje, _ = simulation.symuluj()
    kartki = "".join(karta(w, zgody, zdarzenia) for w in kolejka)
    dec = "".join(f"<li>Brak publikacji: {html.escape(x['wpis'])} ({html.escape(x['powod'])}). Czeka na decyzję człowieka.</li>"
                  for x in decyzje)
    return f"""<!doctype html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Kolejka treści</title>
<style>
:root{{--n:#0A95C9;--o:#FC6E08;--g:#021836;--bg:#f5f8fb;--line:#dbe4ec}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.5 system-ui,Segoe UI,sans-serif;background:var(--bg);color:var(--g)}}
main{{max-width:1100px;margin:0 auto;padding:26px 20px 40px}}h1{{margin:0 0 4px;font-size:26px}}
.s{{margin:0 0 20px;color:#476}}
.list{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}
@media(max-width:800px){{.list{{grid-template-columns:1fr}}}}
.c{{display:flex;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden}}
.c.wh{{border-left:5px solid #7a8a99}}.c.er{{border-left:5px solid #c2410c}}.c.ok{{border-left:5px solid var(--n)}}
.im{{width:96px;flex:none;display:flex;align-items:flex-end;padding:8px;color:#fff;font-size:12px;
  background:linear-gradient(160deg,var(--n),var(--g))}}
.tx{{padding:10px 14px;display:flex;flex-direction:column;gap:4px;min-width:0}}
.top{{display:flex;justify-content:space-between;gap:8px}}p{{margin:0}}
small{{color:#58708a}}small.n{{color:var(--g);font-weight:600}}code{{font-size:12px}}
.b{{padding:2px 9px;border-radius:99px;font-size:12px;font-weight:600;color:#fff;white-space:nowrap}}
.b.ok{{background:var(--n)}}.b.wh{{background:#7a8a99}}.b.er{{background:#c2410c}}.b.pl{{background:var(--o)}}
.al{{background:#fff4ec;border:1px solid #f9c9a3;border-radius:12px;padding:6px 18px;margin-bottom:16px}}
</style></head><body><main>
<h1>Kolejka treści Piekarni Przykładowej</h1>
<p class="s">Symulacja dwóch tygodni. Sędzia innego modelu ocenia, zgoda jest przywiązana do odcisku treści, publikator sprawdza w platformie, zanim ponowi.</p>
{('<div class="al"><ul>' + dec + '</ul></div>') if dec else ''}
<div class="list">{kartki}</div></main></body></html>"""


if __name__ == "__main__":
    out = ROOT / "demo" / "queue.html"
    out.write_text(strona(), encoding="utf-8")
    print("zapisano", out.relative_to(ROOT))
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 1280, "height": 800})
            pg.goto(out.as_uri())
            (ROOT / "screenshots").mkdir(exist_ok=True)
            pg.screenshot(path=str(ROOT / "screenshots" / "kolejka.png"), full_page=True)
            b.close()
        print("zrzut ok")
    except ImportError:
        print("brak playwright: pominięto zrzut")
