#!/usr/bin/env python3
"""
Generador de Landing Page + PDF para Propiedades en Bahía de Banderas
Usa la API de Anthropic (Claude) para crear una página HTML profesional con Tailwind CSS.

Uso:
    python generar_landing.py                                         # Características de ejemplo
    python generar_landing.py mis_features.json                       # Carga desde JSON
    python generar_landing.py mis_features.json mi.html               # HTML con nombre propio
    python generar_landing.py descripcion.txt --raw                   # Descripción en texto libre
    python generar_landing.py mis_features.json --pdf                 # HTML + PDF
    python generar_landing.py mis_features.json mi.html --pdf mi.pdf  # Todo personalizado

Instala dependencias opcionales para PDF:
    pip install reportlab
"""

import anthropic
import json
import sys
import base64
import mimetypes
import argparse
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        Image as RLImage, Table, TableStyle, HRFlowable,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ──────────────────────────────────────────────
# CARACTERÍSTICAS DE LA PROPIEDAD
# Modifica estos datos con los de tu propiedad real
# ──────────────────────────────────────────────
HOUSE_FEATURES = {
    "titulo": "Villa Palmeras – Bahía de Banderas",
    "subtitulo": "Exclusiva villa frente al mar con alberca infinita",
    "precio": "$4,500,000 MXN",
    "ubicacion": "Bahía de Banderas, Nayarit, México",
    "whatsapp": "+523221234567",
    "descripcion_larga": (
        "Descubre esta impresionante villa de lujo en la paradisíaca Bahía de Banderas, "
        "uno de los destinos más exclusivos del Pacífico mexicano. "
        "Con vistas panorámicas al océano y acceso a playa privada, esta propiedad combina "
        "la arquitectura contemporánea con el encanto tropical de la Riviera Nayarit. "
        "Perfecta como residencia principal, casa de vacaciones o inversión turística de alto rendimiento."
    ),
    "caracteristicas": [
        "4 recámaras con baño en suite",
        "3.5 baños",
        "Alberca infinita con vista al mar",
        "Terraza de 80 m² con jacuzzi",
        "Cocina gourmet equipada",
        "Sala de estar con techos de 5 m",
        "Jardín tropical con palmas",
        "Estacionamiento para 3 autos",
        "Sistema de seguridad 24/7",
        "Área de BBQ y bar exterior",
        "Acceso a playa privada",
        "350 m² de construcción",
        "700 m² de terreno",
        "Bodega y cuarto de servicio",
        "Sala de cine en casa",
        "Sistema de domótica",
    ],
    "fotos": [
        # Puedes mezclar URLs y rutas locales (ej: "C:/fotos/sala.jpg")
        "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=1200&q=80",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200&q=80",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200&q=80",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200&q=80",
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=1200&q=80",
        "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=1200&q=80",
        "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=1200&q=80",
        "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=1200&q=80",
    ],
    "agente": {
        "nombre": "Ana García Martínez",
        "titulo": "Especialista en Propiedades de Lujo",
        "telefono": "+52 322 123 4567",
        "email": "ana@propiedadesbanderas.com",
        "experiencia_anos": "12",
    },
    "extras": {
        "año_construccion": "2020",
        "estrato": "Residencial de lujo",
        "uso_suelo": "Habitacional / Turístico",
        "amueblada": True,
    },
}

SYSTEM_PROMPT = """Eres un experto en diseño web de alto nivel y en bienes raíces de lujo en México.
Tu especialidad es crear landing pages visualmente impactantes y completamente funcionales
para propiedades premium en destinos como Bahía de Banderas, Puerto Vallarta y la Riviera Nayarit.

Al generar HTML siempre:
- Produces código completo, limpio y listo para producción
- Usas Tailwind CSS desde CDN para estilos modernos y responsivos
- Usas AOS.js (Animate On Scroll) para animaciones elegantes de entrada al hacer scroll
- Usas Playfair Display (serif) para todos los títulos — nunca sans-serif en H1/H2
- Optimizas el diseño para dispositivos móviles (mobile-first)
- Produces SOLO el código HTML, sin explicaciones ni markdown"""


def parse_raw_description(raw_text: str) -> dict:
    """Usa Claude para extraer características estructuradas de una descripción en texto libre."""
    client = anthropic.Anthropic()
    print("🔍 Analizando descripción con IA...", flush=True)

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=3000,
        thinking={"type": "adaptive"},
        messages=[{
            "role": "user",
            "content": f"""Eres un experto en bienes raíces. Analiza esta descripción y extrae la información estructurada.

DESCRIPCIÓN:
{raw_text}

Devuelve ÚNICAMENTE un JSON válido con esta estructura exacta:
{{
    "titulo": "Nombre atractivo de la propiedad",
    "subtitulo": "Frase corta y atractiva",
    "precio": "Precio con formato (ej: $3,500,000 MXN)",
    "ubicacion": "Ciudad, Estado, País",
    "whatsapp": "+52XXXXXXXXXX",
    "descripcion_larga": "Descripción elaborada y atractiva para la landing page",
    "caracteristicas": [
        "Característica 1",
        "Característica 2"
    ],
    "fotos": [],
    "agente": {{
        "nombre": "Nombre del agente",
        "titulo": "Título profesional",
        "telefono": "+52 XXX XXX XXXX",
        "email": "agente@email.com",
        "experiencia_anos": "X"
    }},
    "extras": {{
        "año_construccion": "XXXX",
        "estrato": "Residencial",
        "uso_suelo": "Habitacional",
        "amueblada": false
    }}
}}

Si algún dato no aparece en la descripción, infiere un valor razonable o usa cadena vacía.
Devuelve SOLO el JSON, sin texto adicional ni markdown.""",
        }],
    )

    # Extraer texto saltando bloques de thinking
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

    features = json.loads(json_text.strip())
    print("✅ Características extraídas exitosamente\n")
    return features


def process_photos(fotos: list, json_dir: Path = None) -> tuple:
    """
    Procesa la lista de fotos.
    - URLs HTTP/HTTPS → se usan tal cual en HTML.
    - Rutas de archivo local → se codifican en base64 para HTML autónomo.
    Retorna (html_sources, local_paths):
      html_sources  = lista de src para <img> en HTML
      local_paths   = lista de rutas absolutas (None para URLs) para usar en PDF
    """
    html_sources: list[str] = []
    local_paths: list = []

    for foto in fotos:
        path = Path(foto)
        # Si la ruta es relativa, resolverla desde el directorio del JSON
        if not path.is_absolute() and json_dir:
            path = (json_dir / path).resolve()
        if path.exists() and path.is_file():
            mime, _ = mimetypes.guess_type(str(path))
            mime = mime or "image/jpeg"
            if mime.startswith("image/"):
                data = path.read_bytes()
                b64 = base64.b64encode(data).decode("ascii")
                html_sources.append(f"data:{mime};base64,{b64}")
                local_paths.append(str(path.resolve()))
                print(f"  📸 Foto local: {path.name} ({len(data)/1024:.0f} KB)", flush=True)
            else:
                print(f"  ⚠️  Tipo no reconocido, usando como URL: {foto}")
                html_sources.append(foto)
                local_paths.append(None)
        else:
            html_sources.append(foto)
            local_paths.append(None)

    return html_sources, local_paths


def build_prompt(features: dict) -> str:
    wa_number = features.get("whatsapp", "").replace("+", "").replace(" ", "")
    wa_message = f"Hola, me interesa la propiedad: {features.get('titulo', 'sin título')}"
    wa_url = f"https://wa.me/{wa_number}?text={wa_message.replace(' ', '%20')}"

    fotos_html = "\n".join(f'    "{url}"' for url in features.get("fotos", []))
    caracteristicas_txt = "\n".join(f"  - {c}" for c in features.get("caracteristicas", []))
    agente = features.get("agente", {})

    return f"""Genera una landing page HTML completa y profesional para esta propiedad inmobiliaria.

══════════════════════════════════
DATOS DE LA PROPIEDAD
══════════════════════════════════
Título: {features.get("titulo")}
Subtítulo: {features.get("subtitulo")}
Precio: {features.get("precio")}
Ubicación: {features.get("ubicacion")}
Descripción: {features.get("descripcion_larga")}

CARACTERÍSTICAS:
{caracteristicas_txt}

FOTOS (URLs o data URIs base64 a usar en la galería):
{fotos_html}

AGENTE:
  Nombre: {agente.get("nombre")}
  Título: {agente.get("titulo")}
  Teléfono: {agente.get("telefono")}
  Email: {agente.get("email")}
  Experiencia: {agente.get("experiencia_anos")} años

CONTACTO WHATSAPP:
  URL completa: {wa_url}

══════════════════════════════════
ESPECIFICACIONES TÉCNICAS
══════════════════════════════════

1. TECNOLOGÍAS:
   - HTML5 completo (DOCTYPE, head, body)
   - Tailwind CSS: <script src="https://cdn.tailwindcss.com"></script>
   - Google Fonts: Playfair Display (400, 700, 900 italic) para títulos; Inter para cuerpo
   - AOS.js — incluir en el <head> ANTES del cierre </head>:
       <link href="https://unpkg.com/aos@2.3.4/dist/aos.css" rel="stylesheet">
     Y al final del <body> ANTES del cierre </body>:
       <script src="https://unpkg.com/aos@2.3.4/dist/aos.js"></script>
       <script>AOS.init({{ duration: 1000, easing: 'ease-out-cubic', once: true, offset: 80 }});</script>
   - JavaScript vanilla (NO frameworks externos)

2. PALETA DE COLORES:
   - Primario: azul océano profundo (#0a4d68, #005f73)
   - Secundario: verde tropical (#52b788, #40916c)
   - Acento: arena/oro (#d4a853, #e9c46a)
   - Fondo oscuro: #0d1b2a
   - Texto claro: #f8f9fa

3. SECCIONES OBLIGATORIAS EN ESTE ORDEN:

   A) NAVBAR fijo
      - Logo/nombre de agencia (izquierda)
      - Links: Galería | Características | Contacto
      - Botón "Contactar" en color acento
      - Efecto blur/glassmorphism al hacer scroll

   B) HERO SECTION — diseño asimétrico en dos columnas (100vh, sin scroll)

      ESTRUCTURA DE GRID (CSS Grid, no Flexbox):
      ┌─────────────────────────┬──────────────────────────┐
      │  COLUMNA IZQUIERDA 55%  │   COLUMNA DERECHA 45%    │
      │  fondo: #0d1b2a         │   GRID ASIMÉTRICO        │
      │  texto + CTA            │ ┌────────────┬─────────┐ │
      │                         │ │            │  foto 2 │ │
      │                         │ │   foto 1   ├─────────┤ │
      │                         │ │ (altura    │  foto 3 │ │
      │                         │ │  completa) │         │ │
      │                         │ └────────────┴─────────┘ │
      └─────────────────────────┴──────────────────────────┘
      En mobile: columna izquierda encima, fotos debajo en row de 3.

      COLUMNA IZQUIERDA — contenido:
      - Padding generoso (px-16 py-24 desktop / px-8 py-16 mobile)
      - Etiqueta pequeña en caps: "RIVIERA NAYARIT · LUJO" color acento dorado, tracking-widest, text-xs
      - Título H1: Playfair Display 900, 5xl→7xl, blanco, leading tight
        · El nombre de la propiedad en cursiva (font-italic) en color blanco
        · Salto de línea antes de la segunda parte del título si es largo
      - Subtítulo: Playfair Display italic 400, xl, color #d4a853 (dorado), mt-4
      - Separador decorativo: línea horizontal 60px ancho, 2px, color dorado, my-6
      - Precio: badge/pill — borde 1px dorado, fondo transparente con blur,
        Playfair Display Bold, 2xl, color blanco, px-6 py-2, rounded-full
      - Descripción corta: Inter, text-sm, color #94a3b8 (gris azulado), max-w-sm, mt-4, leading-relaxed
        (solo primeras ~100 palabras de descripcion_larga)
      - Dos botones CTA en fila (mt-8):
          · "Ver Propiedad" — fondo dorado (#d4a853), texto oscuro, rounded-full, font-semibold
          · Botón WhatsApp — borde blanco, texto blanco, rounded-full, ícono SVG WhatsApp inline

      COLUMNA DERECHA — grid asimétrico de fotos (sin padding extra, flush):
      CSS Grid con template-columns: 60% 40% y template-rows: 50% 50%
      - foto[0]: col 1, row 1-2 (span 2 filas), object-cover, w-full h-full
      - foto[1]: col 2, row 1, object-cover, w-full h-full
      - foto[2]: col 2, row 2, object-cover, w-full h-full
      Cada foto tiene un overlay hover con opacity-0 → opacity-30 de color negro, transition 300ms.
      Si hay menos de 3 fotos, la foto[0] ocupa todo el ancho.

      ANIMACIONES AOS (en el HTML, atributos data-aos):
      - Etiqueta "RIVIERA NAYARIT":  data-aos="fade-down" data-aos-delay="0"
      - H1:                          data-aos="fade-right" data-aos-delay="150"
      - Subtítulo + separador:       data-aos="fade-right" data-aos-delay="300"
      - Badge precio:                data-aos="fade-up" data-aos-delay="400"
      - Descripción corta:           data-aos="fade-up" data-aos-delay="500"
      - Botones CTA:                 data-aos="fade-up" data-aos-delay="650"
      - foto[0]:                     data-aos="fade-left" data-aos-delay="200"
      - foto[1]:                     data-aos="fade-left" data-aos-delay="350"
      - foto[2]:                     data-aos="fade-left" data-aos-delay="500"

   C) HIGHLIGHTS (3 tarjetas)
      - Íconos SVG inline (no librerías)
      - Ubicación, Superficie total, Precio por m²
      - Diseño glassmorphism con fondo oscuro

   D) GALERÍA DE FOTOS
      - Grid responsivo: 4 cols desktop / 2 cols tablet / 1 col mobile
      - Todas las fotos de la lista
      - Efecto zoom suave al hacer hover
      - Lightbox funcional en JavaScript puro al hacer click:
        * Fondo negro semitransparente
        * Imagen ampliada centrada
        * Botones anterior/siguiente
        * Botón cerrar (X)
        * Navegar con teclas ←/→/Escape
      - Contador "Foto X de Y" en el lightbox

   E) CARACTERÍSTICAS DETALLADAS
      - Grid de tarjetas con íconos SVG
      - Divide en grupos si hay muchas
      - Diseño elegante con hover effect

   F) DESCRIPCIÓN Y ZONA
      - Texto descriptivo
      - Mención de atractivos de Bahía de Banderas / Riviera Nayarit
      - Imagen decorativa a un lado (segunda foto)

   G) AGENTE INMOBILIARIO
      - Card elegante
      - Foto placeholder con iniciales y avatar generado con CSS
      - Nombre, título, teléfono, email
      - Botón de WhatsApp específico del agente

   H) FORMULARIO DE CONTACTO
      - Nombre, email, teléfono, mensaje
      - Estilo elegante
      - Al submit: alert() agradeciendo la consulta (JavaScript)

   I) FOOTER
      - Nombre de la propiedad y agencia
      - Links rápidos
      - Redes sociales (íconos SVG)
      - Copyright

4. ELEMENTOS ESPECIALES:

   BOTÓN FLOTANTE DE WHATSAPP:
   - Posición: fixed, bottom-6, right-6
   - Verde WhatsApp (#25D366) con ícono SVG oficial de WhatsApp
   - Sombra pronunciada y animación pulse
   - Tooltip al hover: "¡Escríbenos ahora!"
   - URL: {wa_url}
   - Z-index alto para que siempre esté visible

   ANIMACIONES (AOS.js — NO Intersection Observer manual):
   - Cada sección principal: data-aos="fade-up"
   - Tarjetas de highlights: data-aos="zoom-in" con data-aos-delay incrementando 100ms cada una
   - Tarjetas de características: data-aos="fade-up" con delay escalonado (0, 75, 150, 225…)
   - Card del agente: data-aos="fade-right"
   - Formulario: data-aos="fade-left"
   - Parallax suave en el hero con CSS transform en scroll (JS vanilla, translateY)
   - Transiciones suaves (transition-all duration-300) en todos los hover

   SCROLL BEHAVIOR:
   - smooth scroll entre secciones
   - Offset correcto por el navbar fijo

5. SEO BÁSICO en el <head>:
   - title, description, og:title, og:description, og:image
   - viewport meta tag
   - charset UTF-8

══════════════════════════════════
INSTRUCCIÓN FINAL
══════════════════════════════════
Genera ÚNICAMENTE el código HTML completo, comenzando con <!DOCTYPE html>
y terminando con </html>. Sin texto adicional, sin markdown, sin explicaciones.
El código debe funcionar perfectamente al abrir el archivo directamente en un navegador."""


def clean_html(content: str) -> str:
    """Elimina code fences de markdown si Claude los incluye."""
    content = content.strip()
    for prefix in ("```html\n", "```html", "```\n", "```"):
        if content.startswith(prefix):
            content = content[len(prefix):]
            break
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


def generate_landing_page(features: dict, output_file: str = "propiedad.html", json_dir: Path = None) -> list:
    """
    Genera el HTML de la landing page.
    Retorna local_paths (lista de rutas absolutas de fotos locales, None para URLs)
    para uso posterior en generate_pdf().
    """
    client = anthropic.Anthropic()

    # Procesar fotos: detectar locales y convertir a base64
    local_paths: list = []
    if features.get("fotos"):
        print("\n📸 Procesando fotos...", flush=True)
        html_sources, local_paths = process_photos(features["fotos"], json_dir=json_dir)
        features = {**features, "fotos": html_sources}

    print("━" * 50)
    print("  🏡 GENERADOR DE LANDING PAGE INMOBILIARIA")
    print("     Bahía de Banderas · Riviera Nayarit")
    print("━" * 50)
    print(f"  Propiedad : {features.get('titulo')}")
    print(f"  Modelo    : claude-opus-4-7")
    print(f"  Salida    : {output_file}")
    print("━" * 50)
    print("\n⏳ Generando página con IA (puede tardar ~30 seg)...\n")

    html_parts: list[str] = []

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=12000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(features)}],
    ) as stream:
        in_thinking = False
        for event in stream:
            if event.type == "content_block_start":
                if event.content_block.type == "thinking":
                    in_thinking = True
                    print("💭 Claude está planificando la estructura...", flush=True)
                elif event.content_block.type == "text":
                    in_thinking = False
                    if not html_parts:
                        print("✍️  Escribiendo HTML...\n", flush=True)
            elif event.type == "content_block_stop":
                if in_thinking:
                    in_thinking = False
                    print("✅ Estructura planificada. Generando código...\n", flush=True)
            elif event.type == "content_block_delta":
                if not in_thinking and event.delta.type == "text_delta":
                    text = event.delta.text
                    print(text, end="", flush=True)
                    html_parts.append(text)

    html_content = clean_html("".join(html_parts))
    output_path = Path(output_file)
    output_path.write_text(html_content, encoding="utf-8")

    size_kb = output_path.stat().st_size / 1024
    print(f"\n\n{'━'*50}")
    print(f"  ✅ ¡Landing page generada exitosamente!")
    print(f"  📄 Archivo : {output_path.absolute()}")
    print(f"  📦 Tamaño  : {size_kb:.1f} KB")
    print(f"  🌐 Abre el archivo en tu navegador para verlo")
    print("━" * 50)

    return local_paths


# ──────────────────────────────────────────────
# PDF GENERATION
# ──────────────────────────────────────────────

def _make_section_header(text: str, page_width: float) -> "Table":
    """Crea una fila de encabezado de sección con fondo azul océano."""
    OCEAN_BLUE = colors.HexColor("#005f73")
    style = ParagraphStyle(
        "SH",
        fontSize=13,
        textColor=colors.white,
        fontName="Helvetica-Bold",
        leading=18,
    )
    t = Table([[Paragraph(text, style)]], colWidths=[page_width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), OCEAN_BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


def generate_pdf(features: dict, local_paths: list, output_file: str) -> None:
    """Genera una ficha PDF profesional con toda la información de la propiedad."""
    if not REPORTLAB_AVAILABLE:
        print("\n⚠️  reportlab no instalado. Instala con: pip install reportlab")
        print("   Sin PDF — la landing page HTML ya fue generada.")
        return

    print(f"\n📄 Generando PDF: {output_file}...", flush=True)

    OCEAN_BLUE = colors.HexColor("#005f73")
    DARK = colors.HexColor("#0d1b2a")
    GOLD = colors.HexColor("#d4a853")
    GRAY = colors.HexColor("#6c757d")
    LIGHT_BG = colors.HexColor("#f0f8ff")

    page_w = A4[0] - 3 * cm  # usable width

    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=features.get("titulo", "Propiedad"),
        author="Sistema Generador de Landing Page",
    )

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=11, textColor=DARK, leading=16, fontName="Helvetica",
    )
    small_style = ParagraphStyle(
        "Small", parent=styles["Normal"],
        fontSize=9, textColor=GRAY, leading=13, fontName="Helvetica",
        alignment=TA_CENTER,
    )
    feature_style = ParagraphStyle(
        "Feat", parent=styles["Normal"],
        fontSize=10, textColor=DARK, leading=14, fontName="Helvetica",
    )

    story = []

    # ─── FOTO PRINCIPAL ───────────────────────────────────────
    main_photo = next((p for p in local_paths if p), None)
    if main_photo:
        try:
            img = RLImage(main_photo, width=page_w, height=8 * cm)
            img.hAlign = "LEFT"
            story.append(img)
            story.append(Spacer(1, 0.4 * cm))
        except Exception as e:
            print(f"  ⚠️  No se pudo incluir foto principal: {e}")

    # ─── TÍTULO Y PRECIO ─────────────────────────────────────
    story.append(Paragraph(
        features.get("titulo", "Propiedad"),
        ParagraphStyle("T", fontSize=22, textColor=DARK, fontName="Helvetica-Bold",
                       spaceAfter=4, leading=26),
    ))
    story.append(Paragraph(
        features.get("subtitulo", ""),
        ParagraphStyle("ST", fontSize=13, textColor=OCEAN_BLUE, fontName="Helvetica",
                       spaceAfter=8, leading=18),
    ))
    story.append(Paragraph(
        features.get("precio", "Consultar precio"),
        ParagraphStyle("P", fontSize=20, textColor=GOLD, fontName="Helvetica-Bold",
                       spaceAfter=6),
    ))
    ubicacion = features.get("ubicacion", "")
    if ubicacion:
        story.append(Paragraph(f"Ubicación: {ubicacion}", body_style))

    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=OCEAN_BLUE, spaceAfter=8))

    # ─── DESCRIPCIÓN ─────────────────────────────────────────
    desc = features.get("descripcion_larga", "")
    if desc:
        story.append(_make_section_header("Descripción de la Propiedad", page_w))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 0.3 * cm))

    # ─── CARACTERÍSTICAS ─────────────────────────────────────
    caracteristicas = features.get("caracteristicas", [])
    if caracteristicas:
        story.append(_make_section_header("Características", page_w))
        story.append(Spacer(1, 0.3 * cm))

        mid = (len(caracteristicas) + 1) // 2
        left_col = caracteristicas[:mid]
        right_col = caracteristicas[mid:]
        col_w = page_w / 2

        rows = []
        for i in range(max(len(left_col), len(right_col))):
            left = Paragraph(f"✓  {left_col[i]}" if i < len(left_col) else "", feature_style)
            right = Paragraph(f"✓  {right_col[i]}" if i < len(right_col) else "", feature_style)
            rows.append([left, right])

        feat_table = Table(rows, colWidths=[col_w, col_w])
        feat_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
        ]))
        story.append(feat_table)
        story.append(Spacer(1, 0.3 * cm))

    # ─── GALERÍA (fotos locales adicionales) ─────────────────
    extra_photos = [p for p in local_paths if p][1:7]  # hasta 6 fotos extra
    if extra_photos:
        story.append(_make_section_header("Galería de Fotos", page_w))
        story.append(Spacer(1, 0.3 * cm))

        photo_w = (page_w - 0.5 * cm) / 2
        photo_h = 5 * cm
        photo_rows = []
        for i in range(0, len(extra_photos), 2):
            row = []
            for j in range(2):
                idx = i + j
                if idx < len(extra_photos):
                    try:
                        row.append(RLImage(extra_photos[idx], width=photo_w, height=photo_h))
                    except Exception:
                        row.append(Paragraph("", feature_style))
                else:
                    row.append(Paragraph("", feature_style))
            photo_rows.append(row)

        photo_table = Table(photo_rows, colWidths=[photo_w + 0.25 * cm, photo_w + 0.25 * cm])
        photo_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(photo_table)
        story.append(Spacer(1, 0.3 * cm))

    # ─── INFORMACIÓN ADICIONAL ───────────────────────────────
    extras = features.get("extras", {})
    if extras:
        story.append(_make_section_header("Información Adicional", page_w))
        story.append(Spacer(1, 0.3 * cm))

        label_map = {
            "año_construccion": "Año de construcción",
            "estrato": "Estrato",
            "uso_suelo": "Uso de suelo",
            "amueblada": "Amueblada",
        }
        extras_rows = []
        for key, label in label_map.items():
            if key in extras:
                val = extras[key]
                if isinstance(val, bool):
                    val = "Sí" if val else "No"
                extras_rows.append([
                    Paragraph(f"<b>{label}</b>", feature_style),
                    Paragraph(str(val), feature_style),
                ])

        if extras_rows:
            ext_table = Table(extras_rows, colWidths=[6 * cm, page_w - 6 * cm])
            ext_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
            ]))
            story.append(ext_table)
            story.append(Spacer(1, 0.3 * cm))

    # ─── AGENTE ──────────────────────────────────────────────
    agente = features.get("agente", {})
    if agente:
        story.append(_make_section_header("Agente Inmobiliario", page_w))
        story.append(Spacer(1, 0.3 * cm))

        agent_rows = [
            [Paragraph(f"<b>{agente.get('nombre', '')}</b>", body_style)],
            [Paragraph(agente.get("titulo", ""), feature_style)],
            [Paragraph(f"Tel: {agente.get('telefono', '')}", feature_style)],
            [Paragraph(f"Email: {agente.get('email', '')}", feature_style)],
            [Paragraph(f"Experiencia: {agente.get('experiencia_anos', '')} años", feature_style)],
        ]
        agent_table = Table(agent_rows, colWidths=[page_w])
        agent_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
            ("BOX", (0, 0), (-1, -1), 1, OCEAN_BLUE),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ]))
        story.append(agent_table)
        story.append(Spacer(1, 0.5 * cm))

    # ─── FOOTER ──────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=OCEAN_BLUE, spaceAfter=6))
    whatsapp = features.get("whatsapp", "")
    if whatsapp:
        wa_clean = whatsapp.replace("+", "").replace(" ", "")
        story.append(Paragraph(
            f"WhatsApp: {whatsapp}  ·  https://wa.me/{wa_clean}",
            small_style,
        ))
    story.append(Paragraph(
        f"© {features.get('titulo', 'Propiedad')} · Todos los derechos reservados",
        small_style,
    ))

    doc.build(story)

    size_kb = Path(output_file).stat().st_size / 1024
    print(f"  ✅ PDF generado: {Path(output_file).absolute()} ({size_kb:.1f} KB)")


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generador de landing page + PDF para propiedades inmobiliarias",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Archivo JSON con características, o archivo de texto con --raw",
    )
    parser.add_argument(
        "output_html",
        nargs="?",
        default="propiedad_banderas.html",
        help="Nombre del archivo HTML de salida (default: propiedad_banderas.html)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Interpreta el archivo de entrada como descripción en texto libre",
    )
    parser.add_argument(
        "--pdf",
        nargs="?",
        const="propiedad_banderas.pdf",
        metavar="ARCHIVO.pdf",
        help="También genera un PDF (default: propiedad_banderas.pdf)",
    )
    args = parser.parse_args()

    # ── Cargar características ──────────────────────────────
    json_dir = Path.cwd()
    if args.input is None:
        features = HOUSE_FEATURES
        print("ℹ️  Usando características de ejemplo.")
        print("   → Edita HOUSE_FEATURES o pasa un archivo JSON / --raw como argumento.\n")
    elif args.raw:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ Archivo no encontrado: {input_path}")
            sys.exit(1)
        json_dir = input_path.resolve().parent
        raw_text = input_path.read_text(encoding="utf-8")
        try:
            features = parse_raw_description(raw_text)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ Error al parsear la respuesta de Claude: {e}")
            sys.exit(1)
    else:
        json_path = Path(args.input)
        if not json_path.exists():
            print(f"❌ Archivo no encontrado: {json_path}")
            sys.exit(1)
        json_dir = json_path.resolve().parent
        try:
            features = json.loads(json_path.read_text(encoding="utf-8"))
            print(f"✅ Características cargadas desde: {json_path}\n")
        except json.JSONDecodeError as e:
            print(f"❌ JSON inválido en {json_path}: {e}")
            sys.exit(1)

    # ── Generar HTML ────────────────────────────────────────
    try:
        local_paths = generate_landing_page(features, args.output_html, json_dir=json_dir)
    except anthropic.AuthenticationError:
        print("\n❌ API key inválida. Verifica la variable ANTHROPIC_API_KEY.")
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"\n❌ Error de API: {e}")
        sys.exit(1)

    # ── Generar PDF (opcional) ──────────────────────────────
    if args.pdf:
        generate_pdf(features, local_paths, args.pdf)

    print("\n✨ ¡Proceso completado!")


if __name__ == "__main__":
    main()
