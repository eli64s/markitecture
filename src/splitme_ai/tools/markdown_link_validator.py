import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import requests

from splitme_ai.logger import Logger

_logger = Logger(__name__)


class MarkdownLinkValidator:
    def __init__(self, timeout: int = 10, max_workers: int = 5):
        """
        Initialize the link checker with configurable timeout and concurrency.

        Args:
            timeout (int): Seconds to wait for each HTTP request
            max_workers (int): Maximum number of concurrent requests
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.inline_link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        self.ref_link_pattern = re.compile(r"\[([^\]]+)\]:\s*(\S+)")

    def extract_links(self, content: str) -> List[Tuple[str, str, int]]:
        """
        Extract inline and reference links from markdown content.

        Args:
            content (str): Markdown content

        Returns:
            List[Tuple[str, str, int]]: List of (text, url, line_number)
        """
        links = []

        # Extract inline links
        for line_num, line in enumerate(content.splitlines(), 1):
            links.extend(
                (match.group(1), match.group(2).strip(), line_num)
                for match in self.inline_link_pattern.finditer(line)
            )

        # Extract reference links
        links.extend(
            (match.group(1), match.group(2).strip(), line_num)
            for line_num, line in enumerate(content.splitlines(), 1)
            for match in self.ref_link_pattern.finditer(line)
        )

        return links

    def check_link(self, url: str) -> Dict:
        """
        Check if a link is accessible.

        Args:
            url (str): URL to check

        Returns:
            Dict: Dictionary with status and error information
        """
        result = {"url": url, "status": "unknown", "error": None}

        if url.startswith("#"):  # Skip internal links
            result["status"] = "internal"
            return result

        if not urlparse(url).scheme:  # Handle local file paths
            if os.path.exists(url):
                result["status"] = "ok"
            else:
                result["status"] = "error"
                result["error"] = "File not found"
            return result

        try:
            response = requests.head(url, timeout=self.timeout, allow_redirects=True)
            if response.status_code == 405:
                response = requests.get(url, timeout=self.timeout)

            if response.status_code == 200:
                result["status"] = "ok"
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"
        except requests.RequestException as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def check_markdown_file(self, filepath: str) -> List[Dict]:
        """
        Check all links in a markdown file.

        Args:
            filepath (str): Path to the markdown file

        Returns:
            List[Dict]: List of results for each link check
        """
        try:
            content = Path(filepath).read_text(encoding="utf-8")
        except OSError as e:
            return [{"error": f"Failed to read file: {e}"}]

        links = self.extract_links(content)
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.check_link, url): (text, url, line)
                for text, url, line in links
            }
            for future in futures:
                text, url, line = futures[future]
                result = future.result()
                results.append({
                    "text": text,
                    "url": url,
                    "line": line,
                    "status": result["status"],
                    "error": result.get("error"),
                })

        return results


def main():
    """
    Example usage of the MarkdownLinkValidator.
    """
    filepath = "../README.md"
    checker = MarkdownLinkValidator()
    results = checker.check_markdown_file(filepath)

    _logger.info("\nMarkdown Link Check Results:")
    _logger.info("-" * 80)

    for result in results:
        status = "✅" if result["status"] == "ok" else "❌"
        _logger.info(
            f"{status} Line {result['line']}: [{result['text']}]({result['url']})"
        )
        if result["error"]:
            _logger.info(f"   Error: {result['error']}")

    total = len(results)
    broken = sum(1 for r in results if r["status"] != "ok")
    _logger.info(f"\nSummary: {broken} broken links out of {total} total links")
