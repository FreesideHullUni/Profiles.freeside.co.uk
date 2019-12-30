import os

# Mail
MAIL_SERVER = "smtp.elasticemail.com"
MAIL_PORT = 2525
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = "admin@freeside.co.uk"
MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
MAIL_DEFAULT_SENDER = ("Freeside", "no-reply@freeside.co.uk")

IPA_USERNAME = os.environ["IPA_USERNAME"]
IPA_PASSWORD = os.environ["IPA_PASSWORD"]

SQLALCHEMY_DATABASE_URI = "sqlite:///data/users.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ["SECRET"]
DEBUG = os.environ.get("DEBUG", None)

# Discord OAuth
OAUTH2_CLIENT_ID = os.environ["OAUTH2_CLIENT_ID"]
OAUTH2_CLIENT_SECRET = os.environ["OAUTH2_CLIENT_SECRET"]
OAUTH2_REDIRECT_URI = os.environ.get(
    "OAUTH2_REDIRECT_URI", "http://freeside.co.uk/callback"
)
API_BASE_URL = os.environ.get("API_BASE_URL", "https://discordapp.com/api")
AUTHORIZATION_BASE_URL = API_BASE_URL + "/oauth2/authorize"
TOKEN_URL = API_BASE_URL + "/oauth2/token"

# Discord Tokens
DISCORD_INVITE = "gGd6qc2"
GUILD_ID = 364428045093699594
FREESIDE_ROLE = 366661244284829697
BOT_TOKEN = os.environ["BOT_TOKEN"]

if DEBUG is None or DEBUG is False:
    DEBUG = False
else:
    DEBUG = True
