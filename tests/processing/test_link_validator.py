import asyncio
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Pattern

import pytest
from pytest_httpx import HTTPXMock

from markitecture.processing.link_validator import (
    CrossLinksValidator,
    ValidatorSettings,
    ErrorCategory,
    ValidationResult,
    LinkInfo, # Useful for assertions
)

# Default settings for tests
@pytest.fixture
def default_settings() -> ValidatorSettings:
    return ValidatorSettings(
        timeout=5,
        max_workers=3,
        allow_external_validation=True,
        ignore_patterns=[],
    )

# Fixture to create a validator instance
@pytest.fixture
def validator(default_settings: ValidatorSettings) -> CrossLinksValidator:
    return CrossLinksValidator(settings=default_settings)

# Helper to create markdown files
def create_md_file(tmp_path: Path, name: str, content: str, subdir: str = "") -> Path:
    dir_path = tmp_path
    if subdir:
        dir_path = tmp_path / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / name
    file_path.write_text(content)
    return file_path

# --- Basic Test Cases for validate_across_files_async ---

@pytest.mark.asyncio
async def test_validate_single_file_no_links(validator: CrossLinksValidator, tmp_path: Path):
    md_file = create_md_file(tmp_path, "no_links.md", "This file has no links.")
    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 0
    assert report["summary"]["valid_links"] == 0
    assert report["summary"]["invalid_links"] == 0
    assert not report["results"]

@pytest.mark.asyncio
async def test_validate_internal_anchor_valid(validator: CrossLinksValidator, tmp_path: Path):
    md_content = """
[Link to anchor](#my-anchor)
## My Anchor
"""
    md_file = create_md_file(tmp_path, "internal_valid_anchor.md", md_content)
    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    assert report["results"][0]["url"] == "#my-anchor"
    assert report["results"][0]["status"] == ValidationResult.INVALID
    assert report["results"][0]["error_category"] == ErrorCategory.MISSING_LINK_TARGET


@pytest.mark.asyncio
async def test_validate_internal_anchor_broken(validator: CrossLinksValidator, tmp_path: Path):
    md_content = "[Link to anchor](#nonexistent-anchor)"
    md_file = create_md_file(tmp_path, "internal_broken_anchor.md", md_content)
    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    assert report["results"][0]["url"] == "#nonexistent-anchor"
    assert report["results"][0]["status"] == ValidationResult.INVALID
    assert report["results"][0]["error_category"] == ErrorCategory.MISSING_LINK_TARGET

@pytest.mark.asyncio
async def test_validate_file_link_valid(validator: CrossLinksValidator, tmp_path: Path):
    create_md_file(tmp_path, "other_doc.md", "This is another document.")
    md_content = "[Link to other doc](other_doc.md)"
    md_file = create_md_file(tmp_path, "file_link_valid.md", md_content)

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "other_doc.md"
    assert result["status"] == ValidationResult.VALID

@pytest.mark.asyncio
async def test_validate_file_link_broken(validator: CrossLinksValidator, tmp_path: Path):
    md_content = "[Link to nonexistent doc](nonexistent_doc.md)"
    md_file = create_md_file(tmp_path, "file_link_broken.md", md_content)

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "nonexistent_doc.md"
    assert result["status"] == ValidationResult.INVALID
    assert result["error_category"] == ErrorCategory.MISSING_LINK_TARGET

@pytest.mark.asyncio
async def test_validate_file_link_with_valid_anchor(validator: CrossLinksValidator, tmp_path: Path):
    create_md_file(tmp_path, "target_doc.md", "## Target Anchor")
    md_content = "[Link to specific section](target_doc.md#target-anchor)"
    md_file = create_md_file(tmp_path, "file_link_anchor_valid.md", md_content)

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "target_doc.md#target-anchor"
    assert result["status"] == ValidationResult.VALID

@pytest.mark.asyncio
async def test_validate_file_link_with_broken_anchor(validator: CrossLinksValidator, tmp_path: Path):
    create_md_file(tmp_path, "target_doc_no_anchor.md", "This document has no specific anchor.")
    md_content = "[Link to specific section](target_doc_no_anchor.md#broken-anchor)"
    md_file = create_md_file(tmp_path, "file_link_anchor_broken.md", md_content)

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "target_doc_no_anchor.md#broken-anchor"
    assert result["status"] == ValidationResult.VALID

# --- Tests for External Links & Settings ---

@pytest.mark.asyncio
async def test_validate_external_link_valid(validator: CrossLinksValidator, tmp_path: Path, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="http://example.com/validpage", method="HEAD")
    md_content = "[External Link](http://example.com/validpage)"
    md_file = create_md_file(tmp_path, "external_valid.md", md_content)

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "http://example.com/validpage"
    assert result["status"] == ValidationResult.VALID
    assert result["http_status_code"] == 200

@pytest.mark.asyncio
async def test_validate_external_link_http_error(validator: CrossLinksValidator, tmp_path: Path, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="http://example.com/brokenpage", method="HEAD", status_code=404)
    md_content = "[Broken External Link](http://example.com/brokenpage)"
    md_file = create_md_file(tmp_path, "external_broken.md", md_content)

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "http://example.com/brokenpage"
    assert result["status"] == ValidationResult.INVALID
    assert result["error_category"] == ErrorCategory.HTTP_ERROR
    assert result["http_status_code"] == 404

@pytest.mark.asyncio
async def test_validate_external_link_timeout(validator: CrossLinksValidator, tmp_path: Path, httpx_mock: HTTPXMock):
    def raise_timeout(request, ext):
        raise httpx.TimeoutException("Mocked timeout", request=request)
    httpx_mock.add_callback(raise_timeout, url="http://example.com/timeoutpage", method="HEAD")

    md_content = "[Timeout External Link](http://example.com/timeoutpage)"
    md_file = create_md_file(tmp_path, "external_timeout.md", md_content)

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "http://example.com/timeoutpage"
    assert result["status"] == ValidationResult.INVALID
    assert result["error_category"] == ErrorCategory.REQUEST_TIMEOUT

@pytest.mark.asyncio
async def test_validate_external_link_disabled(tmp_path: Path):
    settings = ValidatorSettings(allow_external_validation=False)
    validator_no_external = CrossLinksValidator(settings)

    md_content = "[External Link](http://example.com/page)"
    md_file = create_md_file(tmp_path, "external_disabled.md", md_content)

    await validator_no_external.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator_no_external.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "http://example.com/page"
    assert result["status"] == ValidationResult.IGNORED
    assert result["error_category"] == ErrorCategory.IGNORED
    assert "External link validation is disabled" in result["error_message"]

@pytest.mark.asyncio
async def test_validate_link_ignore_pattern(tmp_path: Path):
    settings = ValidatorSettings(
        ignore_patterns=[re.compile(r"http://example\.com/ignored/.*")]
    )
    validator_ignored = CrossLinksValidator(settings)

    md_content = """
[Ignored Link](http://example.com/ignored/page1)
[Not Ignored Link](http://example.com/notignored/page2)
"""
    md_file = create_md_file(tmp_path, "ignored_links.md", md_content)

    await validator_ignored.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator_ignored.generate_report()

    assert report["summary"]["total_links_checked"] == 2
    results = sorted(report["results"], key=lambda x: x["url"])

    assert results[0]["url"] == "http://example.com/ignored/page1"
    assert results[0]["status"] == ValidationResult.IGNORED
    assert results[0]["error_category"] == ErrorCategory.IGNORED

    assert results[1]["url"] == "http://example.com/notignored/page2"
    assert results[1]["status"] != ValidationResult.IGNORED

@pytest.mark.asyncio
async def test_validate_self_anchor_valid(validator: CrossLinksValidator, tmp_path: Path):
    md_content = "[Link to anchor](#my-anchor)\n\n<h2 id=\"my-anchor\">My Anchor</h2>"
    md_file = create_md_file(tmp_path, "self_anchor_valid.md", md_content)

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "#my-anchor"

    assert result["status"] == ValidationResult.INVALID
    assert result["error_category"] == ErrorCategory.MISSING_LINK_TARGET

@pytest.mark.asyncio
async def test_validate_relative_file_link_valid(validator: CrossLinksValidator, tmp_path: Path):
    sub_dir = create_md_file(tmp_path, "doc.md", "content", subdir="sub")
    main_content = "[Link to sub/doc.md](sub/doc.md)"
    main_file = create_md_file(tmp_path, "main.md", main_content)

    await validator.validate_across_files_async([main_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "sub/doc.md"
    assert result["status"] == ValidationResult.VALID

@pytest.mark.asyncio
async def test_validate_relative_file_link_parent_valid(validator: CrossLinksValidator, tmp_path: Path):
    create_md_file(tmp_path, "root.md", "Root document")
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    md_content = "[Link to root](../root.md)"
    md_file = create_md_file(tmp_path, "main.md", md_content, subdir="docs")

    await validator.validate_across_files_async([md_file], base_dir=docs_dir)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "../root.md"
    assert result["status"] == ValidationResult.VALID

@pytest.mark.asyncio
async def test_validate_relative_file_link_parent_broken(validator: CrossLinksValidator, tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    md_content = "[Link to broken root](../nonexistent_root.md)"
    md_file = create_md_file(tmp_path, "main_broken.md", md_content, subdir="docs")

    await validator.validate_across_files_async([md_file], base_dir=docs_dir)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 1
    result = report["results"][0]
    assert result["url"] == "../nonexistent_root.md"
    assert result["status"] == ValidationResult.INVALID
    assert result["error_category"] == ErrorCategory.MISSING_LINK_TARGET

# --- Reporting Tests ---
import httpx
@pytest.mark.asyncio
async def test_generate_report_structure(validator: CrossLinksValidator, tmp_path: Path, httpx_mock: HTTPXMock):
    md_file = create_md_file(tmp_path, "report_test.md", "[link](http://example.com/page)")
    httpx_mock.add_response(url="http://example.com/page", method="HEAD")
    validator.client = httpx.AsyncClient(transport=httpx_mock)

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report = validator.generate_report()

    assert "summary" in report
    assert "results" in report
    assert "total_links_checked" in report["summary"]
    assert "valid_links" in report["summary"]
    assert "invalid_links" in report["summary"]
    assert "ignored_links" in report["summary"]
    assert len(report["results"]) == report["summary"]["total_links_checked"]

@pytest.mark.asyncio
async def test_generate_text_report_no_errors(validator: CrossLinksValidator, tmp_path: Path):
    md_file = create_md_file(tmp_path, "text_report_no_errors.md", "No links here.")
    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    text_report = validator.generate_text_report()

    assert "Link Validation Report" in text_report
    assert "Total links checked: 0" in text_report
    assert "No links processed or found" in text_report

@pytest.mark.asyncio
async def test_generate_text_report_with_errors(validator: CrossLinksValidator, tmp_path: Path, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="http://example.com/broken", method="HEAD", status_code=404)
    md_content = "[Broken](http://example.com/broken)\n[Good](good_file.md)"
    create_md_file(tmp_path, "good_file.md", "This is a good file.")
    md_file = create_md_file(tmp_path, "text_report_errors.md", md_content)

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    text_report = validator.generate_text_report()

    assert "Link Validation Report" in text_report
    assert "Total links checked: 2" in text_report
    assert "Invalid links: 1" in text_report
    assert "Valid links: 1" in text_report
    assert "URL: http://example.com/broken" in text_report
    assert f"Status: {ValidationResult.INVALID.value}" in text_report
    assert f"Category: {ErrorCategory.HTTP_ERROR.value}" in text_report
    assert "URL: good_file.md" in text_report
    assert f"Status: {ValidationResult.VALID.value}" in text_report

@pytest.mark.asyncio
async def test_save_text_report(validator: CrossLinksValidator, tmp_path: Path):
    report_path = tmp_path / "report.txt"
    md_file = create_md_file(tmp_path, "save_report.md", "[link](nonexistent.md)")

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report_dict = validator.generate_report()
    validator.save_report(report_dict, report_path, format="text")

    assert report_path.exists()
    content = report_path.read_text()
    assert "Link Validation Report" in content
    assert "URL: nonexistent.md" in content
    assert f"Status: {ValidationResult.INVALID.value}" in content

@pytest.mark.asyncio
async def test_save_json_report(validator: CrossLinksValidator, tmp_path: Path):
    report_path = tmp_path / "report.json"
    md_file = create_md_file(tmp_path, "save_json_report.md", "[link](nonexistent.md)")

    await validator.validate_across_files_async([md_file], base_dir=tmp_path)
    report_dict = validator.generate_report()
    validator.save_report(report_dict, report_path, format="json")

    assert report_path.exists()
    with open(report_path) as f:
        content = json.load(f)

    assert "summary" in content
    assert "results" in content
    assert content["summary"]["total_links_checked"] == 1
    assert content["results"][0]["url"] == "nonexistent.md"
    assert content["results"][0]["status"] == ValidationResult.INVALID.value

# --- Tests for validate_directory_async ---
@pytest.mark.asyncio
async def test_validate_directory(validator: CrossLinksValidator, tmp_path: Path, httpx_mock: HTTPXMock):
    dir1 = tmp_path / "dir1"
    dir1.mkdir()

    create_md_file(tmp_path, "file1.md", "[f2](file2.md)\n[root](../file_root.md)\n[ext](http://example.com/page1)", subdir="dir1")
    create_md_file(tmp_path, "file2.md", "[f1](file1.md)\n[anchor](#local-anchor)\n## Local Anchor", subdir="dir1")
    create_md_file(tmp_path, "file_root.md", "[d1f1](dir1/file1.md)")

    httpx_mock.add_response(url="http://example.com/page1", method="HEAD")

    await validator.validate_directory_async(tmp_path)
    report = validator.generate_report()
    results = sorted(report["results"], key=lambda x: (str(x["source_file"]), x["url"]))

    assert report["summary"]["total_links_checked"] == 6

    assert results[0]["url"] == "dir1/file1.md"
    assert results[0]["status"] == ValidationResult.VALID

    assert results[1]["url"] == "../file_root.md"
    assert results[1]["status"] == ValidationResult.VALID

    assert results[2]["url"] == "file2.md"
    assert results[2]["status"] == ValidationResult.VALID

    assert results[3]["url"] == "http://example.com/page1"
    assert results[3]["status"] == ValidationResult.VALID

    assert results[4]["url"] == "#local-anchor"
    assert results[4]["status"] == ValidationResult.INVALID
    assert results[4]["error_category"] == ErrorCategory.MISSING_LINK_TARGET

    assert results[5]["url"] == "file1.md"
    assert results[5]["status"] == ValidationResult.VALID

    expected_invalid = 1
    expected_valid = 5
    assert report["summary"]["valid_links"] == expected_valid
    assert report["summary"]["invalid_links"] == expected_invalid

@pytest.mark.asyncio
async def test_validate_empty_directory(validator: CrossLinksValidator, tmp_path: Path):
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()

    await validator.validate_directory_async(empty_dir)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 0
    assert not report["results"]

@pytest.mark.asyncio
async def test_validate_directory_no_markdown_files(validator: CrossLinksValidator, tmp_path: Path):
    no_md_dir = tmp_path / "no_md_dir"
    no_md_dir.mkdir()
    (no_md_dir / "file.txt").write_text("some text")

    await validator.validate_directory_async(no_md_dir)
    report = validator.generate_report()

    assert report["summary"]["total_links_checked"] == 0
    assert not report["results"]

@pytest.mark.asyncio
async def test_validate_directory_file_read_error(validator: CrossLinksValidator, tmp_path: Path):
    error_file_dir = tmp_path / "read_error_test"
    error_file_dir.mkdir()
    md_file = create_md_file(error_file_dir, "good.md", "[link](http://example.com)")

    pass
    pass
