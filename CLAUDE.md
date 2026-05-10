# Zenith Bahia Properties — Contexto del Proyecto

## Qué es esto
Sitio web estático de **Zenith Bahia Properties**, agencia inmobiliaria especializada en rentas vacacionales de lujo y difusión de propiedades en Bahía de Banderas y Puerto Vallarta (Riviera Nayarit, México).

- Contacto agencia: +52 322 139 9350 / hola@zenithbahia.com
- Repo GitHub: https://github.com/mistersql420/ZENITH
- Sitio en vivo: https://mistersql420.github.io/ZENITH/
- Formularios: Formspree ID `xaqvdzlg`

---

## Stack técnico
- HTML estático puro — sin framework, sin build step
- Tailwind CSS CDN (`https://cdn.tailwindcss.com`)
- Google Fonts: **Cormorant Garamond** (títulos, italic 600) + **Montserrat** (cuerpo, 300/400/600)
- AOS.js animate-on-scroll (`https://unpkg.com/aos@2.3.4/dist/aos.js`)
- Lucide icons vanilla (`https://unpkg.com/lucide@latest`)
- JS vanilla — sin frameworks

## Paleta de colores
```
Ocean dark:  #0a2540
Ocean mid:   #005f73
Gold:        #d4a853
Gold hover:  #c5a059
Fondo:       linear-gradient(180deg, #0a2540 0%, #005f73 18%, #a8d5e8 48%, #ffffff 100%) fixed
```

## Tipografía (reglas obligatorias)
- `h1, h2, h3, h4`: Cormorant Garamond italic 600 — NUNCA sans-serif en títulos
- `body`: Montserrat 300/400/600
- Eyebrows/labels: `tracking-[0.3em] uppercase text-xs` en dorado
- Font-size mínimo body: 16px — line-height mínimo: 1.7
- font-weight mínimo en párrafos: 400 (font-normal) — nunca font-light (300) en mobile

---

## Estructura de archivos
```
/
├── index.html              — Home de la agencia
├── catalogo.html           — Catálogo con filtros (zona, recámaras, precio)
├── publicar.html           — Formulario multi-paso para propietarios (Formspree)
├── contacto.html           — Contacto general
├── propiedades/
│   └── casa-naga-sayulita.html  — Landing individual (4.5MB, fotos base64)
├── assets/
│   ├── favicon.svg         — Z dorada sobre fondo ocean, esquinas redondeadas
│   └── casa-naga-thumb.jpg — Thumbnail para el catálogo
├── propiedades.json        — Datos de propiedades para el catálogo (JS lo lee en runtime)
├── casa-naga.json          — Datos de Casa Naga (referencia para el script)
├── generar_landing.py      — Genera landing HTML usando API de Anthropic
├── generar_brochure.py     — Genera brochure HTML usando API de Anthropic
├── INSTRUCCIONES_SCRIPT.md — Cómo agregar propiedades nuevas
├── herramientas.txt        — Requisitos de software
└── bot.py                  — Bot de Telegram (local, no subir a GitHub aún)
```

---

## Sistema i18n ES/EN
**Todas las páginas** tienen un toggle ES/EN en el navbar implementado con JS vanilla:
- Botón `id="lang-toggle"` con `onclick="toggleLang()"`
- Atributos `data-i18n="clave"` en elementos de texto
- Atributos `data-i18n-html="clave"` en elementos con HTML interno (em, br)
- Función `setLang(l)` aplica las traducciones y guarda en `localStorage('zbp_lang')`
- El JS **DEBE estar al final del body**, nunca en el head

**IMPORTANTE:** Al inyectar JS de i18n, colocarlo siempre antes de `</body>`, NUNCA dentro de un `<script src="...">` externo.

---

## Propiedades actuales

### Casa Naga — Sayulita (Renta vacacional)
- Precio: $4,000 USD / noche
- Suites: 5 Master Suites, 10 huéspedes
- WhatsApp: 523221399350
- Landing: `propiedades/casa-naga-sayulita.html` (fotos embebidas en base64)
- Thumbnail en catálogo: `assets/casa-naga-thumb.jpg`
- Tiene: galería masonry + lightbox, toggle EN/ES completo (50+ claves), sticky CTA mobile, text-shadow luxury, lazy loading

---

## Reglas de legibilidad mobile (VALIDADAS)
- Texto sobre fondo oscuro: mínimo `rgba(255,255,255,0.85)` — nunca opacity < 0.7
- Texto sobre fondo claro: mínimo `text-gray-700` — nunca `text-gray-400` o `text-gray-500`
- Overlay hero: mínimo `bg-ocean-900/20`
- Secciones con `bg-white/60-70`: subir a `bg-white/90`
- Amenity cards: `bg-white/95` + `box-shadow` sutil
- Text-shadow en H1 hero: `0 2px 16px rgba(0,0,0,0.55), 0 0 40px rgba(0,0,0,0.25)`
- Text-shadow en H2 sobre oscuro: `0 1px 8px rgba(0,0,0,0.40)`

---

## Cómo agregar una propiedad nueva
1. Crear carpeta con fotos: `fotos/nombre-propiedad/`
2. Crear JSON con datos: `nombre-propiedad.json`
3. Generar landing (con API key Anthropic):
   ```powershell
   $env:PYTHONUTF8="1"
   python generar_landing.py nombre-propiedad.json propiedades/nombre-propiedad.html
   ```
4. Copiar una foto como thumbnail a `assets/nombre-propiedad-thumb.jpg`
5. Agregar entrada en `propiedades.json`
6. Agregar entrada en el array JS de `catalogo.html`
7. Aplicar correcciones de legibilidad mobile (ver sección anterior)
8. Agregar toggle i18n ES/EN
9. `git add . && git commit -m "agrega [nombre]" && git push`

---

## Lo que NO modificar sin cuidado
- `propiedades/casa-naga-sayulita.html`: archivo de 4.5MB con fotos base64 — usar Grep/edits puntuales, nunca reescribir
- `assets/favicon.svg`: ya aprobado por el usuario
- Paleta de colores y fuentes: son la identidad de marca

---

## Pendientes conocidos
- [ ] Nueva propiedad en venta — $12 millones MXN, casa independiente (fotos pendientes)
- [ ] `bot.py` — bot de Telegram para automatización (en desarrollo, no subir aún)
- [ ] `contacto.html` — el formulario de contacto no tiene Formspree conectado aún
- [ ] Más propiedades en el catálogo (actualmente solo Casa Naga)
- [ ] Dominio personalizado (mencionado para el futuro)

---

## Git
```powershell
git add .
git commit -m "descripcion del cambio"
git push
```
Rama principal: `main`. Remote: `https://github.com/mistersql420/ZENITH.git`
