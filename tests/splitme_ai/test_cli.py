from pathlib import Path

from splitme_ai.cli import SplitmeSettings


def test_default_values():
    settings = SplitmeSettings()
    assert settings.case_sensitive is False
    assert settings.exclude_patterns == set()
    assert settings.generate_mkdocs is False
    assert settings.heading_level == "##"
    assert settings.output_dir == Path(".splitme-ai/output")
