from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from consumer_insights.data import generate_demo_dataset, save_demo_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic consumer survey data.")
    parser.add_argument("--respondents", type=int, default=5200)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--data-dir", default=str(ROOT / "data"))
    args = parser.parse_args()
    survey = generate_demo_dataset(n_respondents=args.respondents, seed=args.seed)
    save_demo_dataset(survey, args.data_dir)
    print(f"generated respondents={len(survey):,} nps={survey['nps'].mean():.2f}")


if __name__ == "__main__":
    main()

