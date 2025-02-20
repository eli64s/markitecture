from pathlib import Path

from pydantic import AliasChoices, BaseModel, Field

from markitecture.metrics.analyzer import ReadabilityAnalyzer, ReadabilityMetrics
from markitecture.metrics.svg_generator import (
    BadgeStyle,
    MetricsSvgGenerator,
)
from markitecture.settings.validators import ExistingFilePath
from markitecture.utils.file_handler import FileHandler
from markitecture.utils.printer import RichPrinter

_printer = RichPrinter()


class MetricsCommand(BaseModel):
    """
    Generate reading time estimates and complexity metrics for markdown files.
    """

    input: ExistingFilePath = Field(
        ...,
        description="Path to the markdown file.",
        validation_alias=AliasChoices("i", "input"),
    )
    output: Path | None = Field(
        default=None,
        description=f"Path to save the SVG badge. If not specified, creates {input}_metrics.svg",
        validation_alias=AliasChoices("o", "output"),
    )
    output_dir: Path | None = Field(
        default=None,
        description="Directory to save all badge styles when using --style all",
        validation_alias=AliasChoices("d", "dir", "output-dir"),
    )
    insert: bool = Field(
        default=True,
        description="Insert metrics badge into the document.",
        validation_alias=AliasChoices("ins", "insert"),
    )
    position: str = Field(
        default="top",
        description="Position to insert badge (top/bottom).",
        validation_alias=AliasChoices("p", "pos", "position"),
    )
    style: BadgeStyle | str = Field(
        default=BadgeStyle.MODERN,
        description="Badge style (modern/compact/detailed/minimal/retro) or 'all' for all styles",
        validation_alias=AliasChoices("s", "style"),
    )

    def _generate_single_badge(
        self,
        metrics: ReadabilityMetrics,
        style: BadgeStyle,
        content: str,
        output_path: Path,
    ) -> None:
        """Generate a single badge style."""
        generator = MetricsSvgGenerator()
        svg_content = generator.generate_svg(metrics, style)

        # Save badge
        Path(output_path).write_text(svg_content, encoding="utf-8")
        _printer.print_info(f"Generated {style.value} style badge: {output_path}")

        # Insert if requested and this is the primary style
        if self.insert and style == self.style:
            doc_content = content
            svg_ref = f"![Reading Metrics]({output_path})"
            if self.position.lower() == "top":
                doc_content = f"{svg_ref}\n\n{content}"
            else:
                doc_content = f"{content}\n\n{svg_ref}"
            Path(self.input).write_text(doc_content, encoding="utf-8")
            _printer.print_info(f"Metrics badge added to document at: {self.position}")

    def _generate_all_badges(self, metrics: ReadabilityAnalyzer, content: str) -> None:
        """Generate badges in all available styles."""
        # Create output directory if needed
        output_dir = self.output_dir or Path(self.input).parent / "metrics_badges"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate each style
        for style in BadgeStyle:
            output_path = output_dir / f"metrics_{style.value}.svg"
            self._generate_single_badge(metrics, style, content, output_path)

        _printer.print_info(f"\nAll badge styles generated in: {output_dir}")

        # Generate preview HTML
        preview_path = output_dir / "preview.html"
        self._generate_preview_page(metrics, output_dir, preview_path)
        _printer.print_info(f"Preview page generated: {preview_path}")

    def _generate_preview_page(
        self, metrics: ReadabilityMetrics, badge_dir: Path, output_path: Path
    ) -> None:
        """Generate HTML preview page showing all badge styles."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Metrics Badge Styles - {self.input.name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            background: #f5f5f5;
        }}
        .badge-container {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #666;
            margin-top: 30px;
        }}
        .badge {{
            margin: 20px 0;
        }}
        .style-name {{
            color: #888;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <h1>Metrics Badge Styles</h1>
    <p>Document: <strong>{self.input.name}</strong></p>
"""

        # Add each badge
        for style in BadgeStyle:
            badge_path = f"metrics_{style.value}.svg"
            html += f'''
    <div class="badge-container">
        <div class="style-name">{style.value.title()} Style</div>
        <div class="badge">
            <img src="{badge_path}" alt="Metrics Badge - {style.value} Style">
        </div>
    </div>'''

        html += """
</body>
</html>"""

        output_path.write_text(html, encoding="utf-8")

    def cli_cmd(self) -> None:
        """Execute the metrics generation command."""
        _printer.print_info(f"Analyzing document metrics for: {self.input}")

        # Read content and generate metrics
        content = FileHandler().read(self.input)
        analyzer = ReadabilityAnalyzer()
        metrics = analyzer.analyze_document(content)

        # Generate badges based on style option
        if self.style == "all":
            self._generate_all_badges(metrics, content)
        else:
            output_path = self.output or Path(f"{self.input.stem}_metrics.svg")
            self._generate_single_badge(
                metrics, BadgeStyle(self.style), content, output_path
            )

        # Display metrics summary
        _printer.print_title("Document Metrics Summary")
        _printer.print_key_value_table(
            "Metrics",
            {
                "Reading Time": f"{metrics.reading_time_mins} minutes",
                "Word Count": f"{metrics.word_count:,}",
                "Complexity Score": f"{metrics.complexity_score}%",
                "Average Words/Sentence": f"{metrics.avg_words_per_sentence:.1f}",
                "Headings": f"{metrics.heading_count}",
                "Code Blocks": f"{metrics.code_block_count}",
                "Links": f"{metrics.link_count}",
                "Images": f"{metrics.image_count}",
            },
        )
