"""The anchors docs.html promises, to itself and to other repos.

This file exists to make the restructure safe rather than to describe the page.
Sections are about to be reordered and some ``<h2>``s demoted to ``<h3>``, and
the thing that breaks when you do that is silent: ``tabForHash`` resolves an
unknown hash by falling back to the Overview tab. So a link to a heading that
was renamed does not 404 and does not land on the wrong section — it lands on
the front page of the docs, looking like the reader mis-clicked. Nothing in the
page or the browser reports it.

Two audiences, and the second is the one that cannot be fixed by editing this
file:

* **This page**, linking to its own sections, and the sidebar.
* **Other repos.** ``baton/README.md`` is published verbatim as the PyPI
  description, so an anchor it names is live on pypi.org until the next
  release — editing the README does not retract it. ``baton-console`` renders
  two links into its own pages. Those hashes are a published interface.

The external set below is MEASURED, not assumed:

    grep -rhoE 'docs\\.html#[a-z0-9-]+' ~/workplace/website ~/workplace/baton*/README.md \\
        ~/workplace/baton-console/backend/src | sort | uniq -c

run 2026-09-15. A style note had listed ``#without-dsn`` and ``#pii`` here;
neither is linked from anywhere, and it had missed ``#gateway-identity``,
``#sdk`` and ``#proxy`` — including the two console hits, i.e. a whole second
repo. Re-run the grep rather than trusting this comment if the set matters.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

_DOCS = Path(__file__).resolve().parents[1] / "docs.html"
_HTML = _DOCS.read_text()

# Tab names are valid hashes without being ids: ``tabForHash`` checks
# ``panes[h]`` first, so ``#sdk`` opens the SDK tab and no element carries
# ``id="sdk"``. Kept in sync with the ``data-tab`` buttons by the test below.
_TABS = {"overview", "proxy", "sdk", "gateway", "console"}

# Markup only. The page's scroll-spy builds a selector by concatenation —
# ``'.sidebar-link[href="#' + e.target.id + '"]'`` — so scanning the raw file
# for hrefs picks that fragment up as an anchor literally named
# ``' + e.target.id + '``. Strip the scripts before looking for links.
_MARKUP = re.sub(r"<script\b.*?</script>", "", _HTML, flags=re.S)

_IDS = set(re.findall(r'\sid="([^"]+)"', _MARKUP))
_INTERNAL = set(re.findall(r'href="#([^"]+)"', _MARKUP))

# Hashes other repositories link to. See the module docstring for the grep.
_PUBLISHED = {
    "gateway-identity": "baton-console auth/routes.py + dashboard/strings.py",
    "vendorconfig": "baton/README.md (published to PyPI)",
    "off-switch": "baton/README.md (published to PyPI)",
    "sdk": "baton/README.md (published to PyPI)",
    "proxy": "baton/README.md (published to PyPI)",
}


def test_the_tab_names_this_file_hardcodes_are_the_page_s_tabs() -> None:
    """Guards ``_TABS``. If a tab is renamed, the anchor tests below would
    otherwise start accepting a hash that no longer resolves."""
    assert set(re.findall(r'data-tab="([^"]+)"', _HTML)) == _TABS


@pytest.mark.parametrize("anchor", sorted(_INTERNAL))
def test_every_internal_anchor_resolves(anchor: str) -> None:
    """Every ``href="#x"`` on the page reaches something.

    Includes the sidebar, which is the page's own table of contents, and the
    cross-references inside the prose.
    """
    assert anchor in _IDS or anchor in _TABS, (
        f'#{anchor} is linked but no element has id="{anchor}" and it is not a tab; '
        "the reader silently lands on Overview"
    )


@pytest.mark.parametrize("anchor", sorted(_PUBLISHED))
def test_the_anchors_other_repos_publish_still_resolve(anchor: str) -> None:
    """These are not ours to rename.

    A PyPI description is frozen at release: editing ``baton/README.md`` does
    not change the page already on pypi.org, so an anchor it names has to keep
    working until at least the release after the edit.
    """
    assert anchor in _IDS or anchor in _TABS, (
        f"#{anchor} is linked from {_PUBLISHED[anchor]} and no longer resolves"
    )


def test_every_sidebar_link_points_into_its_own_tab() -> None:
    """A sidebar is rendered per tab, and the scroll-spy observer looks the
    link up inside ``sidebars[tab]``. A sidebar entry pointing at a heading in
    a DIFFERENT tab therefore scrolls nowhere and never highlights."""
    for tab in _TABS:
        nav = re.search(rf'<nav id="sidebar-{tab}"[^>]*>(.*?)</nav>', _HTML, re.S)
        assert nav, f"no sidebar for tab {tab}"
        pane = re.search(rf'<div id="tab-{tab}"[^>]*>(.*)', _HTML, re.S)
        assert pane, f"no pane for tab {tab}"
        # The pane runs to the start of the next pane, or to </main>.
        body = re.split(r'<div id="tab-|</main>', pane.group(1))[0]
        for href in re.findall(r'href="#([^"]+)"', nav.group(1)):
            assert f'id="{href}"' in body, f"sidebar-{tab} links #{href}, which is not in tab-{tab}"


class _Outline(HTMLParser):
    """Which tab pane each heading actually lands in, per a real parser.

    The point is that it does not pattern-match. A regex that slices the file
    "from ``<div id="tab-x">`` to the next ``<div id="tab-``" measures the
    SOURCE ORDER of the text, and the browser measures NESTING. On 2026-09-15
    those disagreed: reordering the gateway tab moved its last section to
    second, and the last section was carrying the pane's own closing
    ``</div>``, so three sections ended up outside the pane. Every regex check
    in this file passed. The browser showed a tab with two headings and a
    sidebar listing five.

    So this tracks open ``<div>``s the way a parser does, and reports the
    heading's real ancestor.
    """

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str | None] = []
        self.headings: list[tuple[str, str, str | None]] = []  # (tag, id, tab)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "div":
            el_id = a.get("id") or ""
            self.stack.append(el_id[4:] if el_id.startswith("tab-") else None)
        elif tag in ("h2", "h3") and a.get("id"):
            tab = next((x for x in reversed(self.stack) if x), None)
            self.headings.append((tag, a["id"] or "", tab))

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self.stack:
            self.stack.pop()


def _outline() -> _Outline:
    o = _Outline()
    o.feed(_MARKUP)
    return o


@pytest.mark.parametrize("tab", sorted(_TABS))
def test_every_section_is_nested_inside_its_tab_pane(tab: str) -> None:
    """Sections belong to a pane by NESTING, not by sitting after its opening
    tag. A pane that closes early leaves the rest of its sections in the
    document body: they render on every tab at once, and the tab switcher —
    which hides panes, not headings — cannot hide them."""
    sidebar = re.search(rf'<nav id="sidebar-{tab}"[^>]*>(.*?)</nav>', _MARKUP, re.S)
    assert sidebar
    listed = re.findall(r'href="#([^"]+)"', sidebar.group(1))
    placed = {hid: owner for _, hid, owner in _outline().headings}
    for hid in listed:
        assert placed.get(hid) == tab, (
            f"#{hid} is listed in sidebar-{tab} but nests inside "
            f"{placed.get(hid) or 'no tab pane at all'}"
        )


def test_no_heading_escapes_every_tab_pane() -> None:
    """The symmetric check, for a heading no sidebar happens to list."""
    loose = [hid for _, hid, tab in _outline().headings if tab is None]
    assert not loose, f"headings outside every tab pane: {loose}"


@pytest.mark.parametrize("tab", sorted(_TABS))
def test_each_sidebar_mirrors_its_tab_s_h2s_in_order(tab: str) -> None:
    """The sidebar IS the tab's outline, so it lists the ``<h2>``s — all of
    them, only them, in page order.

    Restructuring is what this catches. Re-ordering sections and demoting an
    ``<h2>`` to ``<h3>`` leaves a sidebar that still lists the old sequence and
    still links the demoted headings: every link resolves, the scroll-spy still
    highlights, and nothing else in this file complains. The reader gets a
    contents page for a shape the document no longer has. That is exactly what
    happened here on 2026-09-15, and it passed the whole suite.
    """
    nav = re.search(rf'<nav id="sidebar-{tab}"[^>]*>(.*?)</nav>', _MARKUP, re.S)
    pane = re.search(
        rf'<div id="tab-{tab}"[^>]*>(.*?)(?=\n    <div id="tab-|\n  </main>)', _MARKUP, re.S
    )
    assert nav and pane

    linked = re.findall(r'href="#([^"]+)"', nav.group(1))
    headings = re.findall(r'<h2 id="([^"]+)"', pane.group(1))
    assert linked == headings, (
        f"sidebar-{tab} lists {linked}\n"
        f"but tab-{tab} has h2s {headings}\n"
        "the sidebar is a contents page for a shape the document no longer has"
    )


def test_every_code_tab_group_has_one_pane_per_button() -> None:
    """The switcher indexes panes by button position.

    ``btns.forEach((btn, i) => ... codePanes[j].hidden = ...)`` reads
    ``codePanes[j]`` for every button index, so one button more than there are
    panes throws ``Cannot set properties of undefined`` inside the click
    handler. That is not a cosmetic break: it happens during setup, so every
    later listener on the page — the other code-tab groups, the main tab bar —
    never gets wired.
    """
    for group in re.findall(r'<div class="code-tabs">.*?\n      </div>', _HTML, re.S):
        buttons = len(re.findall(r"<button", group))
        # Only DIRECT children count, which is what ``:scope >`` selects.
        panes = len(re.findall(r"\n        <(?:pre|div class=\"code-pane\")", group))
        assert buttons == panes, f"code-tabs group has {buttons} buttons and {panes} panes"
