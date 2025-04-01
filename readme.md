# koppiebot

It's armed with Koppie's knowledge, and absolutely nothing else.

## Installation

We're currently operating out of the `kands` branch:

```shell
git pull origin kands
pip install -r requirements.txt
```

## Updating

Koppiebot is not automatically updated; it relies on manual updates, thanks to the `embed.py` script.  This script will do a fresh import from the blog, and then process all blog posts into a vector database, which is stored in `embeddings.csv`.

```shell
python embed.py
systemctl restart koppiebot
```

Notes: 
- The embedding script takes about a minute to run (on an M4 processor)
- koppiebot won't "know" the new information until the service is restarted
