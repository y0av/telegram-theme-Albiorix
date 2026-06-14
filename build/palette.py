"""
Albiorix — master colour palette (single source of truth).

Albiorix is an irregular moon of Saturn, named after a Gaulish war-god.
The theme is a deep-space dark theme: a cool indigo-charcoal base (never pure
black), one confident aurora-teal accent, and a teal-tinted outgoing bubble.
Bright teal is used only for accents that sit on dark surfaces (text, icons,
links, outlines); filled accent areas that carry light text use a deeper teal so
contrast stays within WCAG AA.

All values are 6-digit lowercase hex (no leading '#'). Alpha, where needed, is
applied per-platform in build.py.
"""

PALETTE = {
    # ── Deep-space surfaces (dark, cool, never pure black) ────────────────
    "bgDeep":      "0a0d13",  # deepest base (status bar / behind everything)
    "bg":          "0c0f16",  # app background — chat list, settings, screens
    "bgOver":      "12161f",  # base with pointer hover
    "bgRipple":    "171c27",  # ripple / pressed on base
    "surface":     "141a24",  # elevated surface — action bar, search, sections
    "surface2":    "1b2230",  # higher elevation — menus, dialogs, sheets
    "border":      "232c3a",  # hairlines, dividers, outlines

    # ── Message bubbles ───────────────────────────────────────────────────
    "inBubble":    "161d28",  # incoming bubble (cool elevated)
    "inBubbleSel": "1d2738",  # incoming, selected
    "outBubble":   "0f564e",  # outgoing bubble (deep aurora teal)
    "outBubbleGrad":"15695d", # outgoing bubble subtle gradient stop (Android)
    "outBubbleSel":"18675d",  # outgoing, selected
    "serviceBg":   "0f1620",  # service-message pill (alpha applied per platform)

    # ── Text ──────────────────────────────────────────────────────────────
    "text":        "e9eef5",  # primary text (cool off-white, not pure white)
    "textSub":     "8a99ae",  # secondary text, subtitles, timestamps
    "textDim":     "5c6776",  # disabled / hints / placeholders
    "onAccent":    "ffffff",  # text/icon on filled accent (deep teal -> white ok)

    # ── Accent (aurora teal) ──────────────────────────────────────────────
    "accent":      "35d6be",  # bright teal — links/icons/online/outline on dark
    "accentText":  "4fe3cd",  # brighter teal for in-bubble links
    "accentFill":  "0c8071",  # deep teal fill — buttons, send, active areas (AA)
    "accentFillOver":"0f9282",# fill hover
    "accentFillRipple":"12a392",# fill ripple
    "accentDeep":  "103f3a",  # deep teal — selected chat row, pressed accent
    "accentDim":   "1c5048",  # muted teal — selected incoming bubble overlay

    # ── Functional / semantic (kept hued, tuned for dark) ─────────────────
    "red":         "ff5c5c",  # destructive / errors
    "redDim":      "e0484c",  # pressed destructive
    "green":       "4fc97a",  # success / calls answered / verified
    "gold":        "e6b873",  # Saturn-ring micro-accent: stars, premium, pinned
    "orange":      "e8a85f",  # warnings / some file types

    # ── Avatar / accent palette spread (placeholder avatars, folders) ─────
    # cohesive cool/jewel set so default avatars don't clash with the theme
    "av1":         "35d6be",  # teal
    "av2":         "5aa7ff",  # azure
    "av3":         "9d8cff",  # violet
    "av4":         "e6b873",  # gold
    "av5":         "ff7a9c",  # rose
    "av6":         "4fc97a",  # green
    "av7":         "f08a5d",  # coral
}


def hx(token):
    """Return the 6-digit hex for a palette token (or pass through a literal)."""
    return PALETTE.get(token, token)
