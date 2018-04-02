import os
MAIL_SERVER = 'smtp.elasticemail.com'
MAIL_PORT = 2525
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "admin@freeside.co.uk"
MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
MAIL_DEFAULT_SENDER = "no-reply@freeside.co.uk"
SECRET_KEY = os.environ['SECRET']
IPA_PASSWORD = os.environ['IPA_PASSWORD']
SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
