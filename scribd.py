"""
Author: Bisnu Ray
https://t.me/itsSmartDev
"""

import logging
import re
import requests
import asyncio
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import MessageToDeleteNotFound

# Initialize bot and dispatcher
bot_token = '1234567890:AAGNaKh6J5jrK4og9FWkiGR1jifbZjTniik'  # Replace with your bot's token
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

# Function to load cookies from a file
def load_cookies(file_path):
    with open(file_path, 'r') as file:
        cookies_raw = json.load(file)
        if isinstance(cookies_raw, dict):
            return cookies_raw
        elif isinstance(cookies_raw, list):
            cookies = {}
            for cookie in cookies_raw:
                if 'name' in cookie and 'value' in cookie:
                    cookies[cookie['name']] = cookie['value']
            return cookies
        else:
            raise ValueError("Cookies are in an unsupported format.")

# Function to extract necessary information from the first response
def extract_information(response_json):
    print(extract_information)
    document = response_json.get('document', {})
    title = document.get('title', 'Not Available')
    access_key = document.get('access_key', 'Not Available')
    author = document.get('author', {})
    author_name = author.get('name', 'Not Available')
    receipt_url = response_json.get('receipt_url', 'Not Available')

    return {
        "title": title,
        "access_key": access_key,
        "author_name": author_name,
        "receipt_url": receipt_url
    }

# Load cookies
cookies = load_cookies('cookie.json')

# First request
try:
    response = requests.get(first_url, cookies=cookies)
    if response.status_code == 200:
        info = extract_information(response.json())
        print("Title:", info['title'])
        print("Author Name:", info['author_name'])
        print("Receipt URL:", info['receipt_url'])

        # Construct the second URL using the extracted access_key and URL ID
        url_id = first_url.split('/')[-1]
        second_url = f"{base_second_url}{url_id}/?secret_password={info['access_key']}&extension=pdf"

        # Second request
        response = requests.get(second_url, cookies=cookies, allow_redirects=False)
        if response.status_code in [301, 302]:  # Check if it's a redirect
            redirect_url = response.headers.get('Location')
            if redirect_url:
                print("Redirect URL from second request:", redirect_url)

                # Third request to the redirect URL
                third_response = requests.get(redirect_url, cookies=cookies, allow_redirects=False)
                if third_response.status_code in [301, 302]:
                    final_redirect_url = third_response.headers.get('Location')
                    if final_redirect_url:
                        print("Final Redirect URL from third request:", final_redirect_url)
                    else:
                        print("No 'Location' header found in the third request.")
                else:
                    print("Third request status code:", third_response.status_code)
                    print("This URL didn't redirect as expected.")

            else:
                print("No redirect URL found in the headers of the second request.")
        else:
            print("Second request status code:", response.status_code)
            print("Response:")
            print(response.text)

    else:
        print("First request failed with status code:", response.status_code)
except Exception as e:
    print("An error occurred:", e)



@dp.message_handler(commands=['scribd']) # You Can Change the command scribd to any thing 
async def process_scribd_url(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Check if the URL is valid
    url = message.get_args()
    match = re.search(r'scribd\.com/document/(\d+)|scribd\.com/doc/(\d+)|scribd\.com/presentation/(\d+)', url)
    if not url or not match:
        await message.answer("<b>Please provide a valid Scribd URL after the /scribd </b>", parse_mode='HTML')
        return

    document_id = match.group(1) or match.group(2)
    first_url = f'https://www.scribd.com/doc-page/download-receipt-modal-props/{document_id}'

    # Send a loading message
    loading_message = await message.answer("<b>Processing your request...</b>", parse_mode='HTML')

    try:
        # Load cookies
        cookies = load_cookies('cookie.json')  # Ensure the 'sc.json' file is in the correct path

        # First request
        response = requests.get(first_url, cookies=cookies)
        if response.status_code == 200:
            info = extract_information(response.json())
            title = info['title']
            author_name = info['author_name']
            receipt_url = info['receipt_url']

            # Construct the second URL using the extracted access_key and URL ID
            second_url = f"https://www.scribd.com/document_downloads/{document_id}/?secret_password={info['access_key']}&extension=pdf"

            # Second request
            response = requests.get(second_url, cookies=cookies, allow_redirects=False)
            if response.status_code in [301, 302]:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    # Third request to the redirect URL
                    third_response = requests.get(redirect_url, cookies=cookies, allow_redirects=False)
                    if third_response.status_code in [301, 302]:
                        final_redirect_url = third_response.headers.get('Location')
                        if final_redirect_url:
                            # Create the message text
                            message_text = (
                                f"<b>Here is the Download Link ✅\n"
                                f"━━━━━━━━━━━━━━━━\n"
                                f"Title: {title}\n"
                                f"Author Name: {author_name}\n"
                                f"Main Url: <a href='{receipt_url}'>Click Here</a>\n"
                                f"Download Link: <a href='{final_redirect_url}'>Download Now</a>\n"
                                f"━━━━━━━━━━━━━━━━\n"
                                f"Scribd Downloader By: <a href='https://t.me/theStudyMateBot'>Study Mate</a></b>"
                            )
                            download_button = types.InlineKeyboardMarkup()
                            download_button.add(types.InlineKeyboardButton(text="Download Now", url=final_redirect_url))

                            # Send the message with the inline button
                            await message.answer(message_text, reply_markup=download_button, parse_mode='HTML')
                        else:
                            await message.answer("Failed to get the final redirect URL.", parse_mode='HTML')
                    else:
                        await message.answer("Failed to redirect from the second request.", parse_mode='HTML')
                else:
                    await message.answer("No redirect URL found in the headers of the second request.", parse_mode='HTML')
            else:
                await message.answer(f"Second request failed with status code: {response.status_code}", parse_mode='HTML')
        else:
            await message.answer(f"First request failed with status code: {response.status_code}", parse_mode='HTML')

    except Exception as e:
        await message.answer(f"<code>An error occurred: {e}</code>", parse_mode='HTML')

    # After processing is complete, delete the loading message
    try:
        await bot.delete_message(chat_id, loading_message.message_id)
    except MessageToDeleteNotFound:
        pass  # Message was already deleted


# Be sure to start the reset task when the bot starts up
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
