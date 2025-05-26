# koppiebot

A headless, retrieval augmented generation chatbot.  Meant to operate alongside a headless blog, and provide context for the blog posts.

## Installation

```shell
git pull origin main
pip install -r requirements.txt
```

### Environment Variables

You will need to set the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key.  Get one [here](https://platform.openai.com/account/api-keys)
- `ALLOW_ORIGINS`: A comma-separated list of origins that are allowed to access the API.  For example:

```shell
ALLOW_ORIGINS="['https://kands10.ddev.site:3000', 'https://koplowiczandsons.com']"
```

## Running as a Linux Service

To run koppiebot as a systemd service on Linux:

1. Create a systemd service file, e.g. `/etc/systemd/system/koppiebot.service`:

```ini
[Unit]
Description=Koppiebot Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/koppiebot
ExecStart=/usr/bin/python3 /path/to/koppiebot/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

2. Reload systemd and enable the service:

```shell
sudo systemctl daemon-reload
sudo systemctl enable koppiebot
sudo systemctl start koppiebot
```

Replace `/path/to/koppiebot` and `YOUR_USERNAME` as appropriate for your setup.

## Updating

Koppiebot is not automatically updated; it relies on manual updates, thanks to the `embed.py` script.  This script will do a fresh import from the blog, and then process all blog posts into a vector database, which is stored in `embeddings.csv`.

The script takes one argument, which is the URL of the CSV file to import.  If no argument is provided, the default URL is used.

```shell
python embed.py https://d10.koplowiczandsons.com/export
systemctl restart koppiebot
```

Notes: 
- The embedding script takes about a minute to run (on an M4 processor)
- koppiebot won't "know" the new information until the service is restarted
