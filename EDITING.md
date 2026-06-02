# Baton Website — Editing Guide

## Overview

Single-page static site. No build system, no npm, no framework. Everything lives in one file:

- **`index.html`** — the entire homepage (HTML + CSS + JS, all inline)
- **`privacy.html`** / **`terms.html`** / **`cookies.html`** — legal pages
- **`404.html`** — redirects to `/`
- **`baton-icon.svg`** — favicon (amber rounded square with diagonal baton)
- **`CNAME`** — GitHub Pages domain config, do not touch

Hosted on GitHub Pages via `good-timing/website`, branch `master`. Push to `master` = live in ~60 seconds.

---

## Design tokens

| Token | Value | Used for |
|---|---|---|
| Background | `#0b0c10` | Page background |
| Accent (amber) | `#F5A623` | CTAs, labels, highlights |
| Accent soft | `#FFC36B` | Hover states |
| Text primary | `#ECEEF2` | Headlines, body |
| Text secondary | `#95989F` | Subtext, card body |
| Text dim | `#62656D` | Captions, diagram labels |
| Body font | Inter | All prose |
| Mono font | JetBrains Mono | Labels, diagram sub-text, code-like elements |

---

## Page structure (top to bottom)

1. **Nav** — logo + "Request early access" button
2. **Hero** — amber eyebrow label, H1, subhead, email CTA form
3. **Problem** — H2 + two body paragraphs
4. **How it works** — H2 + body + inline SVG diagram + 5 step cards (3+2 layout)
5. **Five things** — H2 centered, body centered, 5 capture cards (3+2 layout)
6. **Security & Governance** — H2 + 4 bullet list
7. **Integrations** — Pylon, Slack, Zendesk
8. **Final CTA** — email form, anchored at `#early-access`
9. **Footer** — copyright + legal links

---

## Making common changes

### Edit copy
Find the text in `index.html` and edit in place. Most prose is in `<p class="body">` or `<li>` tags. Headlines are `<h2>`. No special syntax.

### Change a section headline
Search for the current H2 text and replace it. H2s have `max-width: 28ch` by default to prevent overly wide lines — override with `style="max-width: none;"` if centering.

### Add/remove a step card
Step cards are in `.steps-row-top` (3 cards) and `.steps-row-bottom` (2 cards, centered). If you change the count, update the grid layout in the CSS (`.steps-row-top` uses `repeat(3, 1fr)`, `.steps-row-bottom` uses `repeat(2, 1fr)`).

### Add/remove a capture card
Same 3+2 layout as steps — `.capture-row-top` and `.capture-row-bottom`.

### Update the CTA form endpoint
The form POSTs to a Google Apps Script URL. Search for `AKfycbyFp7RmjjPpfKG7H32y` in `index.html` to find it. Replace with the new endpoint if needed.

### Update the diagram
The diagram is an inline `<svg>` with `viewBox="0 0 880 380"`. Key elements:
- Two node `<rect>` elements with text inside `<g>` groups
- Two arc paths with gradient strokes (`url(#gradLeft)` / `url(#gradRight)`)
- A center "BATON" pill
- Labels above/below the arcs (`SIGNAL`, `RESPONSE`, and the five context items)

Edit text content directly; adjust `x`/`y` coordinates to reposition.

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
