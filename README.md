# instaxtractor

A small tool to extract Instagram reel media and meta data from HARs.

## Usage

```
Usage: instaxtractor [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

  iNsTa-X-TrAcToR

Options:
  -v, --log-level          logging verbosity, counting up. [0]
  -l, --log_file FILENAME
  -i, --input TEXT         Globbing pattern [*.har]
  -o, --output DIRECTORY   results directory [results/]
  --help                   Show this message and exit.

Commands:
  posts  collect post data
  reels  collect reel data
```

## Developer Installation

1. Install `poetry` if you don't have it: `pipx install poetry`.
2. Clone this repo, go into the repo's folder.
3. Install the dependencies with `poetry install` and spawn a shell in your new virtual environment with `poetry shell`.
3. To run tests type `pytest`, to try instaxtractor run `instaxtractor --help`.

---

[Philipp Kessling](mailto:p.kessling@leibniz-hbi.de) under MIT.
