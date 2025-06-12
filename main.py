import re
import aiohttp
import json
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN
from utils import LOGGER

# Configure logging
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workers=1000)

# Function to load cookies from a file
def load_cookies(file_path):
    LOGGER.info("Loading cookies from file: %s", file_path)
    try:
        with open(file_path, 'r') as file:
            cookies_raw = json.load(file)
            if isinstance(cookies_raw, dict):
                LOGGER.debug("Cookies loaded as dictionary")
                return cookies_raw
            elif isinstance(cookies_raw, list):
                cookies = {}
                for cookie in cookies_raw:
                    if 'name' in cookie and 'value' in cookie:
                        cookies[cookie['name']] = cookie['value']
                LOGGER.debug("Cookies converted from list to dictionary")
                return cookies
            else:
                LOGGER.error("Unsupported cookies format in %s", file_path)
                raise ValueError("Cookies are in an unsupported format.")
    except Exception as e:
        LOGGER.error("Failed to load cookies: %s", str(e))
        raise

# Function to extract necessary information from the first response
def extract_information(response_json):
    LOGGER.info("Extracting information from response JSON")
    try:
        document = response_json.get('document', {})
        title = document.get('title', '**Not Available**')
        access_key = document.get('access_key', '**Not Available**')
        author = document.get('author', {})
        author_name = author.get('name', '**Not Available**')
        receipt_url = response_json.get('receipt_url', '**Not Available**')

        extracted_info = {
            "title": title,
            "access_key": access_key,
            "author_name": author_name,
            "receipt_url": receipt_url
        }
        LOGGER.debug("Extracted information: %s", extracted_info)
        return extracted_info
    except Exception as e:
        LOGGER.error("Error extracting information: %s", str(e))
        raise

# Async function to process Scribd URL
async def process_scribd_url_task(client, message, url, document_id, chat_id):
    LOGGER.info("Processing Scribd URL: %s for document_id: %s", url, document_id)
    # Send a loading message
    try:
        loading_message = await client.send_message(
            chat_id=chat_id,
            text="**Processing your request... ⏳**",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        LOGGER.info("Sent loading message to chat_id: %s", chat_id)
    except Exception as e:
        LOGGER.error("Failed to send loading message: %s", str(e))
        return

    try:
        # Load cookies
        cookies = load_cookies('cookie.json')  # Ensure the 'cookie.json' file is in the correct path
        first_url = f'https://www.scribd.com/doc-page/download-receipt-modal-props/{document_id}'
        LOGGER.debug("Making first request to: %s", first_url)

        async with aiohttp.ClientSession(cookies=cookies) as session:
            # First request
            async with session.get(first_url) as response:
                LOGGER.debug("First request status: %s", response.status)
                if response.status == 200:
                    info = extract_information(await response.json())
                    title = info['title']
                    author_name = info['author_name']
                    receipt_url = info['receipt_url']

                    # Construct the second URL using the extracted access_key and URL ID
                    second_url = f"https://www.scribd.com/document_downloads/{document_id}/?secret_password={info['access_key']}&extension=pdf"
                    LOGGER.debug("Making second request to: %s", second_url)

                    # Second request
                    async with session.get(second_url, allow_redirects=False) as response:
                        LOGGER.debug("Second request status: %s", response.status)
                        if response.status in [301, 302]:
                            redirect_url = response.headers.get('Location')
                            if redirect_url:
                                LOGGER.debug("Redirect URL found: %s", redirect_url)
                                # Third request to the redirect URL
                                async with session.get(redirect_url, allow_redirects=False) as third_response:
                                    LOGGER.debug("Third request status: %s", third_response.status)
                                    if third_response.status in [301, 302]:
                                        final_redirect_url = third_response.headers.get('Location')
                                        if final_redirect_url:
                                            LOGGER.info("Final redirect URL obtained: %s", final_redirect_url)
                                            # Create the message text
                                            message_text = (
                                                f"**Scribd Download Link Ready! ✅**\n"
                                                f"**━━━━━━━━━━━━━━━━━━━━━━**\n"
                                                f"**Title**: {title}\n"
                                                f"**Author**: {author_name}\n"
                                                f"**Main URL**: [Click Here]({receipt_url})\n"
                                                f"**Download Link** : [Download Now]({final_redirect_url})\n"
                                                f"**━━━━━━━━━━━━━━━━━━━━━━**\n"
                                                f"**Powered by**: **@TheSmartDev**"
                                            )
                                            download_button = InlineKeyboardMarkup(
                                                [[InlineKeyboardButton("Download Now", url=final_redirect_url)]]
                                            )

                                            # Send the message with the inline button
                                            await client.send_message(
                                                chat_id=chat_id,
                                                text=message_text,
                                                reply_markup=download_button,
                                                parse_mode=ParseMode.MARKDOWN,
                                                disable_web_page_preview=True
                                            )
                                            LOGGER.info("Successfully sent download link to chat_id: %s", chat_id)
                                        else:
                                            LOGGER.warning("No final redirect URL found")
                                            await client.send_message(
                                                chat_id=chat_id,
                                                text="**Sorry Bro SCRIBD API Dead**",
                                                parse_mode=ParseMode.MARKDOWN,
                                                disable_web_page_preview=True
                                            )
                                    else:
                                        LOGGER.warning("Third request failed with status: %s", third_response.status)
                                        await client.send_message(
                                            chat_id=chat_id,
                                            text="**Sorry Bro SCRIBD API Dead**",
                                            parse_mode=ParseMode.MARKDOWN,
                                            disable_web_page_preview=True
                                        )
                            else:
                                LOGGER.warning("No redirect URL found in second request")
                                await client.send_message(
                                    chat_id=chat_id,
                                    text="**Sorry Bro SCRIBD API Dead**",
                                    parse_mode=ParseMode.MARKDOWN,
                                    disable_web_page_preview=True
                                )
                        else:
                            LOGGER.warning("Second request failed with status: %s", response.status)
                            await client.send_message(
                                chat_id=chat_id,
                                text="**Sorry Bro SCRIBD API Dead**",
                                parse_mode=ParseMode.MARKDOWN,
                                disable_web_page_preview=True
                            )
                else:
                    LOGGER.warning("First request failed with status: %s", response.status)
                    await client.send_message(
                        chat_id=chat_id,
                        text="**Sorry Bro SCRIBD API Dead**",
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True
                    )

    except Exception as e:
        LOGGER.error("Error processing Scribd URL: %s", str(e))
        await client.send_message(
            chat_id=chat_id,
            text="**Sorry Bro SCRIBD API Dead**",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

    # After processing is complete, delete the loading message
    try:
        await loading_message.delete()
        LOGGER.info("Deleted loading message from chat_id: %s", chat_id)
    except Exception as e:
        LOGGER.warning("Failed to delete loading message: %s", str(e))

# Start command handler
@app.on_message(filters.command("start") & (filters.private | filters.group))
async def start_command(client, message):
    LOGGER.info("Received /start command from user: %s", message.from_user.id)
    full_name = message.from_user.first_name
    if message.from_user.last_name:
        full_name += f" {message.from_user.last_name}"
    start_message = (
        f"**Hi {full_name}! Welcome to this bot**\n"
        f"**━━━━━━━━━━━━━━━━━━━━━━**\n"
        f"**ScribdDL** is your ultimate toolkit on Telegram, packed with AI tools, educational resources, downloaders, temp mail, crypto utilities, and more. Simplify your tasks with ease!\n"
        f"**━━━━━━━━━━━━━━━━━━━━━━**\n"
        f"**Don't forget to [JoinNow](t.me/TheSmartDev) for updates!**"
    )
    update_button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Update Channel", url="t.me/TheSmartDev")]]
    )
    try:
        await client.send_message(
            chat_id=message.chat.id,
            text=start_message,
            reply_markup=update_button,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        LOGGER.info("Sent start message to chat_id: %s", message.chat.id)
    except Exception as e:
        LOGGER.error("Failed to send start message: %s", str(e))

# Scribd link handler
@app.on_message(filters.regex(r'scribd\.com/(document|doc|presentation)/(\d+)' ) & (filters.private | filters.group))
async def process_scribd_url(client, message):
    chat_id = message.chat.id
    url = message.text
    LOGGER.info("Received Scribd URL: %s from chat_id: %s", url, chat_id)

    # Extract document ID from the URL
    match = re.search(r'scribd\.com/(document|doc|presentation)/(\d+)', url)
    if not match:
        LOGGER.warning("Invalid Scribd URL provided: %s", url)
        await client.send_message(
            chat_id=chat_id,
            text="**Please provide a valid Scribd URL**",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return

    document_id = match.group(2)
    LOGGER.debug("Extracted document_id: %s", document_id)

    # Run the processing task asynchronously
    asyncio.create_task(process_scribd_url_task(client, message, url, document_id, chat_id))
    LOGGER.info("Created task to process Scribd URL for document_id: %s", document_id)

# Start the bot
if __name__ == '__main__':
    LOGGER.info("Starting the bot")
    try:
        app.run()
        LOGGER.info("Bot stopped")
    except Exception as e:
        LOGGER.error("Bot crashed: %s", str(e))
