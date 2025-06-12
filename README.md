# Scribd Downloader

<p align="center">
  <a href="https://github.com/bisnuray/ScribdDownloader/stargazers"><img src="https://img.shields.io/github/stars/bisnuray/ScribdDownloader?color=blue&style=flat" alt="GitHub Repo stars"></a>
  <a href="https://github.com/bisnuray/ScribdDownloader/issues"><img src="https://img.shields.io/github/issues/bisnuray/ScribdDownloader" alt="GitHub issues"></a>
  <a href="https://github.com/bisnuray/ScribdDownloader/pulls"><img src="https://img.shields.io/github/issues-pr/bisnuray/ScribdDownloader" alt="GitHub pull requests"></a>
  <a href="https://github.com/bisnuray/ScribdDownloader/graphs/contributors"><img src="https://img.shields.io/github/contributors/bisnuray/ScribdDownloader?style=flat" alt="GitHub contributors"></a>
  <a href="https://github.com/bisnuray/ScribdDownloader/network/members"><img src="https://img.shields.io/github/forks/bisnuray/ScribdDownloader?style=flat" alt="GitHub forks"></a>
</p>

<p align="center">
  <em>Scribd Downloader is a Python-based Telegram bot capable of downloading Scribd documents as PDF files using cookies from a premium account.</em>
</p>

## Features

- Download Scribd documents as PDFs.
- Support for various Scribd URL formats (document, doc, presentation).
- Utilizes premium account cookies for access.
- Inline download link with document details (title, author).
- Logging for debugging and monitoring.
- Deployable on Heroku, Docker, or VPS.

## Requirements

- Python 3.10
- Pyrofork (`pyrogram` fork for Telegram MTProto API)
- A Telegram bot token.
- Access to a Scribd premium account (for cookies).
- A `cookie.json` file with premium account cookies.

1. Install the required dependencies:

    ```bash
    pip3 install -r requirements.txt
    ```

## Changelog

- **2025-06-12**: Migrated from `aiogram` to `pyrofork` for improved Telegram API performance and reliability.
- **2025-06-12**: Added support for Heroku deployment with `app.json` and environment variable management via `.env`.
- **2025-06-12**: Introduced Docker and Docker Compose support for containerized deployment.
- **2025-06-12**: Added VPS deployment instructions with `screen` for persistent bot operation.

## Deploy the Bot

### Heroku Deployment

1. Click the button below to deploy to Heroku:
   [![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/bisnuray/ScribdDownloader)
2. Set the environment variables (`API_ID`, `API_HASH`, `BOT_TOKEN`) in the Heroku dashboard or via CLI:
   ```bash
   heroku config:set API_ID=your_api_id API_HASH=your_api_hash BOT_TOKEN=your_bot_token
   ```
3. Ensure the `cookie.json` file is uploaded to the Heroku app (e.g., via Git or Heroku CLI).

### Deploy with Docker Compose

Ensure Docker and Docker Compose are installed. The bot will run in a containerized environment with dependencies managed automatically.

```bash
docker compose up --build --remove-orphans
```

To stop the bot:

```bash
docker compose down
```

### Deploy on VPS with Screen

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/bisnuray/ScribdDownloader
   cd ScribdDownloader
   ```
2. Install Python 3.10 and dependencies:
   ```bash
   sudo apt update
   sudo apt install python3.10 python3-pip
   pip3 install -r requirements.txt
   ```
3. Set up environment variables in `.env` or export them:
   ```bash
   export API_ID=your_api_id
   export API_HASH=your_api_hash
   export BOT_TOKEN=your_bot_token
   ```
4. Create a `screen` session to run the bot persistently:
   ```bash
   screen -S scribd_bot
   python3 main.py
   ```
5. Detach from the screen session with `Ctrl+A` followed by `d`.
6. To reattach to the session later:
   ```bash
   screen -r scribd_bot
   ```
7. To stop the bot, reattach to the session and press `Ctrl+C`.

### Setting Up the Bot

1. Create a new bot with [@BotFather](https://t.me/botfather) on Telegram to obtain the bot token.
2. Update the `.env` file or Heroku config vars with your `API_ID`, `API_HASH`, and `BOT_TOKEN`.
3. Ensure a valid `cookie.json` file with premium Scribd account cookies is present in the project directory.

### Running the Bot Locally

Execute the script to start the bot:

```bash
python3 main.py
```

## Usage 🛠️

The bot supports the following commands:

- `/start`: Initializes the bot and provides a welcome message.
- Send a Scribd URL (e.g., `https://www.scribd.com/document/123456789`) to receive a download link.

## Author 📝

- Name: Bisnu Ray
- Telegram: [@SmartBisnuBio](https://t.me/SmartBisnuBio)

Feel free to reach out for questions or feedback.

