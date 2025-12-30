from os import environ

def get_env(name, default=None, cast=str):
    value = environ.get(name, default)
    if value is None or value == "":
        return default
    try:
        return cast(value)
    except Exception:
        raise ValueError(f"Invalid value for environment variable: {name}")

# Telegram Account API credentials
API_ID = get_env("API_ID", cast=int)
API_HASH = get_env("API_HASH")

# Bot token
BOT_TOKEN = get_env("BOT_TOKEN")

# Owner / Admin ID
OWNER_ID = get_env("OWNER_ID", cast=int)

# Force Subscribe Channel ID (optional)
# Use -100xxxxxx format
F_SUB = get_env("F_SUB", default=None, cast=int)

# MongoDB URI
MONGO_DB_URI = get_env("MONGO_DB_URI")

# Web server port
PORT = get_env("PORT", default=8080, cast=int)
