# Python DSPAM email plugin

Plugin for python-dspam for handling email messages.

## Setup

```shell
pip install python-dspam-plugin-email
```

After installation, enable the plugin by setting env var `DSPAM_PARSER_PLUGIN=email` or by adding the following lines to your `config.toml`:

```toml
[dspam.parser]
plugin = "email"
```

# License

This project is licensed under the BSD-3-Clause License. See the [LICENSE](../../LICENSE) file for details.
