"""Guard the layout contracts that prevent fixed-card content compression."""

from pathlib import Path
import re


SOURCE = (Path(__file__).resolve().parents[1] /
          "app/components/dashboard/cards/planning_card.py").read_text(encoding="utf-8")


def test_weekly_plan_fixed_card_children_do_not_shrink():
    assert '.st-key-dashboard_top_plan [data-testid="stVerticalBlock"] > *' in SOURCE
    assert "flex-shrink: 0 !important;" in SOURCE


def test_selector_no_longer_pulls_following_row_up():
    rule = re.search(r'div\[class\*="st-key-weekly_plan_selector_"\] \{([^}]+)', SOURCE)
    assert rule
    assert "margin-bottom: 0;" in rule.group(1)


def test_description_has_separation_and_keeps_wrapping():
    rule = re.search(r"\.weekly-plan-next \{([^}]+)", SOURCE).group(1)
    assert "margin-top: 8px;" in rule
    assert "white-space: normal;" in rule
    assert "overflow: visible;" in rule


def test_day_text_not_clamped_or_truncated():
    for name in ("weekly-plan-day", "weekly-plan-title", "weekly-plan-details"):
        rule = re.search(r"\." + name + r" \{([^}]+)", SOURCE).group(1)
        assert "overflow: hidden" not in rule
        assert "line-clamp" not in rule
        assert not re.search(r"^\s*height:", rule, re.MULTILINE)
