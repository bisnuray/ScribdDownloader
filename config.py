# Copyright (C) @TheSmartBisnu
# Channel: https://t.me/itsSmartDev

import os
from dotenv import load_dotenv

load_dotenv()

def get_env_or_default(key, default=None, cast_func=str):
    value = os.getenv(key)
    if value is not None and value.strip() != "":
        try:
            return cast_func(value)
        except (ValueError, TypeError):
            return default
    return default

API_ID = get_env_or_default("API_ID", "Your_API_ID_Here")
API_HASH = get_env_or_default("API_HASH", "Your_API_HASH_Here")
BOT_TOKEN = get_env_or_default("BOT_TOKEN", "Your_BOT_TOKEN_Here")

required_vars = {
    "API_ID": API_ID,
    "API_HASH": API_HASH,
    "BOT_TOKEN": BOT_TOKEN
}

for var_name, var_value in required_vars.items():
    if var_value is None or var_value == f"Your_{var_name}_Here" or (isinstance(var_value, str) and var_value.strip() == ""):
        raise ValueError(f"Required variable {var_name} is missing or invalid. Set it in .env, config.py, or Heroku config vars.")
