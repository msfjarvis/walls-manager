# walls-manager

Tooling used to maintain my public collection of desktop walls

## Usage

- Create a `config.ini` files based on the sample provided in this repository
- Run `manager.py` with the needed arguments

```
$ ./manager.py -h
usage: manager.py [-h] [-d] [-m] [-s SYNC]

optional arguments:
  -h, --help            show this help message and exit
  -d, --details         List statistics of local directory
  -m, --markdown        Output file names as Markdown links
  -s SYNC, --sync SYNC  Set direction of sync, local for pull and remote for
                        push
```
