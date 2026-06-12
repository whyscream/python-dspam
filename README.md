# python-dspam

A Python implementation of the DSPAM spam filter.

And a way to play around with various concepts in python that I haven't investigated fully:

- `asyncio` and `async`/`await`
- plugin architecture (entry points, pluggy, https://oneuptime.com/blog/post/2026-01-30-python-plugin-systems/view)
- dependency injection (https://github.com/sfermigier/awesome-dependency-injection-in-python)
- CLI alternatives to `argparse` or `click`

## Original DSPAM resources

- Most of DSPAM's wiki docs are gone, but this seems a fair backup: https://wiki.ledhed.net/index.php?title=Category:DSpam
- Mirrors of the original source code: https://sourceforge.net/p/dspam/code/ci/master/tree/, https://github.com/ensc/dspam, https://github.com/Ilgrim/dspam


## Architecture

- The original DSPAM is a monolithic C application. This implementation will be modular, with a plugin architecture for the various components (tokenization, training, classification, etc.). The core will be responsible for orchestrating the flow of data between the plugins.
- The core will also handle the storage of the trained model, which will be a simple key-value store (e.g. a dictionary) that maps tokens to their spam/innocent probabilities. This will be persisted to disk using a simple serialization format (e.g. JSON or pickle).
- The tokenization plugin will be responsible for extracting tokens from the email content. This will be a simple implementation that splits the email into words and normalizes them (e.g. lowercasing, removing punctuation).
- The training plugin will be responsible for updating the model based on the tokens extracted from the email and whether it is spam or innocent. This will involve updating the counts of how many times each token has been seen in spam and innocent emails, and calculating the probabilities accordingly.
- The classification plugin will be responsible for classifying new emails based on the tokens extracted and the probabilities in the model. This will involve calculating the overall probability that the email is spam based on the tokens it contains and the probabilities in the model, and comparing it to a threshold to make a final classification.
-

### Classification flow

For classification, the basic flow of data through the system will be as follows:

- Read input data (plain text data, an email message). More formats can be supported by implementing additional input plugins.
- Tokenize the content using the tokenization plugins. This will produce a list of tokens that represent the data content. Several tokenizer plugins can be implemented to support different tokenization strategies (e.g. word-based, character-based, n-grams, etc.). Original DSPAM supported
- Classify the tokens using the classification plugin, which will use the trained model to calculate the probability that the email is spam. This will involve looking up the probabilities for each token in the model and combining them to get an overall probability for the data.
- Output the classification result (spam or innocent) and the associated probability. This can be done through a simple CLI output, or through a more complex output plugin that supports different formats (e.g. JSON, XML, etc.).
