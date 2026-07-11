# Coco Analytics

Repositorio del emprendimiento de aceite de coco. Por ahora concentra el **análisis de datos** previo a la producción; más adelante sumará la tecnología del negocio (agentes de IA, dashboards, automatizaciones).

## Estructura

```
coco-analytics/
├── analisis/         # Estudios de análisis (notebooks + datos curados + figuras + resúmenes)
│   ├── 00_resumen_ejecutivo.md
│   ├── 01_analisis_competencia_aceite_coco.ipynb
│   ├── datos/        # CSV curados con su fuente (versionados)
│   └── figuras/      # Gráficos exportados (PNG)
├── docs/             # 📊 Dashboard web (GitHub Pages): index.html + datos.js
├── data/
│   ├── raw/          # Datos crudos (no se versionan; microdato INE viene del Drive)
│   └── processed/    # Datos procesados (no se versionan)
├── src/              # Código reutilizable (estilo, preparar_ine.py, preparar_web.py)
└── requirements.txt  # Dependencias de Python
```

## Dashboard web

`docs/` contiene un dashboard estático (sin dependencias externas) con las
importaciones oficiales del INE, el contexto global, la competencia y el marco
legal — con filtros por período, tooltips, vista de tabla y modo claro/oscuro.

- **Publicarlo:** GitHub → *Settings → Pages → Deploy from a branch* → rama
  `main`, carpeta `/docs`. Queda en `https://<usuario>.github.io/coco-analytics/`.
- **Actualizar los datos:** `python src/preparar_web.py` regenera `docs/datos.js`
  desde el microdato del INE y los CSV de `analisis/datos/`.
- **Probar local:** `python -m http.server -d docs 8000` → http://localhost:8000

> Nota: los datasets *curados* del análisis (pequeños, con fuente documentada) se
> versionan dentro de `analisis/datos/` para que cada estudio sea reproducible.
> Las descargas crudas y voluminosas siguen yendo a `data/` (fuera de git).

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Convenciones

- Los datos van en `data/` y están fuera de git; documentar en cada notebook de dónde salen.
- Nombrar notebooks con prefijo numérico y tema: `01_analisis_mercado.ipynb`, `02_costos_produccion.ipynb`.
- Código que se repite entre notebooks se mueve a `src/`.

## Roadmap

- [x] Análisis de competencia e importaciones (aceite de coco en Bolivia) → [`analisis/`](analisis/)
- [ ] Análisis de mercado y demanda
- [ ] Costos de producción y punto de equilibrio
- [ ] Proveedores y materia prima
- [ ] Dashboards (cuando haya datos operativos)
- [ ] Agentes de IA (cuando arranque la operación)
