"""Consumer insights analytics toolkit."""

from .analytics import build_outputs, brand_funnel, nps_score, price_sensitivity, segment_profiles, topic_model
from .data import generate_demo_dataset, save_demo_dataset

__all__ = [
    "brand_funnel",
    "build_outputs",
    "generate_demo_dataset",
    "nps_score",
    "price_sensitivity",
    "save_demo_dataset",
    "segment_profiles",
    "topic_model",
]

