from flask import Flask, flash, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from wtforms import Form, StringField, PasswordField, validators
from python_freeipa import Client
import python_freeipa
import uuid
import paramiko
import re

app = Flask(__name__)
app.config.from_object('config')
mail = Mail(app)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    uuid = db.Column(db.String(120), unique=True)
    account_created = db.Column(db.Boolean(), unique=False, default=False)

    def __repr__(self):
        return '<User %r>' % self.username


class EmailForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35)])


class RegisterForm(Form):
    display_name = StringField('Display Name', validators=[validators.Length(min=2, max=35), validators.DataRequired()])
    first_name = StringField('Forename', validators=[validators.Length(min=2, max=35), validators.DataRequired()])
    password = PasswordField('Password', [
        validators.Length(min=8),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


@app.route('/', methods=['GET', 'POST'])
def register():
    form = EmailForm(request.form)
    if request.method == 'POST' and form.validate():
        # Todo: Better Email Validation
        email = form.email.data
        domain = email.split('@')[1]
        if "hull.ac.uk" not in domain:
            flash("Please enter a valid email, it should be your Uni email.")
        else:
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                msg = Message("Please verify your email!",
                              recipients=[form.email.data])
                uid = str(uuid.uuid4())
                user = User(email=form.email.data, uuid=uid)
                db.session.add(user)
                db.session.commit()
                msg.html = render_template("verify.html", uid=uid)
                mail.send(msg)
                flash("Email sent this may take a while to arrive, "
                       "Click the link in the activation email. "
                       "If you can not find the email check your junk "
                       "folder. If you have any issues please email "
                       "support@freeside.co.uk or join our Discord "
                       "http://discord.freeside.co.uk")
                return render_template('message.html')
            else:
                if user.account_created is True:
                    flash("Account already exists!")
                else:
                    flash("Please click the link in the activation email. "
                          "If you can not find the email check your junk "
                          "folder. If you have any issues please email "
                          "support@freeside.co.uk or join our Discord "
                          "http://discord.freeside.co.uk")
    return render_template('register.html', form=form)


@app.route('/verify/<uid>', methods=['GET', 'POST'])
def verify_user(uid):
    form = RegisterForm(request.form)
    user = User.query.filter_by(uuid=uid).first_or_404()
    if request.method == 'POST' and form.validate():
        client = Client('ipa.freeside.co.uk', verify_ssl=False, version='2.215')
        client.login('admin', app.config['IPA_PASSWORD'])
        username = user.email.split('@')[0]
        firstname = form.first_name.data
        firstname = firstname.title()
        lastname = username.split('.')[-1].title()
        username = re.sub("[^a-zA-Z]+", "", username)
        username = username.lower()
        try:
            ipauser = client.user_add(username, firstname,
                                      lastname, form.first_name.data + " " + lastname, display_name=form.display_name.data,
                                      mail=user.email, preferred_language='EN', random_pass=True)
        except python_freeipa.exceptions.DuplicateEntry:
            flash("Account already exists@")
            return render_template('message.html')
        client.change_password(username, ipauser['randompassword'], form.password.data)
        user.account_created = True
        db.session.commit()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('storage.freeside.co.uk', username='root', password=app.config['IPA_PASSWORD'])
        ssh.exec_command('userdir.sh {}'.format(username))
        flash("Account created! Your username is: " + username)
        msg = Message("Welcome to Freeside",
                      recipients=[user.email])
        msg.html = render_template("welcome-email.html", firstname=firstname, username=username)
        mail.send(msg)
        return render_template('message.html')
    else:
        if user.account_created is True:
            flash("Account already verified!")
            return render_template('message.html')
        else:
            return render_template('complete_registration.html', form=form)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000,debug=True)
