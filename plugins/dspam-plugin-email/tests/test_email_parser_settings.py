from dspam_plugin_email.parse import EmailParserSettings


def test_settings_default():
    plugin_settings = EmailParserSettings()
    assert plugin_settings.ignore_headers == []


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("DSPAM_PLUGIN_PARSER_EMAIL_IGNORE_HEADERS", '["from-env"]')

    plugin_settings = EmailParserSettings()
    assert plugin_settings.ignore_headers == ["from-env"]


def test_settings_from_config_file(empty_config):
    config_file = empty_config / "python-dspam/config.toml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("""
    [dspam.plugin.parser.email]
    ignore_headers = ["from-config-file"]
    """)

    plugin_settings = EmailParserSettings()
    assert plugin_settings.ignore_headers == ["from-config-file"]
