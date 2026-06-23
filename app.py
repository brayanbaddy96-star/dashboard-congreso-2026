from pathlib import Path
import base64
import html
import math
import re
import unicodedata
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "congresistas_2026_2030.csv"
COMMISSIONS_PATH = BASE_DIR / "data" / "comisiones_definicion.csv"
PLACEHOLDER = BASE_DIR / "assets" / "placeholder.svg"

st.set_page_config(
    page_title="Congreso 2026–2030",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# ESTILO VISUAL: OSCURO, INSTITUCIONAL Y LEGIBLE
# =============================================================================
st.markdown(
    """
<style>
:root{
  --bg:#07111f;
  --panel:#0b1220;
  --panel2:#111827;
  --card:#101827;
  --card2:#151f33;
  --ink:#f8fafc;
  --muted:#a7b1c2;
  --muted2:#77849a;
  --line:rgba(255,255,255,.12);
  --red:#e30613;
  --accent:#f43f5e;
  --cyan:#38bdf8;
}
html, body, [data-testid="stAppViewContainer"]{
  background:
    radial-gradient(circle at 10% -5%, rgba(227,6,19,.18), transparent 30%),
    radial-gradient(circle at 90% 0%, rgba(56,189,248,.13), transparent 28%),
    linear-gradient(180deg,#07111f 0%,#09101d 60%,#0b1020 100%) !important;
  color:var(--ink) !important;
}
/* Corrección final: evita que la barra superior de Streamlit tape el encabezado */
[data-testid="stHeader"]{background:rgba(7,17,31,.96) !important;}
.block-container{max-width:1640px; padding-top:4.6rem !important; padding-bottom:2.5rem;}
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#070b14 0%,#0f172a 60%,#350914 100%) !important;
  border-right:1px solid var(--line);
}
[data-testid="stSidebar"] *{color:#f8fafc !important;}
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div{
  background:#101827 !important; border:1px solid rgba(255,255,255,.16) !important; border-radius:14px !important;
}
[data-testid="stSidebar"] .stRadio label{padding:.18rem 0;}
div[data-baseweb="select"] > div{
  background:#121a2a !important; color:#f8fafc !important; border:1px solid rgba(255,255,255,.16) !important; border-radius:16px !important;
}
div[data-baseweb="popover"] div{background:#111827 !important; color:#f8fafc !important;}
label, .stSelectbox label, .stRadio label, .stMultiSelect label{color:#e5e7eb !important; font-weight:800 !important;}

.hero{
  background:
    radial-gradient(circle at 6% 0%, rgba(227,6,19,.36), transparent 30%),
    radial-gradient(circle at 92% 0%, rgba(56,189,248,.18), transparent 32%),
    linear-gradient(135deg,#0b1220 0%,#111827 52%,#550f1c 100%);
  border:1px solid rgba(255,255,255,.12); color:#fff; border-radius:30px; padding:1.35rem 1.55rem;
  box-shadow:0 24px 80px rgba(0,0,0,.36); margin-bottom:1rem;
}
.hero h1{font-size:2.35rem; line-height:1.03; letter-spacing:-.045em; margin:.25rem 0 .35rem;}
.hero p{max-width:1250px; margin:0; color:#dbe4f0; line-height:1.42; font-size:.98rem;}
.micro{display:flex; flex-wrap:wrap; gap:.42rem; margin-bottom:.35rem;}
.badge{display:inline-flex; align-items:center; gap:.32rem; padding:.30rem .66rem; border-radius:999px; border:1px solid rgba(255,255,255,.18); background:rgba(255,255,255,.08); font-size:.78rem; font-weight:900;}

.guide{background:linear-gradient(180deg,rgba(16,24,39,.98),rgba(13,20,34,.98)); border:1px solid var(--line); border-left:6px solid var(--red); border-radius:22px; padding:1rem 1.1rem; margin:.45rem 0 1rem; box-shadow:0 16px 44px rgba(0,0,0,.22);}
.guide h3{margin:0 0 .45rem; color:#fff; font-size:1.05rem; letter-spacing:-.01em;}
.guide p{margin:.22rem 0; color:#c7d2e4; line-height:1.42; font-size:.92rem;}

.kpi-grid{display:grid; grid-template-columns:repeat(5,minmax(170px,1fr)); gap:.8rem; margin:.75rem 0 1.05rem;}
@media(max-width:1350px){.kpi-grid{grid-template-columns:repeat(3,minmax(145px,1fr));}}
@media(max-width:800px){.kpi-grid{grid-template-columns:repeat(2,minmax(145px,1fr));}}
.kpi-card{
  min-height:126px; background:linear-gradient(180deg,#121b2d 0%,#0d1526 100%); border:1px solid rgba(255,255,255,.12); border-radius:22px; padding:.9rem .95rem; box-shadow:0 18px 50px rgba(0,0,0,.23); overflow:hidden; display:flex; flex-direction:column; justify-content:space-between;
}
.kpi-label{font-size:.68rem; text-transform:uppercase; letter-spacing:.085em; color:#93a4bb; font-weight:950; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.kpi-value{font-size:clamp(1.18rem,1.55vw,1.68rem); line-height:1.08; margin-top:.33rem; color:#fff; font-weight:950; white-space:normal; overflow-wrap:anywhere; word-break:normal;}
.kpi-help{font-size:.75rem; line-height:1.25; margin-top:.38rem; color:#a7b1c2; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;}

.section-title{font-size:1.28rem; font-weight:950; color:#f8fafc; margin:1rem 0 .48rem; letter-spacing:-.025em;}
.card{background:linear-gradient(180deg,#101827,#0b1220); border:1px solid var(--line); border-radius:24px; padding:1rem 1.1rem; margin:.45rem 0 1rem; box-shadow:0 18px 50px rgba(0,0,0,.23);}
.card h3{font-size:1.02rem; margin:0 0 .55rem; color:#fff;}
.note{color:#c7d2e4; font-size:.90rem; line-height:1.45;}
.small{font-size:.78rem; color:#9aa7bc; line-height:1.35;}

[data-testid="stPlotlyChart"]{background:#0b1220; border:1px solid var(--line); border-radius:26px; padding:.35rem; box-shadow:0 18px 52px rgba(0,0,0,.26); margin:.25rem 0 1rem;}

.legend-grid{display:grid; grid-template-columns:repeat(4,minmax(190px,1fr)); gap:.45rem .7rem; margin:.25rem 0 1rem;}
@media(max-width:1200px){.legend-grid{grid-template-columns:repeat(3,minmax(180px,1fr));}}
@media(max-width:850px){.legend-grid{grid-template-columns:repeat(2,minmax(160px,1fr));}}
.legend-item{display:flex; align-items:center; gap:.48rem; background:#0d1628; border:1px solid rgba(255,255,255,.09); border-radius:14px; padding:.42rem .55rem; min-width:0;}
.legend-dot{width:13px; height:13px; border-radius:50%; flex:0 0 auto; border:1px solid rgba(255,255,255,.75);}
.legend-text{font-size:.78rem; color:#d9e2ef; font-weight:850; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.legend-count{margin-left:auto; font-size:.75rem; color:#93a4bb; font-weight:900;}

.party-head{display:grid; grid-template-columns:82px 1fr; gap:1rem; align-items:center; background:linear-gradient(180deg,#111a2b,#0c1424); border:1px solid var(--line); border-radius:24px; padding:1rem; margin:.45rem 0 1rem; box-shadow:0 18px 50px rgba(0,0,0,.25);}
.logo-badge{width:70px;height:70px;border-radius:22px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:950;font-size:1.12rem;letter-spacing:-.02em;box-shadow:0 14px 28px rgba(0,0,0,.35); border:1px solid rgba(255,255,255,.25);}
.party-title{font-size:1.32rem;font-weight:950;color:#fff;letter-spacing:-.025em;margin-bottom:.15rem;}
.party-sub{font-size:.88rem;color:#a7b1c2;line-height:1.35;}

/* Reporte visual del grupo seleccionado */
.group-report{margin:.25rem 0 1rem;}
.group-kpis{display:grid; grid-template-columns:repeat(5,minmax(150px,1fr)); gap:.62rem; margin:.65rem 0 .85rem;}
@media(max-width:1350px){.group-kpis{grid-template-columns:repeat(3,minmax(150px,1fr));}}
@media(max-width:850px){.group-kpis{grid-template-columns:repeat(2,minmax(140px,1fr));}}
.group-kpi{background:linear-gradient(180deg,#121b2d,#0b1220); border:1px solid rgba(255,255,255,.12); border-radius:20px; padding:.78rem .86rem; min-height:102px; box-shadow:0 16px 42px rgba(0,0,0,.23); overflow:hidden;}
.group-kpi-label{font-size:.66rem; text-transform:uppercase; letter-spacing:.085em; color:#93a4bb; font-weight:950; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.group-kpi-value{font-size:clamp(1.18rem,1.7vw,1.75rem); color:#fff; font-weight:950; line-height:1.05; margin-top:.34rem; overflow-wrap:anywhere;}
.group-kpi-help{font-size:.73rem; color:#a7b1c2; line-height:1.25; margin-top:.3rem;}
.group-panels{display:grid; grid-template-columns:repeat(3,minmax(240px,1fr)); gap:.72rem; margin:.55rem 0 .75rem;}
@media(max-width:1100px){.group-panels{grid-template-columns:1fr;}}
.group-panel{background:linear-gradient(180deg,#101827,#0c1424); border:1px solid rgba(255,255,255,.12); border-radius:22px; padding:.9rem .95rem; box-shadow:0 16px 46px rgba(0,0,0,.22);}
.group-panel-title{display:flex; align-items:center; justify-content:space-between; gap:.55rem; color:#f8fafc; font-size:.88rem; text-transform:uppercase; letter-spacing:.07em; font-weight:950; margin-bottom:.7rem;}
.group-panel-title span{color:#93a4bb; font-size:.72rem; letter-spacing:0; text-transform:none; font-weight:800;}
.dist-item{display:grid; grid-template-columns:minmax(96px,1fr) 44px 56px; align-items:center; gap:.5rem; margin:.48rem 0;}
.dist-label{font-size:.80rem; color:#e5edf8; font-weight:900; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.dist-count{font-size:.82rem; font-weight:950; color:#fff; text-align:right;}
.dist-pct{font-size:.75rem; font-weight:900; color:#93a4bb; text-align:right;}
.dist-track{grid-column:1 / -1; height:8px; border-radius:999px; background:rgba(255,255,255,.08); overflow:hidden; border:1px solid rgba(255,255,255,.06);}
.dist-fill{height:100%; width:var(--w); background:var(--accent); border-radius:999px; box-shadow:0 0 18px color-mix(in srgb, var(--accent) 45%, transparent);}
.group-note{background:rgba(245,158,11,.10); border:1px solid rgba(251,191,36,.28); border-radius:18px; padding:.76rem .88rem; color:#fde68a; font-size:.84rem; line-height:1.38; margin:.55rem 0 .85rem;}
.pill{display:inline-block; padding:.30rem .58rem; border-radius:999px; background:#172033; color:#dbeafe; font-size:.74rem; font-weight:900; margin:.13rem .15rem .13rem 0; border:1px solid rgba(255,255,255,.12);}
.pill-red{background:rgba(227,6,19,.15);color:#fecaca;border-color:rgba(248,113,113,.35);}
.pill-blue{background:rgba(59,130,246,.15);color:#bfdbfe;border-color:rgba(96,165,250,.35);}
.pill-green{background:rgba(34,197,94,.14);color:#bbf7d0;border-color:rgba(74,222,128,.35);}
.pill-amber{background:rgba(245,158,11,.14);color:#fde68a;border-color:rgba(251,191,36,.35);}


.tie-panel{background:linear-gradient(135deg,rgba(245,158,11,.14),rgba(15,23,42,.96));border:1px solid rgba(251,191,36,.30);border-radius:24px;padding:1rem 1.05rem;margin:.7rem 0 1.1rem;box-shadow:0 18px 54px rgba(0,0,0,.26);}
.tie-head{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;margin-bottom:.72rem;}
.tie-title{font-size:1.02rem;font-weight:950;color:#fef3c7;letter-spacing:-.01em;}
.tie-sub{font-size:.84rem;color:#fde68a;line-height:1.38;margin-top:.18rem;max-width:1050px;}
.tie-pill{display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.42rem .7rem;background:rgba(251,191,36,.14);border:1px solid rgba(251,191,36,.35);color:#fef3c7;font-size:.78rem;font-weight:950;white-space:nowrap;}
.tie-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:.65rem;margin-top:.65rem;}
.tie-card{background:rgba(8,16,30,.78);border:1px solid rgba(255,255,255,.13);border-radius:18px;padding:.78rem .82rem;min-height:106px;}
.tie-bancada{display:flex;align-items:center;gap:.5rem;font-size:.88rem;font-weight:950;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tie-dot{width:14px;height:14px;border-radius:50%;border:1px solid rgba(255,255,255,.7);flex:0 0 auto;}
.tie-meta{display:grid;grid-template-columns:1fr 1fr;gap:.42rem;margin-top:.65rem;}
.tie-mini{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:.48rem .55rem;}
.tie-mini-lab{font-size:.62rem;color:#93a4bb;text-transform:uppercase;letter-spacing:.065em;font-weight:950;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tie-mini-val{font-size:1.08rem;color:#fff;font-weight:950;line-height:1;margin-top:.22rem;}
.tie-slot-row{display:flex;flex-wrap:wrap;gap:.38rem;margin:.55rem 0 .35rem;}
.tie-slot{width:34px;height:34px;border-radius:12px;background:rgba(251,191,36,.16);border:1px dashed rgba(251,191,36,.55);display:flex;align-items:center;justify-content:center;color:#fef3c7;font-weight:950;}
.tie-empty{background:rgba(34,197,94,.11);border:1px solid rgba(74,222,128,.30);border-radius:22px;padding:.85rem .95rem;color:#bbf7d0;margin:.75rem 0 1.05rem;line-height:1.42;}

.profile-card{display:grid; grid-template-columns:310px 1fr; gap:1.35rem; background:linear-gradient(180deg,#111a2b,#0d1526); border:1px solid var(--line); border-radius:30px; padding:1.15rem; box-shadow:0 22px 62px rgba(0,0,0,.32); margin:.45rem 0 1.15rem;}
@media(max-width:950px){.profile-card{grid-template-columns:1fr;}.profile-photo{max-width:280px;}}
.profile-photo{width:100%; border-radius:24px; object-fit:cover; aspect-ratio:4/4.2; background:#1f2937; border:1px solid rgba(255,255,255,.14);}
.profile-name{font-size:1.65rem; font-weight:950; color:#fff; letter-spacing:-.03em; line-height:1.05; margin:.65rem 0 .28rem;}
.profile-sub{color:#a7b1c2; font-size:.94rem; font-weight:850; margin-bottom:.5rem;}
.profile-metrics{display:grid; grid-template-columns:repeat(4,minmax(120px,1fr)); gap:.65rem; margin:.8rem 0 .9rem;}
@media(max-width:1200px){.profile-metrics{grid-template-columns:repeat(2,minmax(120px,1fr));}}
.profile-metric{border:1px solid rgba(255,255,255,.11); background:#0b1220; border-radius:18px; padding:.72rem .76rem; min-height:88px; overflow:hidden;}
.profile-metric .lab{font-size:.65rem;text-transform:uppercase;color:#93a4bb;font-weight:950;letter-spacing:.075em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.profile-metric .val{font-size:1.22rem;color:#fff;font-weight:950;line-height:1.08;margin-top:.32rem;word-break:break-word;}
.profile-section{border-top:1px solid rgba(255,255,255,.10); padding-top:.78rem; margin-top:.78rem;}
.profile-section h4{font-size:.82rem; color:#f8fafc; margin:0 0 .35rem; text-transform:uppercase; letter-spacing:.075em;}
.profile-section p{font-size:.91rem; color:#cbd5e1; line-height:1.48; margin:.1rem 0;}
.selector-note{background:rgba(59,130,246,.12);border:1px solid rgba(96,165,250,.28);border-radius:18px;padding:.72rem .9rem;color:#bfdbfe;font-size:.86rem;line-height:1.38;margin:.4rem 0 .8rem;}
.method-card{background:rgba(245,158,11,.10);border:1px solid rgba(251,191,36,.28);border-radius:18px;padding:.8rem .92rem;color:#fde68a;margin:.48rem 0 .7rem;}
hr{border:none;border-top:1px solid rgba(255,255,255,.10);margin:1rem 0;}
</style>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# CARGA Y NORMALIZACIÓN
# =============================================================================
_cache_data = getattr(st, "cache_data", st.cache)


def _norm_key(x: str) -> str:
    s = "" if pd.isna(x) else str(x)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^A-Z0-9]+", " ", s.upper()).strip()
    return re.sub(r"\s+", " ", s)


SPECIAL_CIRC = {"CITREP", "AFRODESCENDIENTES", "INDÍGENAS", "INDIGENAS", "OPOSICIÓN", "OPOSICION"}


@_cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    text_cols = [
        "cargo", "corporacion", "circunscripcion", "departamento", "territorio_lectura", "partido", "partido_corto",
        "nombre", "nombre_titulo", "perfil", "participacion_politica", "casa_politica", "familia_apoyos",
        "formula", "sector", "apoyo_presidencia_primera", "apoyo_presidencia_segunda", "observacion_adicional",
        "asesor", "foto_path", "tipo_votacion", "grupo_lista_id"
    ]
    for c in text_cols:
        if c in df.columns:
            df[c] = df[c].fillna("").astype(str).str.strip()
    for c in ["votos_esc", "votos_pre", "votos_partido_original", "votos_lista_grupo", "votos_partido_visible", "votos_lista_ficha", "orden_original"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["es_lider_lista", "tiene_foto"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.lower().isin(["true", "1", "yes", "si", "sí"])

    df["circunscripcion"] = df["circunscripcion"].replace({"AFRODESCENDI": "AFRODESCENDIENTES"})
    df["partido_corto"] = df["partido_corto"].replace("", np.nan).fillna(df["partido"])
    df["nombre_titulo"] = df["nombre_titulo"].replace("", np.nan).fillna(df["nombre"].str.title())
    df["territorio_lectura"] = df["territorio_lectura"].replace("", np.nan).fillna(df["departamento"])
    df["sector"] = df["sector"].replace("", "No registra").fillna("No registra")
    df["apoyo_presidencia_primera"] = df["apoyo_presidencia_primera"].replace("", "No registra").fillna("No registra")
    df["apoyo_presidencia_segunda"] = df["apoyo_presidencia_segunda"].replace("", "No registra").fillna("No registra")

    # Para análisis agregados se conserva votos_partido_visible solo en la fila líder,
    # evitando duplicar votación de listas. Para fichas individuales sí se muestra
    # la votación total de la lista/grupo a todos sus integrantes.
    if "votos_lista_ficha" not in df.columns:
        df["votos_lista_ficha"] = np.nan
    df["votos_lista_ficha"] = df["votos_lista_ficha"].fillna(df.get("votos_lista_grupo"))
    df["votos_lista_ficha"] = df["votos_lista_ficha"].fillna(df.get("votos_partido_visible"))
    df["votos_lista_ficha"] = df["votos_lista_ficha"].fillna(df.get("votos_partido_original"))

    def block(row):
        circ = str(row.get("circunscripcion", "")).strip().upper()
        if circ in {"CITREP"}:
            return "CITREP"
        if circ in {"AFRODESCENDIENTES", "AFRODESCENDI"}:
            return "AFRO"
        if circ in {"INDÍGENAS", "INDIGENAS"}:
            return "INDÍGENAS"
        if circ in {"OPOSICIÓN", "OPOSICION"}:
            return "OPOSICIÓN"
        return str(row.get("partido_corto", "")).strip() or str(row.get("partido", "")).strip()

    df["bloque_visual"] = df.apply(block, axis=1)
    df["bloque_key"] = df["bloque_visual"].map(_norm_key)

    def territory_base(row):
        circ_key = _norm_key(row.get("circunscripcion", ""))
        raw_dep = row.get("departamento", "")
        dep = "" if pd.isna(raw_dep) else str(raw_dep).strip()
        dep = "" if dep.lower() in {"nan", "none", "null", "no registra"} else dep
        raw_terr = row.get("territorio_lectura", "")
        terr = "" if pd.isna(raw_terr) else str(raw_terr).strip()
        terr = terr if terr and terr.lower() not in {"nan", "none", "null", "no registra"} else dep
        if circ_key == "CITREP":
            return "CITREP"
        if circ_key in {"AFRODESCENDIENTES", "AFRODESCENDI"}:
            return "AFRO"
        if circ_key in {"INDIGENAS", "INDIGENAS"}:
            return "INDÍGENAS"
        if circ_key in {"OPOSICION"}:
            return "OPOSICIÓN"
        # Para Senado nacional se usa el departamento de origen registrado,
        # evitando duplicar ANTIOQUIA vs NACIONAL · ANTIOQUIA.
        if dep:
            return dep
        terr = re.sub(r"^NACIONAL\s*[·\-:]\s*", "", terr, flags=re.I).strip()
        return terr or "No registra"

    df["territorio_resumen"] = df.apply(territory_base, axis=1)
    return df


df0 = load_data()


@_cache_data(show_spinner=False)
def load_commissions() -> pd.DataFrame:
    if not COMMISSIONS_PATH.exists():
        return pd.DataFrame(columns=["categoria", "corporacion", "tipo_comision", "nombre_comision", "cantidad_integrantes", "integrantes", "restriccion"])
    cm = pd.read_csv(COMMISSIONS_PATH, encoding="utf-8-sig")
    for c in ["categoria", "corporacion", "tipo_comision", "nombre_comision", "cantidad_integrantes", "cantidad_texto", "restriccion"]:
        if c in cm.columns:
            cm[c] = cm[c].fillna("").astype(str).str.strip()
    if "integrantes" in cm.columns:
        cm["integrantes"] = pd.to_numeric(cm["integrantes"], errors="coerce").fillna(0).astype(int)
    else:
        cm["integrantes"] = cm["cantidad_integrantes"].astype(str).str.extract(r"(\d+)").fillna(0).astype(int)
    for c in ["adicional_citrep", "adicional_oposicion", "integrantes_sin_citrep", "integrantes_con_adiciones", "orden_comision"]:
        if c in cm.columns:
            cm[c] = pd.to_numeric(cm[c], errors="coerce").fillna(0).astype(int)
        else:
            cm[c] = 0
    if "ley_2267" not in cm.columns:
        cm["ley_2267"] = ""
    return cm


comisiones_df = load_commissions()

# =============================================================================
# UTILIDADES
# =============================================================================
def h(x) -> str:
    return html.escape("" if pd.isna(x) else str(x))


def clean_value(x, fallback="No registra") -> str:
    if pd.isna(x):
        return fallback
    s = str(x).strip()
    return s if s and s.lower() not in {"nan", "none", "null", "no registra"} else fallback


def fmt_int(x) -> str:
    if pd.isna(x):
        return "—"
    try:
        return f"{int(round(float(x))):,}".replace(",", ".")
    except Exception:
        return "—"


def fmt_compact(x) -> str:
    if pd.isna(x):
        return "—"
    try:
        v = float(x)
        if abs(v) >= 1_000_000:
            return f"{v/1_000_000:.1f}M".replace(".", ",")
        if abs(v) >= 1_000:
            return f"{v/1_000:.0f}K"
        return fmt_int(v)
    except Exception:
        return "—"


def fmt_pct(x) -> str:
    if pd.isna(x):
        return "—"
    return f"{float(x):.1f}%".replace(".", ",")


def abbreviate(s: str, max_len: int = 22) -> str:
    s = clean_value(s, "No registra")
    repl = {
        "PARTIDO ": "", "COLOMBIANO": "", "COLOMBIANA": "", "MOVIMIENTO ": "MOV. ",
        "ASOCIACIÓN": "ASOC.", "AFRODESCENDIENTES": "AFRO", "DE LA UNIÓN POR LA GENTE - ": "",
        "CENTRO DEMOCRÁTICO": "CENTRO DEM.", "PACTO HISTÓRICO": "PACTO HIST.",
        "CONSERVADOR": "CONSERV.", "CAMBIO RADICAL": "CAMBIO RAD.", "NUEVO LIBERALISMO": "NUEVO LIB.",
        "SALVACIÓN NACIONAL": "SALVACIÓN NAC.", "DEMÓCRATA COLOMBIANO": "DEMÓCRATA"
    }
    out = s
    for a, b in repl.items():
        out = out.replace(a, b)
    out = re.sub(r"\s+", " ", out).strip(" -")
    return out if len(out) <= max_len else out[: max_len - 1].rstrip() + "…"


def initials(label: str) -> str:
    key = _norm_key(label)
    special = {
        "PACTO HISTORICO": "PH", "CENTRO DEMOCRATICO": "CD", "LIBERAL": "PL", "CONSERVADOR": "PC",
        "PARTIDO DE LA U": "U", "CAMBIO RADICAL": "CR", "ALIANZA VERDE": "AV", "CITREP": "CITREP",
        "AFRO": "AFRO", "INDIGENAS": "IND", "OPOSICION": "OP", "MOVIMIENTO SALVACION NACIONAL": "MSN",
        "COLOMBIA RENACIENTE": "CR", "NUEVO LIBERALISMO": "NL", "DEMOCRATA COLOMBIANO": "DC",
    }
    if key in special:
        return special[key]
    words = [w for w in key.split() if w not in {"DE", "DEL", "LA", "EL", "LOS", "LAS", "Y", "POR", "PARA"}]
    if not words:
        return "—"
    return (words[0][:3] if len(words) == 1 else "".join(w[0] for w in words[:3]))[:5]


def top_mode(s: pd.Series) -> str:
    s = s.dropna().astype(str).str.strip()
    s = s[(s != "") & (s.str.lower() != "no registra")]
    return "No registra" if s.empty else s.value_counts().index[0]


def _palette_lookup(label: str, palette: dict, default: str = "#64748B") -> str:
    key = _norm_key(label)
    return palette.get(key, default)


SECTOR_COLORS = {
    "IZQUIERDA": "#EF4444",
    "DERECHA": "#3B82F6",
    "INDEPENDIENTE": "#10B981",
    "NO REGISTRA": "#94A3B8",
}

PRES_COLORS = {
    "IVAN CEPEDA": "#60A5FA",
    "PALOMA VALENCIA": "#F87171",
    "ABELARDO DE LA ESPRIELLA": "#C084FC",
    "MAURICIO LIZCANO": "#34D399",
    "SERGIO FAJARDO": "#FBBF24",
    "NO REGISTRA": "#94A3B8",
}


def distribution_bars(series: pd.Series, order: List[str] = None, max_items: int = 8, palette: dict = None) -> str:
    """Bloque visual de distribución para el reporte de bancada/grupo.

    Se devuelve HTML compacto, sin sangrías iniciales, para evitar que
    Markdown lo interprete como bloque de código dentro de Streamlit.
    """
    s = series.fillna("No registra").replace("", "No registra").astype(str).str.strip()
    vc = s.value_counts()
    if order:
        used = set()
        ordered = []
        for x in order:
            v = int(vc.get(x, 0))
            if v > 0:
                ordered.append((x, v))
                used.add(x)
        ordered += [(idx, int(val)) for idx, val in vc.items() if idx not in used]
    else:
        ordered = [(idx, int(val)) for idx, val in vc.items()]
    ordered = ordered[:max_items]
    total = max(int(vc.sum()), 1)
    if not ordered:
        return "<div class='dist-item'><div class='dist-label'>No registra</div><div class='dist-count'>0</div><div class='dist-pct'>0%</div><div class='dist-track'><div class='dist-fill' style='--w:0%;--accent:#64748B;'></div></div></div>"
    html = []
    for label, val in ordered:
        pct = (val / total) * 100
        color = _palette_lookup(label, palette or {}, default="#64748B")
        html.append(
            "<div class='dist-item'>"
            f"<div class='dist-label' title='{h(label)}'>{h(abbreviate(label, 32))}</div>"
            f"<div class='dist-count'>{fmt_int(val)}</div>"
            f"<div class='dist-pct'>{pct:.0f}%</div>"
            f"<div class='dist-track'><div class='dist-fill' style='--w:{pct:.2f}%;--accent:{color};'></div></div>"
            "</div>"
        )
    return "".join(html)


def selected_party_report(group_df: pd.DataFrame) -> str:
    total = len(group_df)
    sen = int((group_df["corporacion"] == "Senado").sum()) if total else 0
    cam = int((group_df["corporacion"] == "Cámara").sum()) if total else 0
    orgs = int(group_df["partido"].replace("", np.nan).nunique()) if total else 0
    circ = int(group_df["circunscripcion"].replace("", np.nan).nunique()) if total else 0
    vot_lista = group_df[["grupo_lista_id", "votos_lista_ficha"]].drop_duplicates()["votos_lista_ficha"].sum(min_count=1)
    kpis = "".join([
        f"<div class='group-kpi'><div class='group-kpi-label'>Curules del grupo</div><div class='group-kpi-value'>{fmt_int(total)}</div><div class='group-kpi-help'>Total bajo filtros activos</div></div>",
        f"<div class='group-kpi'><div class='group-kpi-label'>Senado / Cámara</div><div class='group-kpi-value'>{fmt_int(sen)} / {fmt_int(cam)}</div><div class='group-kpi-help'>Distribución corporativa</div></div>",
        f"<div class='group-kpi'><div class='group-kpi-label'>Organizaciones reales</div><div class='group-kpi-value'>{fmt_int(orgs)}</div><div class='group-kpi-help'>Partidos/listas registrados</div></div>",
        f"<div class='group-kpi'><div class='group-kpi-label'>Circunscripciones</div><div class='group-kpi-value'>{fmt_int(circ)}</div><div class='group-kpi-help'>Tipos presentes en el grupo</div></div>",
        f"<div class='group-kpi'><div class='group-kpi-label'>Voto lista/grupo</div><div class='group-kpi-value'>{fmt_compact(vot_lista)}</div><div class='group-kpi-help'>Contexto electoral, sin duplicar agregados</div></div>",
    ])
    sector_html = distribution_bars(group_df['sector'], SECTOR_ORDER, max_items=5, palette=SECTOR_COLORS)
    pv_html = distribution_bars(group_df['apoyo_presidencia_primera'], max_items=6, palette=PRES_COLORS)
    sv_html = distribution_bars(group_df['apoyo_presidencia_segunda'], max_items=6, palette=PRES_COLORS)
    panels = (
        "<div class='group-panels'>"
        "<div class='group-panel'><div class='group-panel-title'>Composición política <span>curules</span></div>" + sector_html + "</div>"
        "<div class='group-panel'><div class='group-panel-title'>Apoyo presidencial · 1ª vuelta <span>registros</span></div>" + pv_html + "</div>"
        "<div class='group-panel'><div class='group-panel-title'>Apoyo presidencial · 2ª vuelta <span>registros</span></div>" + sv_html + "</div>"
        "</div>"
    )
    note = "<div class='group-note'><b>Nota de lectura.</b> Esta sección describe la composición interna registrada para los congresistas del grupo seleccionado. No debe leerse como posición oficial única de toda la bancada. La votación de lista/grupo se muestra como contexto de la ficha, pero no se duplica en rankings ni KPIs agregados.</div>"
    return "<div class='group-report'><div class='group-kpis'>" + kpis + "</div>" + panels + note + "</div>"

def options_from(df: pd.DataFrame, col: str) -> List[str]:
    return sorted([str(v) for v in df[col].dropna().unique() if str(v).strip() and str(v).lower() != "nan"])


# Paleta recuperada de criterios previos del usuario: color estable por partido/grupo.
PARTY_COLORS_BY_KEY = {
    # Paleta histórica definida previamente para análisis electoral colombiano.
    "PACTO HISTORICO": "#6A1B9A",
    "PACTO HIST": "#6A1B9A",
    "COLOMBIA HUMANA": "#6A1B9A",
    "LIBERAL": "#E41E26",
    "PARTIDO LIBERAL COLOMBIANO": "#E41E26",
    "CENTRO DEMOCRATICO": "#0D2B52",
    "PARTIDO CENTRO DEMOCRATICO": "#0D2B52",
    "CONSERVADOR": "#3A86E0",
    "PARTIDO CONSERVADOR COLOMBIANO": "#3A86E0",
    "CAMBIO RADICAL": "#E84393",
    "PARTIDO CAMBIO RADICAL": "#E84393",
    "ALIANZA VERDE": "#00B050",
    "PARTIDO ALIANZA VERDE": "#00B050",
    "PARTIDO DE LA U": "#F39C12",
    "PARTIDO DE LA UNION POR LA GENTE PARTIDO DE LA U": "#F39C12",
    "NUEVO LIBERALISMO": "#A00000",
    "MIRA": "#0B3D91",
    "PARTIDO POLITICO MIRA": "#0B3D91",
    "DIGNIDAD COMPROMISO": "#7E22CE",
    "ASI": "#9AD165",
    "PARTIDO ALIANZA SOCIAL INDEPENDIENTE ASI": "#9AD165",
    "POLO": "#FDE047",
    "MAIS": "#CA8A04",
    "MOVIMIENTO ALTERNATIVO INDIGENA Y SOCIAL MAIS": "#CA8A04",
    "AICO": "#111111",
    "MOVIMIENTO AUTORIDADES INDIGENAS DE COLOMBIA AICO": "#111111",
    "UP": "#FACC15",
    "GENTE EN MOVIMIENTO": "#16A34A",
    "DEMOCRATA COLOMBIANO": "#4F6DCC",
    "PARTIDO DEMOCRATA COLOMBIANO": "#4F6DCC",
    "COMUNES": "#9CA3AF",
    "VERDE OXIGENO": "#84CC16",
    "ECOLOGISTA": "#14532D",
    "LIGA": "#EAB308",
    "POLITICO LA FUERZA": "#F08A80",
    "PARTIDO POLITICO LA FUERZA": "#F08A80",
    "ALIANZA DEMOCRATICA AMPLIA": "#FEF08A",
    "MOVIMIENTO SALVACION NACIONAL": "#737373",
    "COLOMBIA RENACIENTE": "#FDBA74",
    "COLOMBIA JUSTA LIBRES": "#27272A",
    "PODER POPULAR": "#F87171",
    "CREEMOS": "#B57AD3",
    "EN MARCHA": "#06B6D4",
    "POR DEFINIR": "#94A3B8",
    "CITREP": "#C69200",
    "AFRO": "#111111",
    "AFRODESCENDIENTES": "#111111",
    "INDIGENAS": "#7FBF4D",
    "OPOSICION": "#BDBDBD",
    "NO REGISTRA": "#94A3B8",
}
FALLBACK_PALETTE = ["#ef4444", "#3b82f6", "#22c55e", "#f59e0b", "#8b5cf6", "#06b6d4", "#f97316", "#10b981", "#d946ef", "#eab308"]
SECTOR_ORDER = ["IZQUIERDA", "INDEPENDIENTE", "DERECHA", "No registra"]
SECTOR_COLORS = {"IZQUIERDA": "#ef4444", "DERECHA": "#3b82f6", "INDEPENDIENTE": "#10b981", "No registra": "#94a3b8"}
APOYO_COLORS = {
    "IVAN CEPEDA": "#ef4444",
    "ABELARDO DE LA ESPRIELLA": "#3b82f6",
    "PALOMA VALENCIA": "#f59e0b",
    "SERGIO FAJARDO": "#06b6d4",
    "MAURICIO LIZCANO": "#10b981",
    "No registra": "#94a3b8",
}


def party_color(label: str) -> str:
    key = _norm_key(label)
    if key in PARTY_COLORS_BY_KEY:
        return PARTY_COLORS_BY_KEY[key]
    for k, v in PARTY_COLORS_BY_KEY.items():
        if k and (k in key or key in k):
            return v
    return FALLBACK_PALETTE[abs(hash(key)) % len(FALLBACK_PALETTE)]


def color_for(label: str, mode: str = "party") -> str:
    if mode == "sector":
        return SECTOR_COLORS.get(clean_value(label), "#94a3b8")
    if mode == "apoyo":
        return APOYO_COLORS.get(clean_value(label), party_color(label))
    if mode == "corporacion":
        return {"Senado": "#38bdf8", "Cámara": "#f43f5e"}.get(clean_value(label), "#94a3b8")
    return party_color(label)


def guide(title, lines):
    html_lines = "".join([f"<p>• {h(line)}</p>" for line in (lines if isinstance(lines, list) else [lines])])
    st.markdown(f"<div class='guide'><h3>{h(title)}</h3>{html_lines}</div>", unsafe_allow_html=True)


def kpi_grid(items: List[Tuple[str, str, str]]):
    content = "".join(
        f"<div class='kpi-card'><div class='kpi-label'>{h(label)}</div><div class='kpi-value' title='{h(value)}'>{h(value)}</div><div class='kpi-help'>{h(help)}</div></div>"
        for label, value, help in items
    )
    st.markdown(f"<div class='kpi-grid'>{content}</div>", unsafe_allow_html=True)


def legend_grid(summary: pd.DataFrame, label_col: str, color_mode: str = "party", value_col: str = "curules", max_items: int = 24):
    if summary.empty:
        return
    d = summary.sort_values(value_col, ascending=False).head(max_items).copy()
    items = []
    for _, r in d.iterrows():
        label = clean_value(r[label_col])
        items.append(
            f"<div class='legend-item'><span class='legend-dot' style='background:{color_for(label, color_mode)}'></span>"
            f"<span class='legend-text' title='{h(label)}'>{h(abbreviate(label, 26))}</span>"
            f"<span class='legend-count'>{fmt_int(r[value_col])}</span></div>"
        )
    st.markdown("<div class='legend-grid'>" + "".join(items) + "</div>", unsafe_allow_html=True)


def safe_plot(fig: go.Figure, height: int = None):
    fig.update_layout(
        template="plotly_dark",
        font=dict(family="Arial, sans-serif", size=12, color="#e5e7eb"),
        paper_bgcolor="#0b1220",
        plot_bgcolor="#0b1220",
        margin=dict(l=28, r=28, t=58, b=45),
        legend=dict(font=dict(color="#e5e7eb", size=11), bgcolor="rgba(0,0,0,0)"),
    )
    if height:
        fig.update_layout(height=height)
    try:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    except TypeError:
        st.plotly_chart(fig, config={"displayModeBar": False, "responsive": True})


def safe_df(dataframe: pd.DataFrame, height: int = None):
    try:
        st.dataframe(dataframe, use_container_width=True, hide_index=True, height=height)
    except TypeError:
        st.dataframe(dataframe, height=height)


@_cache_data(show_spinner=False)
def image_data_uri(rel_path: str) -> str:
    p = BASE_DIR / str(rel_path)
    if not p.exists():
        p = PLACEHOLDER
    suffix = p.suffix.lower()
    mime = "image/svg+xml" if suffix == ".svg" else "image/png" if suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("utf-8")


def party_summary(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(columns=["bloque_visual", "curules", "senado", "camara", "sector", "primera", "segunda", "votos_senado", "votos_camara"])
    base = data.groupby("bloque_visual", as_index=False).agg(
        curules=("nombre_titulo", "count"),
        senado=("corporacion", lambda s: int((s == "Senado").sum())),
        camara=("corporacion", lambda s: int((s == "Cámara").sum())),
        organizaciones=("partido", pd.Series.nunique),
        sector=("sector", top_mode),
        primera=("apoyo_presidencia_primera", top_mode),
        segunda=("apoyo_presidencia_segunda", top_mode),
    )
    votes = data.groupby(["bloque_visual", "corporacion"], as_index=False)["votos_partido_visible"].sum(min_count=1)
    piv = votes.pivot(index="bloque_visual", columns="corporacion", values="votos_partido_visible").reset_index().rename_axis(None, axis=1)
    for c in ["Senado", "Cámara"]:
        if c not in piv.columns:
            piv[c] = np.nan
    out = base.merge(piv[["bloque_visual", "Senado", "Cámara"]], on="bloque_visual", how="left")
    out = out.rename(columns={"Senado": "votos_senado", "Cámara": "votos_camara"})
    return out.sort_values("curules", ascending=False)


def _basic_counts(data: pd.DataFrame):
    total = len(data)
    sen = int((data["corporacion"] == "Senado").sum()) if not data.empty else 0
    cam = int((data["corporacion"] == "Cámara").sum()) if not data.empty else 0
    cam_votes = data.loc[data["corporacion"] == "Cámara", "votos_partido_visible"].sum(min_count=1) if not data.empty else np.nan
    sen_votes = data.loc[data["corporacion"] == "Senado", "votos_partido_visible"].sum(min_count=1) if not data.empty else np.nan
    return total, sen, cam, cam_votes, sen_votes


def kpis_for_module(data: pd.DataFrame, view_label: str, modulo_label: str) -> List[Tuple[str, str, str]]:
    """KPIs propios por módulo. Evita repetir la misma lectura en todo el dashboard."""
    if data.empty:
        return [("Sin registros", "0", "Ajuste los filtros"), ("Vista", view_label, "Universo seleccionado"), ("Cámara", "—", "Sin datos"), ("Senado", "—", "Sin datos"), ("Mayoría", "—", "No aplica")]

    ps = party_summary(data)
    total, sen, cam, cam_votes, sen_votes = _basic_counts(data)
    majority = total // 2 + 1
    top = ps.iloc[0]
    top_name = clean_value(top["bloque_visual"])
    top_curules = int(top["curules"])
    top_share = top_curules / total * 100 if total else 0

    if modulo_label.startswith("1"):
        return [
            ("Curules", fmt_int(total), f"{sen} Senado · {cam} Cámara" if view_label == "Congreso en pleno" else f"Vista: {view_label}"),
            ("Bancada líder", top_name, f"{top_curules} curules · {fmt_pct(top_share)}"),
            ("Mayoría decisoria", fmt_int(majority), "Mitad más uno del universo filtrado"),
            ("Votación Cámara", fmt_compact(cam_votes), "Lista/partido · no se suma con Senado"),
            ("Votación Senado", fmt_compact(sen_votes), "Lista/partido · no se suma con Cámara"),
        ]

    if modulo_label.startswith("2"):
        second = ps.iloc[1] if len(ps) > 1 else None
        gap = top_curules - (int(second["curules"]) if second is not None else 0)
        missing = max(majority - top_curules, 0)
        return [
            ("Bancadas", fmt_int(ps["bloque_visual"].nunique()), "Partidos + grupos especiales"),
            ("Bancada líder", top_name, f"{top_curules} curules · {fmt_pct(top_share)}"),
            ("Segunda bancada", clean_value(second["bloque_visual"]) if second is not None else "—", f"{int(second['curules'])} curules" if second is not None else "Sin segunda fuerza"),
            ("Diferencia líder", fmt_int(gap), "Curules de ventaja frente a la segunda"),
            ("Faltan para mayoría", fmt_int(missing), "Respecto a la bancada líder"),
        ]

    if modulo_label.startswith("3"):
        closed = int((data["tipo_votacion"].astype(str).str.contains("cerrada", case=False, na=False)).sum())
        with_individual = int(data[["votos_esc", "votos_pre"]].notna().any(axis=1).sum())
        sen_leader = ps.sort_values("votos_senado", ascending=False).dropna(subset=["votos_senado"]).head(1)
        cam_leader = ps.sort_values("votos_camara", ascending=False).dropna(subset=["votos_camara"]).head(1)
        return [
            ("Votación Cámara", fmt_compact(cam_votes), "Lista/partido · lectura separada"),
            ("Votación Senado", fmt_compact(sen_votes), "Lista/partido · lectura separada"),
            ("Líder Cámara", clean_value(cam_leader.iloc[0]["bloque_visual"]) if not cam_leader.empty else "—", fmt_compact(cam_leader.iloc[0]["votos_camara"]) if not cam_leader.empty else "Sin dato"),
            ("Líder Senado", clean_value(sen_leader.iloc[0]["bloque_visual"]) if not sen_leader.empty else "—", fmt_compact(sen_leader.iloc[0]["votos_senado"]) if not sen_leader.empty else "Sin dato"),
            ("Listas cerradas", fmt_int(closed), f"{with_individual} registros con voto individual"),
        ]

    if modulo_label.startswith("4"):
        first = data["apoyo_presidencia_primera"].replace("", "No registra").fillna("No registra").value_counts()
        second = data["apoyo_presidencia_segunda"].replace("", "No registra").fillna("No registra").value_counts()
        changed = int((data["apoyo_presidencia_primera"].fillna("") != data["apoyo_presidencia_segunda"].fillna("")).sum())
        no2 = int(second.get("No registra", 0)) if not second.empty else 0
        return [
            ("Líder 1ª vuelta", clean_value(first.index[0]) if not first.empty else "—", f"{int(first.iloc[0]) if not first.empty else 0} curules"),
            ("Líder 2ª vuelta", clean_value(second.index[0]) if not second.empty else "—", f"{int(second.iloc[0]) if not second.empty else 0} curules"),
            ("Realineadas", fmt_int(changed), "Curules con apoyo distinto entre vueltas"),
            ("Sin registro 2ª", fmt_int(no2), "Dato no reportado o no aplica"),
            ("Opciones 2ª", fmt_int(len(second)), "Destinos de apoyo registrados"),
        ]

    if modulo_label.startswith("5"):
        dpt = data.groupby("territorio_resumen").size().sort_values(ascending=False)
        specials = int(data["circunscripcion"].isin(["CITREP", "AFRODESCENDIENTES", "INDÍGENAS", "OPOSICIÓN"]).sum())
        return [
            ("Territorios", fmt_int(data["territorio_resumen"].nunique()), "Departamentos + especiales"),
            ("Territorio líder", clean_value(dpt.index[0]) if not dpt.empty else "—", f"{int(dpt.iloc[0]) if not dpt.empty else 0} dignidades"),
            ("Cámara", fmt_int(cam), "Curules/dignidades bajo filtros"),
            ("Senado", fmt_int(sen), "Curules/dignidades bajo filtros"),
            ("Especiales", fmt_int(specials), "CITREP, Afro, Indígenas, Oposición"),
        ]

    if modulo_label.startswith("7"):
        cm = load_commissions()
        total_comm = len(cm)
        constitutional = int((cm["tipo_comision"].str.upper() == "CONSTITUCIONAL").sum()) if not cm.empty else 0
        legal = int((cm["tipo_comision"].str.upper() == "LEGAL").sum()) if not cm.empty else 0
        sen_comm = int((cm["corporacion"] == "Senado").sum()) if not cm.empty else 0
        cam_comm = int((cm["corporacion"] == "Cámara").sum()) if not cm.empty else 0
        return [
            ("Comisiones", fmt_int(total_comm), "Registros del archivo de integración"),
            ("Constitucionales", fmt_int(constitutional), "Comisiones permanentes por corporación"),
            ("Legales", fmt_int(legal), "Propias, bicamerales e interparlamentarias"),
            ("Cámara/Senado", f"{fmt_int(cam_comm)} / {fmt_int(sen_comm)}", "Registros por corporación"),
            ("Método", "Cuociente", "Parte entera + mayores residuos"),
        ]

    if modulo_label.startswith("6"):
        photos = int(data["tiene_foto"].sum()) if "tiene_foto" in data else 0
        prof = int(data["perfil"].astype(str).str.len().gt(5).sum()) if "perfil" in data else 0
        return [
            ("Fichas", fmt_int(total), "Disponibles bajo filtros"),
            ("Bancadas", fmt_int(data["bloque_visual"].nunique()), "Grupos consultables"),
            ("Con foto", fmt_int(photos), "Imagen extraída del Excel"),
            ("Con perfil", fmt_int(prof), "Texto diligenciado"),
            ("Asesores", fmt_int(data["asesor"].replace("", np.nan).nunique()), "Asignaciones registradas"),
        ]

    return [
        ("Registros", fmt_int(total), "Bajo filtros actuales"),
        ("Bancadas", fmt_int(data["bloque_visual"].nunique()), "Partidos + grupos especiales"),
        ("Listas cerradas", fmt_int((data["tipo_votacion"].astype(str).str.contains("cerrada", case=False, na=False)).sum()), "Sin voto individual imputado"),
        ("Votación Cámara", fmt_compact(cam_votes), "Lectura separada"),
        ("Votación Senado", fmt_compact(sen_votes), "Lectura separada"),
    ]


# =============================================================================
# GRÁFICAS OSCURAS Y LEGIBLES
# =============================================================================
def group_order(data: pd.DataFrame, mode: str = "Tamaño de bancada") -> List[str]:
    ps = party_summary(data)
    if mode == "Sector político":
        sector_rank = {"IZQUIERDA": 0, "INDEPENDIENTE": 1, "DERECHA": 2, "No registra": 3}
        ps["_rank"] = ps["sector"].map(sector_rank).fillna(9)
        ps = ps.sort_values(["_rank", "curules"], ascending=[True, False])
    else:
        ps = ps.sort_values("curules", ascending=False)
    return ps["bloque_visual"].tolist()


def hemicycle_positions(n: int) -> pd.DataFrame:
    # Capacidades crecientes para formar un hemiciclo estable y sin recortes.
    rows = 8 if n >= 220 else 7 if n >= 120 else 5
    weights = np.linspace(0.75, 1.65, rows)
    caps = np.maximum(2, np.round(n * weights / weights.sum()).astype(int))
    diff = n - caps.sum()
    i = rows - 1
    while diff != 0:
        if diff > 0:
            caps[i] += 1; diff -= 1
        elif caps[i] > 2:
            caps[i] -= 1; diff += 1
        i = (i - 1) % rows
    pts = []
    for r, cap in enumerate(caps, start=1):
        radius = 1.15 + r * 0.50
        angles = np.linspace(math.radians(164), math.radians(16), int(cap))
        for a in angles:
            pts.append({"x": radius * math.cos(a), "y": radius * math.sin(a), "row": r, "angle": a})
    pos = pd.DataFrame(pts)
    # La asignación por ángulo produce bloques contiguos por bancada, no puntos dispersos.
    return pos.sort_values(["angle", "row"], ascending=[False, True]).reset_index(drop=True).iloc[:n]


def hemicycle_fig(data: pd.DataFrame, color_by: str = "bloque_visual", order_mode: str = "Tamaño de bancada", title: str = "Hemiciclo del Congreso") -> go.Figure:
    if data.empty:
        return go.Figure()
    d = data.copy()
    if color_by == "bloque_visual":
        order = group_order(d, order_mode)
        d["_g"] = pd.Categorical(d["bloque_visual"], categories=order, ordered=True)
        d = d.sort_values(["_g", "corporacion", "territorio_lectura", "nombre_titulo"]).reset_index(drop=True)
        color_mode = "party"
    elif color_by == "sector":
        order = {v: i for i, v in enumerate(SECTOR_ORDER)}
        d["_g"] = d["sector"].map(order).fillna(9)
        d = d.sort_values(["_g", "bloque_visual", "corporacion", "nombre_titulo"]).reset_index(drop=True)
        color_mode = "sector"
    elif color_by == "corporacion":
        d["_g"] = d["corporacion"].map({"Senado": 0, "Cámara": 1}).fillna(9)
        d = d.sort_values(["_g", "bloque_visual", "nombre_titulo"]).reset_index(drop=True)
        color_mode = "corporacion"
    else:
        d = d.sort_values([color_by, "bloque_visual", "corporacion", "nombre_titulo"]).reset_index(drop=True)
        color_mode = "apoyo"

    pos = hemicycle_positions(len(d)).reset_index(drop=True)
    seats = pd.concat([d, pos], axis=1)
    fig = go.Figure()
    marker_size = 15 if len(seats) > 240 else 18
    for label, g in seats.groupby(color_by, dropna=False, sort=False):
        label = clean_value(label)
        custom = np.stack([
            g["nombre_titulo"].astype(str), g["corporacion"].astype(str), g["circunscripcion"].astype(str),
            g["territorio_lectura"].astype(str), g["bloque_visual"].astype(str), g["partido_corto"].astype(str),
            g["sector"].astype(str), g["apoyo_presidencia_primera"].astype(str), g["apoyo_presidencia_segunda"].astype(str),
        ], axis=-1)
        fig.add_trace(go.Scatter(
            x=g["x"], y=g["y"], mode="markers", name=abbreviate(label, 24),
            marker=dict(size=marker_size, color=color_for(label, color_mode), line=dict(width=1.4, color="rgba(255,255,255,.85)"), opacity=.98),
            customdata=custom,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>Corporación: %{customdata[1]}<br>Circunscripción: %{customdata[2]}<br>Territorio: %{customdata[3]}<br>"
                "Grupo visual: %{customdata[4]}<br>Partido real: %{customdata[5]}<br>Sector: %{customdata[6]}<br>1ª vuelta: %{customdata[7]}<br>2ª vuelta: %{customdata[8]}<extra></extra>"
            )
        ))
    fig.update_layout(title=dict(text=title, x=.02, font=dict(size=20, color="#f8fafc")), height=560, showlegend=False, margin=dict(l=10, r=10, t=56, b=10))
    fig.update_xaxes(visible=False, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False)
    return fig


def barh_fig(data: pd.DataFrame, label_col: str, value_col: str, title: str, color_mode: str = "party", max_rows: int = 14, suffix: str = "") -> go.Figure:
    d = data.copy().sort_values(value_col, ascending=False).head(max_rows)
    d["label_short"] = d[label_col].map(lambda x: abbreviate(x, 28))
    d = d.sort_values(value_col, ascending=True)
    colors = [color_for(x, color_mode) for x in d[label_col]]
    mx = float(d[value_col].max()) if not d.empty else 1
    fig = go.Figure(go.Bar(
        x=d[value_col], y=d["label_short"], orientation="h", marker=dict(color=colors, line=dict(color="rgba(255,255,255,.72)", width=1)),
        text=[fmt_int(v) + suffix for v in d[value_col]], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Valor: %{x}<extra></extra>",
    ))
    fig.update_layout(title=dict(text=title, x=.02, font=dict(color="#f8fafc")), height=max(410, 31 * len(d) + 120), margin=dict(l=165, r=78, t=58, b=38))
    fig.update_xaxes(range=[0, mx * 1.18], gridcolor="rgba(255,255,255,.10)", zeroline=False, color="#cbd5e1")
    fig.update_yaxes(color="#e5e7eb", automargin=True)
    return fig


def sector_balance_fig(data: pd.DataFrame, title="Balance político por sectores") -> go.Figure:
    d = data["sector"].value_counts().reindex(SECTOR_ORDER).dropna().reset_index()
    d.columns = ["sector", "curules"]
    total = d["curules"].sum()
    fig = go.Figure()
    for _, r in d.iterrows():
        pct = r["curules"] / total * 100 if total else 0
        fig.add_trace(go.Bar(
            y=["Congreso"], x=[r["curules"]], orientation="h", name=r["sector"],
            marker=dict(color=SECTOR_COLORS.get(r["sector"], "#94a3b8"), line=dict(color="rgba(255,255,255,.7)", width=1)),
            text=[f"{r['sector']} · {int(r['curules'])} ({pct:.1f}%)".replace(".", ",")], textposition="inside", insidetextanchor="middle",
            hovertemplate="%{fullData.name}<br>Curules: %{x}<extra></extra>"
        ))
    fig.update_layout(barmode="stack", title=dict(text=title, x=.02), height=235, margin=dict(l=28, r=28, t=58, b=28), legend=dict(orientation="h", y=-.20))
    fig.update_xaxes(showgrid=False, visible=False)
    fig.update_yaxes(showgrid=False, visible=False)
    return fig


def split_corp_fig(data: pd.DataFrame, title="Senado/Cámara por bancada", max_rows=12) -> go.Figure:
    """Barras horizontales apiladas, ordenadas de mayor a menor de arriba hacia abajo."""
    d = data.groupby(["bloque_visual", "corporacion"], as_index=False).size().rename(columns={"size": "curules"})
    order_desc = d.groupby("bloque_visual")["curules"].sum().sort_values(ascending=False).head(max_rows).index.tolist()
    d = d[d["bloque_visual"].isin(order_desc)].copy()
    y_full = list(reversed(order_desc))  # Plotly ubica el último valor arriba en barras horizontales.
    y_labels = [abbreviate(x, 28) for x in y_full]
    fig = go.Figure()
    for corp, col in [("Senado", "#38bdf8"), ("Cámara", "#f43f5e")]:
        g = d[d["corporacion"] == corp].set_index("bloque_visual")
        vals = [int(g.loc[b, "curules"]) if b in g.index else 0 for b in y_full]
        fig.add_trace(go.Bar(
            y=y_labels, x=vals, orientation="h", name=corp,
            marker=dict(color=col, line=dict(color="rgba(255,255,255,.72)", width=1)),
            text=[v if v > 0 else "" for v in vals], textposition="inside",
            customdata=[[b, sum(int(d[(d["bloque_visual"] == b) & (d["corporacion"] == c)]["curules"].sum()) for c in ["Senado", "Cámara"])] for b in y_full],
            hovertemplate="Bancada: %{customdata[0]}<br>" + corp + ": %{x}<br>Total bancada: %{customdata[1]}<extra></extra>"
        ))
    fig.update_layout(
        barmode="stack", title=dict(text=title, x=.02), height=480,
        margin=dict(l=165, r=38, t=58, b=46), legend=dict(orientation="h", y=-.13),
        yaxis=dict(categoryorder="array", categoryarray=y_labels)
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.10)", color="#cbd5e1")
    fig.update_yaxes(color="#e5e7eb", automargin=True)
    return fig


def votes_fig(data: pd.DataFrame, corp: str, top=12) -> go.Figure:
    d = data[data["corporacion"] == corp].groupby("bloque_visual", as_index=False)["votos_partido_visible"].sum(min_count=1).dropna()
    return barh_fig(d, "bloque_visual", "votos_partido_visible", f"Votos de lista · {corp} (sin mezclar corporaciones)", max_rows=top)


def votes_per_seat_fig(data: pd.DataFrame, corp: str, top=12) -> go.Figure:
    dd = data[data["corporacion"] == corp]
    if dd.empty:
        return go.Figure()
    d = dd.groupby("bloque_visual", as_index=False).agg(curules=("nombre_titulo", "count"), votos=("votos_partido_visible", "sum"))
    d = d.dropna(subset=["votos"])
    d["votos_por_curul"] = d["votos"] / d["curules"]
    return barh_fig(d, "bloque_visual", "votos_por_curul", f"Votos por curul · {corp}", max_rows=top)


def presidential_flow_fig(data: pd.DataFrame) -> go.Figure:
    """Diagrama de flujo 1ª → 2ª vuelta. Más legible que una matriz de calor."""
    d = data.copy()
    d["primera"] = d["apoyo_presidencia_primera"].replace("", "No registra").fillna("No registra")
    d["segunda"] = d["apoyo_presidencia_segunda"].replace("", "No registra").fillna("No registra")
    flow = d.groupby(["primera", "segunda"], as_index=False).size().rename(columns={"size": "curules"})
    flow = flow[flow["curules"] > 0].sort_values("curules", ascending=False)
    left_nodes = flow["primera"].drop_duplicates().tolist()
    right_nodes = flow["segunda"].drop_duplicates().tolist()
    nodes = [f"1ª · {x}" for x in left_nodes] + [f"2ª · {x}" for x in right_nodes]
    idx = {n: i for i, n in enumerate(nodes)}
    labels = [abbreviate(n, 30) for n in nodes]
    node_colors = [color_for(x.replace("1ª · ", "").replace("2ª · ", ""), "apoyo") for x in nodes]
    sources = [idx[f"1ª · {r.primera}"] for r in flow.itertuples()]
    targets = [idx[f"2ª · {r.segunda}"] for r in flow.itertuples()]
    values = [int(r.curules) for r in flow.itertuples()]
    link_colors = []
    for r in flow.itertuples():
        base = color_for(r.segunda, "apoyo").lstrip("#")
        try:
            rgb = tuple(int(base[i:i+2], 16) for i in (0, 2, 4))
            link_colors.append(f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.34)")
        except Exception:
            link_colors.append("rgba(203,213,225,0.34)")
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=22, thickness=18,
            line=dict(color="rgba(255,255,255,.55)", width=1),
            label=labels, color=node_colors,
            hovertemplate="%{label}<extra></extra>",
        ),
        link=dict(
            source=sources, target=targets, value=values, color=link_colors,
            hovertemplate="Curules: %{value}<extra></extra>",
        )
    ))
    fig.update_layout(
        title=dict(text="Realineamiento presidencial · flujo de apoyos 1ª → 2ª vuelta", x=.02, font=dict(size=20)),
        height=520, margin=dict(l=20, r=20, t=70, b=28),
    )
    return fig


def presidential_flow_table(data: pd.DataFrame) -> pd.DataFrame:
    d = data.copy()
    d["primera"] = d["apoyo_presidencia_primera"].replace("", "No registra").fillna("No registra")
    d["segunda"] = d["apoyo_presidencia_segunda"].replace("", "No registra").fillna("No registra")
    out = d.groupby(["primera", "segunda"], as_index=False).size().rename(columns={"primera": "1ª vuelta", "segunda": "2ª vuelta", "size": "Curules"})
    out["% del filtro"] = out["Curules"] / len(d) * 100 if len(d) else 0
    out["% del filtro"] = out["% del filtro"].map(lambda x: f"{x:.1f}%".replace(".", ","))
    return out.sort_values("Curules", ascending=False)


def presidential_bar(data: pd.DataFrame, col: str, title: str) -> go.Figure:
    d = data[col].replace("", "No registra").fillna("No registra").value_counts().reset_index()
    d.columns = [col, "curules"]
    return barh_fig(d, col, "curules", title, color_mode="apoyo", max_rows=8)


def territory_stacked_col_fig(data: pd.DataFrame) -> go.Figure:
    """Columnas apiladas: integra Cámara y Senado en una sola columna por departamento/territorio."""
    d = data.copy()
    if "territorio_resumen" not in d.columns:
        d["territorio_resumen"] = d["territorio_lectura"].astype(str).str.replace(r"^NACIONAL\s*[·\-:]\s*", "", regex=True)
    d = d.groupby(["territorio_resumen", "corporacion"], as_index=False).size().rename(columns={"size": "curules"})
    order = d.groupby("territorio_resumen")["curules"].sum().sort_values(ascending=False).index.tolist()
    totals = d.groupby("territorio_resumen")["curules"].sum().to_dict()
    fig = go.Figure()
    x_labels = [abbreviate(x, 14) for x in order]
    for corp, col in [("Cámara", "#f43f5e"), ("Senado", "#38bdf8")]:
        g = d[d["corporacion"] == corp].set_index("territorio_resumen")
        vals = [int(g.loc[t, "curules"]) if t in g.index else 0 for t in order]
        fig.add_trace(go.Bar(
            x=x_labels, y=vals, name=corp,
            marker=dict(color=col, line=dict(color="rgba(255,255,255,.72)", width=1)),
            text=[v if v > 0 else "" for v in vals], textposition="inside", insidetextanchor="middle",
            customdata=[[t, totals.get(t, 0)] for t in order],
            hovertemplate="Territorio: %{customdata[0]}<br>Corporación: " + corp + "<br>Curules: %{y}<br>Total territorio: %{customdata[1]}<extra></extra>",
        ))
    fig.update_layout(
        barmode="stack",
        title=dict(text="Dignidades por departamento/territorio · Cámara + Senado integradas", x=.02),
        height=620, margin=dict(l=55, r=35, t=68, b=150),
        legend=dict(orientation="h", y=-.24, x=.02),
    )
    fig.update_yaxes(title="Curules", gridcolor="rgba(255,255,255,.10)", color="#cbd5e1")
    fig.update_xaxes(tickangle=-48, color="#e5e7eb", tickfont=dict(size=10))
    return fig


def circ_special_fig(data: pd.DataFrame) -> go.Figure:
    """Columnas apiladas por circunscripción, ordenadas por total de curules descendente."""
    d = data.groupby(["circunscripcion", "sector"], as_index=False).size().rename(columns={"size": "curules"})
    order = d.groupby("circunscripcion")["curules"].sum().sort_values(ascending=False).index.tolist()
    fig = go.Figure()
    for sector in SECTOR_ORDER:
        g = d[d["sector"] == sector].set_index("circunscripcion")
        if g.empty:
            continue
        vals = [int(g.loc[c, "curules"]) if c in g.index else 0 for c in order]
        fig.add_trace(go.Bar(
            x=order, y=vals, name=sector,
            marker=dict(color=SECTOR_COLORS.get(sector, "#94a3b8"), line=dict(color="rgba(255,255,255,.72)", width=1)),
            text=[v if v > 0 else "" for v in vals], textposition="inside"
        ))
    totals = d.groupby("circunscripcion")["curules"].sum().to_dict()
    fig.update_layout(
        barmode="stack", title=dict(text="Circunscripciones por sector político", x=.02), height=410,
        margin=dict(l=45, r=38, t=58, b=88), legend=dict(orientation="h", y=-.25),
        xaxis=dict(categoryorder="array", categoryarray=order)
    )
    fig.update_yaxes(gridcolor="rgba(255,255,255,.10)", color="#cbd5e1", title="Curules")
    fig.update_xaxes(color="#e5e7eb", tickangle=-28)
    return fig


# =============================================================================
# INTEGRACIÓN DE COMISIONES POR CUOCIENTE
# =============================================================================
def parse_int_safe(x) -> int:
    try:
        return int(float(x))
    except Exception:
        m = re.search(r"\d+", str(x))
        return int(m.group(0)) if m else 0


def effective_commission_seats(row, include_citrep: bool = True) -> int:
    """Cupos efectivos de la comisión.

    La columna integrantes conserva el cupo base. Las adiciones de la Ley 2267
    se suman cuando aplica: CITREP si el usuario activa el botón; oposición
    siempre se computa como cupo adicional, pero su curul se imputa al partido
    registrado en la base para el universo de bancadas.
    """
    base = parse_int_safe(row.get("integrantes", 0))
    add_opp = parse_int_safe(row.get("adicional_oposicion", 0))
    add_citrep = parse_int_safe(row.get("adicional_citrep", 0)) if include_citrep else 0
    return int(base + add_opp + add_citrep)


def commission_bancada(row) -> str:
    """Agrupación específica para el módulo de comisiones.

    - Las curules por oposición se imputan al partido real registrado, no a un bloque separado.
    - CITREP se conserva como bloque especial y puede incluirse/excluirse desde el módulo.
    """
    circ = _norm_key(row.get("circunscripcion", ""))
    if circ == "OPOSICION":
        partido = clean_value(row.get("partido_corto", ""), "") or clean_value(row.get("partido", ""), "")
        return partido or "PACTO HISTÓRICO"
    if circ == "CITREP":
        return "CITREP"
    return clean_value(row.get("bloque_visual", ""), "") or clean_value(row.get("partido_corto", ""), "") or clean_value(row.get("partido", ""), "No registra")


def commission_universe(data: pd.DataFrame, corporation: str, restriction: str = "", include_citrep: bool = True) -> pd.DataFrame:
    d = data[data["corporacion"] == corporation].copy()
    circ_keys = d["circunscripcion"].map(_norm_key)
    restricted_citrep = bool(restriction and _norm_key(restriction) == "CITREP")

    if restricted_citrep:
        d = d[circ_keys == "CITREP"].copy()
    elif not include_citrep:
        d = d[circ_keys != "CITREP"].copy()

    if not d.empty:
        d["bancada_comision"] = d.apply(commission_bancada, axis=1)
    return d


def allocate_commission(data: pd.DataFrame, corporation: str, seats: int, restriction: str = "", include_citrep: bool = True) -> pd.DataFrame:
    """Proyección por cuociente electoral: cuota = curules corporación / cupos comisión.

    Se asigna parte entera de la división curules_partido / cuota. Los cupos restantes
    se asignan por mayores residuos solo cuando no existe empate decisivo. Si varias
    bancadas tienen el mismo residuo y compiten por menos cupos que competidores, el
    cupo queda marcado como pendiente por desempate y no se adjudica automáticamente.
    """
    columns = [
        "bancada", "curules_corporacion", "cuociente", "cuota_decimal", "parte_entera",
        "residuo", "curules_residuo", "curules_comision", "participacion",
        "empate_residuo", "cupos_empate_disputados", "grupo_empate", "competidores_empate"
    ]
    d = commission_universe(data, corporation, restriction, include_citrep=include_citrep)
    if d.empty or seats <= 0:
        return pd.DataFrame(columns=columns)

    counts = d.groupby("bancada_comision", as_index=False).size().rename(columns={"size": "curules_corporacion"})
    counts = counts.sort_values(["curules_corporacion", "bancada_comision"], ascending=[False, True]).reset_index(drop=True)
    total_curules = int(counts["curules_corporacion"].sum())
    quotient = total_curules / seats if seats else np.nan
    counts["cuociente"] = quotient
    counts["cuota_decimal"] = counts["curules_corporacion"] / quotient if quotient else 0
    counts["parte_entera"] = np.floor(counts["cuota_decimal"]).astype(int)
    counts["residuo"] = counts["cuota_decimal"] - counts["parte_entera"]
    assigned = int(counts["parte_entera"].sum())
    remaining = max(seats - assigned, 0)
    counts["curules_residuo"] = 0
    counts["empate_residuo"] = False
    counts["cupos_empate_disputados"] = 0
    counts["grupo_empate"] = ""
    counts["competidores_empate"] = ""

    if remaining > 0 and not counts.empty:
        ranked = counts.sort_values(["residuo", "curules_corporacion", "bancada_comision"], ascending=[False, False, True]).copy()
        ranked["residuo_key"] = ranked["residuo"].round(12)
        seats_left = remaining
        tie_counter = 1
        for residue_key, grp in ranked.groupby("residuo_key", sort=False):
            if seats_left <= 0:
                break
            grp_idx = grp.index.tolist()
            n_competitors = len(grp_idx)
            if n_competitors <= seats_left:
                counts.loc[grp_idx, "curules_residuo"] = 1
                seats_left -= n_competitors
            else:
                # Empate decisivo: no se adjudican automáticamente los cupos de este tramo.
                # Quedan pendientes los cupos disponibles y compiten todas las bancadas con el mismo residuo.
                competitors = counts.loc[grp_idx, "bancada_comision"].astype(str).tolist()
                tie_id = f"Empate {tie_counter}"
                counts.loc[grp_idx, "empate_residuo"] = True
                counts.loc[grp_idx, "cupos_empate_disputados"] = int(seats_left)
                counts.loc[grp_idx, "grupo_empate"] = tie_id
                counts.loc[grp_idx, "competidores_empate"] = "; ".join(competitors)
                break

    counts["curules_comision"] = counts["parte_entera"] + counts["curules_residuo"]
    counts["participacion"] = counts["curules_comision"] / seats * 100 if seats else 0
    counts = counts.rename(columns={"bancada_comision": "bancada"})
    counts = counts.sort_values(["curules_comision", "curules_corporacion", "residuo"], ascending=[False, False, False]).reset_index(drop=True)
    return counts[columns]


def commission_allocation_fig(alloc: pd.DataFrame, commission_name: str) -> go.Figure:
    d = alloc[alloc["curules_comision"] > 0].copy()
    d = d.sort_values("curules_comision", ascending=True)
    colors = [party_color(x) for x in d["bancada"]]
    fig = go.Figure(go.Bar(
        x=d["curules_comision"], y=[abbreviate(x, 28) for x in d["bancada"]], orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(255,255,255,.72)", width=1)),
        text=[fmt_int(x) for x in d["curules_comision"]], textposition="outside", cliponaxis=False,
        customdata=np.stack([d["bancada"], d["curules_corporacion"], d["parte_entera"], d["residuo"], d["curules_residuo"]], axis=-1) if not d.empty else None,
        hovertemplate="<b>%{customdata[0]}</b><br>Curules corporación: %{customdata[1]}<br>Parte entera: %{customdata[2]}<br>Residuo: %{customdata[3]:.3f}<br>Curul por residuo: %{customdata[4]}<br>Total comisión: %{x}<extra></extra>",
    ))
    mx = float(d["curules_comision"].max()) if not d.empty else 1
    fig.update_layout(title=dict(text=f"Asignación proyectada · {commission_name}", x=.02), height=max(420, 31*len(d)+115), margin=dict(l=185, r=55, t=65, b=45), showlegend=False)
    fig.update_xaxes(range=[0, mx*1.25], gridcolor="rgba(255,255,255,.10)", color="#cbd5e1", title="Curules en comisión")
    fig.update_yaxes(color="#e5e7eb", automargin=True)
    return fig


def commission_overview_fig(data: pd.DataFrame, commissions: pd.DataFrame, corporation: str, tipo: str = "Todas", include_citrep: bool = True) -> go.Figure:
    cm = commissions[commissions["corporacion"] == corporation].copy()
    if tipo != "Todas":
        cm = cm[cm["tipo_comision"] == tipo].copy()
    rows = []
    for _, r in cm.iterrows():
        if not include_citrep and _norm_key(r.get("restriccion", "")) == "CITREP":
            continue
        eff_seats = effective_commission_seats(r, include_citrep=include_citrep)
        alloc = allocate_commission(data, r["corporacion"], eff_seats, r.get("restriccion", ""), include_citrep=include_citrep)
        if alloc.empty:
            continue
        for a in alloc.itertuples(index=False):
            if int(a.curules_comision) > 0:
                rows.append({"comision": abbreviate(r["nombre_comision"], 30), "bancada": a.bancada, "curules": int(a.curules_comision)})
    dd = pd.DataFrame(rows)
    if dd.empty:
        return go.Figure()
    # top bancadas por cupos acumulados en las comisiones de esa vista
    top_b = dd.groupby("bancada")["curules"].sum().sort_values(ascending=False).head(10).index.tolist()
    dd = dd[dd["bancada"].isin(top_b)]
    pivot = dd.pivot_table(index="comision", columns="bancada", values="curules", aggfunc="sum", fill_value=0)
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]
    fig = go.Figure()
    y_labels = [abbreviate(x, 44) for x in pivot.index.tolist()]
    for b in top_b:
        vals = pivot[b].tolist() if b in pivot.columns else [0]*len(pivot)
        fig.add_trace(go.Bar(
            y=y_labels,
            x=vals,
            orientation="h",
            name=abbreviate(b, 18),
            marker=dict(color=party_color(b), line=dict(color="rgba(255,255,255,.55)", width=.6)),
            hovertemplate="<b>%{y}</b><br>" + h(abbreviate(b, 26)) + ": %{x}<extra></extra>",
        ))
    fig.update_layout(
        barmode="stack",
        title=dict(text=f"Mapa de asignación por comisión · {corporation}", x=.02),
        height=max(560, 34*len(pivot)+160),
        margin=dict(l=260, r=35, t=65, b=120),
        legend=dict(orientation="h", y=-.18),
    )
    fig.update_xaxes(title="Curules proyectadas", gridcolor="rgba(255,255,255,.10)", color="#cbd5e1")
    fig.update_yaxes(color="#e5e7eb", automargin=True, autorange="reversed")
    return fig


def commission_tie_display(alloc: pd.DataFrame) -> pd.DataFrame:
    if alloc.empty or "empate_residuo" not in alloc.columns:
        return pd.DataFrame(columns=["Empate", "Curules pendientes", "Residuo empatado", "Bancadas que compiten", "Curules corporación"] )
    t = alloc[alloc["empate_residuo"].fillna(False)].copy()
    if t.empty:
        return pd.DataFrame(columns=["Empate", "Curules pendientes", "Residuo empatado", "Bancadas que compiten", "Curules corporación"] )
    rows = []
    for tie_id, g in t.groupby("grupo_empate", sort=False):
        g = g.sort_values(["curules_corporacion", "bancada"], ascending=[False, True])
        rows.append({
            "Empate": tie_id or "Empate por residuo",
            "Curules pendientes": int(g["cupos_empate_disputados"].max()),
            "Residuo empatado": f"{float(g['residuo'].iloc[0]):.3f}".replace(".", ","),
            "Bancadas que compiten": " · ".join(g["bancada"].astype(str).tolist()),
            "Curules corporación": " · ".join([f"{b}: {int(c)}" for b, c in zip(g["bancada"], g["curules_corporacion"])]),
        })
    return pd.DataFrame(rows)


def commission_tie_cards(alloc: pd.DataFrame) -> str:
    """Renderiza empates decisivos como HTML compacto.
    Importante: se evita HTML indentado en múltiples líneas porque Streamlit/Markdown
    puede interpretarlo como bloque de código y mostrar etiquetas visibles.
    """
    if alloc.empty or "empate_residuo" not in alloc.columns:
        return ""
    t = alloc[alloc["empate_residuo"].fillna(False)].copy()
    if t.empty:
        return ""
    panels = []
    for tie_id, g in t.groupby("grupo_empate", sort=False):
        g = g.sort_values(["curules_corporacion", "bancada"], ascending=[False, True])
        pending = int(g["cupos_empate_disputados"].max())
        residue = f"{float(g['residuo'].iloc[0]):.3f}".replace(".", ",")
        slots = "".join("<div class='tie-slot'>?</div>" for _ in range(max(pending, 1)))
        cards = []
        for _, row in g.iterrows():
            bancada = clean_value(row.get("bancada"), "No registra")
            color = party_color(bancada)
            cards.append(
                "<div class='tie-card'>"
                f"<div class='tie-bancada'><span class='tie-dot' style='background:{color};'></span><span>{h(bancada)}</span></div>"
                "<div class='tie-meta'>"
                f"<div class='tie-mini'><div class='tie-mini-lab'>Curules corp.</div><div class='tie-mini-val'>{fmt_int(row.get('curules_corporacion', 0))}</div></div>"
                f"<div class='tie-mini'><div class='tie-mini-lab'>Residuo</div><div class='tie-mini-val'>{residue}</div></div>"
                "</div>"
                "</div>"
            )
        panels.append(
            "<div class='tie-panel'>"
            "<div class='tie-head'>"
            "<div>"
            f"<div class='tie-title'>{h(tie_id or 'Empate por residuo')}</div>"
            f"<div class='tie-sub'>Hay <b>{fmt_int(pending)}</b> curul(es) pendiente(s) por un empate en residuo. El sistema no adjudica automáticamente estos cupos para evitar una asignación arbitraria.</div>"
            "</div>"
            f"<div class='tie-pill'>Residuo empatado · {residue}</div>"
            "</div>"
            f"<div class='tie-slot-row'>{slots}</div>"
            f"<div class='tie-grid'>{''.join(cards)}</div>"
            "</div>"
        )
    return "".join(panels)


def commission_table_display(alloc: pd.DataFrame) -> pd.DataFrame:
    table = alloc.copy()
    if table.empty:
        return table
    table = table.rename(columns={
        "bancada": "Bancada / grupo",
        "curules_corporacion": "Curules corporación",
        "cuociente": "Cuociente",
        "cuota_decimal": "Curules / cuociente",
        "parte_entera": "Asignación por parte entera",
        "residuo": "Residuo",
        "curules_residuo": "Curules por residuo",
        "curules_comision": "Total comisión",
        "participacion": "% comisión",
    })
    for c in ["Cuociente", "Curules / cuociente", "Residuo"]:
        table[c] = table[c].map(lambda x: f"{x:.3f}".replace(".", ",") if pd.notna(x) else "—")
    table["% comisión"] = table["% comisión"].map(lambda x: f"{x:.1f}%".replace(".", ",") if pd.notna(x) else "—")
    if "empate_residuo" in table.columns:
        table["Estado residuo"] = table["empate_residuo"].map(lambda x: "Pendiente por empate" if bool(x) else "Asignado / no compite")
        return table[["Bancada / grupo", "Curules corporación", "Cuociente", "Curules / cuociente", "Asignación por parte entera", "Residuo", "Curules por residuo", "Total comisión", "% comisión", "Estado residuo"]]
    return table[["Bancada / grupo", "Curules corporación", "Cuociente", "Curules / cuociente", "Asignación por parte entera", "Residuo", "Curules por residuo", "Total comisión", "% comisión"]]

# =============================================================================
# FILTROS GLOBALES
# =============================================================================
with st.sidebar:
    st.markdown("# 🏛️ Congreso 2026–2030")
    st.markdown("<p style='font-size:.86rem;color:#cbd5e1;line-height:1.35;'>Tablero político-electoral. Use los filtros en orden: corporación → circunscripción → territorio → sector.</p>", unsafe_allow_html=True)
    st.markdown("---")
    module_options = [
        "1. Congreso en pleno",
        "2. Bancadas y poder político",
        "3. Votación de lista",
        "4. Apoyos presidenciales",
        "5. Territorio y especiales",
        "6. Fichas técnicas",
        "7. Integración de comisiones",
        "8. Directorio y método",
    ]
    modulo = st.radio("Módulo", module_options, index=0)
    st.markdown("---")
    ambito = st.selectbox("1) Corporación", ["Congreso en pleno", "Senado", "Cámara"], index=0)
    df_scope = df0.copy() if ambito == "Congreso en pleno" else df0[df0["corporacion"] == ambito].copy()
    circ_opts = ["Todas"] + options_from(df_scope, "circunscripcion")
    circ = st.selectbox("2) Circunscripción", circ_opts, index=0)
    df_scope = df_scope if circ == "Todas" else df_scope[df_scope["circunscripcion"] == circ].copy()
    terr_opts = ["Todos"] + options_from(df_scope, "territorio_resumen")
    territorio = st.selectbox("3) Territorio", terr_opts, index=0)
    sector_opts = ["Todos"] + [x for x in SECTOR_ORDER if x in df_scope["sector"].unique()]
    sector_sel = st.selectbox("4) Sector político", sector_opts, index=0)
    st.markdown("<div class='small' style='color:#cbd5e1;margin-top:.6rem;'>No se suma votación Senado+Cámara. En listas cerradas no se imputa voto individual.</div>", unsafe_allow_html=True)

filtered = df_scope.copy()
if territorio != "Todos":
    filtered = filtered[filtered["territorio_resumen"] == territorio]
if sector_sel != "Todos":
    filtered = filtered[filtered["sector"] == sector_sel]

st.markdown(
    f"""
<div class='hero'>
  <div class='micro'>
    <span class='badge'>Vista: {h(ambito)}</span>
    <span class='badge'>Circunscripción: {h(circ)}</span>
    <span class='badge'>Territorio: {h(territorio)}</span>
    <span class='badge'>Sector: {h(sector_sel)}</span>
  </div>
  <h1>Dashboard Congreso 2026–2030</h1>
  <p>Lectura integrada del Congreso electo: hemiciclo por bancadas, balance sectorial, votación de listas por corporación, apoyos presidenciales, circunscripciones especiales y fichas individuales.</p>
</div>
""",
    unsafe_allow_html=True,
)

kpi_grid(kpis_for_module(filtered, ambito, modulo))
if filtered.empty:
    st.warning("No hay registros para la combinación seleccionada. Ajuste los filtros.")
    st.stop()

# =============================================================================
# MÓDULOS
# =============================================================================
if modulo.startswith("1"):
    guide("Cómo leer este módulo", [
        "El hemiciclo es la vista principal: cada punto es una curul y los puntos quedan agrupados por bancada, no dispersos.",
        "Use el selector para cambiar el color: bancada, sector, corporación o apoyo presidencial.",
        "La leyenda aparece separada del gráfico para evitar sobreposición y mejorar lectura visual."
    ])
    c1, c2 = st.columns([1.15, .85])
    with c1:
        color_label = st.selectbox("Colorear hemiciclo por", ["Bancada / grupo electoral", "Sector político", "Corporación", "Apoyo presidencial 1ª vuelta", "Apoyo presidencial 2ª vuelta"], index=0)
    with c2:
        order_mode = st.selectbox("Orden visual de bancadas", ["Tamaño de bancada", "Sector político"], index=0)
    color_by = {
        "Bancada / grupo electoral": "bloque_visual",
        "Sector político": "sector",
        "Corporación": "corporacion",
        "Apoyo presidencial 1ª vuelta": "apoyo_presidencia_primera",
        "Apoyo presidencial 2ª vuelta": "apoyo_presidencia_segunda",
    }[color_label]
    safe_plot(hemicycle_fig(filtered, color_by=color_by, order_mode=order_mode, title=f"Hemiciclo · {color_label}"), height=560)
    if color_by == "bloque_visual":
        legend_grid(party_summary(filtered), "bloque_visual", color_mode="party", value_col="curules", max_items=28)
    elif color_by == "sector":
        d = filtered["sector"].value_counts().reset_index(); d.columns = ["sector", "curules"]
        legend_grid(d, "sector", color_mode="sector", value_col="curules")
    elif color_by == "corporacion":
        d = filtered["corporacion"].value_counts().reset_index(); d.columns = ["corporacion", "curules"]
        legend_grid(d, "corporacion", color_mode="corporacion", value_col="curules")
    else:
        d = filtered[color_by].value_counts().reset_index(); d.columns = [color_by, "curules"]
        legend_grid(d, color_by, color_mode="apoyo", value_col="curules")
    a, b = st.columns([1.05, .95])
    with a:
        safe_plot(barh_fig(party_summary(filtered), "bloque_visual", "curules", "Bancadas / grupos con más curules", max_rows=14), height=470)
    with b:
        safe_plot(sector_balance_fig(filtered), height=235)
        safe_plot(split_corp_fig(filtered, "Composición Senado/Cámara · principales bancadas", max_rows=9), height=400)

elif modulo.startswith("2"):
    guide("Qué mirar en este módulo", [
        "La lectura de poder no depende solo del número de partidos, sino de concentración, tamaño de bancadas y capacidad de formar mayorías.",
        "CITREP, Afro, Indígenas y Oposición se leen como grupos especiales para evitar ruido visual de organizaciones de una curul.",
        "Los colores corresponden a una paleta estable por partido/grupo, no a colores aleatorios."
    ])
    ps = party_summary(filtered)
    c1, c2 = st.columns([1.05, .95])
    with c1:
        safe_plot(barh_fig(ps, "bloque_visual", "curules", "Ranking de bancadas y grupos especiales", max_rows=18), height=610)
    with c2:
        safe_plot(sector_balance_fig(filtered, "Bloques de gobernabilidad por sector"), height=250)
        safe_plot(split_corp_fig(filtered, "Senado/Cámara dentro de cada bancada", max_rows=12), height=440)
    st.markdown("<div class='section-title'>Leyenda institucional de bancadas</div>", unsafe_allow_html=True)
    legend_grid(ps, "bloque_visual", color_mode="party", value_col="curules", max_items=28)

elif modulo.startswith("3"):
    guide("Regla de votación", [
        "La votación de Senado y Cámara no se suma: son universos electorales distintos.",
        "La votación del partido/lista se muestra como atributo de lista. En listas cerradas no se crea un voto individual ficticio.",
        "Use votos por curul como indicador de eficiencia electoral, no como suma nacional del Congreso."
    ])
    a, b = st.columns(2)
    with a:
        safe_plot(votes_fig(filtered, "Senado", top=12), height=520)
    with b:
        safe_plot(votes_fig(filtered, "Cámara", top=12), height=520)
    a, b = st.columns(2)
    with a:
        safe_plot(votes_per_seat_fig(filtered, "Senado", top=12), height=500)
    with b:
        safe_plot(votes_per_seat_fig(filtered, "Cámara", top=12), height=500)

elif modulo.startswith("4"):
    guide("Cómo leer los apoyos presidenciales", [
        "La primera vuelta y la segunda vuelta se leen por separado para evitar confundir apoyos iniciales con realineamientos posteriores.",
        "El flujo 1ª → 2ª vuelta muestra hacia dónde se reacomodaron las curules según la información del Excel.",
        "El hemiciclo permite visualizar si los apoyos están concentrados por bancada o distribuidos en varias fuerzas."
    ])
    a, b = st.columns(2)
    with a:
        safe_plot(presidential_bar(filtered, "apoyo_presidencia_primera", "Primera vuelta · curules por apoyo"), height=450)
    with b:
        safe_plot(presidential_bar(filtered, "apoyo_presidencia_segunda", "Segunda vuelta · curules por apoyo"), height=450)
    safe_plot(presidential_flow_fig(filtered), height=520)
    with st.expander("Ver tabla de flujos 1ª → 2ª vuelta", expanded=False):
        safe_df(presidential_flow_table(filtered), height=260)
    st.markdown("<div class='section-title'>Hemiciclo coloreado por segunda vuelta</div>", unsafe_allow_html=True)
    safe_plot(hemicycle_fig(filtered, color_by="apoyo_presidencia_segunda", title="Hemiciclo · apoyo presidencial en segunda vuelta"), height=540)

elif modulo.startswith("5"):
    guide("Qué aporta el módulo territorial", [
        "Diferencia curules territoriales, nacionales y especiales, para no mezclar lógicas electorales distintas.",
        "La columna de cada departamento integra Cámara y Senado para una lectura territorial compacta y comparable.",
        "CITREP, Afro, Indígenas y Oposición aparecen como categorías institucionales de lectura."
    ])
    a, b = st.columns([1.08, .92])
    with a:
        safe_plot(territory_stacked_col_fig(filtered), height=560)
    with b:
        safe_plot(circ_special_fig(filtered), height=430)
        sp = filtered[filtered["circunscripcion"].isin(["CITREP", "AFRODESCENDIENTES", "INDÍGENAS", "OPOSICIÓN"])]
        if not sp.empty:
            st.markdown("<div class='card'><h3>Curules especiales bajo filtros</h3><div class='note'>Tabla resumida para revisar CITREP, Afro, Indígenas y Oposición sin fragmentar el hemiciclo por organizaciones menores.</div></div>", unsafe_allow_html=True)
            table = sp[["nombre_titulo", "corporacion", "circunscripcion", "territorio_lectura", "partido", "sector", "apoyo_presidencia_primera", "apoyo_presidencia_segunda"]].copy()
            table.columns = ["Congresista", "Corporación", "Circunscripción", "Territorio", "Organización real", "Sector", "1ª vuelta", "2ª vuelta"]
            safe_df(table, height=320)

elif modulo.startswith("7"):
    guide("Integración de comisiones por cuociente", [
        "Seleccione corporación, tipo de comisión y comisión específica para proyectar la distribución de cupos por bancada o grupo visual.",
        "El cálculo usa las curules de la corporación correspondiente; Senado y Cámara se calculan por separado.",
        "La proyección aplica cuociente electoral: parte entera de la cuota y asignación de cupos restantes por mayores residuos."
    ])
    if comisiones_df.empty:
        st.warning("No se encontró el archivo de integración de comisiones.")
    else:
        c1, c2, c3, c4 = st.columns([.85, .95, 1.55, .9])
        with c1:
            corp_comm = st.selectbox("Corporación para comisión", ["Cámara", "Senado"], index=0)
        cm_scope = comisiones_df[comisiones_df["corporacion"] == corp_comm].copy()
        with c2:
            tipo_opts = ["Todas"] + sorted(cm_scope["tipo_comision"].dropna().unique().tolist())
            tipo_comm = st.selectbox("Tipo de comisión", tipo_opts, index=0)
        cm_type = cm_scope if tipo_comm == "Todas" else cm_scope[cm_scope["tipo_comision"] == tipo_comm].copy()
        with c3:
            selected_comm = st.selectbox("Comisión", cm_type["nombre_comision"].tolist(), index=0)
        row = cm_type[cm_type["nombre_comision"] == selected_comm].iloc[0]
        restriction = clean_value(row.get("restriccion", ""), "")
        restricted_citrep = bool(restriction and _norm_key(restriction) == "CITREP")
        with c4:
            if restricted_citrep:
                include_citrep = st.checkbox("Incluir CITREP", value=True, disabled=True, help="Esta comisión está restringida a CITREP; por eso el universo se mantiene en esas curules.")
            else:
                include_citrep = st.checkbox("Incluir CITREP", value=True, help="Active o desactive las curules CITREP dentro del universo usado para calcular el cuociente y los cupos adicionales CITREP cuando estén registrados.")
        seats = effective_commission_seats(row, include_citrep=include_citrep or restricted_citrep)
        universe = commission_universe(df0, corp_comm, restriction, include_citrep=include_citrep)
        alloc = allocate_commission(df0, corp_comm, seats, restriction, include_citrep=include_citrep)
        parties_with_seats = int((alloc["curules_comision"] > 0).sum()) if not alloc.empty else 0
        quotient = float(alloc["cuociente"].dropna().iloc[0]) if not alloc.empty and alloc["cuociente"].notna().any() else np.nan
        residue_seats = int(alloc["curules_residuo"].sum()) if not alloc.empty else 0
        tie_pending = int(alloc["cupos_empate_disputados"].max()) if not alloc.empty and "cupos_empate_disputados" in alloc.columns else 0
        khtml = "".join([
            f"<div class='group-kpi'><div class='group-kpi-label'>Cupos comisión</div><div class='group-kpi-value'>{fmt_int(seats)}</div><div class='group-kpi-help'>{h(corp_comm)} · {h(clean_value(row['tipo_comision']))}</div></div>",
            f"<div class='group-kpi'><div class='group-kpi-label'>Universo curules</div><div class='group-kpi-value'>{fmt_int(len(universe))}</div><div class='group-kpi-help'>{'CITREP incluido' if include_citrep or restricted_citrep else 'CITREP excluido'}</div></div>",
            f"<div class='group-kpi'><div class='group-kpi-label'>Cuociente</div><div class='group-kpi-value'>{str(round(quotient,3)).replace('.', ',') if pd.notna(quotient) else '—'}</div><div class='group-kpi-help'>Curules corporación / cupos</div></div>",
            f"<div class='group-kpi'><div class='group-kpi-label'>Bancadas con cupo</div><div class='group-kpi-value'>{fmt_int(parties_with_seats)}</div><div class='group-kpi-help'>Grupos que obtienen representación</div></div>",
            f"<div class='group-kpi'><div class='group-kpi-label'>Cupos asignados por residuo</div><div class='group-kpi-value'>{fmt_int(residue_seats)}</div><div class='group-kpi-help'>Sin empate decisivo</div></div>",
            f"<div class='group-kpi'><div class='group-kpi-label'>Pendientes por empate</div><div class='group-kpi-value'>{fmt_int(tie_pending)}</div><div class='group-kpi-help'>Requieren definición política/reglamentaria</div></div>",
        ])
        st.markdown(f"<div class='group-kpis'>{khtml}</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
<div class='method-card'>
<b>Proceso aplicado para distribuir los cupos.</b><br>
1) Se toma el universo de curules de <b>{h(corp_comm)}</b>{' restringido a CITREP' if restriction else ''}, con CITREP <b>{'incluido' if include_citrep or restricted_citrep else 'excluido'}</b> en el análisis general.<br>
2) Los cupos efectivos de la comisión corresponden al cupo base más las adiciones registradas en la base normativa, cuando aplican: CITREP se suma si el botón está activo y oposición se computa como cupo adicional imputado al partido registrado.<br>
3) Para este módulo, las curules de <b>oposición</b> se imputan al partido registrado en la base; en este caso, <b>Pacto Histórico</b>, y no a un bloque separado de oposición.<br>
4) Se calcula el <b>cuociente</b>: total de curules de la corporación dividido por los <b>{fmt_int(seats)}</b> cupos efectivos de la comisión.<br>
5) Cada bancada recibe la parte entera de <i>curules de la bancada / cuociente</i>.<br>
6) Los cupos no asignados por parte entera se entregan a los <b>mayores residuos</b>. Si hay empate decisivo en el residuo y los cupos disponibles son menores que las bancadas empatadas, el sistema <b>no adjudica automáticamente</b> esos cupos y los reporta como pendientes.
<br><span class='small'>Lectura: esta es una proyección matemática de integración por bancada/grupo visual; la designación nominal depende de postulaciones, acuerdos internos y reglas aplicables en cada Cámara.</span>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='section-title'>Asignación proyectada de la comisión seleccionada</div>", unsafe_allow_html=True)
        safe_plot(commission_allocation_fig(alloc, selected_comm), height=560)
        tie_table = commission_tie_display(alloc)
        if not tie_table.empty:
            st.markdown("<div class='section-title'>Curules pendientes por empate en residuo</div>", unsafe_allow_html=True)
            st.markdown(commission_tie_cards(alloc), unsafe_allow_html=True)
            with st.expander("Ver detalle técnico de empates", expanded=False):
                safe_df(tie_table, height=180)
        else:
            st.markdown("<div class='tie-empty'><b>Sin empates decisivos.</b><br>En esta comisión los cupos por residuo pueden asignarse sin conflicto matemático entre bancadas empatadas.</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Detalle de asignación por cuociente</div>", unsafe_allow_html=True)
        detalle_alloc = commission_table_display(alloc)
        safe_df(detalle_alloc, height=430)
        csv_alloc = detalle_alloc.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("Descargar asignación de la comisión CSV", data=csv_alloc, file_name="asignacion_comision_por_cuociente.csv", mime="text/csv")
        st.markdown("<div class='section-title'>Resumen general de comisiones de esta vista</div>", unsafe_allow_html=True)
        st.markdown("<div class='note'>Lectura consolidada posterior al detalle: compara la distribución proyectada de las comisiones de la corporación y tipo seleccionados.</div>", unsafe_allow_html=True)
        safe_plot(commission_overview_fig(df0, comisiones_df, corp_comm, tipo_comm, include_citrep=include_citrep), height=700)

elif modulo.startswith("6"):
    guide("Flujo recomendado de consulta", [
        "Primero seleccione bancada o grupo especial. Después se habilita el listado de congresistas de ese grupo.",
        "La ficha diferencia partido real, grupo visual, circunscripción, territorio, sector, apoyos presidenciales y votación de lista/grupo.",
        "Cuando no existe voto individual, la ficha lo marca como lista cerrada; muestra la votación total de la lista/grupo sin convertirla en voto personal del congresista."
    ])
    ps = party_summary(filtered)
    groups = ps["bloque_visual"].tolist()
    selected_group = st.selectbox("1) Seleccione bancada / grupo electoral", groups, format_func=lambda x: f"{initials(x)} · {x}")
    group_df = filtered[filtered["bloque_visual"] == selected_group].copy()
    color = party_color(selected_group)
    st.markdown(
        f"""
<div class='party-head'>
  <div class='logo-badge' style='background:{color};'>{h(initials(selected_group))}</div>
  <div>
    <div class='party-title'>{h(selected_group)}</div>
    <div class='party-sub'>Reporte previo del grupo seleccionado: composición por corporación, sector político y apoyos presidenciales registrados en la base.</div>
  </div>
</div>
{selected_party_report(group_df)}
""",
        unsafe_allow_html=True,
    )
    names = group_df.sort_values(["corporacion", "territorio_lectura", "nombre_titulo"])["nombre_titulo"].tolist()
    selected_name = st.selectbox("2) Seleccione congresista", names)
    person = group_df[group_df["nombre_titulo"] == selected_name].iloc[0]
    img_uri = image_data_uri(person.get("foto_path", ""))
    vote_ind = person["votos_esc"] if pd.notna(person["votos_esc"]) else person["votos_pre"]
    profile_html = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
  *{{box-sizing:border-box}} body{{margin:0;background:#0b1220;color:#f8fafc;font-family:Arial, Helvetica, sans-serif;}}
  .card{{display:grid;grid-template-columns:310px 1fr;gap:22px;background:linear-gradient(180deg,#111a2b,#0d1526);border:1px solid rgba(255,255,255,.13);border-radius:28px;padding:18px;box-shadow:0 22px 62px rgba(0,0,0,.32);}}
  .photo{{width:100%;aspect-ratio:4/4.2;object-fit:cover;border-radius:22px;background:#1f2937;border:1px solid rgba(255,255,255,.16);}}
  .name{{font-size:27px;font-weight:900;letter-spacing:-.03em;line-height:1.05;margin:14px 0 6px;color:#fff;}}
  .sub{{font-size:15px;color:#a7b1c2;font-weight:800;margin-bottom:10px;}}
  .pill{{display:inline-block;padding:6px 10px;border-radius:999px;background:#172033;color:#dbeafe;font-size:12px;font-weight:900;margin:3px;border:1px solid rgba(255,255,255,.12);}}
  .red{{background:rgba(227,6,19,.18);color:#fecaca;border-color:rgba(248,113,113,.38)}}
  .blue{{background:rgba(59,130,246,.16);color:#bfdbfe;border-color:rgba(96,165,250,.35)}}
  .green{{background:rgba(34,197,94,.16);color:#bbf7d0;border-color:rgba(74,222,128,.35)}}
  .amber{{background:rgba(245,158,11,.16);color:#fde68a;border-color:rgba(251,191,36,.35)}}
  .title{{font-size:24px;font-weight:900;letter-spacing:-.02em;margin:2px 0 12px;color:#fff;}}
  .metrics{{display:grid;grid-template-columns:repeat(4,minmax(115px,1fr));gap:10px;margin:12px 0 14px;}}
  .metric{{background:#0b1220;border:1px solid rgba(255,255,255,.11);border-radius:16px;padding:12px;min-height:84px;}}
  .lab{{font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:#93a4bb;font-weight:900;margin-bottom:8px;}}
  .val{{font-size:19px;line-height:1.08;font-weight:900;color:#fff;overflow-wrap:anywhere;}}
  .section{{border-top:1px solid rgba(255,255,255,.10);padding-top:12px;margin-top:12px;}}
  .section h4{{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#f8fafc;margin:0 0 6px;}}
  .section p{{font-size:15px;line-height:1.48;color:#cbd5e1;margin:0;}}
  @media(max-width:850px){{.card{{grid-template-columns:1fr}}.photo{{max-width:300px}}.metrics{{grid-template-columns:repeat(2,minmax(115px,1fr));}}}}
</style>
</head>
<body>
<div class="card">
  <div>
    <img class="photo" src="{img_uri}" />
    <div class="name">{h(person['nombre_titulo'])}</div>
    <div class="sub">{h(person['partido_corto'])}</div>
    <span class="pill red">{h(person['corporacion'])}</span>
    <span class="pill blue">{h(person['circunscripcion'])}</span>
    <span class="pill">{h(person['territorio_lectura'])}</span>
    <span class="pill green">{h(person['sector'])}</span>
    <span class="pill amber">{h(person['tipo_votacion'])}</span>
  </div>
  <div>
    <div class="title">Ficha técnica individual</div>
    <div class="metrics">
      <div class="metric"><div class="lab">Voto individual</div><div class="val">{fmt_int(vote_ind)}</div></div>
      <div class="metric"><div class="lab">Voto lista / grupo</div><div class="val">{fmt_int(person['votos_lista_ficha'])}</div></div>
      <div class="metric"><div class="lab">Corporación</div><div class="val">{h(person['corporacion'])}</div></div>
      <div class="metric"><div class="lab">Grupo visual</div><div class="val">{h(person['bloque_visual'])}</div></div>
    </div>
    <span class="pill blue">Primera vuelta: {h(person['apoyo_presidencia_primera'])}</span>
    <span class="pill red">Segunda vuelta: {h(person['apoyo_presidencia_segunda'])}</span>
    <span class="pill">Asesor: {h(clean_value(person['asesor']))}</span>
    <div class="section"><h4>Perfil / trayectoria</h4><p>{h(clean_value(person['perfil']))}</p></div>
    <div class="section"><h4>Participación en política</h4><p>{h(clean_value(person['participacion_politica']))}</p></div>
    <div class="section"><h4>Casa política</h4><p>{h(clean_value(person['casa_politica']))}</p></div>
    <div class="section"><h4>Familia / apoyos</h4><p>{h(clean_value(person['familia_apoyos']))}</p></div>
    <div class="section"><h4>Fórmula / articulación</h4><p>{h(clean_value(person['formula']))}</p></div>
    <div class="section"><h4>Observación adicional</h4><p>{h(clean_value(person['observacion_adicional']))}</p></div>
  </div>
</div>
</body>
</html>
"""
    components.html(profile_html, height=980, scrolling=True)
    same_list = df0[df0["grupo_lista_id"] == person["grupo_lista_id"]].copy()
    if len(same_list) > 1:
        st.markdown("<div class='section-title'>Integrantes de la misma lista / territorio</div>", unsafe_allow_html=True)
        table = same_list[["nombre_titulo", "corporacion", "circunscripcion", "territorio_lectura", "partido_corto", "tipo_votacion", "votos_esc", "votos_lista_ficha"]].copy()
        table.columns = ["Congresista", "Corporación", "Circunscripción", "Territorio", "Partido", "Tipo votación", "Voto individual", "Voto lista / grupo"]
        table["Voto individual"] = table["Voto individual"].map(fmt_int)
        table["Voto lista / grupo"] = table["Voto lista / grupo"].map(fmt_int)
        safe_df(table, height=330)

else:
    guide("Criterio metodológico", [
        "El directorio permite descargar los registros bajo filtros actuales.",
        "El tablero separa votación de Senado y Cámara; no hace una suma nacional impropia de votos.",
        "Las listas cerradas se reportan como sin voto individual y conservan la votación de lista como atributo del grupo."
    ])
    cols = ["nombre_titulo", "corporacion", "circunscripcion", "territorio_lectura", "bloque_visual", "partido", "sector", "apoyo_presidencia_primera", "apoyo_presidencia_segunda", "tipo_votacion", "votos_esc", "votos_pre", "votos_lista_ficha", "asesor"]
    table = filtered[cols].copy()
    table.columns = ["Congresista", "Corporación", "Circunscripción", "Territorio", "Grupo visual", "Partido / organización real", "Sector", "1ª vuelta", "2ª vuelta", "Tipo votación", "Voto ESC", "Voto PRE", "Voto lista / grupo", "Asesor"]
    display = table.copy()
    for c in ["Voto ESC", "Voto PRE", "Voto lista / grupo"]:
        display[c] = display[c].map(fmt_int)
    safe_df(display, height=520)
    csv = table.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("Descargar directorio filtrado CSV", data=csv, file_name="directorio_congreso_2026_2030_filtrado.csv", mime="text/csv")
    st.markdown("<div class='section-title'>Reglas incorporadas</div>", unsafe_allow_html=True)
    st.markdown(
        """
<div class='method-card'><b>1. Senado y Cámara no se suman en votación.</b><br>El Congreso en pleno se analiza por curules y composición política; los votos se muestran por corporación.</div>
<div class='method-card'><b>2. Lista cerrada no equivale a voto individual.</b><br>Si el archivo no trae voto del candidato, el tablero no le asigna artificialmente la votación de partido.</div>
<div class='method-card'><b>3. CITREP y circunscripciones especiales se consolidan visualmente.</b><br>Se agrupan como categorías institucionales para evitar que el tablero se fragmente por organizaciones de una sola curul.</div>
""",
        unsafe_allow_html=True,
    )
