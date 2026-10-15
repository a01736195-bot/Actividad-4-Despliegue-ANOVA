"""
Actividad 4 (Despliegue ANOVA) — Dashboard interactivo
TC2003B.201 · Socio formador: GAC Motor

Bonus de la consigna: widgets adicionales a la plantilla de clase —
selectores de base/variable/factores, boxplot, violin, barras IC 95%,
heatmap de medias, interaction plot, tablas ANOVA y métricas,
con el tema borgoña GAC.

Ejecutar:  streamlit run app.py
"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.graphics.factorplots import interaction_plot
import matplotlib.pyplot as plt
import seaborn as sns

VINO = "#800020"
PALETA = ["#800020", "#B84A5E", "#D98E9A", "#4A0414", "#E8C4CB", "#A62639", "#5C0A1E", "#F2DDE0"]
sns.set_style("whitegrid")

st.set_page_config(page_title="ANOVA · GAC", page_icon="📊", layout="wide")

st.markdown(
    f"<h1 style='color:{VINO}; margin-bottom:0'>Actividad 4 · Despliegue ANOVA</h1>"
    "<p style='color:#4A0414'>Socio formador <b>GAC Motor</b> — ANOVA de una vía y multifactorial "
    "sobre las bases reales de la agencia</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# Carga y preparación de bases (mismas transformaciones del notebook)
# ---------------------------------------------------------------
@st.cache_data
def cargar_bases():
    bases = {}

    b = pd.read_csv("Bitacora de Piso.csv")
    b["Score_Cierre"] = b["SDC"] + b["Venta"]
    bases["Bitácora de Piso"] = {
        "df": b, "obj": "Score_Cierre", "f1": "Asesor", "f2": "Prueba_Manejo",
        "desc": "197 visitas de piso (abr–jul 2025). Objetivo: score de cierre (SDC + Venta) por visita.",
    }

    l = pd.read_csv("Leads Reales.csv")
    l["Periodo_Analisis"] = np.where(l["Año"] == 2024, "2024", "2025-2026")
    bases["Leads Reales"] = {
        "df": l, "obj": "Conversion", "f1": "Nivel_Efectividad", "f2": "Periodo_Analisis",
        "desc": "28 cortes mensuales de efectividad de leads. Objetivo: conversión (ventas / efectivos).",
    }

    bl = pd.read_csv("base_leads_limpia.csv")
    bl["Score_Temperatura"] = bl["Temperatura"].map(
        {"Lead Interes Bajo": 1, "Lead Interes Medio": 2, "Lead Muy Interesado": 3})
    bl = bl[bl["Producto"].isin(["EMZOOM", "EMKOO"])].copy()
    bases["Base de Leads (plaza)"] = {
        "df": bl, "obj": "Score_Temperatura", "f1": "Producto", "f2": "Estado",
        "desc": "183 leads captados en Plaza Angelópolis (EMZOOM / EMKOO). Objetivo: temperatura del lead (1–3).",
    }

    r = pd.read_csv("base_resumen_limpio.csv")
    r["CAL_Ventas"] = r["% CAL Ventas"]
    r["Semestre"] = np.where(r["Mes"] <= 6, "S1", "S2")
    r["Periodo_Analisis"] = np.where(r["Año"] == 2024, "2024", "2025-2026")
    bases["Resumen Mensual"] = {
        "df": r, "obj": "CAL_Ventas", "f1": "Periodo_Analisis", "f2": "Semestre",
        "desc": "30 meses de resultados vs objetivo. Objetivo: % de cumplimiento del objetivo de ventas.",
    }

    f = pd.read_csv("funnel_mensual.csv")
    etapas = ["Leads_Generados", "Leads_Efectivos", "Cita_Programada", "Cita_Efectiva",
              "Prueba_Manejo", "SDC_Generada", "SDC_Aprobada", "Formalizado"]
    f["Año"] = f["Mes"].str.extract(r"(\d{4})").astype(int)
    long = f.melt(id_vars=["Mes", "Año"], value_vars=etapas,
                  var_name="Etapa", value_name="Registros")
    long["Ano"] = long["Año"].astype(str)
    long["Etapa"] = pd.Categorical(long["Etapa"], categories=etapas, ordered=True)
    bases["Funnel Mensual"] = {
        "df": long, "obj": "Registros", "f1": "Etapa", "f2": "Ano",
        "desc": "18 meses × 8 etapas del embudo comercial. Objetivo: registros por etapa.",
    }
    return bases

BASES = cargar_bases()

# ---------------------------------------------------------------
# Sidebar — widgets de selección
# ---------------------------------------------------------------
st.sidebar.header("⚙️ Configuración")
nombre = st.sidebar.selectbox("Base de datos", list(BASES.keys()))
cfg = BASES[nombre]
df, obj, f1, f2 = cfg["df"], cfg["obj"], cfg["f1"], cfg["f2"]
st.sidebar.caption(cfg["desc"])

alfa = st.sidebar.slider("Nivel de significancia α", 0.01, 0.10, 0.05, 0.01)
vista = st.sidebar.radio("Análisis", ["ANOVA de una vía", "ANOVA multifactorial"])

# ---------------------------------------------------------------
# Encabezado de la base + métricas
# ---------------------------------------------------------------
st.subheader(f"📁 {nombre}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Observaciones", len(df))
c2.metric("Grupos " + f1, df[f1].nunique())
c3.metric("Grupos " + f2, df[f2].nunique())
c4.metric("Media " + obj, f"{df[obj].mean():.2f}")

tab1, tab2, tab3 = st.tabs(["📈 Gráficas", "🧮 ANOVA", "📋 Datos"])

with tab1:
    tipo = st.selectbox("Tipo de gráfica",
                        ["Boxplot", "Barras con IC 95%", "Violin", "Heatmap de medias", "Interaction plot"])
    fig, ax = plt.subplots(figsize=(10, 4.6))
    if tipo == "Boxplot":
        sns.boxplot(data=df, x=f1, y=obj, ax=ax, color=VINO)
    elif tipo == "Barras con IC 95%":
        sns.barplot(data=df, x=f1, y=obj, ax=ax, errorbar=("ci", 95), color=VINO)
    elif tipo == "Violin":
        sns.violinplot(data=df, x=f1, y=obj, ax=ax, color="#B84A5E")
    elif tipo == "Heatmap de medias":
        medias = df.groupby([f1, f2], observed=True)[obj].mean().unstack()
        sns.heatmap(medias, annot=True, fmt=".2f", cmap="Reds", ax=ax)
    else:
        interaction_plot(df[f1], df[f2].astype(str), df[obj], ax=ax,
                         colors=PALETA[:df[f2].nunique()], ms=8)
    ax.set_title(f"{tipo}: {obj} ~ {f1}" + (f" × {f2}" if tipo in ("Heatmap de medias", "Interaction plot") else ""))
    ax.tick_params(axis="x", rotation=30)
    st.pyplot(fig)

with tab2:
    if vista == "ANOVA de una vía":
        grupos = [g[obj].dropna().values for _, g in df.groupby(f1)]
        F, p = stats.f_oneway(*grupos)
        mod = ols(f"Q('{obj}') ~ C(Q('{f1}'))", data=df).fit()
        tabla = anova_lm(mod, typ=1)
    else:
        formula = f"Q('{obj}') ~ C(Q('{f1}')) + C(Q('{f2}')) + C(Q('{f1}')):C(Q('{f2}'))"
        mod = ols(formula, data=df).fit()
        tabla = anova_lm(mod, typ=1)
        F = tabla["F"].iloc[0]
        p = tabla["PR(>F)"].iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Estadístico F (primer factor)", f"{F:.3f}")
    m2.metric("p-value", f"{p:.2e}" if p < 1e-4 else f"{p:.4f}")
    m3.metric("R² del modelo", f"{mod.rsquared:.4f}")

    st.dataframe(tabla.round(4), use_container_width=True)

    if p < alfa:
        st.success(f"p < {alfa} → se rechaza que las medias sean iguales: **{f1} sí influye** en {obj}.")
    else:
        st.info(f"p ≥ {alfa} → no hay evidencia de que {f1} influya en la media de {obj}.")

    with st.expander("Medias por grupo"):
        st.dataframe(df.groupby(f1)[obj].agg(["count", "mean", "std"]).round(3),
                     use_container_width=True)

with tab3:
    st.dataframe(df, use_container_width=True)
    st.caption(f"{len(df)} renglones · archivo fuente en el repositorio")

st.sidebar.markdown("---")
st.sidebar.caption("Plantilla base: 7_ANOVA.ipynb del curso · Widgets extra: selectores, "
                   "heatmap, boxplot, violin, IC 95%, interaction plot, métricas y tablas.")
