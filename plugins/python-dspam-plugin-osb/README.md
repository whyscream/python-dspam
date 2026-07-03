# Python DSPAM OSB tokenizer plugin

Plugin for python-dspam providing OSB tokenization.

## Setup

```shell
pip install python-dspam-plugin-osb
```

After installation, enable the plugin by setting env var `DSPAM_PARSER_TOKENIZER=chain` or by adding the following lines to your `config.toml`:

```toml
[dspam.tokenizer]
plugin = "chain"
```

## Orthogonal sparse bigrams (OSB)

Using orthogonal sparse bigrams was originally introduced in DSPAM based on an idea from Bill Yerazunis.

The generation of OSB tokens is based on the SBPH algorithm, but produces fewer tokens. Where SBPH generates tokens for all permutations in a sliding window, OSB keeps only permutations containing the latest word (e.g. the last single word token in the sliding window)

An example comparison based on the content `The quick brown fox jumps over the fence` with a sliding window of 5:

| Unigram/single-word tokens | OSB tokens        |
|----------------------------|-------------------|
| The                        | The # # # jumps   |
| quick                      | # quick # # jumps |
| brown                      | # # brown # jumps |
| fox                        | # # # fox jumps   |
| jumps                      | quick # # # over  |
| over                       | # brown # # over  |
| the                        | # # fox # over    |
| fence                      | # # # jumps over  |
|                            | brown # # # the   |
|                            | # fox # # the     |
|                            | # # jumps # the   |
|                            | # # # over the    |
|                            | fox # # # fence   |
|                            | # jumps # # fence |
|                            | # # over # fence  |
|                            | # # # the fence   |


Detailed explanation available at: https://www.siefkes.net/papers/winnow-spam.pdf



# License

This project is licensed under the BSD-3-Clause License. See the [LICENSE](../../LICENSE) file for details.
