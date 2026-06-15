# Albiorix on iOS

## 📲 Install

Open **[t.me/addtheme/Albiorix](https://t.me/addtheme/Albiorix)** on your iPhone or iPad and tap **Apply**. That's it — same cloud link as Android and Desktop, and it auto-updates.

## Why there's no `.ios` theme file here

Telegram on **iOS installs themes from a cloud link, not from a file.** Unlike Android (`.attheme`) and Telegram Desktop (`.tdesktop-theme`), iOS has no openly documented, hand-editable theme-file format you can drop into a repo and import. So the iOS edition of Albiorix is delivered the supported way — through the cloud theme at the link above.

## Build it natively (optional)

Prefer to recreate it yourself in the app? **Settings → Appearance → tap `+` → Create New Theme**, start from a dark base, and set:

| In-app setting | Value |
|---|---|
| **Accent** | `#35d6be` |
| **Background** (surfaces) | `#0c0f16` (deepest `#0a0d13`, elevated `#141a24`) |
| **Messages — outgoing tint** | `#0f564e` |
| **Wallpaper** | upload [`../assets/wallpaper.jpg`](../assets/wallpaper.jpg) |
| **Primary text** | `#e9eef5` |

The complete per-role palette is in [`../palette.json`](../palette.json).

## Pixel-perfect iOS variant

The cloud link applies on iOS today. To attach a fine-tuned iOS-specific variant to the **same** `t.me/addtheme/Albiorix` slug (so every platform is exact), follow the iOS + web-editor steps in [`../docs/PUBLISH.md`](../docs/PUBLISH.md).
