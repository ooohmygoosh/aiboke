from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class TagWeightRule:
    favorite_delta: float = 0.8
    skip_delta: float = -0.6
    complete_delta: float = 0.1
    min_weight: float = -5.0
    max_weight: float = 10.0


class TagProfileEngine:
    """Simple user tag pool engine.

    The engine stores a weight dictionary in memory and applies behavior-driven updates.
    """

    def __init__(self, rule: TagWeightRule | None = None) -> None:
        self.rule = rule or TagWeightRule()

    def initialize(self, selected_tags: Iterable[str]) -> Dict[str, float]:
        return {tag: 1.0 for tag in selected_tags}

    def update(self, profile: Dict[str, float], tags: Iterable[str], action: str) -> Dict[str, float]:
        delta = self._delta_for(action)
        for tag in tags:
            current = profile.get(tag, 0.0)
            profile[tag] = self._clamp(current + delta)
        return profile

    def pick_prompt_tags(self, profile: Dict[str, float], top_n: int = 5) -> List[str]:
        ordered = sorted(profile.items(), key=lambda item: item[1], reverse=True)
        return [tag for tag, _ in ordered[:top_n]]

    def _delta_for(self, action: str) -> float:
        if action == "favorite":
            return self.rule.favorite_delta
        if action == "skip":
            return self.rule.skip_delta
        if action == "complete":
            return self.rule.complete_delta
        raise ValueError(f"Unsupported action: {action}")

    def _clamp(self, value: float) -> float:
        return max(self.rule.min_weight, min(self.rule.max_weight, value))
