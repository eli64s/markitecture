import asyncio
import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Set
from urllib.parse import urlparse, urljoin

import httpx

# Assuming ValidatorSettings will be imported from markitecture.settings.validators
# For now, to make this self-contained for the tool, I might need to redefine a placeholder
# or ensure the actual ValidatorSettings is available in the environment.
# For the purpose of this step, I'll assume it's importable.
from markitecture.settings.validators import ValidatorSettings # This line might cause issues if file is not found by linter


class ErrorCategory(Enum):
    INVALID_LINK_STRUCTURE = "Invalid Link Structure"
    MISSING_LINK_TARGET = "Missing Link Target" # For relative links
    HTTP_ERROR = "HTTP Error"
    REQUEST_TIMEOUT = "Request Timeout"
    GENERIC_VALIDATION_ERROR = "Generic Validation Error"
    IGNORED = "Ignored" # For links matching ignore patterns

class ValidationResult(Enum):
    VALID = "Valid"
    INVALID = "Invalid"
    IGNORED = "Ignored"
    ERROR = "Error" # For issues during validation itself

class LinkInfo(BaseModel):
    url: str
    source_file: Path
    line_number: Optional[int] = None # Placeholder, not yet implemented
    status: ValidationResult = ValidationResult.VALID
    error_category: Optional[ErrorCategory] = None
    error_message: Optional[str] = None
    http_status_code: Optional[int] = None

class CrossLinksValidator:
    def __init__(self, settings: ValidatorSettings):
        self.settings = settings
        self.client = httpx.AsyncClient(timeout=settings.timeout, follow_redirects=True)
        self._results: List[LinkInfo] = []
        self._processed_urls: Set[str] = set() # To avoid re-checking same URL

    async def _validate_single_url(self, url: str, source_file: Path, base_dir: Path) -> LinkInfo:
        """Validates a single URL."""
        if url in self._processed_urls and not url.startswith("#"): # Don't cache fragments yet
             # Find previous result (this is simplistic, might need better caching)
            for res in self._results:
                if res.url == url:
                    return res 
        self._processed_urls.add(url)

        link_info = LinkInfo(url=url, source_file=source_file)

        # Check ignore patterns
        if self.settings.ignore_patterns:
            for pattern in self.settings.ignore_patterns:
                if pattern.search(url):
                    link_info.status = ValidationResult.IGNORED
                    link_info.error_category = ErrorCategory.IGNORED
                    link_info.error_message = f"URL matched ignore pattern: {pattern.pattern}"
                    self._results.append(link_info)
                    return link_info
        
        parsed_url = urlparse(url)

        if parsed_url.scheme in ["http", "https"]:
            if not self.settings.allow_external_validation:
                link_info.status = ValidationResult.IGNORED
                link_info.error_category = ErrorCategory.IGNORED
                link_info.error_message = "External link validation is disabled."
                self._results.append(link_info)
                return link_info
            try:
                response = await self.client.head(url, timeout=self.settings.timeout)
                link_info.http_status_code = response.status_code
                if 400 <= response.status_code < 600: # client or server error
                    link_info.status = ValidationResult.INVALID
                    link_info.error_category = ErrorCategory.HTTP_ERROR
                    link_info.error_message = f"HTTP status code {response.status_code}"
            except httpx.TimeoutException:
                link_info.status = ValidationResult.INVALID
                link_info.error_category = ErrorCategory.REQUEST_TIMEOUT
                link_info.error_message = f"Request timed out after {self.settings.timeout}s."
            except httpx.RequestError as e:
                link_info.status = ValidationResult.INVALID
                link_info.error_category = ErrorCategory.HTTP_ERROR
                link_info.error_message = f"HTTP request error: {str(e)}"
            except Exception as e: # Catch any other error during request
                link_info.status = ValidationResult.ERROR
                link_info.error_category = ErrorCategory.GENERIC_VALIDATION_ERROR
                link_info.error_message = f"Unexpected error during validation: {str(e)}"

        elif parsed_url.scheme in ["", "file"]: # Relative path or local file
            if parsed_url.scheme == "file":
                target_path_str = parsed_url.path
            else: # Relative path
                # If URL is like '../other/file.md#section'
                path_part = url.split('#')[0]
                target_path_str = urljoin(str(base_dir.joinpath(source_file.name)), path_part)
            
            target_path = Path(target_path_str).resolve()

            if not target_path.exists():
                link_info.status = ValidationResult.INVALID
                link_info.error_category = ErrorCategory.MISSING_LINK_TARGET
                link_info.error_message = f"Relative link target not found: {target_path}"
            # TODO: Add check for section anchors if #fragment is present
        
        elif parsed_url.scheme in ["mailto", "tel"]:
            pass # Typically, these are considered valid if structurally sound.
        else:
            link_info.status = ValidationResult.INVALID
            link_info.error_category = ErrorCategory.INVALID_LINK_STRUCTURE
            link_info.error_message = f"Unsupported URL scheme: {parsed_url.scheme}"

        self._results.append(link_info)
        return link_info

    async def _process_file(self, file_path: Path, base_dir: Path) -> None:
        """Reads a file and validates all links found within it."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            # Report error for this file
            self._results.append(LinkInfo(
                url=str(file_path), 
                source_file=file_path, 
                status=ValidationResult.ERROR,
                error_category=ErrorCategory.GENERIC_VALIDATION_ERROR,
                error_message=f"Could not read file: {e}"
            ))
            return

        # Basic regex for Markdown links: [text](url) or ![alt text](url)
        # Does not handle reference links or links with titles well.
        markdown_link_regex = re.compile(r"(?:!\[[^\]]*\]|\[[^\]]+\])\(([^)]+?)\)")
        
        tasks = []
        for match in markdown_link_regex.finditer(content):
            url = match.group(1)
            # Line number extraction would require more complex parsing
            tasks.append(self._validate_single_url(url, file_path, base_dir))
        
        await asyncio.gather(*tasks)

    async def validate_across_files_async(self, file_paths: List[Path], base_dir: Path) -> None:
        """Validates links found in a list of files."""
        self._results = [] # Reset results for this run
        self._processed_urls = set()
        
        await asyncio.gather(*(self._process_file(fp, base_dir) for fp in file_paths))
        await self.client.aclose() # Close the httpx client

    async def validate_directory_async(self, directory_path: Path) -> None:
        """Validates links in all markdown files within a directory (recursively)."""
        self._results = [] # Reset results
        self._processed_urls = set()

        markdown_files = list(directory_path.rglob("*.md")) + list(directory_path.rglob("*.markdown"))
        
        await asyncio.gather(*(self._process_file(fp, directory_path) for fp in markdown_files))
        await self.client.aclose()

    def generate_report(self) -> Dict[str, Any]:
        """Generates a dictionary report of the validation results."""
        summary = {
            "total_links_checked": len(self._results),
            "valid_links": sum(1 for r in self._results if r.status == ValidationResult.VALID),
            "invalid_links": sum(1 for r in self._results if r.status == ValidationResult.INVALID),
            "ignored_links": sum(1 for r in self._results if r.status == ValidationResult.IGNORED),
            "errors_during_validation": sum(1 for r in self._results if r.status == ValidationResult.ERROR),
        }
        return {
            "summary": summary,
            "results": [r.model_dump(exclude_none=True) for r in self._results],
        }

    def generate_text_report(self, report_dict: Optional[Dict[str, Any]] = None) -> str:
        """Generates a human-readable text report."""
        if report_dict is None:
            report_dict = self.generate_report()

        lines = ["Link Validation Report"]
        lines.append("=" * len(lines[0]))
        lines.append("\nSummary:")
        for key, value in report_dict["summary"].items():
            lines.append(f"  {key.replace('_', ' ').capitalize()}: {value}")
        
        lines.append("\nDetails:")
        if not report_dict["results"]:
            lines.append("  No links processed or found.")
        
        for result in report_dict["results"]:
            lines.append(f"  - URL: {result['url']}")
            lines.append(f"    Source: {result['source_file']}")
            lines.append(f"    Status: {result['status']}")
            if result.get('error_category'):
                lines.append(f"    Category: {result['error_category']}")
            if result.get('error_message'):
                lines.append(f"    Message: {result['error_message']}")
            if result.get('http_status_code'):
                lines.append(f"    HTTP Status: {result['http_status_code']}")
            lines.append("") # Blank line for readability
        return "\n".join(lines)

    def save_report(self, report_dict: Dict[str, Any], output_path: Path, format: str = "text") -> None:
        """Saves the report to a file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "text":
            content = self.generate_text_report(report_dict)
            output_path.write_text(content, encoding="utf-8")
        elif format == "json":
            import json # Standard library
            content = json.dumps(report_dict, indent=2)
            output_path.write_text(content, encoding="utf-8")
        # elif format == "html": # Placeholder for HTML report
        #     raise NotImplementedError("HTML report format is not yet implemented.")
        else:
            raise ValueError(f"Unsupported report format: {format}. Supported formats: 'text', 'json'.")

# Need Pydantic's BaseModel for LinkInfo
from pydantic import BaseModel, Field
from typing import Optional

class LinkInfo(BaseModel):
    url: str
    source_file: Path
    line_number: Optional[int] = None
    status: ValidationResult = ValidationResult.VALID
    error_category: Optional[ErrorCategory] = None
    error_message: Optional[str] = None
    http_status_code: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True # For Path objects
        use_enum_values = True # Serialize enums to their values
