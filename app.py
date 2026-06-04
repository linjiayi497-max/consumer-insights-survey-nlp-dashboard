from __future__ import annotations

from pathlib import Path
import sys
import json

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from consumer_insights.analytics import build_outputs
from consumer_insights.data import generate_demo_dataset, load_demo_dataset, save_demo_dataset


DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"


@st.cache_data
def load_or_create_data() -> pd.DataFrame:
    if not (DATA_DIR / "demo_consumer_survey.csv").exists():
        survey = generate_demo_dataset()
        save_demo_dataset(survey, DATA_DIR)
    return load_demo_dataset(DATA_DIR)


@st.cache_data
def load_or_build_outputs(survey: pd.DataFrame) -> dict[str, object]:
    required = {
        "survey_kpis.json",
        "segmented_survey.csv",
        "segment_profiles.csv",
        "brand_funnel_overall.csv",
        "brand_funnel_by_segment.csv",
        "topic_terms.csv",
        "price_sensitivity.csv",
        "opportunity_map.csv",
        "nps_by_segment.csv",
    }
    if all((OUTPUT_DIR / name).exists() for name in required):
        return {
            "survey_kpis": json.loads((OUTPUT_DIR / "survey_kpis.json").read_text(encoding="utf-8")),
            "segmented_survey": pd.read_csv(OUTPUT_DIR / "segmented_survey.csv"),
            "segment_profiles": pd.read_csv(OUTPUT_DIR / "segment_profiles.csv"),
            "brand_funnel_overall": pd.read_csv(OUTPUT_DIR / "brand_funnel_overall.csv"),
            "brand_funnel_by_segment": pd.read_csv(OUTPUT_DIR / "brand_funnel_by_segment.csv"),
            "topic_terms": pd.read_csv(OUTPUT_DIR / "topic_terms.csv"),
            "price_sensitivity": pd.read_csv(OUTPUT_DIR / "price_sensitivity.csv"),
            "opportunity_map": pd.read_csv(OUTPUT_DIR / "opportunity_map.csv"),
            "nps_by_segment": pd.read_csv(OUTPUT_DIR / "nps_by_segment.csv"),
        }
    return build_outputs(survey, OUTPUT_DIR)


st.set_page_config(page_title="Consumer Insights Dashboard", layout="wide")
st.title("Consumer Insights Dashboard")

survey = load_or_create_data()
outputs = load_or_build_outputs(survey)
kpis = outputs["survey_kpis"]
segments = outputs["segment_profiles"]
funnel = outputs["brand_funnel_by_segment"]
topics = outputs["topic_terms"]
pricing = outputs["price_sensitivity"]
opportunities = outputs["opportunity_map"]
nps_by_segment = outputs["nps_by_segment"]

cols = st.columns(5)
cols[0].metric("Respondents", f"{kpis['respondents']:,}")
cols[1].metric("Awareness", f"{kpis['awareness_rate']:.1%}")
cols[2].metric("Trial", f"{kpis['trial_rate']:.1%}")
cols[3].metric("Repeat", f"{kpis['repeat_rate']:.1%}")
cols[4].metric("NPS", f"{kpis['nps']:.1f}")

funnel_tab, segment_tab, topic_tab, price_tab, opportunity_tab = st.tabs(
    ["Brand Funnel", "Segments", "Text Topics", "Pricing", "Opportunity Map"]
)

with funnel_tab:
    st.plotly_chart(px.bar(funnel, x="stage", y="rate_from_total", color="group", barmode="group", title="Brand Funnel by Segment"), use_container_width=True)
    st.dataframe(funnel, use_container_width=True)

with segment_tab:
    st.plotly_chart(px.scatter(segments, x="price_sensitivity", y="willingness_to_pay", size="respondents", color="segment", title="Segment Price Sensitivity vs WTP"), use_container_width=True)
    st.plotly_chart(px.bar(nps_by_segment, x="segment", y="nps_score", title="NPS by Segment"), use_container_width=True)
    st.dataframe(segments, use_container_width=True)

with topic_tab:
    st.plotly_chart(px.bar(topics, x="topic_id", y="share", color="nps_score", title="Open-ended Feedback Topics"), use_container_width=True)
    st.dataframe(topics, use_container_width=True)

with price_tab:
    st.plotly_chart(px.line(pricing, x="price", y=["demand_share", "revenue_index"], markers=True, title="Price Sensitivity Curve"), use_container_width=True)
    st.dataframe(pricing, use_container_width=True)

with opportunity_tab:
    st.plotly_chart(px.scatter(opportunities, x="avg_nps", y="opportunity_score", size="responses", color="segment", hover_data=["topic_id"], title="Segment x Topic Opportunity Map"), use_container_width=True)
    st.dataframe(opportunities.head(100), use_container_width=True)

