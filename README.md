# Empleos en datos en Latinoamérica

Dashboard del proyecto final de Electiva II (Introducción a la Ciencia de Datos), Fundación Universitaria de Popayán, 2026-2.

Hecho por Camilo Dorado y Sebastián Beltrán.

Usamos las ofertas de empleo que sacamos de LinkedIn con web scraping el 29/10/2026 para los cargos Data Engineer, Data Analyst, Data Scientist, BI Analyst y ML Engineer. La base original tenía 3.045 registros y después de limpiarla quedaron 2.572. El dashboard muestra cómo se reparten las ofertas por país, ciudad, rol, nivel de experiencia y modalidad, y tiene filtros en la barra lateral.

## Archivos

- `app.py`: el dashboard (Streamlit + Plotly)
- `requirements.txt`: librerías que necesita
- `datos/ofertas_empleo_limpias.csv`: la base ya limpia

## Para correrlo

```
pip install -r requirements.txt
streamlit run app.py
```

Abre en http://localhost:8501
