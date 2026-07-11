# Coco Analytics

Repositorio del emprendimiento de aceite de coco. Por ahora concentra el **análisis de datos** previo a la producción; más adelante sumará la tecnología del negocio (agentes de IA, dashboards, automatizaciones).

## Estructura

```
coco-analytics/
├── notebooks/        # Notebooks de análisis (mercado, costos, proveedores, etc.)
├── data/
│   ├── raw/          # Datos crudos (no se versionan)
│   └── processed/    # Datos procesados (no se versionan)
├── src/              # Código reutilizable (funciones de carga, limpieza, gráficos)
└── requirements.txt  # Dependencias de Python
```

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

- [ ] Análisis de mercado y demanda
- [ ] Costos de producción y punto de equilibrio
- [ ] Proveedores y materia prima
- [ ] Dashboards (cuando haya datos operativos)
- [ ] Agentes de IA (cuando arranque la operación)
