COLORS = {
    "primary": "#23395D",
    "primary_dark": "#1B2D49",
    "primary_soft": "#E8EEF8",

    "background": "#F4F7FB",
    "surface": "#FFFFFF",
    "card": "#FFFFFF",
    "card_muted": "#F8FAFC",

    "text": "#172033",
    "text_secondary": "#64748B",
    "text_muted": "#94A3B8",

    "border": "#E2E8F0",
    "border_strong": "#CBD5E1",

    "low": "#D9ECFF",
    "medium": "#5DA7D8",
    "high": "#1F5F99",

    "shadow": "0 12px 30px rgba(15, 23, 42, 0.08)",
    "shadow_soft": "0 6px 18px rgba(15, 23, 42, 0.06)",
}

CARD_STYLE = {
    "backgroundColor": COLORS["surface"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "18px",
    "boxShadow": COLORS["shadow_soft"],
}

PANEL_STYLE = {
    **CARD_STYLE,
    "minHeight": 0,
    "overflow": "hidden",
}
