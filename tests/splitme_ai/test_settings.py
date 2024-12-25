from pathlib import Path

import pytest

from splitme_ai.settings import SplitmeSettings


def test_default_values():
    settings = SplitmeSettings()
    assert settings.case_sensitive is False
    assert settings.exclude_patterns == set()
    assert settings.generate_mkdocs is False
    assert settings.heading_level == "##"
    assert settings.output_dir == Path(".splitme-ai/output")


# def test_process_mkdocs_disabled(mocker):
#     settings = SplitmeSettings(generate_mkdocs=False)
#     mock_generate_config = mocker.patch(
#         "splitme_ai.generators.mkdocs_config.MkDocsConfig.generate_config"
#     )
#     settings.process_mkdocs()
#     mock_generate_config.assert_not_called()


# def test_process_mkdocs_enabled(mocker):
#     settings = SplitmeSettings(generate_mkdocs=True)
#     mock_generate_config = mocker.patch(
#         "splitme_ai.generators.mkdocs_config.MkDocsConfig.generate_config"
#     )
#     settings.process_mkdocs()
#     mock_generate_config.assert_called_once()


if __name__ == "__main__":
    pytest.main()
