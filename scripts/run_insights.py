from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from consumer_insights.analytics import build_outputs
from consumer_insights.data import load_demo_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Run consumer insights analysis.")
    parser.add_argument("--data-dir", default=str(ROOT / "data"))
    parser.add_argument("--output-dir", default=str(ROOT / "outputs"))
    args = parser.parse_args()
    survey = load_demo_dataset(args.data_dir)
    outputs = build_outputs(survey, args.output_dir)
    kpis = outputs["survey_kpis"]
    top_opp = outputs["opportunity_map"].iloc[0]
    print(
        "insights complete "
        f"respondents={kpis['respondents']:,} "
        f"nps={kpis['nps']} "
        f"top_opportunity={top_opp['segment']}/topic_{int(top_opp['topic_id'])}"
    )


if __name__ == "__main__":
    main()

