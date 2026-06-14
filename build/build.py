#!/usr/bin/env python3
"""
Albiorix theme builder.

Generates, from one master palette (palette.py):

  desktop/colors.tdesktop-theme      recoloured Telegram-Desktop palette (text)
  desktop/Albiorix.tdesktop-theme    zip: colors.tdesktop-theme + background.jpg
  android/Albiorix.attheme           complete dark theme + embedded wallpaper
  assets/wallpaper.jpg               JPEG chat background (from assets/wallpaper.png)
  palette.json                       machine-readable palette

Desktop strategy: take Telegram's official dark base palette and remap its
structural colours (blue-grey surfaces -> deep-space indigo; Telegram blue ->
aurora teal; outgoing bubble -> teal) so all ~470 keys stay present and coherent.

Android strategy: start from Telegram's *default* (light) colour table and apply
a light->dark transform (neutral lightness inversion + blue->teal accent remap),
then layer precise brand overrides on top. Result covers every one of the ~770
keys, so no surface is left light.

Run:  python3 build/build.py
"""

import json, os, re, struct, sys, zipfile, colorsys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import PALETTE, hx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
BASE = os.path.join(BUILD, "base")


# ───────────────────────── colour helpers ──────────────────────────────────
def parse6(h):
    h = h.lstrip("#").lower()
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def parse8(h):
    """aarrggbb -> (a,r,g,b)"""
    h = h.lstrip("#").lower()
    if len(h) == 6:
        h = "ff" + h
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16)

def hex6(r, g, b):
    return f"{r:02x}{g:02x}{b:02x}"

def lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def luminance(r, g, b):
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def contrast(rgb1, rgb2):
    l1, l2 = luminance(*rgb1), luminance(*rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)

def rgb_to_hls(r, g, b):
    return colorsys.rgb_to_hls(r / 255, g / 255, b / 255)  # (h, l, s)

def hls_to_rgb(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return round(r * 255), round(g * 255), round(b * 255)


# ───────────────────────── DESKTOP ─────────────────────────────────────────
# Map Telegram-night structural hexes -> Albiorix tokens. Alpha on a source
# value is preserved (handled per-line). Anything not listed (whites, reds,
# greens, golds, neutral greys, shadows) is intentionally kept.
DESKTOP_SUBST = {
    # surfaces (blue-grey -> deep-space indigo)
    "17212b": "bg",          # windowBg, compose area, main background
    "16222d": "bgDeep",
    "232e3c": "bgOver",      # background with hover
    "24303d": "bgRipple",    # ripple
    "242f3d": "surface",     # sections / custom title / elevated
    "25303e": "surface",
    "24292e": "inBubble",    # incoming bubble
    "1e2429": "serviceBg",   # service-message base (keeps alpha)
    "2b5278": "accentDeep",  # selected chat row in the list
    # accent fills (Telegram blue -> deep teal, carry light text)
    "5288c1": "accentFill",        # windowBgActive
    "2f6ea5": "accentFill",        # activeButtonBg
    "3476ab": "accentFillOver",    # activeButtonBgOver
    "3b7cb1": "accentFillRipple",  # activeButtonBgRipple
    "4082bc": "accentFill",        # dialogsUnreadBg
    "2a6da1": "accentFillOver",
    "035e90": "accentDeep",
    "3f96d0": "accentFillRipple",  # inbox file download circle
    # accent text / links / online (blue -> bright teal)
    "6ab3f3": "accent",      # windowActiveTextFg / online
    "429bdb": "accent",      # inbox reply bar
    "70baf5": "accentText",  # inbox link
    "73b9f5": "accentText",
    "72bcfd": "accentText",
    "5eb5f7": "accent",
    # outgoing bubble + its selected state
    "265e8c": "outBubble",
    "387aad": "outBubbleSel",
    "2e70a5": "accentDim",   # inbox selected bubble
    # light-blue outbox time text -> light teal
    "c2e4ff": "cfeae3",
    "bad9f6": "cfeae3",
}

def build_desktop(background_jpg):
    src = open(os.path.join(BASE, "night-base.colors.tdesktop-theme"),
               encoding="utf-8").read()
    out_lines, remapped, unmapped_blue = [], 0, set()
    line_re = re.compile(r"^(\s*[A-Za-z0-9_]+\s*:\s*)#([0-9a-fA-F]{3,8})(\s*;.*)$")
    for line in src.splitlines():
        m = line_re.match(line)
        if not m:
            out_lines.append(line)
            continue
        head, val, tail = m.groups()
        v = val.lower()
        if len(v) == 3:                       # expand shorthand
            v = "".join(c * 2 for c in v)
        rgb, alpha = v[:6], v[6:]
        if rgb in DESKTOP_SUBST:               # precise structural override
            rgb = hx(DESKTOP_SUBST[rgb])
            remapped += 1
        else:
            r, g, b = parse6(rgb)
            h, l, s = rgb_to_hls(r, g, b)
            if s > 0.20 and 0.50 <= h <= 0.70 and 0.10 < l < 0.95:
                # stray Telegram blue: bright/saturated -> aurora teal accent,
                # darker/muted blue-grey -> cool indigo surface/border.
                if l >= 0.45 and s >= 0.30:
                    rgb = hex6(*to_teal_keepL(r, g, b))
                else:
                    rgb = hex6(*hls_to_rgb(0.61, l, min(s, 0.14)))
                remapped += 1
                unmapped_blue.add(v[:6])
        out_lines.append(f"{head}#{rgb}{alpha}{tail}")

    header = (
        "// Albiorix — a deep-space dark theme for Telegram Desktop\n"
        "// Aurora teal on Saturnian indigo.  https://yoav.xyz\n"
        "// Generated from Telegram's night base by build/build.py — edit the\n"
        "// master palette in build/palette.py, not this file.\n\n"
    )
    palette_text = header + "\n".join(out_lines) + "\n"
    with open(os.path.join(ROOT, "desktop", "colors.tdesktop-theme"), "w",
              encoding="utf-8") as f:
        f.write(palette_text)

    # deterministic zip: fixed timestamps + attrs so rebuilds are byte-identical
    theme_path = os.path.join(ROOT, "desktop", "Albiorix.tdesktop-theme")
    fixed_date = (2026, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(theme_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in (("colors.tdesktop-theme", palette_text.encode("utf-8")),
                           ("background.jpg", open(background_jpg, "rb").read())):
            zi = zipfile.ZipInfo(name, date_time=fixed_date)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, data)

    print(f"  desktop: remapped {remapped} colour occurrences "
          f"({len(unmapped_blue)} blues auto-tealed), {len(out_lines)} lines")
    return theme_path


# ───────────────────────── ANDROID ─────────────────────────────────────────
ACCENT_RGB = parse6(hx("accent"))
TEAL_H = rgb_to_hls(*ACCENT_RGB)[0]   # hue of our aurora teal
COOL_H = 0.61                          # indigo hue for tinted neutrals

# Role of a key, decided by name, to pick the light<->dark direction.
FG_RE = re.compile(
    r"(text|title|name|hint|icon|link|fg|message|subtitle|caption|"
    r"placeholder|cursor|value|check|arrow|drawable|search$)", re.I)
BG_RE = re.compile(
    r"(background|bubble|panel|listview|view|field|cell|row|sheet|menu|"
    r"tabbar|gradient|overlay|selector|fill|track|circle|emptyview|"
    r"container|counter|badge)", re.I)

def chroma(r, g, b):
    return (max(r, g, b) - min(r, g, b)) / 255.0

def to_teal_keepL(r, g, b):
    """Recolour a (blue) accent to teal, preserving perceived lightness."""
    h, l, s = rgb_to_hls(r, g, b)
    s = min(max(s, 0.45), 0.78)
    return hls_to_rgb(TEAL_H, l, s)

def neutral_to_dark(name, r, g, b):
    """Neutral light->dark, direction chosen by the key's role."""
    h, l, s = rgb_to_hls(r, g, b)
    is_fg, is_bg = bool(FG_RE.search(name)), bool(BG_RE.search(name))
    if is_fg and not is_bg:                 # foreground -> light, cool off-white
        nl = 0.60 + (1.0 - l) * 0.32        #   darker source = brighter text
        return hls_to_rgb(COOL_H, min(nl, 0.95), 0.06)
    if is_bg and not is_fg:                  # surface -> dark indigo
        nl = 0.05 + l * 0.12                 #   lighter source = slightly raised
        return hls_to_rgb(COOL_H, nl, 0.15 * (1 - nl / 0.17))
    # ambiguous: invert around mid by source lightness
    nl = 0.045 + (1.0 - l) * 0.885
    tint = 0.06 if nl > 0.55 else 0.13 * (1 - min(nl, 0.13) / 0.13 + 0.2)
    return hls_to_rgb(COOL_H, nl, max(0.04, tint))

def transform(name, a, r, g, b):
    """Light default colour -> Albiorix dark colour (rgb only; alpha kept)."""
    if a == 0:                                    # fully transparent: keep
        return r, g, b
    if "shadow" in name.lower():                  # shadows stay dark
        return parse6(hx("bgDeep"))
    h, l, s = rgb_to_hls(r, g, b)
    ch = chroma(r, g, b)
    if ch > 0.12 and 0.50 <= h <= 0.70 and 0.18 < l < 0.95:
        return to_teal_keepL(r, g, b)             # Telegram blue -> aurora teal
    if ch < 0.12:                                 # neutral / grey
        return neutral_to_dark(name, r, g, b)
    return r, g, b                                # strong hue (red/green/gold)

# Precise brand overrides. Value = palette token, ('token'|'hex6', alpha), or hex6.
A = "accent"; AF = "accentFill"; AFO = "accentFillOver"; AFR = "accentFillRipple"
ANDROID_OVERRIDES = {
    # ---- surfaces / elevation ----
    "windowBackgroundWhite": "surface",
    "windowBackgroundGray": "bg",
    "windowBackgroundGrayShadow": ("000000", 0x40),
    "windowBackgroundWhiteBlackText": "text",
    "windowBackgroundWhiteGrayText": "textSub",
    "windowBackgroundWhiteGrayText2": "textSub",
    "windowBackgroundWhiteGrayText3": "textSub",
    "windowBackgroundWhiteGrayText4": "textSub",
    "windowBackgroundWhiteGrayText5": "textSub",
    "windowBackgroundWhiteGrayText6": "textSub",
    "windowBackgroundWhiteGrayText7": "textSub",
    "windowBackgroundWhiteGrayText8": "textSub",
    "windowBackgroundWhiteHintText": "textDim",
    "windowBackgroundWhiteValueText": A,
    "windowBackgroundWhiteLinkText": A,
    "windowBackgroundWhiteLinkSelection": (A, 0x33),
    "windowBackgroundWhiteBlueText": A,
    "windowBackgroundWhiteBlueText2": A,
    "windowBackgroundWhiteBlueText3": A,
    "windowBackgroundWhiteBlueText4": A,
    "windowBackgroundWhiteBlueText5": A,
    "windowBackgroundWhiteBlueText6": A,
    "windowBackgroundWhiteBlueText7": A,
    "windowBackgroundWhiteBlueHeader": A,
    "windowBackgroundWhiteBlueButton": A,
    "windowBackgroundWhiteBlueIcon": A,
    "text_RedRegular": "red",
    "text_RedBold": "red",
    "windowBackgroundWhiteGreenText": "green",
    "windowBackgroundWhiteGreenText2": "green",
    "windowBackgroundWhiteInputField": "border",
    "windowBackgroundWhiteInputFieldActivated": A,
    "windowBackgroundChecked": ("accentDeep", None),
    "windowBackgroundCheckText": "onAccent",
    "windowBackgroundUnchecked": "surface2",
    "switchTrack": "border",
    "switchTrackChecked": AF,
    "switchTrackBlue": "border",
    "switchTrackBlueChecked": AF,
    "switch2Track": "border",
    "switch2TrackChecked": AF,
    "switchTrackBlueThumb": "text",
    "switchTrackBlueThumbChecked": "onAccent",
    "divider": "border",
    "listSelector": ("ffffff", 0x14),
    "graySection": "bgDeep",
    "graySectionText": "textSub",
    "fastScrollActive": A,
    "fastScrollInactive": "border",
    "fastScrollText": "onAccent",

    # ---- action bar ----
    "actionBarDefault": "surface",
    "actionBarDefaultIcon": "text",
    "actionBarDefaultTitle": "text",
    "actionBarDefaultSubtitle": "textSub",
    "actionBarDefaultSelector": "bgRipple",
    "actionBarWhiteSelector": "bgRipple",
    "actionBarDefaultSearch": "text",
    "actionBarDefaultSearchPlaceholder": "textDim",
    "actionBarDefaultSubmenuItem": "text",
    "actionBarDefaultSubmenuItemIcon": "textSub",
    "actionBarDefaultSubmenuBackground": "surface2",
    "actionBarDefaultSubmenuSeparator": "border",
    "actionBarActionModeDefault": "surface",
    "actionBarActionModeDefaultIcon": "text",
    "actionBarActionModeDefaultTop": ("000000", 0x40),
    "actionBarActionModeDefaultSelector": "bgRipple",
    "actionBarTabActiveText": A,
    "actionBarTabUnactiveText": "textSub",
    "actionBarTabLine": A,
    "actionBarTabSelector": "bgRipple",
    "actionBarDefaultArchived": "surface",
    "actionBarDefaultArchivedIcon": "text",
    "actionBarDefaultArchivedTitle": "text",
    "actionBarDefaultArchivedSelector": "bgRipple",
    "actionBarDefaultArchivedSearch": "text",
    "actionBarDefaultArchivedSearchPlaceholder": "textDim",

    # ---- chat list ----
    "chats_name": "text",
    "chats_secretName": A,
    "chats_secretIcon": A,
    "chats_message": "textSub",
    "chats_message_threeLines": "textSub",
    "chats_nameMessage": "text",
    "chats_nameMessage_threeLines": "text",
    "chats_draft": "red",
    "chats_date": "textDim",
    "chats_pinnedIcon": "textSub",
    "chats_pinnedOverlay": ("surface2", 0xff),
    "chats_unreadCounter": AF,
    "chats_unreadCounterText": "onAccent",
    "chats_unreadCounterMuted": "41505f",
    "chats_sentCheck": A,
    "chats_sentReadCheck": A,
    "chats_sentClock": "textDim",
    "chats_sentError": "red",
    "chats_sentErrorIcon": "onAccent",
    "chats_attachMessage": A,
    "chats_actionBackground": AF,
    "chats_actionPressedBackground": AFO,
    "chats_actionIcon": "onAccent",
    "chats_actionMessage": A,
    "chats_menuBackground": "surface2",
    "chats_menuTopBackground": "accentDeep",
    "chats_menuItemText": "text",
    "chats_menuItemIcon": "textSub",
    "chats_menuName": "text",
    "chats_menuPhone": "textSub",
    "chats_menuPhoneCats": A,
    "chats_archiveBackground": AF,
    "chats_archivePinBackground": "surface2",
    "chats_archiveIcon": "onAccent",
    "chats_archiveText": "onAccent",
    "chats_archivePullDownBackground": "surface2",
    "chats_archivePullDownBackgroundActive": AF,
    "chats_onlineCircle": A,
    "chats_verifiedBackground": A,
    "chats_verifiedCheck": "bg",
    "chats_tabletSelectedOverlay": (A, 0x14),

    # ---- chat: incoming bubble ----
    "chat_inBubble": "inBubble",
    "chat_inBubbleSelected": "inBubbleSel",
    "chat_inBubbleShadow": ("000000", 0x33),
    "chat_inBubbleSelectedOverlay": (A, 0x12),
    "chat_messageTextIn": "text",
    "chat_inTimeText": "textSub",
    "chat_inTimeSelectedText": "text",
    "chat_inReplyLine": A,
    "chat_inReplyNameText": A,
    "chat_inReplyMessageText": "text",
    "chat_inReplyMediaMessageText": "textSub",
    "chat_inReplyMediaMessageSelectedText": "text",
    "chat_inForwardedNameText": A,
    "chat_inViaBotNameText": A,
    "chat_inInstant": A,
    "chat_inInstantSelected": "accentText",
    "chat_messageLinkIn": A,
    "chat_inLoader": AF,
    "chat_inLoaderSelected": AFO,
    "chat_inMediaIcon": "inBubble",
    "chat_inFileBackground": "surface2",
    "chat_inFileNameText": A,
    "chat_inFileInfoText": "textSub",
    "chat_inFileProgress": "surface2",
    "chat_inAudioProgress": "inBubble",
    "chat_inAudioSeekbar": "border",
    "chat_inAudioSeekbarFill": A,
    "chat_inAudioSeekbarSelected": A,
    "chat_inAudioTitleText": "text",
    "chat_inAudioPerformerText": "textSub",
    "chat_inAudioDurationText": "textSub",
    "chat_inContactNameText": A,
    "chat_inContactPhoneText": "text",
    "chat_inContactBackground": A,
    "chat_inContactIcon": "inBubble",
    "chat_inPreviewLine": A,
    "chat_inSiteNameText": A,
    "chat_inVenueInfoText": "textSub",
    "chat_inSentClock": "textSub",
    "chat_inViews": "textSub",
    "chat_inMenu": "textSub",
    "chat_inPsaNameText": "green",

    # ---- chat: outgoing bubble (aurora teal) ----
    "chat_outBubble": "outBubble",
    "chat_outBubbleGradient1": "outBubbleGrad",
    "chat_outBubbleGradient2": "outBubbleGrad",
    "chat_outBubbleGradient3": "outBubble",
    "chat_outBubbleGradientAnimated": ("000000", 0x00),
    "chat_outBubbleGradientSelectedOverlay": ("ffffff", 0x14),
    "chat_outBubbleSelected": "outBubbleSel",
    "chat_outBubbleShadow": ("000000", 0x33),
    "chat_outBubbleSelectedOverlay": ("ffffff", 0x12),
    "chat_messageTextOut": "text",
    "chat_outTimeText": "b9ddd5",
    "chat_outTimeSelectedText": "text",
    "chat_outSentClock": "cfeae3",
    "chat_outSentCheck": "cfeae3",
    "chat_outSentCheckSelected": "ffffff",
    "chat_outSentCheckRead": "cfeae3",
    "chat_outSentCheckReadSelected": "ffffff",
    "chat_outReplyLine": "cfeae3",
    "chat_outReplyNameText": "cfeae3",
    "chat_outReplyMessageText": "text",
    "chat_outReplyMediaMessageText": "cfeae3",
    "chat_outReplyMediaMessageSelectedText": "ffffff",
    "chat_outForwardedNameText": "cfeae3",
    "chat_outViaBotNameText": "cfeae3",
    "chat_outInstant": "ffffff",
    "chat_outInstantSelected": "ffffff",
    "chat_messageLinkOut": "cfeae3",
    "chat_outLoader": ("ffffff", 0xff),
    "chat_outLoaderSelected": "cfeae3",
    "chat_outMediaIcon": "outBubble",
    "chat_outFileBackground": ("ffffff", 0x1f),
    "chat_outFileNameText": "ffffff",
    "chat_outFileInfoText": "cfeae3",
    "chat_outFileProgress": "outBubble",
    "chat_outAudioProgress": "outBubble",
    "chat_outAudioSeekbar": ("ffffff", 0x33),
    "chat_outAudioSeekbarFill": "ffffff",
    "chat_outAudioSeekbarSelected": "ffffff",
    "chat_outAudioTitleText": "ffffff",
    "chat_outAudioPerformerText": "cfeae3",
    "chat_outAudioDurationText": "cfeae3",
    "chat_outContactNameText": "ffffff",
    "chat_outContactPhoneText": "cfeae3",
    "chat_outContactBackground": "ffffff",
    "chat_outContactIcon": "outBubble",
    "chat_outPreviewLine": "cfeae3",
    "chat_outSiteNameText": "ffffff",
    "chat_outVenueInfoText": "cfeae3",
    "chat_outViews": "cfeae3",
    "chat_outMenu": "cfeae3",
    "chat_outPsaNameText": "cfeae3",

    # ---- chat: service / general ----
    "chat_serviceText": "text",
    "chat_serviceLink": A,
    "chat_serviceIcon": "text",
    "chat_serviceBackground": ("serviceBg", 0xcc),
    "chat_serviceBackgroundSelected": ("serviceBg", 0xe6),
    "chat_linkSelectBackground": (A, 0x33),
    "chat_wallpaper": "bg",
    "chat_wallpaper_gradient_to1": "bgDeep",
    "chat_wallpaper_gradient_to2": "accentDeep",
    "chat_wallpaper_gradient_to3": "bg",
    "chat_mediaTimeBackground": ("000000", 0x66),
    "chat_mediaTimeText": "text",
    "chat_selectedBackground": (A, 0x16),
    "chat_emojiPanelBackground": "surface",
    "chat_emojiSearchBackground": "bgDeep",
    "chat_emojiPanelIcon": "textSub",
    "chat_emojiPanelIconSelected": A,
    "chat_emojiPanelStickerPackSelector": "bgRipple",
    "chat_emojiPanelShadowLine": "border",
    "chat_emojiBottomPanelIcon": "textSub",
    "chat_goDownButton": "surface2",
    "chat_goDownButtonCounter": "onAccent",
    "chat_goDownButtonCounterBackground": AF,
    "chat_messagePanelCancelInlineBot": "textSub",
    "chat_topPanelBackground": "surface",
    "chat_topPanelTitle": A,
    "chat_topPanelMessage": "textSub",
    "chat_topPanelLine": A,
    "chat_addContact": A,
    "chat_replyPanelIcons": A,
    "chat_replyPanelClose": "textSub",
    "chat_replyPanelName": A,
    "chat_replyPanelLine": "border",
    "chat_searchPanelIcons": A,
    "chat_searchPanelText": A,
    "chat_secretTimeText": "textSub",
    "chat_stickerNameText": "ffffff",
    "chat_stickerReplyLine": "ffffff",
    "chat_stickerReplyNameText": "ffffff",
    "chat_stickerReplyMessageText": "ffffff",

    # ---- input panel ----
    "chat_messagePanelBackground": "surface",
    "chat_messagePanelShadow": ("000000", 0x40),
    "chat_messagePanelText": "text",
    "chat_messagePanelHint": "textDim",
    "chat_messagePanelCursor": A,
    "chat_messagePanelIcons": "textSub",
    "chat_messagePanelSend": A,
    "chat_messagePanelVoicePressed": "onAccent",
    "chat_messagePanelVoiceBackground": AF,
    "chat_messagePanelVoiceDelete": "textSub",
    "chat_messagePanelVoiceDuration": "textSub",
    "chat_recordedVoiceBackground": AF,
    "chat_recordedVoiceProgress": ("ffffff", 0x66),
    "chat_recordedVoiceProgressInner": "onAccent",
    "chat_recordedVoiceDot": "red",
    "chat_recordVoiceCancel": A,
    "chat_fieldOverlayText": A,
    "chat_gifSaveHintText": "text",
    "chat_gifSaveHintBackground": ("serviceBg", 0xe6),

    # ---- dialogs / sheets ----
    "dialogBackground": "surface2",
    "dialogBackgroundGray": "bg",
    "dialogTextBlack": "text",
    "dialogTextLink": A,
    "dialogLinkSelection": (A, 0x33),
    "dialogTextBlue": A,
    "dialogTextBlue2": A,
    "dialogTextBlue4": A,
    "dialogTextGray": "textSub",
    "dialogTextGray2": "textSub",
    "dialogTextGray3": "textSub",
    "dialogTextGray4": "textSub",
    "dialogTextHint": "textDim",
    "dialogIcon": "textSub",
    "dialogInputField": "border",
    "dialogInputFieldActivated": A,
    "dialogCheckboxSquareBackground": AF,
    "dialogCheckboxSquareCheck": "onAccent",
    "dialogCheckboxSquareUnchecked": "textDim",
    "dialogRadioBackground": "textDim",
    "dialogRadioBackgroundChecked": AF,
    "dialogButton": A,
    "dialogButtonSelector": "bgRipple",
    "dialogScrollGlow": "surface",
    "dialogRoundCheckBox": AF,
    "dialogRoundCheckBoxCheck": "onAccent",
    "dialogShadowLine": "border",
    "dialogFloatingButton": AF,
    "dialogFloatingButtonPressed": AFO,
    "dialogFloatingIcon": "onAccent",
    "dialogGrayLine": "border",
    "sheet_scrollUp": "border",
    "sheet_other": "textSub",

    # ---- checkboxes / radios (global) ----
    "checkbox": "surface2",
    "checkboxCheck": "onAccent",
    "checkboxSquareBackground": AF,
    "checkboxSquareCheck": "onAccent",
    "checkboxSquareUnchecked": "textDim",
    "checkboxSquareDisabled": "border",
    "radioBackground": "textDim",
    "radioBackgroundChecked": AF,

    # ---- buttons / featured ----
    "featuredStickers_addButton": AF,
    "featuredStickers_addButtonPressed": AFO,
    "featuredStickers_buttonText": "onAccent",
    "featuredStickers_addedIcon": A,
    "featuredStickers_buttonProgress": "onAccent",
    "featuredStickers_unread": A,
    "contacts_inviteBackground": AF,
    "contacts_inviteText": "onAccent",
    "changephoneinfo_image2": A,

    # ---- profile ----
    "profile_title": "text",
    "profile_actionIcon": "text",
    "profile_actionBackground": "surface2",
    "profile_actionPressedBackground": "bgRipple",
    "profile_verifiedBackground": A,
    "profile_verifiedCheck": "bg",
    "profile_creatorIcon": A,
    "profile_status": "accentText",
    "profile_tabText": "textSub",
    "profile_tabSelectedText": A,
    "profile_tabSelectedLine": A,
    "profile_tabSelector": "bgRipple",

    # ---- avatar ----
    "avatar_text": "onAccent",
    "avatar_backgroundActionBarBlue": "surface",
    "avatar_actionBarSelectorBlue": "bgRipple",
    "avatar_actionBarIconBlue": "text",
    "avatar_subtitleInProfileBlue": "textSub",
    "avatar_backgroundSaved": AF,
    "avatar_background2Saved": AFO,
    "avatar_backgroundArchived": "surface2",
    "avatar_backgroundArchivedHidden": "bg",
    "avatar_backgroundBlue": "av2",
    "avatar_background2Blue": "5288c1",
    "avatar_backgroundCyan": "av1",
    "avatar_background2Cyan": "0f9282",
    "avatar_backgroundGreen": "av6",
    "avatar_background2Green": "3aa861",
    "avatar_backgroundOrange": "av7",
    "avatar_background2Orange": "d06a3a",
    "avatar_backgroundPink": "av5",
    "avatar_background2Pink": "e0486f",
    "avatar_backgroundRed": "ff5c5c",
    "avatar_background2Red": "d6444a",
    "avatar_backgroundViolet": "av3",
    "avatar_background2Violet": "7a67e0",

    # ---- misc widgets ----
    "undo_background": ("surface2", 0xf2),
    "undo_cancelColor": A,
    "undo_infoColor": "text",
    "player_actionBarItems": "text",
    "player_actionBarTitle": "text",
    "player_actionBarSubtitle": "textSub",
    "player_actionBarSelector": "bgRipple",
    "player_background": "surface",
    "player_button": "text",
    "player_buttonActive": A,
    "player_progress": A,
    "player_progressBackground": "border",
    "player_time": "textSub",
    "progressCircle": A,
    "contextProgressInner1": "border",
    "contextProgressOuter1": A,
    "calls_callReceivedGreenIcon": "green",
    "calls_callReceivedRedIcon": "red",
    "premiumGradient1": A,
    "premiumGradient2": "av2",
    "premiumGradient3": "av3",
    "premiumGradient4": "av5",
    "premiumCoinGradient1": "gold",
    "premiumCoinGradient2": "orange",

    # ---- audit polish: reactions, code blocks, selected media, misc ----
    "chat_inReactionButtonBackground": (A, 0x22),
    "chat_inReactionButtonText": A,
    "chat_inReactionButtonTextSelected": "onAccent",
    "chat_outReactionButtonBackground": ("ffffff", 0x1f),
    "chat_outReactionButtonText": "cfeae3",
    "chat_outReactionButtonTextSelected": "outBubble",
    "chat_inCodeBackground": ("000000", 0x33),
    "chat_outCodeBackground": ("000000", 0x2b),
    "chat_inFileBackgroundSelected": AFO,
    "chat_outFileBackgroundSelected": ("ffffff", 0x33),
    "player_progressCachedBackground": ("ffffff", 0x1f),
    "passport_authorizeBackground": AF,
    "passport_authorizeBackgroundSelected": AFO,
    "passport_authorizeText": "onAccent",
    "dialogTopBackground": "accentDeep",
    "chat_recordedVoiceDarkerBackground": ("ffffff", 0x1f),
}

def resolve(value):
    """Override value -> (r,g,b,a)."""
    alpha = None
    if isinstance(value, tuple):
        value, alpha = value
    rgb6 = hx(value)
    r, g, b = parse6(rgb6)
    a = 0xff if alpha is None else alpha
    return r, g, b, a

def signed_argb(a, r, g, b):
    v = (a << 24) | (r << 16) | (g << 8) | b
    return v - (1 << 32) if v >= (1 << 31) else v

def build_android(wallpaper_jpeg_bytes):
    defaults = json.load(open(os.path.join(BASE, "android_default_colors.json")))
    colors = {}                                   # name -> (r,g,b,a)

    for name, hex8 in defaults.items():
        if name == "wallpaperFileOffset":
            continue
        a, r, g, b = parse8(hex8)
        nr, ng, nb = transform(name, a, r, g, b)
        colors[name] = (nr, ng, nb, a)

    # warn about any override key Telegram won't recognise (it would be ignored).
    # Validate against the full key table (ThemeColors.java), not just the
    # literal defaults, since many valid keys are assigned non-literally.
    keylist = os.path.join(BASE, "android_keys.txt")
    valid = set(open(keylist).read().split()) if os.path.exists(keylist) else set(defaults)
    valid |= {"wallpaperFileOffset"}
    unknown = [k for k in ANDROID_OVERRIDES if k not in valid]
    if unknown:
        print(f"  ! {len(unknown)} override keys not in the base key table "
              f"(check spelling): {', '.join(unknown)}")

    overridden = 0
    for name, value in ANDROID_OVERRIDES.items():
        r, g, b, a = resolve(value)
        colors[name] = (r, g, b, a)
        overridden += 1

    lines = [
        "// Albiorix — a deep-space dark theme for Telegram (Android).",
        "// Aurora teal on Saturnian indigo.  https://yoav.xyz",
    ]
    for name in sorted(colors):
        r, g, b, a = colors[name]
        lines.append(f"{name}={signed_argb(a, r, g, b)}")
    text = "\n".join(lines) + "\n"

    out = os.path.join(ROOT, "android", "Albiorix.attheme")
    with open(out, "wb") as f:
        f.write(text.encode("utf-8"))
        f.write(b"WPS\n")
        f.write(wallpaper_jpeg_bytes)
        f.write(b"\nWPE\n")
    print(f"  android: {len(colors)} keys "
          f"({overridden} brand overrides, {len(colors)-overridden} transformed), "
          f"+{len(wallpaper_jpeg_bytes)//1024} KB wallpaper")
    return out


# ───────────────────────── wallpaper / assets ──────────────────────────────
def make_wallpapers():
    from PIL import Image
    src = os.path.join(ROOT, "assets", "wallpaper.png")
    img = Image.open(src).convert("RGB")

    # desktop background (square, covers any aspect): high quality
    desk = img.resize((1280, 1280), Image.LANCZOS)
    desk_jpg = os.path.join(ROOT, "assets", "wallpaper.jpg")
    desk.save(desk_jpg, "JPEG", quality=90, optimize=True)

    # android embed: portrait crop centred (keeps the aurora), modest size
    w, h = img.size
    target_ratio = 1080 / 2160
    crop_w = int(h * target_ratio)
    left = (w - crop_w) // 2
    port = img.crop((left, 0, left + crop_w, h)).resize((1080, 2160), Image.LANCZOS)
    import io
    buf = io.BytesIO()
    port.save(buf, "JPEG", quality=87, optimize=True)
    return desk_jpg, buf.getvalue()


# ───────────────────────── contrast report ─────────────────────────────────
def contrast_report():
    pairs = [
        ("primary text / bg", "text", "bg"),
        ("primary text / surface", "text", "surface"),
        ("secondary text / bg", "textSub", "bg"),
        ("text / inBubble", "text", "inBubble"),
        ("text / outBubble", "text", "outBubble"),
        ("onAccent / accentFill (buttons)", "onAccent", "accentFill"),
        ("accent link / bg", "accent", "bg"),
        ("accent link / inBubble", "accent", "inBubble"),
        ("accentText link / outBubble", "cfeae3", "outBubble"),
        ("outTime / outBubble", "b9ddd5", "outBubble"),
        ("unread text / unread badge", "onAccent", "accentFill"),
    ]
    print("  contrast (WCAG AA: body>=4.5, large/UI>=3.0):")
    worst = 99
    for label, fg, bgk in pairs:
        c = contrast(parse6(hx(fg)), parse6(hx(bgk)))
        flag = "ok " if c >= 4.5 else ("AA-large" if c >= 3.0 else "LOW!")
        worst = min(worst, c)
        print(f"    {c:4.1f}:1  {flag:8}  {label}")
    return worst


# ───────────────────────── main ────────────────────────────────────────────
def main():
    for d in ("desktop", "android", "assets"):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    print("Albiorix build")
    contrast_report()
    desk_jpg, port_bytes = make_wallpapers()
    build_desktop(desk_jpg)
    build_android(port_bytes)
    json.dump({k: "#" + v for k, v in PALETTE.items()},
              open(os.path.join(ROOT, "palette.json"), "w"), indent=2)
    print("  wrote palette.json")
    print("done.")

if __name__ == "__main__":
    main()
