# Dashboard Congreso 2026–2030 · V9

Versión ajustada del dashboard interactivo del Congreso 2026–2030.

## Cambios V9

- En las fichas técnicas, la votación de lista/grupo se muestra para todos los integrantes de una lista cerrada o grupo electoral, no solo para quien encabezaba la lista.
- Se mantiene la regla metodológica para análisis agregados: la votación de partido/lista no se duplica en los rankings ni en los KPIs.
- El selector de bancada ahora muestra un reporte previo del grupo seleccionado antes de elegir congresista:
  - curules totales;
  - Senado/Cámara;
  - organizaciones reales;
  - circunscripciones;
  - distribución por sector político;
  - apoyos presidenciales registrados en primera y segunda vuelta.
- Se eliminó la lectura de “sector dominante” o “candidato predominante” como si fuera posición única de toda la bancada.

## Ejecutar localmente

```bash
cd ~/Downloads/dashboard_congreso_2026_2030_v9
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## Publicar actualización en GitHub

```bash
git add .
git commit -m "Ajuste fichas y reporte de bancada"
git push
```
