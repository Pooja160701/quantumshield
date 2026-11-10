"""Transparent, deterministic security event scoring."""

from collections import Counter
from quantumshield.models import SecurityEvent

_EVENTS: list[SecurityEvent] = []


def record_event(category: str, description: str, severity: str = "low") -> SecurityEvent:
    weights = {"info": 5, "low": 15, "medium": 40, "high": 70, "critical": 95}
    normalized = severity.lower()
    if normalized not in weights:
        normalized = "low"
    event = SecurityEvent(
        category=category,
        severity=normalized,
        description=description[:500],
        score=weights[normalized],
    )
    _EVENTS.append(event)
    del _EVENTS[:-500]
    return event


def summary() -> dict:
    counts = Counter(event.severity for event in _EVENTS)
    return {
        "total_events": len(_EVENTS),
        "by_severity": dict(counts),
        "average_risk_score": round(sum(e.score for e in _EVENTS) / len(_EVENTS), 2)
        if _EVENTS else 0,
        "recent_events": [e.model_dump() for e in _EVENTS[-20:]],
        "scoring": "transparent fixed severity weights; not an ML prediction",
    }
