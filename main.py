from flask import Flask, flash, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from python_freeipa import Client
import uuid

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
    username = StringField('Username', validators=[validators.Length(min=4, max=35),validators.DataRequired()])
    first_name = StringField('Firstname', validators=[validators.Length(min=4, max=35),validators.DataRequired()])
    last_name = StringField('Lastname', validators=[validators.Length(min=4, max=35),validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

@app.route('/', methods=['GET', 'POST'])
def register():
    form = EmailForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user == None:
            msg = Message("Welcome to Freeside",
                      recipients=[form.email.data])
            uid = str(uuid.uuid4())
            user = User(email=form.email.data, uuid=uid)
            db.session.add(user)
            db.session.commit()
            msg.body =  "Click here to continue with registering your Freeside account http://register.freeside.co.uk/" + uid + " If you did not request a Freeside account please ignore this email."
            mail.send(msg)
        else:
            if user.account_created == True:
                flash("Account already exists.")
            else:
                flash("Please click the link in the activation email. If you did not recieve an activation check your junk folder. If you still can not find the email support@freeside.co.uk")
    return render_template('register.html', form=form)

@app.route('/<uid>', methods=['GET', 'POST'])
def verify_user(uid):
    form = RegisterForm(request.form)
    user = User.query.filter_by(uuid=uid).first_or_404()
    if request.method == 'POST' and form.validate():
        client = Client('ipa.demo1.freeipa.org', version='2.215')
        client.login('admin', 'Secret123')
        try:
            ipauser = client.user_add(form.username.data, form.first_name.data,
                                        form.last_name.data, form.first_name.data + " " + form.last_name.data,
                                        mail=user.email, preferred_language='EN')
        except python_freeipa.exceptions.DuplicateEntry as e:
            flash("account already exists")
            return render_template('error.html')
        else:
            print(ipauser)
            user.account_created = True
            db.session.commit()
            flash("Account created")
            return render_template('error.html')
    else:
        if user.account_created == True:
            flash("Account already verified")
            return render_template('error.html')
        else:
            return render_template('complete_registration.html', form=form)
