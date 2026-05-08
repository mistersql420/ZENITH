#!/usr/bin/env python3
"""
Generador de Brochure de Lujo para Propiedades Inmobiliarias
Crea un brochure estilo magazine en HTML listo para imprimir como PDF.

Uso:
    python generar_brochure.py                        # Demo con datos de ejemplo
    python generar_brochure.py datos.json             # Desde JSON
    python generar_brochure.py datos.json salida.html # Con nombre de archivo

Para imprimir como PDF:
    Abre el HTML en Chrome → Ctrl+P → Guardar como PDF
    Configuración: Sin márgenes · Gráficos de fondo: activado
"""

import anthropic
import json
import sys
import base64
import mimetypes
import argparse
from pathlib import Path

# ── DATOS DE EJEMPLO ──────────────────────────────────────────────────────────
EXAMPLE_DATA = {
    "nombre": "Treetop Sanctuary",
    "tagline": "Donde la Selva Construyó a Su Alrededor",
    "ubicacion": "Riviera Nayarit, México",
    "descripcion": (
        "Villa de lujo de 370 m² elevada sobre la ladera selvática de Riviera Nayarit. "
        "Troncos ancestrales atraviesan el techo de palapa. Árboles reales sirven como columnas. "
        "Alberca privada iluminada de noche, cocina de chef con isla de mármol, "
        "terrazas multinivel, acceso a beach club exclusivo y seguridad privada 24/7. "
        "Limpieza diaria incluida. Textiles mexicanos artesanales. Baños con amenidades premium."
    ),
    "precio": "Consultar disponibilidad",
    "whatsapp": "+523221234567",
    "fotos": [
        "https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=1600&q=90",
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1600&q=90",
        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1600&q=90",
        "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=1600&q=90",
        "https://images.unsplash.com/photo-1560185007-cde436f6a4d0?w=1600&q=90",
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1600&q=90",
    ],
    "agente": {
        "nombre": "Ana García",
        "telefono": "+52 322 123 4567",
        "email": "ana@luxurynayarit.com",
    },
}

SYSTEM_PROMPT = """Eres un copywriter de lujo especializado en bienes raíces premium en México.
Tu estilo es evocador, sensorial y aspiracional — como las mejores revistas de arquitectura y viajes.
Nunca uses lenguaje de vendedor ni clichés. Cada frase debe hacer que el lector quiera estar ahí.
Devuelve ÚNICAMENTE JSON válido, sin markdown ni explicaciones."""


# ── PROCESAMIENTO DE FOTOS ────────────────────────────────────────────────────

def process_photos(fotos: list) -> list:
    sources = []
    for foto in fotos:
        path = Path(foto)
        if path.exists() and path.is_file():
            mime, _ = mimetypes.guess_type(str(path))
            mime = mime or "image/jpeg"
            if mime.startswith("image/"):
                data = path.read_bytes()
                b64 = base64.b64encode(data).decode("ascii")
                sources.append(f"data:{mime};base64,{b64}")
                print(f"  📸 {path.name} ({len(data)/1024:.0f} KB)")
            else:
                sources.append(foto)
        else:
            sources.append(foto)
    return sources


# ── GENERACIÓN DE COPY ────────────────────────────────────────────────────────

def generate_copy(data: dict) -> dict:
    client = anthropic.Anthropic()
    print("✍️  Generando copy de marketing con IA...", flush=True)

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Crea el copy completo para un brochure de lujo de esta propiedad.

PROPIEDAD: {data.get('nombre')}
UBICACIÓN: {data.get('ubicacion')}
DESCRIPCIÓN: {data.get('descripcion')}
PRECIO: {data.get('precio')}

Devuelve este JSON exacto con copy evocador y poético para cada sección:
{{
    "portada": {{
        "titulo": "Título impactante de 2-5 palabras (puede ser en 2 líneas con \\n)",
        "subtitulo": "Frase poética que completa el título — máx 8 palabras",
        "etiqueta": "RIVIERA NAYARIT · MÉXICO"
    }},
    "experiencia": {{
        "seccion": "LA EXPERIENCIA",
        "titular": "Frase de impacto en negrita (6-8 palabras)",
        "subtitular": "Frase en cursiva complementaria (4-6 palabras)",
        "parrafos": [
            "Párrafo 1 — 45-60 palabras, evocador y sensorial",
            "Párrafo 2 — 40-55 palabras, profundiza en la experiencia",
            "Párrafo 3 — 25-35 palabras, cierre poético"
        ]
    }},
    "arquitectura": {{
        "seccion": "DISEÑO Y ARQUITECTURA",
        "titular": "Título evocador sobre la arquitectura (4-6 palabras)",
        "parrafos": [
            "Párrafo 1 — 35-50 palabras sobre materiales y estructura",
            "Párrafo 2 — 35-50 palabras sobre espacios y luz",
            "Párrafo final en cursiva — 15-25 palabras, filosófico"
        ]
    }},
    "amenidades": {{
        "seccion": "AMENIDADES DE CLASE MUNDIAL",
        "lista": [
            {{"titulo": "Nombre amenidad", "descripcion": "detalle corto · en este formato"}},
            {{"titulo": "Nombre amenidad", "descripcion": "detalle corto · en este formato"}},
            {{"titulo": "Nombre amenidad", "descripcion": "detalle corto · en este formato"}},
            {{"titulo": "Nombre amenidad", "descripcion": "detalle corto · en este formato"}},
            {{"titulo": "Nombre amenidad", "descripcion": "detalle corto · en este formato"}},
            {{"titulo": "Nombre amenidad", "descripcion": "detalle corto · en este formato"}},
            {{"titulo": "Nombre amenidad", "descripcion": "detalle corto · en este formato"}},
            {{"titulo": "Nombre amenidad", "descripcion": "detalle corto · en este formato"}},
            {{"titulo": "Nombre amenidad", "descripcion": "detalle corto · en este formato"}}
        ]
    }},
    "habitaciones": {{
        "seccion": "LAS HABITACIONES",
        "titular": "Título evocador sobre el descanso (3-5 palabras)",
        "parrafos": [
            "Párrafo 1 — 40-55 palabras sobre los espacios de dormir",
            "Párrafo 2 — 35-50 palabras sobre los detalles y textiles",
            "Cierre en cursiva — 15-20 palabras, invitación poética"
        ]
    }},
    "quote": "Una frase memorable de 3-6 palabras que defina la esencia de la propiedad",
    "cta": {{
        "titular_linea1": "Primera línea del título CTA (2-3 palabras)",
        "titular_linea2": "Segunda línea del título CTA (1-2 palabras)",
        "cuerpo": "Párrafo de cierre — 30-40 palabras, crea urgencia elegante y emocional",
        "boton": "CONSULTA DISPONIBILIDAD AHORA",
        "pie": "{data.get('ubicacion', 'RIVIERA NAYARIT · MÉXICO').upper()}"
    }}
}}"""
        }],
    )

    json_text = ""
    for block in response.content:
        if block.type == "text":
            json_text = block.text
            break

    json_text = json_text.strip()
    for prefix in ("```json\n", "```json", "```\n", "```"):
        if json_text.startswith(prefix):
            json_text = json_text[len(prefix):]
            break
    if json_text.endswith("```"):
        json_text = json_text[:-3]

    return json.loads(json_text.strip())


# ── CONSTRUCCIÓN DEL HTML ─────────────────────────────────────────────────────

def build_html(data: dict, copy: dict, fotos: list) -> str:

    def foto(idx: int) -> str:
        if fotos:
            return fotos[idx % len(fotos)]
        return ""

    wa = data.get("whatsapp", "").replace("+", "").replace(" ", "")
    agente = data.get("agente", {})

    p   = copy.get("portada", {})
    exp = copy.get("experiencia", {})
    arq = copy.get("arquitectura", {})
    ame = copy.get("amenidades", {})
    hab = copy.get("habitaciones", {})
    cta = copy.get("cta", {})

    titulo_portada = p.get("titulo", data.get("nombre", "")).replace("\n", "<br>")

    exp_html = "".join(
        f'<p class="italic">{t}</p>' if i == len(exp.get("parrafos", [])) - 1
        else f"<p>{t}</p>"
        for i, t in enumerate(exp.get("parrafos", []))
    )
    arq_html = "".join(
        f'<p class="italic">{t}</p>' if i == len(arq.get("parrafos", [])) - 1
        else f"<p>{t}</p>"
        for i, t in enumerate(arq.get("parrafos", []))
    )
    hab_html = "".join(
        f'<p class="italic">{t}</p>' if i == len(hab.get("parrafos", [])) - 1
        else f"<p>{t}</p>"
        for i, t in enumerate(hab.get("parrafos", []))
    )

    amenidades_html = ""
    for a in ame.get("lista", []):
        amenidades_html += f"""
            <div class="amenidad">
                <span class="amenidad-titulo">{a.get('titulo','')}</span>
                <span class="amenidad-desc">{a.get('descripcion','')}</span>
            </div>"""

    agente_info = " · ".join(filter(None, [
        agente.get("nombre", ""),
        agente.get("telefono", ""),
        agente.get("email", ""),
    ]))

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{data.get('nombre','Propiedad')} — Brochure</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Cormorant+Garamond:ital,wght@0,300;1,400;1,600&family=Montserrat:wght@300;400;600&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
    --gold:       #d4a853;
    --gold-light: #e9c46a;
    --dark:       #0a0a0a;
    --dark2:      #111111;
    --text:       #f0ece4;
    --muted:      #a89880;
}}

body {{
    font-family: 'Montserrat', sans-serif;
    background: #000;
    color: var(--text);
}}

/* ── PRINT ──────────────────────────────────────────── */
@media print {{
    @page {{ size: A4 portrait; margin: 0; }}
    body {{ background: #000; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .page {{ page-break-after: always; page-break-inside: avoid; }}
    .no-print {{ display: none !important; }}
}}

/* ── PAGE BASE ───────────────────────────────────────── */
.page {{
    width: 210mm;
    min-height: 297mm;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    background: var(--dark);
    margin: 0 auto;
}}

/* ── CORNER FRAMES ───────────────────────────────────── */
.frame > .f-inner::before,
.frame > .f-inner::after,
.frame > .f-inner > .f-bl::before,
.frame > .f-inner > .f-bl::after {{
    content: '';
    position: absolute;
    width: 16mm;
    height: 16mm;
    border-color: var(--gold);
    border-style: solid;
    opacity: 0.55;
    z-index: 20;
}}
.frame > .f-inner::before  {{ top: 7mm; left: 7mm;  border-width: 1px 0 0 1px; }}
.frame > .f-inner::after   {{ top: 7mm; right: 7mm; border-width: 1px 1px 0 0; }}
.frame > .f-inner > .f-bl::before {{ bottom: 7mm; left: 7mm;  border-width: 0 0 1px 1px; }}
.frame > .f-inner > .f-bl::after  {{ bottom: 7mm; right: 7mm; border-width: 0 1px 1px 0; }}
.f-inner {{ position: absolute; inset: 0; }}
.f-bl    {{ position: absolute; inset: 0; }}

/* ── TYPOGRAPHY ──────────────────────────────────────── */
h1, h2, h3 {{ font-family: 'Playfair Display', serif; }}

.section-label {{
    font-family: 'Montserrat', sans-serif;
    font-size: 7.5pt;
    letter-spacing: 0.28em;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 5mm;
    text-align: center;
}}
.section-label::before,
.section-label::after {{ content: '—'; margin: 0 7px; opacity: 0.6; }}

.divider {{
    display: flex;
    align-items: center;
    gap: 3.5mm;
    margin: 4mm 0 6mm;
}}
.divider::before,
.divider::after {{
    content: '';
    flex: 1;
    height: 0.3mm;
    background: var(--gold);
    opacity: 0.45;
}}
.diamond {{
    width: 3.5mm;
    height: 3.5mm;
    background: var(--gold);
    transform: rotate(45deg);
    flex-shrink: 0;
}}

p {{
    font-size: 9.5pt;
    line-height: 1.8;
    color: #c5bbb0;
    margin-bottom: 4mm;
}}
p.italic {{
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 11.5pt;
    color: var(--muted);
    line-height: 1.6;
}}

/* ══ PÁGINA 1 — PORTADA ══════════════════════════════ */
.portada-img {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.62;
}}
.portada-overlay {{
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.88) 28%, rgba(0,0,0,0.15) 65%);
}}
.portada-content {{
    position: relative;
    z-index: 5;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    height: 297mm;
    padding: 18mm 16mm 20mm;
}}
.portada-etiqueta {{
    font-size: 7pt;
    letter-spacing: 0.3em;
    color: var(--gold);
    margin-bottom: 6mm;
}}
.portada-titulo {{
    font-size: 46pt;
    font-weight: 900;
    line-height: 1.05;
    color: #fff;
    margin-bottom: 4mm;
}}
.portada-subtitulo {{
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 16pt;
    color: var(--gold-light);
    margin-bottom: 9mm;
}}
.portada-badges {{
    display: flex;
    gap: 0;
    font-size: 7pt;
    letter-spacing: 0.18em;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
}}
.portada-badges span + span::before {{ content: ' · '; margin: 0 6px; }}

/* ══ PÁGINAS 2–3 — DOS COLUMNAS ══════════════════════ */
.two-col {{
    flex-direction: row;
    min-height: 297mm;
}}
.col-text {{
    flex: 1;
    padding: 22mm 14mm 18mm;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: var(--dark2);
}}
.col-img {{
    width: 48%;
    position: relative;
    overflow: hidden;
}}
.col-img img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}
.two-col h2 {{
    font-size: 24pt;
    font-weight: 700;
    line-height: 1.18;
    color: #fff;
    margin-bottom: 2mm;
}}
.titular-strong {{ font-weight: 900; display: block; }}
.titular-italic {{
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 15pt;
    font-weight: 400;
    color: var(--gold-light);
    display: block;
    margin-top: 2mm;
    margin-bottom: 5mm;
}}

/* ══ PÁGINA 4 — AMENIDADES ════════════════════════════ */
.amenidades-bg {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.22;
}}
.amenidades-content {{
    position: relative;
    z-index: 5;
    padding: 18mm 16mm 16mm;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    min-height: 297mm;
}}
.amenidades-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4.5mm 10mm;
    margin-top: 6mm;
}}
.amenidad {{
    display: flex;
    flex-direction: column;
    padding-bottom: 4mm;
    border-bottom: 0.3mm solid rgba(212,168,83,0.2);
}}
.amenidad-titulo {{
    font-size: 8.5pt;
    font-weight: 600;
    color: var(--gold);
    margin-bottom: 1mm;
    letter-spacing: 0.04em;
}}
.amenidad-desc {{
    font-size: 8pt;
    color: var(--muted);
    line-height: 1.5;
}}

/* ══ PÁGINA 6 — QUOTE ════════════════════════════════ */
.quote-bg {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.28;
}}
.quote-content {{
    position: relative;
    z-index: 5;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 297mm;
    padding: 20mm;
    text-align: center;
}}
.quote-text {{
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 34pt;
    font-weight: 400;
    color: #fff;
    line-height: 1.3;
}}

/* ══ PÁGINA 7 — CTA ══════════════════════════════════ */
.cta-inner {{
    position: relative;
    z-index: 5;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 297mm;
    padding: 22mm 18mm;
    text-align: center;
}}
.cta-titulo {{
    font-size: 40pt;
    font-weight: 900;
    color: #fff;
    line-height: 1.05;
    margin-bottom: 4mm;
}}
.cta-titulo span {{
    display: block;
    font-weight: 300;
    font-size: 34pt;
}}
.cta-cuerpo {{
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 13pt;
    color: var(--muted);
    line-height: 1.85;
    margin-bottom: 9mm;
    max-width: 130mm;
}}
.cta-boton {{
    display: inline-block;
    border: 0.4mm solid var(--gold);
    color: var(--gold);
    font-size: 7pt;
    letter-spacing: 0.25em;
    padding: 4mm 10mm;
    text-decoration: none;
    margin-bottom: 9mm;
    font-family: 'Montserrat', sans-serif;
}}
.cta-agente {{
    font-size: 8pt;
    color: rgba(255,255,255,0.35);
    line-height: 1.9;
    margin-top: 4mm;
}}
.cta-pie {{
    position: absolute;
    bottom: 12mm;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 7pt;
    letter-spacing: 0.22em;
    color: rgba(255,255,255,0.18);
}}

/* ── BOTÓN IMPRIMIR ──────────────────────────────────── */
.print-btn {{
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: var(--gold);
    color: #000;
    border: none;
    padding: 13px 26px;
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.12em;
    cursor: pointer;
    z-index: 999;
    text-transform: uppercase;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}}
.print-btn:hover {{ background: var(--gold-light); }}
</style>
</head>
<body>

<button class="print-btn no-print" onclick="window.print()">🖨 Imprimir / Guardar PDF</button>

<!-- ═══════════════════════════════════════
     PÁGINA 1 — PORTADA
═══════════════════════════════════════ -->
<div class="page frame">
  <div class="f-inner"><div class="f-bl"></div></div>
  <img class="portada-img" src="{foto(0)}" alt="Portada">
  <div class="portada-overlay"></div>
  <div class="portada-content">
    <div class="portada-etiqueta">{p.get('etiqueta', data.get('ubicacion','').upper())}</div>
    <h1 class="portada-titulo">{titulo_portada}</h1>
    <div class="portada-subtitulo">{p.get('subtitulo', data.get('tagline',''))}</div>
    <div class="portada-badges">
      <span>Privado</span>
      <span>Exclusivo</span>
      <span>Inolvidable</span>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════
     PÁGINA 2 — LA EXPERIENCIA
═══════════════════════════════════════ -->
<div class="page two-col">
  <div class="col-text">
    <div class="section-label">{exp.get('seccion','La Experiencia')}</div>
    <h2>
      <span class="titular-strong">{exp.get('titular','')}</span>
      <span class="titular-italic">{exp.get('subtitular','')}</span>
    </h2>
    <div class="divider"><div class="diamond"></div></div>
    {exp_html}
  </div>
  <div class="col-img">
    <img src="{foto(1)}" alt="Experiencia">
  </div>
</div>

<!-- ═══════════════════════════════════════
     PÁGINA 3 — DISEÑO Y ARQUITECTURA
═══════════════════════════════════════ -->
<div class="page two-col">
  <div class="col-img">
    <img src="{foto(2)}" alt="Arquitectura">
  </div>
  <div class="col-text">
    <div class="section-label">{arq.get('seccion','Diseño y Arquitectura')}</div>
    <h2>{arq.get('titular','')}</h2>
    <div class="divider"><div class="diamond"></div></div>
    {arq_html}
  </div>
</div>

<!-- ═══════════════════════════════════════
     PÁGINA 4 — AMENIDADES
═══════════════════════════════════════ -->
<div class="page">
  <img class="amenidades-bg" src="{foto(3)}" alt="Amenidades">
  <div class="amenidades-content">
    <div class="section-label">{ame.get('seccion','Amenidades de Clase Mundial')}</div>
    <div class="divider"><div class="diamond"></div></div>
    <div class="amenidades-grid">
      {amenidades_html}
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════
     PÁGINA 5 — LAS HABITACIONES
═══════════════════════════════════════ -->
<div class="page two-col">
  <div class="col-text">
    <div class="section-label">{hab.get('seccion','Las Habitaciones')}</div>
    <h2>{hab.get('titular','')}</h2>
    <div class="divider"><div class="diamond"></div></div>
    {hab_html}
  </div>
  <div class="col-img">
    <img src="{foto(4)}" alt="Habitaciones">
  </div>
</div>

<!-- ═══════════════════════════════════════
     PÁGINA 6 — QUOTE
═══════════════════════════════════════ -->
<div class="page frame">
  <div class="f-inner"><div class="f-bl"></div></div>
  <img class="quote-bg" src="{foto(5)}" alt="Quote">
  <div class="quote-content">
    <div class="quote-text">"{copy.get('quote','Privacidad.<br>Naturaleza.<br>Lujo.')}"</div>
  </div>
</div>

<!-- ═══════════════════════════════════════
     PÁGINA 7 — CTA
═══════════════════════════════════════ -->
<div class="page frame">
  <div class="f-inner"><div class="f-bl"></div></div>
  <div class="cta-inner">
    <div class="divider" style="width:60mm;margin-bottom:8mm"><div class="diamond"></div></div>
    <h2 class="cta-titulo">
      {cta.get('titular_linea1','Reserva Tu')}
      <span>{cta.get('titular_linea2','Escape.')}</span>
    </h2>
    <p class="cta-cuerpo">{cta.get('cuerpo','')}</p>
    <a class="cta-boton" href="https://wa.me/{wa}" target="_blank">
      {cta.get('boton','CONSULTA DISPONIBILIDAD AHORA')}
    </a>
    <div class="cta-agente">{agente_info}</div>
    <div class="cta-pie">{cta.get('pie', data.get('ubicacion','').upper())}</div>
  </div>
</div>

</body>
</html>"""


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generador de brochure de lujo para propiedades inmobiliarias",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input",  nargs="?", help="JSON con datos de la propiedad")
    parser.add_argument("output", nargs="?", default="brochure.html", help="Archivo HTML de salida")
    args = parser.parse_args()

    if args.input is None:
        data = EXAMPLE_DATA
        print("ℹ️  Usando datos de ejemplo.\n")
    else:
        json_path = Path(args.input)
        if not json_path.exists():
            print(f"❌ Archivo no encontrado: {json_path}")
            sys.exit(1)
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            print(f"✅ Datos cargados desde: {json_path}\n")
        except json.JSONDecodeError as e:
            print(f"❌ JSON inválido: {e}")
            sys.exit(1)

    print("━" * 50)
    print("  📖 GENERADOR DE BROCHURE DE LUJO")
    print(f"  📍 {data.get('ubicacion','')}")
    print("━" * 50)
    print(f"  Propiedad : {data.get('nombre','Sin nombre')}")
    print(f"  Salida    : {args.output}")
    print("━" * 50 + "\n")

    if data.get("fotos"):
        print("📸 Procesando fotos...")
        data["fotos"] = process_photos(data["fotos"])
        print()

    copy = generate_copy(data)
    print("✅ Copy generado\n")

    print("🏗️  Construyendo HTML...", flush=True)
    html = build_html(data, copy, data.get("fotos", []))

    output_path = Path(args.output)
    output_path.write_text(html, encoding="utf-8")
    size_kb = output_path.stat().st_size / 1024

    print(f"\n{'━'*50}")
    print(f"  ✅  ¡Brochure generado!")
    print(f"  📄  Archivo : {output_path.absolute()}")
    print(f"  📦  Tamaño  : {size_kb:.1f} KB")
    print(f"\n  🖨️  Para exportar como PDF:")
    print(f"  1. Abre {args.output} en Chrome")
    print(f"  2. Ctrl+P → Guardar como PDF")
    print(f"  3. Márgenes: Ninguno  |  ✅ Gráficos de fondo")
    print("━" * 50)
    print("\n✨ ¡Listo!")


if __name__ == "__main__":
    main()
