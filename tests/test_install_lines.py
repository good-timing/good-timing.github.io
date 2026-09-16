"""Install lines, checked against each other and against the registry.

The defect this exists for, measured 2026-09-15: `docs.html` pinned
`pip install "baton-sdk>=0.8.8"` while `baton/README.md`'s install block named
no floor at all. One fact, two hand-maintained surfaces, two answers — and the
0.8.8 release had moved the number on one of them only. Nothing was wrong on
either page read alone.

Two things changed that shape, and this file guards what is left:

* The READMEs were thinned, so they no longer restate floors or extras. The
  duplicate surface was removed rather than synchronised — the cheapest fix for
  drift is deleting the second copy.
* What remains is `docs.html`, which names the floor several times and must
  agree with ITSELF, and must agree with what is actually published.

**The comparison is against the registry, not a sibling checkout.** A working
tree can be behind, ahead, or on a branch; PyPI and npm are what a stranger
following these instructions will actually resolve. Registry tests are marked
`network` and skip when it is unreachable, so an offline run still checks the
internal-consistency half.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

import pytest

_HTML = (Path(__file__).resolve().parents[1] / "docs.html").read_text()
# docs.html is HTML: a floor is written `&gt;=`.
_TEXT = _HTML.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")

_PIP = re.findall(r"pip install [\"']?([A-Za-z0-9_.\[\]-]*baton[A-Za-z0-9_.\[\]-]*)[\"']?", _TEXT)
_NPM = re.findall(r"npm install ([@A-Za-z0-9/._-]+)", _TEXT)


def _registry(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=15) as r:  # noqa: S310 - fixed https hosts
            return json.load(r)
    except urllib.error.HTTPError as exc:
        # Caught FIRST, and it has to be: ``HTTPError`` SUBCLASSES ``URLError``,
        # so the clause below used to swallow it. A 404 became
        # skip("registry unreachable") and the name tests could not fail for a
        # typo'd package — the one outcome their docstrings forbid. Measured
        # 2026-09-16 against a bogus scoped name.
        #
        # An answer is reachability. 4xx is a verdict about the name we
        # printed; 5xx is the registry having a bad day and is not ours.
        if exc.code >= 500:
            pytest.skip(f"registry error {exc.code}: {url}")
        pytest.fail(f"registry answered {exc.code} for {url}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        pytest.skip(f"registry unreachable: {exc}")


@pytest.mark.network
def test_a_name_the_registry_does_not_know_fails_rather_than_skipping() -> None:
    """The guard on ``_registry``'s except ORDER, which is load-bearing.

    Without it the three network tests above are decorative: they would report
    green against any name at all. Asserted here rather than trusted, because
    the bug was invisible — a skipped test and a passing test both read as "not
    failing" in the run summary.
    """
    with pytest.raises(pytest.fail.Exception):
        _registry("https://registry.npmjs.org/@goodtiming/baton-sdk-does-not-exist")


def test_the_page_still_has_install_lines_to_check() -> None:
    """Guards the two regexes. A markup change that stopped them matching would
    empty every list below and turn this file green by finding nothing."""
    assert len(_PIP) >= 5, f"only found {_PIP}"
    assert _NPM, "no npm install line found"


def test_one_sdk_floor_everywhere() -> None:
    """Every floor named for `baton-sdk` on this page is the same number.

    This is the half that catches the original defect's descendant: bumping the
    floor in the install table and forgetting the one in the quickstart. Both
    lines are correct in isolation; only together are they wrong.
    """
    floors = set(re.findall(r"baton-sdk(?:\[[a-z,]+\])?>=([0-9.]+)", _TEXT))
    assert len(floors) <= 1, f"docs.html names more than one baton-sdk floor: {sorted(floors)}"


def test_no_install_line_names_a_package_we_do_not_publish() -> None:
    """Typos and renames. The extras are checked separately, against PyPI."""
    named = {re.sub(r"\[.*\]", "", p) for p in _PIP}
    assert named <= {"baton-sdk", "baton-proxy"}, f"unexpected pip package(s): {named}"
    assert set(_NPM) <= {"@goodtiming/baton-sdk"}, f"unexpected npm package(s): {set(_NPM)}"


@pytest.mark.network
def test_every_extra_named_is_actually_published() -> None:
    """`pip install "baton-sdk[fastmcp]"` fails loudly for a stranger if that
    extra does not exist, and the page is the only place it is written down.

    ``provides_extra`` is the published metadata, so this compares the
    instruction to the artifact rather than to a `pyproject.toml` in a checkout
    that may be ahead of the release a reader will resolve.
    """
    published = set(_registry("https://pypi.org/pypi/baton-sdk/json")["info"]["provides_extra"] or [])
    named = {e for p in _PIP for e in re.findall(r"\[([a-z,]+)\]", p) for e in e.split(",")}
    assert named <= published, f"docs.html names extras PyPI does not publish: {sorted(named - published)}"


@pytest.mark.network
def test_the_named_floor_is_a_real_release() -> None:
    """A floor nobody can install is worse than no floor: `pip install
    "baton-sdk>=9.9.9"` resolves to nothing at all."""
    floors = set(re.findall(r"baton-sdk(?:\[[a-z,]+\])?>=([0-9.]+)", _TEXT))
    if not floors:
        pytest.skip("no floor named")
    releases = set(_registry("https://pypi.org/pypi/baton-sdk/json")["releases"])
    missing = floors - releases
    assert not missing, f"docs.html pins baton-sdk {missing}, which was never released"


@pytest.mark.network
@pytest.mark.parametrize("package", sorted(set(_NPM)))
def test_the_npm_package_exists_under_the_name_we_print(package: str) -> None:
    """Resolves the name AS PRINTED ON THE PAGE.

    Hardcoding `@goodtiming/baton-sdk` here would have made this test pass for
    whatever the page said, which is the one thing it must not do: it would be
    checking that our package exists, not that we told the reader the right
    name to type.
    """
    data = _registry(f"https://registry.npmjs.org/{package}")
    assert data.get("name") == package
