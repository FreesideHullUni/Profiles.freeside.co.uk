from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from python_freeipa import Client, exceptions

from database import db
from mail import mail

from app.accounts.models.user import UserSession

from app.accounts.views import accounts_blueprint
from app.oauth.views import oauth_blueprint


app = Flask(__name__)
app.config.from_object("config")
db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

bind = Client("ipa.freeside.co.uk", verify_ssl=False, version="2.215")


@app.login_manager.user_loader
def load_user(uid):
    try:
        bind.login("admin", app.config["IPA_PASSWORD"])
        data = bind.user_show(uid)
        user = UserSession(uid, data)
        return user
    except exceptions.NotFound:
        return None
    except exceptions.Unauthorized:
        return None


app.register_blueprint(accounts_blueprint)
app.register_blueprint(oauth_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=app.config["DEBUG"])
