from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from consumer_insights.analytics import (
    brand_funnel,
    nps_score,
    opportunity_map,
    price_sensitivity,
    segment_profiles,
    survey_kpis,
    topic_model,
)
from consumer_insights.data import generate_demo_dataset


class ConsumerInsightsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.survey = generate_demo_dataset(n_respondents=1500, seed=17)

    def test_survey_data_ranges(self) -> None:
        self.assertEqual(len(self.survey), 1500)
        self.assertGreaterEqual(self.survey["nps"].min(), 0)
        self.assertLessEqual(self.survey["nps"].max(), 10)

    def test_kpis_and_funnel(self) -> None:
        kpis = survey_kpis(self.survey)
        funnel = brand_funnel(self.survey)
        self.assertIn("nps", kpis)
        self.assertEqual(set(funnel["stage"]), {"awareness", "consideration", "trial", "repeat_purchase"})

    def test_segments(self) -> None:
        segmented, profiles = segment_profiles(self.survey)
        self.assertIn("segment", segmented.columns)
        self.assertGreaterEqual(profiles["segment"].nunique(), 3)

    def test_topic_model_and_opportunity(self) -> None:
        segmented, _ = segment_profiles(self.survey)
        feedback_topics, topics = topic_model(self.survey)
        opportunities = opportunity_map(segmented, feedback_topics)
        self.assertEqual(topics["topic_id"].nunique(), 6)
        self.assertFalse(opportunities["opportunity_score"].isna().any())

    def test_price_sensitivity(self) -> None:
        pricing = price_sensitivity(self.survey)
        self.assertGreater(pricing["expected_revenue"].max(), 0)
        self.assertTrue(pricing["demand_share"].is_monotonic_decreasing)
        self.assertIsInstance(nps_score(self.survey["nps"]), float)


if __name__ == "__main__":
    unittest.main()

