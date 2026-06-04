from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler


FUNNEL_STAGES = ["awareness", "consideration", "trial", "repeat_purchase"]
SEGMENT_FEATURES = [
    "price_sensitivity",
    "quality_expectation",
    "convenience_need",
    "sustainability_attitude",
    "willingness_to_pay",
    "monthly_purchase_frequency",
    "satisfaction",
    "nps",
]


def nps_score(scores: pd.Series) -> float:
    promoters = (scores >= 9).mean()
    detractors = (scores <= 6).mean()
    return float((promoters - detractors) * 100)


def survey_kpis(survey: pd.DataFrame) -> dict[str, float | int]:
    return {
        "respondents": int(len(survey)),
        "awareness_rate": round(float(survey["awareness"].mean()), 4),
        "consideration_rate": round(float(survey["consideration"].mean()), 4),
        "trial_rate": round(float(survey["trial"].mean()), 4),
        "repeat_rate": round(float(survey["repeat_purchase"].mean()), 4),
        "avg_satisfaction": round(float(survey["satisfaction"].mean()), 2),
        "nps": round(nps_score(survey["nps"]), 2),
        "avg_willingness_to_pay": round(float(survey["willingness_to_pay"].mean()), 2),
    }


def brand_funnel(survey: pd.DataFrame, group_col: str | None = None) -> pd.DataFrame:
    groups = [("overall", survey)] if group_col is None else list(survey.groupby(group_col))
    rows = []
    for group_name, group in groups:
        base = len(group)
        previous = base
        for stage in FUNNEL_STAGES:
            count = int(group[stage].sum())
            rows.append(
                {
                    "group": group_name,
                    "stage": stage,
                    "count": count,
                    "rate_from_total": count / base if base else 0,
                    "step_conversion": count / previous if previous else 0,
                    "drop_off": previous - count,
                }
            )
            previous = count
    return pd.DataFrame(rows).round(4)


def assign_segments(survey: pd.DataFrame, n_segments: int = 5, seed: int = 2026) -> pd.DataFrame:
    data = survey.copy()
    scaler = StandardScaler()
    x = scaler.fit_transform(data[SEGMENT_FEATURES])
    model = KMeans(n_clusters=n_segments, random_state=seed, n_init=20)
    data["segment_id"] = model.fit_predict(x)
    profiles = data.groupby("segment_id")[SEGMENT_FEATURES].mean()
    labels = {}
    used_labels: set[str] = set()
    for segment_id, row in profiles.iterrows():
        traits = {
            "Value Seekers": row["price_sensitivity"],
            "Quality Loyalists": row["quality_expectation"],
            "Convenience Driven": row["convenience_need"],
            "Eco Advocates": row["sustainability_attitude"],
            "High Value Fans": row["nps"] / 1.2 + row["monthly_purchase_frequency"],
        }
        ranked_labels = sorted(traits, key=traits.get, reverse=True)
        label = next((candidate for candidate in ranked_labels if candidate not in used_labels), ranked_labels[0])
        used_labels.add(label)
        labels[segment_id] = label
    data["segment"] = data["segment_id"].map(labels)
    return data


def segment_profiles(survey: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    segmented = assign_segments(survey)
    profile = (
        segmented.groupby("segment")
        .agg(
            respondents=("respondent_id", "count"),
            awareness_rate=("awareness", "mean"),
            trial_rate=("trial", "mean"),
            repeat_rate=("repeat_purchase", "mean"),
            avg_nps=("nps", "mean"),
            nps_score=("nps", nps_score),
            willingness_to_pay=("willingness_to_pay", "mean"),
            price_sensitivity=("price_sensitivity", "mean"),
            quality_expectation=("quality_expectation", "mean"),
            convenience_need=("convenience_need", "mean"),
            sustainability_attitude=("sustainability_attitude", "mean"),
        )
        .reset_index()
    )
    profile["share"] = profile["respondents"] / profile["respondents"].sum()
    return segmented, profile.round(4)


def topic_model(survey: pd.DataFrame, n_topics: int = 6) -> tuple[pd.DataFrame, pd.DataFrame]:
    vectorizer = TfidfVectorizer(stop_words="english", min_df=3, ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(survey["feedback_text"])
    model = NMF(n_components=n_topics, init="nndsvda", random_state=2026, max_iter=500)
    topic_weights = model.fit_transform(matrix)
    terms = np.array(vectorizer.get_feature_names_out())

    topic_rows = []
    for topic_idx, weights in enumerate(model.components_):
        top_terms = terms[np.argsort(weights)[-8:][::-1]]
        topic_rows.append({"topic_id": topic_idx, "top_terms": ", ".join(top_terms)})
    topic_terms = pd.DataFrame(topic_rows)

    feedback_topics = survey[["respondent_id", "nps", "satisfaction", "feedback_text"]].copy()
    feedback_topics["topic_id"] = topic_weights.argmax(axis=1)
    topic_summary = (
        feedback_topics.groupby("topic_id")
        .agg(
            responses=("respondent_id", "count"),
            avg_nps=("nps", "mean"),
            nps_score=("nps", nps_score),
            avg_satisfaction=("satisfaction", "mean"),
        )
        .reset_index()
        .merge(topic_terms, on="topic_id")
    )
    topic_summary["share"] = topic_summary["responses"] / len(feedback_topics)
    return feedback_topics, topic_summary.round(4)


def price_sensitivity(survey: pd.DataFrame) -> pd.DataFrame:
    price_points = np.arange(8, 51, 3)
    rows = []
    for price in price_points:
        demand_share = float((survey["willingness_to_pay"] >= price).mean())
        expected_units = demand_share * len(survey)
        rows.append(
            {
                "price": price,
                "demand_share": demand_share,
                "expected_units": expected_units,
                "expected_revenue": price * expected_units,
            }
        )
    result = pd.DataFrame(rows)
    result["revenue_index"] = result["expected_revenue"] / result["expected_revenue"].max()
    return result.round(4)


def opportunity_map(segmented: pd.DataFrame, feedback_topics: pd.DataFrame) -> pd.DataFrame:
    merged = segmented.merge(feedback_topics[["respondent_id", "topic_id"]], on="respondent_id", how="left")
    topic_counts = (
        merged.groupby(["segment", "topic_id"])
        .agg(
            responses=("respondent_id", "count"),
            avg_nps=("nps", "mean"),
            purchase_frequency=("monthly_purchase_frequency", "mean"),
            repeat_rate=("repeat_purchase", "mean"),
        )
        .reset_index()
    )
    topic_counts["share"] = topic_counts["responses"] / len(merged)
    topic_counts["nps_gap"] = np.maximum(0, 8 - topic_counts["avg_nps"]) / 8
    topic_counts["opportunity_score"] = (
        topic_counts["share"] * (1 + topic_counts["nps_gap"]) * (1 + topic_counts["purchase_frequency"] / 5)
    )
    return topic_counts.sort_values("opportunity_score", ascending=False).round(4)


def build_outputs(survey: pd.DataFrame, output_dir: str | Path) -> dict[str, object]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    kpis = survey_kpis(survey)
    segmented, segments = segment_profiles(survey)
    funnel_overall = brand_funnel(survey)
    funnel_segment = brand_funnel(segmented, "segment")
    feedback_topics, topics = topic_model(survey)
    pricing = price_sensitivity(survey)
    opportunities = opportunity_map(segmented, feedback_topics)
    nps_by_segment = (
        segmented.groupby("segment")
        .agg(respondents=("respondent_id", "count"), avg_nps=("nps", "mean"), nps_score=("nps", nps_score))
        .reset_index()
        .round(4)
    )

    (output_path / "survey_kpis.json").write_text(json.dumps(kpis, indent=2), encoding="utf-8")
    segmented.to_csv(output_path / "segmented_survey.csv", index=False)
    segments.to_csv(output_path / "segment_profiles.csv", index=False)
    funnel_overall.to_csv(output_path / "brand_funnel_overall.csv", index=False)
    funnel_segment.to_csv(output_path / "brand_funnel_by_segment.csv", index=False)
    feedback_topics.to_csv(output_path / "feedback_topics.csv", index=False)
    topics.to_csv(output_path / "topic_terms.csv", index=False)
    pricing.to_csv(output_path / "price_sensitivity.csv", index=False)
    opportunities.to_csv(output_path / "opportunity_map.csv", index=False)
    nps_by_segment.to_csv(output_path / "nps_by_segment.csv", index=False)
    write_insights_report(output_path / "insights_report.md", kpis, segments, topics, pricing, opportunities)

    return {
        "survey_kpis": kpis,
        "segmented_survey": segmented,
        "segment_profiles": segments,
        "brand_funnel_overall": funnel_overall,
        "brand_funnel_by_segment": funnel_segment,
        "feedback_topics": feedback_topics,
        "topic_terms": topics,
        "price_sensitivity": pricing,
        "opportunity_map": opportunities,
        "nps_by_segment": nps_by_segment,
    }


def write_insights_report(
    path: Path,
    kpis: dict[str, object],
    segments: pd.DataFrame,
    topics: pd.DataFrame,
    pricing: pd.DataFrame,
    opportunities: pd.DataFrame,
) -> None:
    top_segment = segments.sort_values("respondents", ascending=False).iloc[0]
    top_topic = topics.sort_values("responses", ascending=False).iloc[0]
    best_price = pricing.sort_values("expected_revenue", ascending=False).iloc[0]
    top_opp = opportunities.iloc[0]
    lines = [
        "# Consumer Insights Report",
        "",
        "## Survey Snapshot",
        f"- Respondents: {kpis['respondents']:,}",
        f"- Awareness rate: {kpis['awareness_rate']:.2%}",
        f"- Trial rate: {kpis['trial_rate']:.2%}",
        f"- Repeat rate: {kpis['repeat_rate']:.2%}",
        f"- NPS: {kpis['nps']}",
        f"- Average willingness to pay: {kpis['avg_willingness_to_pay']}",
        "",
        "## Key Findings",
        f"- Largest segment: {top_segment['segment']} with {top_segment['share']:.2%} respondent share.",
        f"- Most frequent feedback topic: topic {int(top_topic['topic_id'])}, terms: {top_topic['top_terms']}.",
        f"- Revenue-maximizing demo price point: {best_price['price']} with demand share {best_price['demand_share']:.2%}.",
        f"- Highest opportunity: segment {top_opp['segment']} and topic {int(top_opp['topic_id'])}, score {top_opp['opportunity_score']}.",
        "",
        "## Resume Evidence",
        "- Built a consumer insights dashboard covering survey funnel, NPS, KMeans segmentation, TF-IDF/NMF topic mining, price sensitivity, and opportunity prioritization.",
        "- Translated quantitative survey and text feedback into segment-specific brand, channel, pricing, and CRM recommendations.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
