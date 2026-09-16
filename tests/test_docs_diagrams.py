"""One diagram system across docs.html.

Before this file the five diagrams on the page were five conventions. Four were
inline SVG and the fifth was box-drawing characters in a ``<pre>``, which only
held its shape because ``.diagram pre`` overrode line-height — and which the
page's own JS then hung a "copy" button on, because that JS decorates every
``<pre>``. Their canvases were 680x256, 680x214 twice and 920x360, so the same
``font-size="15"`` rendered at three different sizes depending on which diagram
you were looking at. Every colour was a hex literal, which meant the brand
tokens in ``:root`` described the page and the diagrams separately.

None of that is visible per diagram. Each one looks deliberate on its own; the
set is what is inconsistent, so the checks below read all five and compare them,
the way ``baton-console``'s ``test_brand_tokens.py`` compares layouts rather
than checking each for "has tokens".

What is deliberately NOT pinned: the canvas HEIGHT. 214 suits a one-row flow and
280 a three-row one, and forcing those equal would pad two diagrams with empty
space to satisfy a rule nobody reading the page can perceive. The WIDTH is what
makes a font-size mean the same thing everywhere, so the width is the rule.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_DOCS = Path(__file__).resolve().parents[1] / "docs.html"
_HTML = _DOCS.read_text()

# The ``<div class="diagram">`` blocks, in page order.
_DIAGRAMS = re.findall(r'<div class="diagram">.*?</div>', _HTML, re.S)

# ``:root`` is the one place a hex literal is allowed to appear in a diagram's
# vocabulary: it is where the token is DEFINED.
_ROOT = re.search(r":root \{.*?\n    \}", _HTML, re.S)


def test_the_page_has_the_diagrams_this_file_is_about() -> None:
    """Guards the two regexes above. A markup change that stops them matching
    would otherwise empty every list below and turn this file green by finding
    nothing to check."""
    assert len(_DIAGRAMS) == 5, f"expected 5 diagrams, found {len(_DIAGRAMS)}"
    assert _ROOT is not None, ":root block not found"
    assert "--brand" in _ROOT.group(0)


@pytest.mark.parametrize("i", range(5))
def test_every_diagram_is_an_svg_and_not_box_drawing(i: int) -> None:
    """One medium. A ``<pre>`` here is the ASCII diagram coming back: it depends
    on a line-height override to join up, it cannot carry a token, and the
    page's copy-button JS decorates it like a code sample."""
    assert "<svg" in _DIAGRAMS[i], f"diagram {i} has no <svg>"
    assert "<pre" not in _DIAGRAMS[i], f"diagram {i} is box-drawing, not an SVG"


def test_every_diagram_shares_one_canvas_width() -> None:
    """680, so ``font-size="15"`` is the same size in all five.

    Width only — see the module docstring on why height is free.
    """
    # The ROOT <svg>'s viewBox, not every viewBox in the block: an arrowhead
    # <marker> inside <defs> carries its own ``0 0 10 10`` and is a different
    # coordinate system with nothing to do with the canvas.
    roots = [re.search(r'<svg\b[^>]*viewBox="([^"]+)"', d) for d in _DIAGRAMS]
    assert all(roots), "a diagram's root <svg> has no viewBox"
    widths = {m.group(1).split()[2] for m in roots if m}
    assert widths == {"680"}, f"diagrams disagree on canvas width: {sorted(widths)}"


@pytest.mark.parametrize("i", range(5))
def test_no_diagram_paints_with_a_hex_literal(i: int) -> None:
    """Colour comes from ``:root`` or it does not come.

    ``test_brand_tokens.py`` in baton-console compares the ``:root`` block and
    nothing else, so a hex inside an SVG body was invisible to every check we
    had: the tokens could be edited and the diagrams would keep their old
    colours, silently.
    """
    found = re.findall(r"#[0-9a-fA-F]{3,8}\b", _DIAGRAMS[i])
    assert not found, f"diagram {i} hard-codes {found}; use var(--token)"


@pytest.mark.parametrize("i", range(5))
def test_every_diagram_names_itself_for_a_screen_reader(i: int) -> None:
    """``<title>`` is the short name, ``<desc>`` the sentence describing the
    mechanism. Both already existed on all four original SVGs; this keeps the
    fifth, and any future one, from shipping without them."""
    d = _DIAGRAMS[i]
    assert "<title" in d and "<desc" in d, f"diagram {i} has no title/desc"
    assert "aria-labelledby" in d, f"diagram {i} is not wired to its title/desc"
    desc = re.search(r"<desc[^>]*>(.*?)</desc>", d, re.S)
    assert desc and len(desc.group(1).split()) >= 12, (
        f"diagram {i}'s <desc> is a label, not a description of the mechanism"
    )


def test_every_diagram_is_introduced_and_explained() -> None:
    """A lead-in sentence before, a bulleted legend after.

    This is the one rule here taken from outside: it is what platform.claude.com
    does on every figure it ships, and the reason to copy it is that a diagram
    with no legend makes the reader guess which element carries the point.
    """
    assert _HTML.count("The following diagram illustrates") == 5, (
        "a diagram is missing its lead-in sentence"
    )
    legends = re.findall(r"</svg>\s*</div>\s*<ul>", _HTML)
    assert len(legends) == 5, f"{5 - len(legends)} diagram(s) have no legend"
