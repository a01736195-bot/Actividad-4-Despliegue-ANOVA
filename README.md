# Actividad 4 (Despliegue ANOVA)

**TC2003B.201 — Gestión de Plataformas Tecnológicas**
**Socio formador: GAC Motor**

Análisis de varianza (**ANOVA de una vía** y **ANOVA multifactorial**) sobre 5 bases de datos reales de GAC, siguiendo la metodología de la plantilla de clase (`7_ANOVA.ipynb`): `scipy.stats.f_oneway`, tabla `statsmodels.anova_lm` y `interaction_plot`, con boxplots, barras con IC 95 % y violin plots.

**Regla de interpretación:** si *p-value < 0.05* se rechaza que las medias de los grupos sean iguales → el factor **sí influye** en la variable cuantitativa.

---

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `Actividad_4_ANOVA.ipynb` | Notebook ejecutado con los **10 análisis** (1 one-way + 1 multifactorial por cada una de las 5 bases) |
| `app.py` | Dashboard Streamlit con widgets adicionales a la plantilla (bonus punto 5): selectores de base/análisis/gráfica, boxplot, violin, barras IC 95 %, heatmap de medias, interaction plot, tablas ANOVA y métricas |
| `.streamlit/config.toml` | Tema borgoña GAC para el dashboard |
| `Bitacora de Piso.csv` | Base requerida: 197 visitas de piso (abr–jul 2025), ya limpia |
| `Leads Reales.csv` | Base requerida: 28 cortes mensuales de efectividad de leads, ya limpia |
| `base_leads_limpia.csv` | 208 leads captados en Plaza Angelópolis |
| `base_resumen_limpio.csv` | 30 meses de resultados vs objetivo |
| `funnel_mensual.csv` | 18 meses × 8 etapas del embudo comercial |
| `requirements.txt` | Dependencias |

## Preprocesamiento (punto 3 de la consigna)

- **Nulos:** imputados/depurados en las actividades previas; el notebook **verifica 0 nulos** en las 5 bases.
- **Outliers:** revisión por rango intercuartílico (IQR) sobre cada variable objetivo; los extremos detectados corresponden a meses/categorías reales (picos de captación, temperaturas extremas) y se documenta por qué se conservan.
- **Transformaciones:**
  - Bitácora: `Score_Cierre = SDC + Venta` (score 0–2 por visita, independiente de `Prueba_Manejo`).
  - Leads Reales: `Periodo_Analisis` consolida 2025-2026 (2026 solo tiene 5 cortes) para dar réplicas al factorial.
  - Base de Leads: `Temperatura` → `Score_Temperatura` ordinal (1–3); productos con < 10 registros se excluyen del factorial (EMZOOM y EMKOO concentran 183 leads).
  - Resumen: `Semestre` (S1/S2) y `Periodo_Analisis`.
  - Funnel: formato ancho → largo con `melt` (mes × etapa) y extracción de `Año`.

## Resultados principales (punto 4 de la consigna)

| Base | ANOVA una vía | ANOVA multifactorial | Hallazgo |
|---|---|---|---|
| Bitácora de Piso | Asesor: F = 0.68, p = 0.664 (n.s.) | Prueba de manejo: **p = 0.039** ✔ · interacción p = 0.174 | La prueba de manejo mueve el cierre; el asesor no |
| Leads Reales | Nivel de efectividad: F = 0.13, p = 0.880 (n.s.) | Periodo: **p = 0.0006** ✔ · interacción p = 0.096 | Convertir depende del periodo, no del volumen efectivo |
| Base de Leads | Producto: F = 0.31, p = 0.577 (n.s.) | Estado: **p < 0.0001** ✔ · interacción p = 0.075 | La temperatura del lead anticipa la venta |
| Resumen Mensual | Periodo: F = 8.36, **p = 0.0073** ✔ | Periodo **p = 0.0002**, Semestre **p = 0.0016**, **interacción p < 0.0001** (R² = 0.70) | Cambio de régimen 2024 → 2025-2026 |
| Funnel Mensual | Etapa: F = 202.1, **p < 10⁻⁶⁷** ✔ (R² = 0.91) | Etapa, Año e **interacción p = 0.0003** ✔ | El cuello de botella Cita → Prueba → SDC persiste |

**Insight transversal:** la prueba de manejo y la gestión de citas son la palanca del cierre (Bitácora + Funnel + Leads de plaza lo señalan de forma independiente); las bases de resultados muestran que el cambio vino del periodo/régimen, no de la mezcla de productos ni del volumen de leads.

## Cómo ejecutar

```bash
pip install -r requirements.txt

# Notebook
jupyter notebook Actividad_4_ANOVA.ipynb

# Dashboard (bonus)
streamlit run app.py
```

---
*Gabriel Omar Pérez Hernández · A01736195*
