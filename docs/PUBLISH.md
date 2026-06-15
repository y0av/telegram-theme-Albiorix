# Publishing Albiorix as a `t.me/addtheme/Albiorix` cloud theme

> ℹ️ The official Albiorix cloud theme is already live at **[t.me/addtheme/Albiorix](https://t.me/addtheme/Albiorix)** — just open it to install. This guide is for **forking it under your own slug, adding pixel-perfect per-platform variants, or changing the wallpaper.**

Telegram has two ways to use a theme:

1. **A theme file** you import on one device (`.tdesktop-theme` on Desktop, `.attheme` on Android). Fast, but per-device and doesn't auto-update.
2. **A cloud theme** with a single `t.me/addtheme/<shortname>` link that installs on **iOS, Android and Desktop**, syncs across your devices, and **auto-updates for every subscriber** whenever you edit it.

This guide gets you #2. Minting the link requires *your* Telegram account (it can't be generated offline), but all the inputs are already built in this repo.

> ⚠️ Menu labels move around between Telegram versions and across the official vs. third-party clients. The *flow* below is stable even when a label is renamed — look for the nearest equivalent ("Share", "Create link", "Edit theme", "Set link").

---

## How cross-platform actually works

A cloud theme is identified by its **slug / shortname** (the bit after `t.me/addtheme/`). Under that one slug, Telegram can store a **separate theme document per platform** (Android, iOS, macOS, Desktop), because each client has its own theming engine.

- Opening `t.me/addtheme/Albiorix` on any client installs the variant for *that* platform.
- If you only ever upload one platform's variant, the link still works elsewhere — Telegram applies what it has — but for **pixel-perfect** results on each platform you add each platform's file (or colors) to the same slug.

So the goal is: **one slug (`Albiorix`), with the Android, Desktop and iOS variants all attached to it.**

---

## Step 1 — Mint the link (do this once)

The simplest reliable way to create the cloud theme and choose the slug is from the **Android** app, because `Albiorix.attheme` carries the full, detailed palette *and* the wallpaper.

1. Send [`android/Albiorix.attheme`](../android/Albiorix.attheme) to your **Saved Messages**.
2. Tap it → **Apply** to make it your current theme.
3. Go to **Settings → Chat Settings**. Your **Albiorix** theme is listed under the theme carousel/list.
4. Open its menu (tap it, or long-press → **Share** / **Create link**). The first time you share, Telegram converts it to a **cloud theme** and asks for a short name.
5. Enter **`Albiorix`**. If it's taken, pick a free alternative (see [Shortname rules](#shortname-rules)).
6. Telegram (the official service chat) sends you **`https://t.me/addtheme/Albiorix`**. 🎉

No Android device? Do the same on **Desktop**: apply [`desktop/Albiorix.tdesktop-theme`](../desktop/Albiorix.tdesktop-theme), then **Settings → Chat Settings → ⋮ → Edit theme → Save and apply**, then **Share theme** and set the short name.

---

## Step 2 — Add the other platforms to the same slug

You now have a working link. To give **Desktop** and **iOS/macOS** their own precise variants under that *same* `Albiorix` slug:

### Desktop variant
1. Open `t.me/addtheme/Albiorix` in **Telegram Desktop** and apply it.
2. **Settings → Chat Settings → ⋮ → Edit theme.** This opens the live color editor on the cloud theme.
3. Load this repo's exact Desktop palette: easiest is to apply [`desktop/Albiorix.tdesktop-theme`](../desktop/Albiorix.tdesktop-theme) first, then **Edit theme → Save and apply** so the cloud copy takes the desktop colors.
4. **Save and apply** — it pushes to the cloud under the same slug.

### iOS / macOS variant
iOS's in-app editor exposes three high-level groups (**Accent**, **Background**, **Messages**), which is enough for a faithful Albiorix:
1. Open `t.me/addtheme/Albiorix` on iOS to install the base.
2. **Settings → Appearance → tap `+` → Create New Theme** (or edit the installed one).
3. Set **Accent** = `#35d6be`, a dark **Background**, and **Messages / outgoing tint** = `#0f564e`. Pull the rest from [`palette.json`](../palette.json).
4. Set the wallpaper to [`assets/wallpaper.jpg`](../assets/wallpaper.jpg) (**Settings → Appearance → Chat Background → upload**).
5. Save — on first save Telegram messages you the link; make sure its shortname is `Albiorix` so it joins the same slug.

### Web editor (most control, all platforms in one place)
Telegram's online theme editor lets you sign in with your account, open the **Albiorix** theme, and upload a file **per platform** (`.attheme`, `.tdesktop-theme`, and the iOS variant) plus set the wallpaper, then **Save and apply**. If you have access to it, it's the cleanest way to attach every platform variant to the one slug. (Reach it from the theme's **Share/Edit** options, or the creator docs at <https://core.telegram.org/themes>.)

---

## Step 3 — Set the wallpaper as a cloud background (optional polish)

For the background to follow the theme on every platform, it helps to publish it as a Telegram background and reference its `t.me/bg/...` link:

1. **Settings → Appearance → Chat Background**, choose/upload [`assets/wallpaper.jpg`](../assets/wallpaper.jpg), apply it.
2. Open it → **Share** → copy the `t.me/bg/<id>` link.
3. In the theme editor, set the theme's **wallpaper** to that link. (Append `?mode=tiled` only if you want it tiled — Albiorix is designed to be **scaled/cover**, so leave it off.)

The Android `.attheme` already embeds the wallpaper, so Android works without this step.

---

## Shortname rules

- The shortname is the unique global slug in `t.me/addtheme/<shortname>` — two themes can't share one.
- Use letters, digits and underscores; aim for ≥ 5 characters.
- Try **`Albiorix`** first. If taken, good fallbacks: `AlbiorixDark`, `Albiorix_theme`, `AlbiorixMoon`, `Albiorix_yoav`.
- You can change the shortname later from the theme's **Edit / Set link** menu.

## Updating later

Because it's a cloud theme, editing it and choosing **Save and apply** updates it for **everyone** who installed the link — no need to re-share. To regenerate the source files after a palette change:

```bash
python3 build/build.py && python3 build/preview.py
```

then re-import the updated file in the editor and **Save and apply**.

---

*Questions or a nicer link? — [yoav.xyz](https://yoav.xyz)*
