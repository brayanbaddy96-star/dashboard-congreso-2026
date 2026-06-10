# Dashboard Congreso 2026–2030 V8

Versión final con ajuste de separación superior para evitar que la barra nativa de Streamlit corte el encabezado del dashboard.

# Dashboard Congreso 2026–2030 · V6

Versión ajustada con mejoras de experiencia de usuario, KPIs por módulo y módulo territorial corregido.

## Cambios V6

- Los KPIs ya no repiten los indicadores del módulo nacional en todos los módulos.
- Cada módulo tiene indicadores propios y coherentes con su objetivo analítico.
- Se retiraron los KPIs ambiguos de ENP y Top 3 bancadas del módulo de bancadas.
- El módulo de territorio ahora integra Cámara y Senado en una sola columna por departamento/territorio.
- Se normalizó la lectura territorial para evitar duplicidades como `ANTIOQUIA` y `NACIONAL · ANTIOQUIA`.
- Se mantiene la regla metodológica: no sumar votos de Cámara y Senado, ni imputar votos de lista cerrada como voto individual.

## Ejecutar

```bash
cd ~/Downloads
unzip dashboard_congreso_2026_2030_v6.zip
cd dashboard_congreso_2026_2030_v6
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```
