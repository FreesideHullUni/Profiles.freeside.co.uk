import os
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "no-reply@freeside.co.uk"
MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
MAIL_DEFAULT_SENDER = "Freeside"
SECRET_KEY="\x7f\xa1\xbc:\xdb9!\xa9\x96\x13Fzi\x82v\xf6L\x99\xedy\x07[a\xe1"
IPA_PASSWORD= os.environ['IPA_PASSWORD']
SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
