"""Mobile presentation overrides; desktop layout remains owned by each page."""

import streamlit as st

MOBILE_LAYOUT_CSS = r"""
@media (max-width: 700px) {
.st-key-dashboard_page {display:flex; flex-direction:column; gap:1rem; min-width:0;}
.st-key-dashboard_page :is([data-testid="stVerticalBlock"],[data-testid="stHorizontalBlock"],[data-testid="stColumn"],[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stLayoutWrapper"]):has(.st-key-dashboard_current_state,.st-key-dashboard_next_workout,.st-key-dashboard_brief,.st-key-dashboard_top_plan,.st-key-dashboard_top_latest,.st-key-dashboard_top_event,.st-key-dashboard_summary):not(.st-key-dashboard_current_state,.st-key-dashboard_next_workout,.st-key-dashboard_brief,.st-key-dashboard_top_plan,.st-key-dashboard_top_latest,.st-key-dashboard_top_event,.st-key-dashboard_summary) {display:contents !important;}
.st-key-dashboard_page .st-key-dashboard_current_state {order:1; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-dashboard_page .st-key-dashboard_next_workout {order:2; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-dashboard_page .st-key-dashboard_brief {order:3; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-dashboard_page .st-key-dashboard_top_plan {order:4; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-dashboard_page .st-key-dashboard_top_latest {order:5; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-dashboard_page .st-key-dashboard_top_event {order:6; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-dashboard_page .st-key-dashboard_summary {order:7; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-today_page {display:flex; flex-direction:column; gap:1rem; min-width:0;}
.st-key-today_page :is([data-testid="stVerticalBlock"],[data-testid="stHorizontalBlock"],[data-testid="stColumn"],[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stLayoutWrapper"]):has(.st-key-today-recommendation-card,.st-key-today_session_card,.st-key-today_session_equivalent,.st-key-today_metrics,.st-key-today_recovery_log,.st-key-today_guidance_column,.st-key-today_analysis):not(.st-key-today-recommendation-card,.st-key-today_session_card,.st-key-today_session_equivalent,.st-key-today_metrics,.st-key-today_recovery_log,.st-key-today_guidance_column,.st-key-today_analysis) {display:contents !important;}
.st-key-today_page .st-key-today-recommendation-card {order:1; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-today_page .st-key-today_session_card {order:2; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-today_page .st-key-today_session_equivalent {order:3; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-today_page .st-key-today_metrics {order:4; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-today_page .st-key-today_recovery_log {order:5; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-today_page .st-key-today_analysis {order:7; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-today_page .st-key-today_guidance_column {order:6; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-development_page {display:flex; flex-direction:column; gap:1rem; min-width:0;}
.st-key-development_page :is([data-testid="stVerticalBlock"],[data-testid="stHorizontalBlock"],[data-testid="stColumn"],[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stLayoutWrapper"]):has(.st-key-development_analysis,.st-key-development_kpi_row,.st-key-development_details):not(.st-key-development_analysis,.st-key-development_kpi_row,.st-key-development_details) {display:contents !important;}
.st-key-development_page .st-key-development_analysis {order:1; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-development_page .st-key-development_kpi_row {order:2; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}
.st-key-development_page .st-key-development_details {order:3; width:100% !important; min-width:0 !important; height:auto !important; max-height:none !important; flex-shrink:0 !important;}

.st-key-dashboard_page [data-testid="stVerticalBlock"]:has(> [data-testid="stVerticalBlock"]),
.st-key-dashboard_page [data-testid="stVerticalBlockBorderWrapper"]:has(> .st-key-dashboard_top_plan) {max-height:none;}
.st-key-dashboard_page :is(.st-key-dashboard_current_state,.st-key-dashboard_next_workout,.st-key-dashboard_brief,.st-key-dashboard_top_plan,.st-key-dashboard_top_latest,.st-key-dashboard_top_event,.st-key-dashboard_summary) {
    overflow:visible !important;
}
.st-key-dashboard_week_days {overflow-x:auto; padding-bottom:0.35rem;}
.st-key-dashboard_week_days [data-testid="stHorizontalBlock"] {flex-wrap:nowrap !important; gap:0 !important;}
.st-key-dashboard_week_days [data-testid="stColumn"] {flex:0 0 6rem !important; width:6rem !important; min-width:6rem !important;}
.st-key-dashboard_week_days [data-testid="stColumn"]:first-child,
.st-key-dashboard_week_days [data-testid="stColumn"]:last-child {flex-basis:2.5rem !important; min-width:2.5rem !important; width:2.5rem !important;}
.st-key-dashboard_week_selector [data-testid="stHorizontalBlock"] {flex-wrap:nowrap;}
.st-key-dashboard_week_selector [data-testid="stColumn"]:first-child,
.st-key-dashboard_week_selector [data-testid="stColumn"]:last-child {display:none;}
.st-key-dashboard_week_selector [data-testid="stColumn"]:nth-child(2) {width:100% !important; flex:1 1 100% !important; min-width:0;}
.st-key-dashboard_page .weekly-plan-weekday {font-size:0.85rem;}
.st-key-dashboard_page .weekly-plan-title {font-size:0.85rem; line-height:1.3;}
.st-key-dashboard_page .weekly-plan-details,
.st-key-dashboard_page .weekly-plan-next {font-size:0.78rem; line-height:1.35;}

:is(.st-key-dashboard_page,.st-key-today_page,.st-key-development_page) .current-state-label,
:is(.st-key-dashboard_page,.st-key-today_page,.st-key-development_page) .current-state-status,
:is(.st-key-dashboard_page,.st-key-today_page,.st-key-development_page) .current-state-context,
:is(.st-key-dashboard_page,.st-key-today_page,.st-key-development_page) .current-state-indicator-label,
:is(.st-key-dashboard_page,.st-key-today_page,.st-key-development_page) .current-state-recommendation {
    font-size:0.8rem; line-height:1.35; white-space:normal; overflow:visible;
}
.st-key-development_page .development-kpi-label,
.st-key-development_page .development-kpi-status,
.st-key-development_page .development-kpi-context,
.st-key-development_page .development-chart-subtitle {
    font-size:0.8rem; line-height:1.35; white-space:normal; overflow:visible;
}
.st-key-development_page .development-section-gap,
.st-key-development_page .development-between-charts,
.st-key-development_page .development-lower-row {display:none;}
.st-key-development_page [data-testid="stElementContainer"]:has(:is(.development-section-gap,.development-between-charts,.development-lower-row)) {display:none; margin:0;}
}
"""

MOBILE_SIDEBAR_SCRIPT = r"""
<style>
[data-testid="stElementContainer"]:has(.pl-mobile-navigation-hook) {display:none;}
</style>
<span class="pl-mobile-navigation-hook"></span>
<script>
if (window.__performanceLabMobileNavigation) {
    document.removeEventListener("click", window.__performanceLabMobileNavigation);
}
window.__performanceLabMobileNavigation = function (event) {
    if (!window.matchMedia("(max-width: 700px)").matches) return;
    if (!(event.target instanceof Element)) return;
    if (!event.target.closest(".st-key-sidebar_navigation button, .st-key-sidebar_brand button")) return;
    const close = document.querySelector('[data-testid="stSidebarCollapseButton"] button');
    if (close) close.click();
};
document.addEventListener("click", window.__performanceLabMobileNavigation);
</script>
"""


def apply_mobile_layout():
    st.html("<style>" + MOBILE_LAYOUT_CSS + "</style>")


def apply_mobile_sidebar_navigation():
    st.html(MOBILE_SIDEBAR_SCRIPT, unsafe_allow_javascript=True)
