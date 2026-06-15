# A Python implementation of the DSPAM spam filter.

This repository contains a Python implementation of the DSPAM spam filter, which is a machine learning-based spam filtering system that uses a Bayesian approach to classify emails as spam or innocent. The original DSPAM was written in C and was widely used in the early 2000s, but it has since become outdated and is no longer maintained. This implementation aims to provide a modern, modular, and extensible version of DSPAM that can be easily adapted to different use cases and integrated into various applications.

Not all features will be implemented in the initial version, but the core functionality of tokenization, training, and classification will be included. The modular architecture will allow for easy addition of new features and improvements over time.

# Usage

The `python-dspam` package has only very limited functionality, as it's supposed to be extended by plugin that implement more complex features. The builtin plugins are:
- a plain text parser
- a simple word tokenizer
- a simple trainer that only counts token frequencies
- a simple classifier that uses the token frequencies to classify new input data
- token storage is only available as a JSON file saved to disk

## Installation

To install the package, you can use pip:

```bash
pip install git+https://github.com/whyscream/python-dspam.git
```

## Configuration

The package can be configured using a simple configuration file (e.g. `config.toml`) that specifies the settings for the various plugins (e.g. tokenization strategy, training algorithm, classification threshold, etc.). It's also possible to change settings using environment variables, which will override the settings in the configuration file.

The configuration file is read from `$XDG_CONFIG_HOME/python-dspam/config.toml`, or from `~/.config/python-dspam/config.toml` if `$XDG_CONFIG_HOME` is not set. The configuration options should be available in a future commandline option which will dump the current or default config as toml file to stdout. For now, you'll need to check the source code (`src/dspam/settings.py`) for details.

There is one plugin implemented in the plugins directory, which is a parser for email messages. This plugin can be installed by running `pip install dspam-plugin-email`. To configure the email parser, set in the configuration file:

```toml
[dspam.parser]
plugin = "email"
```

Alternatively, use the environment variable `DSPAM_PARSER_PLUGIN=email` to override the configuration file and default setting.

## Command line interface

The package provides a simple command line interface (CLI) for training and classifying input data. The CLI is implemented in the `dspam` command, which can be run from the terminal.

E,g, to train the classifier using input data, run:

```bash
dspam train -c [innocent|ham] -f <path/to/input_file>
```

The CLI should be very self-documenting, and you can use the `--help` option to see the available commands and options.

# Roadmap

In the future, I plan to implement some of the following features (maybe not all of them, and in no particular order):

- [x] Basic architecture and plugin system
- [x] Basic plugins for tokenization, training, and classification
- [x] Simple CLI for training and classification
- [ ] Support for additional input formats (e.g. email messages, JSON, etc.) through plugins
- [ ] Support for additional tokenization strategies (e.g. n-grams, character-based, etc.) through plugins
- [ ] Support for additional storage backends for the trained model through plugins (e.g. SQLite, Redis, SQL, etc.)
- [ ] Support for output formats (e.g. JSON, XML, etc.)
- [ ] More advanced training algorithms (e.g. smoothing, feature selection, etc.)
- [ ] More advanced classification algorithms (e.g. ensemble methods, etc.)
- [ ] Integration with other applications (e.g. milter interface for email servers, etc.)
- [ ] User and group management for multi-user environments

# Plugin system

The plugin system is designed to be flexible and extensible, allowing for easy addition of new features and improvements over time. The core of the plugin system is based on the concept of "entry points", which are defined in the `pyproject.toml` file and allow for dynamic discovery and loading of plugins at runtime.

## Available plugin types

- `parser`: responsible for parsing the input data (e.g. plain text, email messages) and extracting the relevant information (e.g. headers, body, etc.) for tokenization and classification.
- `tokenizer`: responsible for tokenizing the input data (e.g. email messages) into a format that can be used for training and classification.
- `trainer`: responsible for training the model using the tokenized data and the specified training algorithm.
- `classifier`: responsible for classifying new input data using the trained model and the specified classification algorithm.
- `storage`: responsible for storing the trained model and any relevant metadata (e.g. training data) in a persistent storage backend (e.g. SQLite, Redis, SQL, etc.).

## Plugin development

You can add new plugins by creating a new Python package that defines the plugin and its entry point in the `pyproject.toml` file. The plugin should implement the required interface for the specified plugin type.

The email parser plugin in the `plugins/dspam-plugin-email` directory is an example of how to implement a plugin.

### Plugin implementation requirements:

#### pip installable

The plugin must be a valid Python package that can be installed using pip.

#### Entry point

The plugin must define an entry point in the `pyproject.toml` file that specifies the plugin type and the module that implements the plugin. E.g. for a tokenizer plugin, that uses the `foobar` tokenization technique, the entry point would look like this:

```toml
[project.entry-points."dspam.tokenizer"]
foobar = "dspam_plugin_foobar:FoobarTokenizer"
```
After installation in the same virtualenv as the `python-dspam` package, the plugin should show up in the output of the command `dspam plugin list`.

#### Plugin class

A plugin consists of a single class that is loaded by the plugin manager. This plugin class must subclass the appropriate base class for the plugin type (e.g. `dspam.tokenize.Tokenizer` for a tokenizer plugin) and implement the required methods for that plugin type.

#### API version

The plugin must define the `API_VERSION` attribute, which specifies the version of the plugin API that the plugin is compatible with. This allows for backward compatibility and ensures that plugins will continue to work even if the core DSPAM code is updated in the future.

#### Settings

The plugin may define additional settings that can be configured in the `config.toml` file or via environment variables. To implement this, you need to define a Settings class that subclasses the appropriate settings class from `dspam.settings`. E.g. for a tokenizer plugin, you would define a `FoobarTokenizerSettings` class that subclasses `dspam.settings.TokenizerSettings`.

The settings system uses `pydantic-settings` under the hood, so you can use all the features of that library. The resulting settings object will combine the core settings from `dspam.settings` with the plugin-specific settings from your plugin, and will be passed to your plugin.

Please ensure that no settings from the core `dspam.settings` are overridden by your plugin, as this could lead to unexpected behavior and compatibility issues with other plugins.

# Original DSPAM resources

- Most of DSPAM's wiki docs are gone, but this seems a fair backup: https://wiki.ledhed.net/index.php?title=Category:DSpam
- The original source code: https://sourceforge.net/p/dspam/code/ci/master/tree/
- And some forks/mirrors, sometimes with additions:  https://github.com/ensc/dspam, https://github.com/Ilgrim/dspam

# Motivation

When DSPAM was still actively maintained, I was part of the small group of maintainers, contributing small fixes to documentation and code (but not to the core, as I never learned C). I have fond memories of working on DSPAM, and I think it would be a fun project to revisit and modernize it in Python. I also think that there is still value in the core ideas behind DSPAM, and that a modern implementation could be useful for various applications (e.g. email filtering, content moderation, etc.).

It's also a fun project for me to learn a bit more about machine learning, natural language processing, and software architecture in Python. And a way to play around with various concepts in Python that I haven't investigated fully:
  - async programming (asyncio, trio, `async/await`)
  - plugin architecture (entry points, pluggy, https://oneuptime.com/blog/post/2026-01-30-python-plugin-systems/view)
  - dependency injection (https://github.com/sfermigier/awesome-dependency-injection-in-python)
  - CLI alternatives to `argparse` or `click`

# License

This project is licensed under the BSD-3-Clause License. See the [LICENSE](LICENSE) file for details.

Note that the original DSPAM code was licensed under the **GNU AFFERO GENERAL PUBLIC LICENSE Version 3**, but this implementation is a complete rewrite in Python. It does not contain any code from the original DSPAM project, only ideas , terminology and concepts.
