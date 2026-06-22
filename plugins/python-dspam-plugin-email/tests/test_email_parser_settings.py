# SPDX-License-Identifier: BSD-3-Clause

from dspam_plugin_email.parse import EmailParserSettings


def test_settings_default():
    plugin_settings = EmailParserSettings()
    assert plugin_settings.ignore_headers == []


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("DSPAM_PARSER_IGNORE_HEADERS", '["from-env"]')

    plugin_settings = EmailParserSettings()
    assert plugin_settings.ignore_headers == ["from-env"]


def test_settings_from_config_file(empty_config, monkeypatch):
    config_file = empty_config / "python-dspam/config.toml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("""
    [dspam.parser]
    ignore_headers = ["from-config-file"]
    """)

    monkeypatch.setitem(EmailParserSettings.model_config, "toml_file", config_file)

    plugin_settings = EmailParserSettings()
    assert plugin_settings.ignore_headers == ["from-config-file"]
