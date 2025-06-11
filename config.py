import configparser
import os

CONFIG = configparser.ConfigParser()
CONFIG.read("hotel.ini")

# Override with environment variables if present
if 'DATABASE_NAME' in os.environ:
    CONFIG['database']['name'] = os.environ['DATABASE_NAME']

# Print resolved database path for debugging
print(f"Using database at: {CONFIG['database']['name']}")