"""Tests for Design Pipeline and Asset Structure."""

import os

from server import app


def test_asset_directory_structure():
    """Verify assets directory layout and required subdirectories."""
    base_assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    assert os.path.isdir(base_assets), "assets/ directory should exist"

    subdirs = ["backgrounds", "icons", "themes", "concepts"]
    for subdir in subdirs:
        sub_path = os.path.join(base_assets, subdir)
        assert os.path.isdir(sub_path), f"assets/{subdir} directory should exist"


def test_assets_readme_and_contributing_guide():
    """Verify documentation files for design pipeline."""
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    assets_readme = os.path.join(base_dir, "assets", "README.md")
    contributing_design = os.path.join(base_dir, "CONTRIBUTING_DESIGN.md")

    assert os.path.isfile(assets_readme), "assets/README.md should exist"
    assert os.path.isfile(contributing_design), "CONTRIBUTING_DESIGN.md should exist"


def test_design_preview_route():
    """Verify /design-preview template rendering."""
    client = app.test_client()
    res = client.get("/design-preview")
    assert res.status_code == 200
    assert b"Lux Design Preview" in res.data
    assert b"themePreset" in res.data
