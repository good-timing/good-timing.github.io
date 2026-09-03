# Baton Website Editing Guide

## Overview

Static site, no build system, no npm, no framework. Each page is one self-contained file:

- **`index.html`**: the front door (HTML + CSS + JS, all inline)
- **`docs.html`**: the docs page, same self-contained pattern
- **`privacy.html`** / **`terms.html`** / **`cookies.html`**: legal pages
- **`404.html`**: redirects to `/`
- **`baton-icon.svg`**: favicon, emerald rounded square with diagonal baton
- **`support-teams.html`**: the old support-GTM page. Nothing links to it, still served if you know the URL
- **`CNAME`**: GitHub Pages domain config, do not touch

Hosted on GitHub Pages via `good-timing/website`, branch `master`. Push to `master` = live in ~60 seconds.

---

## Design tokens

Defined as CSS custom properties in the `:root` block at the top of each page. The two brand values are locked, do not change them without saying so out loud.

| Token | Value | Used for |
|---|---|---|
| `--brand` | `#0ca678` | LOCKED. Emerald, the brand colour |
| `--mark` | `#bdeeda` | LOCKED. Highlight wash, derived from emerald |
| `--page` | `#f7f8fa` | Page background |
| `--card` | `#fff` | Card and panel surfaces |
| `--line` / `--line-soft` | `#e5e7eb` / `#f1f3f5` | Borders, dividers |
| `--ink` / `--ink-2` / `--ink-3` | `#111827` / `#1f2937` / `#4b5563` | Headlines, body, secondary body |
| `--mute` / `--mute-2` | `#6b7280` / `#9ca3af` | Captions, diagram labels |
| `--blue` / `--blue-soft` / `--blue-edge` | `#3651d4` / `#eef2ff` / `#c7d2fe` | Links and link-adjacent surfaces |
| `--sans` | Inter | All prose |
| `--mono` | JetBrains Mono | Labels, diagram sub-text, code-like elements |

---

## Page structure (top to bottom)

1. **Nav**: logo, GitHub mark, Get started CTA. Sticky.
2. **Hero**: eyebrow, H1, subhead, single Get started button, 5-beat montage with clickable stop chips
3. **Every session, explained**: the explained-session panel
4. **How capture works**: config chips for SDK / Gateway / Proxy, each with a code pane and a diagram pane
5. **You control what's captured. You can audit the rest.**: the enterprise pillars
6. **Questions, answered**: FAQ
7. **See your first session today**: closing CTA
8. **Footer**: copyright, privacy, terms

---

## Making common changes

### Edit copy
Find the text in `index.html` and edit in place. No special syntax, no templating.

### Change the CTA target
Every Get started button points at `https://baton.goodtiming.ai/`. The founder call link is Calendly. Both appear literally in the markup, search and replace.

### Update a config diagram
The three diagrams under "How capture works" are inline `<svg>` elements carrying `class="dvar"` and a `data-m` attribute of `sdk`, `gw` or `proxy`. They use `viewBox="0 0 920 240"` (`gw` is `0 0 920 270"`). Edit text content directly, adjust `x`/`y` to reposition. The chip row above them toggles which one shows.

### Change a colour
Change the token in `:root`, not the usage site. If you are reaching for a hex value inside a rule, the token is probably missing.

---

## Tone & content rules

- **Product name**: Baton (capital B). Never "baton" lowercase in prose.
- **Company**: Good Timing, Inc. — only appears in footer and legal pages.
- **Never mention**: Ace (the old product), Sarung Tripathi, Together AI, or specific customer company names.
- **AI model examples**: Claude, ChatGPT, Codex — these are OK to name as examples of customer-side agents.
- **Integrations**: Pylon, Slack, Zendesk — OK to name.
- **No dashes (—) in bullet copy** — use periods or restructure the sentence.
- **The five context categories**: intent · tool call · expected · observed · config. These are categories, not fields. Within each category there are individual fields the vendor can control.

---

## Previewing locally

```bash
cd /Users/davideyler/workplace/website
python3 -m http.server 3000
# then open http://localhost:3000
```

Note: links use `.html` extensions (`/privacy.html`, `/terms.html`) so they work on both localhost and GitHub Pages.

---

## Shipping

```bash
cd /Users/davideyler/workplace/website
git add <files>
git commit -m "your message"
git push
```

GitHub Pages picks up `master` automatically. No CI, no deploy step.
