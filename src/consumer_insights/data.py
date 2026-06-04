from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PERSONAS = ["value_seekers", "quality_first", "convenience_first", "eco_advocates", "new_explorers"]
CHANNELS = ["douyin", "tmall", "jd", "offline_supermarket", "xiaohongshu", "private_domain"]
CITY_TIERS = ["tier_1", "new_tier_1", "tier_2", "tier_3_plus"]
CATEGORIES = ["ready_to_drink", "healthy_snack", "personal_care", "home_cleaning"]

THEME_PHRASES = {
    "price": [
        "the price feels high without promotion",
        "discount bundles make me more willing to buy",
        "I compare price across platforms before purchase",
    ],
    "quality": [
        "the product quality is stable and trustworthy",
        "I care about ingredients and product safety",
        "quality improvement would make me repurchase more often",
    ],
    "packaging": [
        "the packaging is convenient but could look more premium",
        "portable packaging is useful for work and travel",
        "the package design should show product benefits more clearly",
    ],
    "delivery": [
        "delivery speed affects whether I choose the brand",
        "offline availability is not always convenient",
        "stockouts make me switch to other brands",
    ],
    "sustainability": [
        "I prefer brands with recyclable packaging",
        "sustainability claims need to be more credible",
        "low carbon packaging would improve brand impression",
    ],
    "promotion": [
        "livestream promotion helps me discover new products",
        "membership coupons can increase repeat purchase",
        "KOL reviews are useful but need to be authentic",
    ],
}


def _clip_score(values: np.ndarray) -> np.ndarray:
    return np.clip(values, 1, 10)


def generate_demo_dataset(n_respondents: int = 5200, seed: int = 2026) -> pd.DataFrame:
    """Generate synthetic consumer survey responses and open-ended feedback."""
    rng = np.random.default_rng(seed)
    persona = rng.choice(PERSONAS, n_respondents, p=[0.27, 0.23, 0.20, 0.16, 0.14])
    channel = rng.choice(CHANNELS, n_respondents, p=[0.21, 0.22, 0.18, 0.17, 0.13, 0.09])
    city_tier = rng.choice(CITY_TIERS, n_respondents, p=[0.22, 0.28, 0.30, 0.20])
    category = rng.choice(CATEGORIES, n_respondents, p=[0.31, 0.28, 0.22, 0.19])
    age = np.clip(rng.normal(31, 8, n_respondents).round(), 18, 58).astype(int)
    monthly_income = np.clip(rng.lognormal(9.25, 0.45, n_respondents), 2500, 52000)

    persona_effects = {
        "value_seekers": (8.7, 6.4, 5.8, 5.0, 17),
        "quality_first": (5.0, 8.9, 6.6, 6.4, 28),
        "convenience_first": (5.8, 7.0, 8.8, 5.4, 24),
        "eco_advocates": (5.6, 7.6, 6.6, 9.0, 30),
        "new_explorers": (6.8, 6.8, 6.4, 6.2, 20),
    }
    price_sensitivity = np.zeros(n_respondents)
    quality_expectation = np.zeros(n_respondents)
    convenience_need = np.zeros(n_respondents)
    sustainability_attitude = np.zeros(n_respondents)
    willingness_to_pay = np.zeros(n_respondents)

    for idx, p in enumerate(persona):
        price, quality, convenience, sustainability, wtp = persona_effects[p]
        income_boost = np.log(monthly_income[idx] / 8000) * 1.8
        price_sensitivity[idx] = price + rng.normal(0, 0.9) - max(income_boost, 0) * 0.25
        quality_expectation[idx] = quality + rng.normal(0, 0.8)
        convenience_need[idx] = convenience + rng.normal(0, 0.8)
        sustainability_attitude[idx] = sustainability + rng.normal(0, 0.8)
        willingness_to_pay[idx] = wtp + income_boost + 0.7 * quality_expectation[idx] - 0.45 * price_sensitivity[idx] + rng.normal(0, 3.4)

    price_sensitivity = _clip_score(price_sensitivity)
    quality_expectation = _clip_score(quality_expectation)
    convenience_need = _clip_score(convenience_need)
    sustainability_attitude = _clip_score(sustainability_attitude)
    willingness_to_pay = np.clip(willingness_to_pay, 7, 65)

    awareness_prob = np.clip(0.62 + 0.04 * (channel == "douyin") + 0.05 * (channel == "tmall") + 0.03 * (city_tier == "tier_1"), 0.35, 0.95)
    awareness = rng.binomial(1, awareness_prob)
    consideration_prob = np.clip(0.28 + 0.48 * awareness + 0.035 * quality_expectation - 0.020 * price_sensitivity, 0.05, 0.92)
    consideration = rng.binomial(1, consideration_prob)
    trial_prob = np.clip(0.16 + 0.50 * consideration + 0.030 * convenience_need - 0.018 * price_sensitivity, 0.03, 0.88)
    trial = rng.binomial(1, trial_prob)
    repeat_prob = np.clip(0.10 + 0.52 * trial + 0.035 * quality_expectation + 0.020 * convenience_need - 0.025 * price_sensitivity, 0.02, 0.90)
    repeat_purchase = rng.binomial(1, repeat_prob)
    monthly_purchase_frequency = np.where(repeat_purchase == 1, rng.poisson(2.0 + convenience_need / 5), rng.poisson(0.45 + trial))

    satisfaction = _clip_score(
        4.7
        + 0.32 * quality_expectation
        + 0.22 * convenience_need
        + 0.12 * sustainability_attitude
        - 0.25 * price_sensitivity
        + 1.05 * repeat_purchase
        + rng.normal(0, 1.1, n_respondents)
    )
    nps = np.clip(np.round((satisfaction - 1) / 9 * 10 + rng.normal(0, 1.2, n_respondents)), 0, 10).astype(int)

    theme_weights = {
        "value_seekers": [0.37, 0.12, 0.12, 0.10, 0.07, 0.22],
        "quality_first": [0.10, 0.38, 0.13, 0.11, 0.09, 0.19],
        "convenience_first": [0.13, 0.15, 0.16, 0.34, 0.05, 0.17],
        "eco_advocates": [0.10, 0.16, 0.11, 0.11, 0.38, 0.14],
        "new_explorers": [0.20, 0.16, 0.14, 0.14, 0.10, 0.26],
    }
    themes = list(THEME_PHRASES.keys())
    feedback_theme = []
    feedback_text = []
    for p in persona:
        theme = rng.choice(themes, p=theme_weights[p])
        feedback_theme.append(theme)
        feedback_text.append(rng.choice(THEME_PHRASES[theme]))

    data = pd.DataFrame(
        {
            "respondent_id": [f"R{idx + 1:06d}" for idx in range(n_respondents)],
            "persona_seed": persona,
            "age": age,
            "monthly_income": monthly_income.round(2),
            "city_tier": city_tier,
            "primary_channel": channel,
            "category": category,
            "price_sensitivity": price_sensitivity.round(2),
            "quality_expectation": quality_expectation.round(2),
            "convenience_need": convenience_need.round(2),
            "sustainability_attitude": sustainability_attitude.round(2),
            "willingness_to_pay": willingness_to_pay.round(2),
            "awareness": awareness,
            "consideration": consideration,
            "trial": trial,
            "repeat_purchase": repeat_purchase,
            "monthly_purchase_frequency": monthly_purchase_frequency,
            "satisfaction": satisfaction.round(2),
            "nps": nps,
            "feedback_theme_seed": feedback_theme,
            "feedback_text": feedback_text,
        }
    )
    return data


def save_demo_dataset(survey: pd.DataFrame, data_dir: str | Path) -> None:
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)
    survey.to_csv(data_path / "demo_consumer_survey.csv", index=False)


def load_demo_dataset(data_dir: str | Path) -> pd.DataFrame:
    return pd.read_csv(Path(data_dir) / "demo_consumer_survey.csv")

