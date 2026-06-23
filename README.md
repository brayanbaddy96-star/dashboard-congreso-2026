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


## V16

- El módulo de integración de comisiones identifica empates decisivos por residuo.
- Cuando hay más bancadas empatadas que cupos disponibles, la curul queda pendiente y se listan las bancadas que compiten por ella, sin asignación automática arbitraria.


## Actualización V19
- Base de integración de comisiones actualizada con el archivo más reciente suministrado por el usuario.
- Total de registros de comisiones procesados: 39.
- El módulo conserva el cálculo por cuociente, el control opcional de inclusión CITREP y la identificación de empates por residuo sin asignación automática.


## Actualización V20

Se incorporó la nueva matriz completa de comisiones (53 registros válidos): Cámara Constitucional/Legal/Especial/Accidental y Senado Constitucional/Legal/Especial/Accidental. El cálculo usa cupos efectivos con adiciones CITREP/oposición cuando aplica.
