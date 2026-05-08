# Instrucciones para generar landings y brochures

## Paso 1 — Crea el archivo JSON de la propiedad

Crea un archivo `.json` con los datos de la propiedad. Ejemplo: `villa-punta-mita.json`

```json
{
  "titulo": "Villa Punta Mita — Frente al Mar",
  "subtitulo": "Exclusiva villa con alberca infinita y acceso a playa privada",
  "precio": "$850 USD / noche",
  "ubicacion": "Punta Mita, Nayarit, México",
  "whatsapp": "+523221234567",
  "descripcion_larga": "Describe aquí la propiedad con detalle. Vistas, diseño, sensaciones, experiencias cercanas. Mínimo 3-4 oraciones.",
  "caracteristicas": [
    "4 recámaras con baño en suite",
    "3.5 baños",
    "Alberca infinita con vista al mar",
    "Terraza con jacuzzi",
    "Cocina gourmet equipada",
    "Estacionamiento para 2 autos",
    "Acceso a playa privada",
    "300 m² de construcción"
  ],
  "fotos": [
    "fotos/foto1.jpg",
    "fotos/foto2.jpg",
    "fotos/foto3.jpg",
    "fotos/foto4.jpg",
    "fotos/foto5.jpg",
    "fotos/foto6.jpg"
  ],
  "agente": {
    "nombre": "Nombre del Agente",
    "titulo": "Especialista en Propiedades de Lujo",
    "telefono": "+52 322 000 0000",
    "email": "correo@zenithbahia.com",
    "experiencia_anos": "5"
  },
  "extras": {
    "año_construccion": "2022",
    "estrato": "Residencial de lujo",
    "uso_suelo": "Habitacional / Turístico",
    "amueblada": true
  }
}
```

---

## Paso 2 — Fotos

- Pon las fotos en una carpeta junto al JSON (ej. `fotos/`)
- Rutas relativas funcionan automáticamente
- Mínimo 6 fotos recomendadas
- Formato: JPG o PNG, mayor a 1200px de ancho
- También puedes usar URLs de internet (https://...)

---

## Paso 3 — Generar la landing page

Abre PowerShell en la carpeta del proyecto y corre:

```powershell
python generar_landing.py villa-punta-mita.json propiedades/villa-punta-mita.html
```

Esto genera el archivo HTML listo en la carpeta `propiedades/`.

---

## Paso 4 — Generar el brochure (PDF)

```powershell
python generar_brochure.py villa-punta-mita.json brochure-villa-punta-mita.html
```

Luego abre ese HTML en Chrome:
- `Ctrl + P` → Guardar como PDF
- Márgenes: **Ninguno**
- Activar: **Gráficos de fondo**

---

## Paso 5 — Subir a GitHub

```powershell
git add .
git commit -m "agrego villa punta mita"
git push
```

---

## Notas importantes

- El JSON debe estar guardado con codificación **UTF-8**
- Si una foto no existe, el script la omite sin romperse
- El script usa IA (Claude) para generar el HTML — tarda ~30 segundos
- Necesitas tener la variable `ANTHROPIC_API_KEY` configurada en tu sistema
