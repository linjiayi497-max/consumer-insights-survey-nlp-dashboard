# Consumer Insights Survey NLP Dashboard

A reproducible market research project for FMCG, brand marketing, user research, and strategy internships. It combines survey analytics, brand funnel tracking, NPS, customer segmentation, open-ended feedback topic mining, price sensitivity, and opportunity prioritization.

The dataset is synthetic and generated locally. The implementation is original; no external project code is copied.

## Open-source Inspiration

- [MaartenGr/BERTopic](https://github.com/MaartenGr/BERTopic): topic modeling and interpretable topic summary inspiration.
- [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn): KMeans, TF-IDF, and NMF modeling workflow.
- [plotly/dash-sample-apps](https://github.com/plotly/dash-sample-apps): data product storytelling and dashboard inspiration.

## What It Does

- Generates 5,200 synthetic consumer survey responses with demographics, attitudes, brand funnel stages, NPS, willingness to pay, and open-ended feedback.
- Profiles consumer segments with KMeans based on price sensitivity, quality expectation, convenience need, sustainability attitude, willingness to pay, purchase frequency, and satisfaction.
- Mines feedback topics with TF-IDF and NMF.
- Builds brand funnel, NPS, price sensitivity, and opportunity prioritization reports.
- Provides SQL examples for channel funnel, segment NPS, and topic pain-point analysis.

## Quick Start

```bash
python -m pip install -r requirements.txt
python scripts/generate_demo_data.py
python scripts/run_insights.py
streamlit run app.py
python -m unittest discover -s tests
```

## Outputs

- `outputs/survey_kpis.json`: executive survey metrics.
- `outputs/segment_profiles.csv`: segment size, funnel, NPS, WTP, and attitude scores.
- `outputs/brand_funnel_overall.csv` and `outputs/brand_funnel_by_segment.csv`: funnel conversion tables.
- `outputs/topic_terms.csv`: feedback topic summaries.
- `outputs/price_sensitivity.csv`: demand and revenue index by price point.
- `outputs/opportunity_map.csv`: segment x topic opportunity priorities.
- `outputs/insights_report.md`: interview-ready insight report.

## Resume Evidence Draft

Use only after the repository is uploaded and reviewed:

> Built a consumer insights dashboard using Python and Streamlit, integrating survey funnel, NPS, KMeans segmentation, TF-IDF/NMF topic mining, price sensitivity, and opportunity prioritization; translated quantitative survey and open-ended feedback into segment-specific brand, channel, pricing, and CRM recommendations.

