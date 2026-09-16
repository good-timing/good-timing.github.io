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
