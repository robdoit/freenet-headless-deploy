#!/usr/bin/env python3
"""
Unit Test Suite for Freenet Headless Deploy (`deploy_freenet_headless.py`).
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")),
)

import deploy_freenet_headless as deployer  # noqa: E402


class TestFreenetHeadlessDeploy(unittest.TestCase):
    def test_rewrites_core_static_assets(self):
        raw = (
            '<link rel="stylesheet" href="/style.css">\n'
            '<script src="/app.js" defer></script>\n'
            '<img src="/qr.png" alt="QR">'
        )
        transformed = deployer.transform_content(raw)
        self.assertIn('href="./style.css"', transformed)
        self.assertIn('src="./app.js"', transformed)
        self.assertIn('src="./qr.png"', transformed)

    def test_rewrites_downloadable_archives_and_docs(self):
        raw = (
            '<a href="/freenet-skills/freenet-headless-deploy.zip">Zip</a>\n'
            '<a href="/freenet-skills/SKILL.md">Skill</a>\n'
            '<a href="/freenet-skills/deploy_freenet_headless.py">Script</a>\n'
            '<a href="/AGENTS.md">Agents</a>\n'
            '<a href="/llms.txt">LLMs</a>'
        )
        transformed = deployer.transform_content(raw)
        self.assertIn('href="./freenet-skills/freenet-headless-deploy.zip"', transformed)
        self.assertIn('href="./freenet-skills/SKILL.md"', transformed)
        self.assertIn('href="./freenet-skills/deploy_freenet_headless.py"', transformed)
        self.assertIn('href="./AGENTS.md"', transformed)
        self.assertIn('href="./llms.txt"', transformed)

    def test_rewrites_extensionless_routes_and_root(self):
        raw = (
            '<a href="/">Home</a>\n'
            '<a href="/skills">Skills</a>\n'
            '<a href="/terms#section-1">Terms</a>\n'
            '<a href="/privacy?v=2">Privacy</a>'
        )
        transformed = deployer.transform_content(raw)
        self.assertIn('href="./index.html"', transformed)
        self.assertIn('href="./skills.html"', transformed)
        self.assertIn('href="./terms.html#section-1"', transformed)
        self.assertIn('href="./privacy.html?v=2"', transformed)

    def test_preserves_external_and_protocol_relative_links(self):
        raw = (
            '<a href="https://github.com/robdoit/freenet-headless-deploy">GitHub</a>\n'
            '<a href="//cdn.example.com/lib.js">CDN</a>\n'
            '<a href="mailto:rob@robdoit.work">Email</a>\n'
            '<a href="/v1/contract/web/771DvtPMwt2PumPyrFvsz7fpvU1gogcmb5qtS1yYEEH9/">Atlas</a>'
        )
        transformed = deployer.transform_content(raw)
        self.assertEqual(raw, transformed)

    def test_rewrites_css_urls(self):
        raw = (
            "background-image: url('/leopard_bg.jpg');\n"
            'src: url("/fonts/inter.woff2") format("woff2");\n'
            "mask-image: url(/assets/mask.svg);"
        )
        transformed = deployer.transform_content(raw)
        self.assertIn("url('./leopard_bg.jpg')", transformed)
        self.assertIn('url("./fonts/inter.woff2")', transformed)
        self.assertIn("url(./assets/mask.svg)", transformed)

    def test_parse_fdev_key_list(self):
        sample_output = (
            "site-key  HCfNYwDV8XbLUHNgiVEdBSCPuQ55hwoUMkJ3pxtuEmhM\n"
            "robdoit-key  CvvqJDgMBUtqWiXqEypXLU9cXFNMhFuPruPPdZ4NWuPi\n"
        )
        parsed = deployer.parse_fdev_key_list(sample_output)
        self.assertEqual(
            parsed,
            {
                "site-key": "HCfNYwDV8XbLUHNgiVEdBSCPuQ55hwoUMkJ3pxtuEmhM",
                "robdoit-key": "CvvqJDgMBUtqWiXqEypXLU9cXFNMhFuPruPPdZ4NWuPi",
            },
        )

    def test_extract_html_metadata_and_format_atlas(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            html_file = os.path.join(tmpdir, "index.html")
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(
                    "<!DOCTYPE html><html><head>"
                    "<title>Freenet Headless Deploy</title>"
                    '<meta name="description" content="Open-source Freenet deployment CLI and skill.">'
                    "</head><body></body></html>"
                )
            title, snippet = deployer.extract_html_metadata(html_file)
            self.assertEqual(title, "Freenet Headless Deploy")
            self.assertEqual(snippet, "Open-source Freenet deployment CLI and skill.")

            atlas_out = deployer.format_atlas_submission(
                "CvvqJDgMBUtqWiXqEypXLU9cXFNMhFuPruPPdZ4NWuPi",
                path="/skills.html",
                title=title,
                snippet=snippet,
            )
            self.assertIn('--kind "site"', atlas_out)
            self.assertIn(
                '--locator "freenet:CvvqJDgMBUtqWiXqEypXLU9cXFNMhFuPruPPdZ4NWuPi/skills.html"',
                atlas_out,
            )
            self.assertIn("--landing general", atlas_out)
            self.assertIn("--adult-sections false", atlas_out)
            self.assertIn("--volatility static", atlas_out)

    def test_transform_asset_paths_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = os.path.join(tmpdir, "src")
            stage_dir = os.path.join(tmpdir, "stage")
            os.makedirs(src_dir)
            with open(os.path.join(src_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write('<link href="/style.css"><a href="/skills">Skills</a>')

            out_dir, count = deployer.transform_asset_paths(src_dir, stage_dir)
            self.assertEqual(out_dir, stage_dir)
            self.assertEqual(count, 1)
            with open(os.path.join(stage_dir, "index.html"), "r", encoding="utf-8") as f:
                staged_html = f.read()
            self.assertIn('href="./style.css"', staged_html)
            self.assertIn('href="./skills.html"', staged_html)


if __name__ == "__main__":
    unittest.main()
