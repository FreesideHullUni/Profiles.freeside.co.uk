from flask import Flask, flash, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
app = Flask(__name__)
app.config.from_object('config')
mail = Mail(app)

from wtforms import Form, BooleanField, StringField, PasswordField, validators

class RegistrationForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35)])


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        msg = Message("Hello",
                  recipients=["kieran@coldron.com"])
        randomcode = "rhrehre"
        msg.body =  "Click here to activate your account http://register.freeside.co.uk/" + randomcode + " If you did not request a Freeside account please ignore this email."
        mail.send(msg)
    return render_template('register.html', form=form)
