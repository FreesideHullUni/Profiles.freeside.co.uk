from app.accounts.models.user import UserSession
from app.accounts.models.database import User

from app.accounts.forms import LoginForm, EmailForm, RegisterForm

from mail import mail

from database import db


from flask import (
    flash,
    request,
    render_template,
    Blueprint,
    redirect,
    url_for,
    Markup,
    current_app as app,
)

from flask_mail import Message
from python_freeipa import Client, exceptions
import uuid
import paramiko
import re
from flask_login import login_user, logout_user, current_user, login_required


accounts_blueprint = Blueprint("accounts", __name__, template_folder="templates")


@accounts_blueprint.route("/")
def home():
    print(current_user)
    # Redirect users who are not logged in.
    if not current_user or current_user.is_anonymous:
        return redirect(url_for("accounts.login"))
    return render_template("profile.html")


@accounts_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        client = Client("ipa.freeside.co.uk", verify_ssl=False, version="2.215")
        try:
            uid = form.username.data
            client.login(uid, form.password.data)
            data = client.user_show(uid)
            login_user(UserSession(uid, data))
            flash("Logged in!")
            return redirect("/")
        except exceptions.Unauthorized:
            flash("Invalid username or password")
        except exceptions.NotFound:
            flash("User not in database.")
    return render_template("login.html", form=form)


@accounts_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@accounts_blueprint.route("/join", methods=["GET", "POST"])
def register():
    form = EmailForm(request.form)
    if request.method == "POST" and form.validate():
        email = form.email.data
        if app.config["DEBUG"] is False and "hull.ac.uk" not in email.split("@")[1]:
            flash("Please enter a valid email, it should be your Uni email.")
        else:
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                uid = str(uuid.uuid4())
                user = User(email=form.email.data, uuid=uid)
                db.session.add(user)
                db.session.commit()

                msg = Message("Please verify your email!", recipients=[form.email.data])
                msg.html = render_template("emails/verify.html", uid=uid)
                with app.app_context():
                    mail.send(msg)
                info_msg = Markup(
                    "Email sent this may take a while to arrive, "
                    "Click the link in the activation email. "
                    "If you can't find the email check your junk "
                    "folder. If you have any issues please email "
                    "support@freeside.co.uk or join our "
                    "<a href='http://discord.freeside.co.uk'>Discord</a>."
                )
                return render_template("layout.html", message=info_msg)
            else:
                info_msg = ""
                if user.account_created is True:
                    info_msg = "Account already exists!"
                else:
                    info_msg = Markup(
                        "Please click the link in the activation email. "
                        "If you can't find the email check your junk "
                        "folder. If you have any issues please email "
                        "support@freeside.co.uk or join our "
                        "<a href='http://discord.freeside.co.uk'>Discord</a>."
                    )
                return render_template("layout.html", message=info_msg)

    return render_template("join.html", form=form)


@accounts_blueprint.route("/verify/<uid>", methods=["GET", "POST"])
def verify_user(uid):
    form = RegisterForm(request.form)
    user = User.query.filter_by(uuid=uid).first_or_404()

    if request.method == "POST" and form.validate():
        client = Client("ipa.freeside.co.uk", verify_ssl=False, version="2.215")
        client.login(app.config["IPA_USERNAME"], app.config["IPA_PASSWORD"])
        username = user.email.split("@")[0]
        firstname = form.first_name.data
        firstname = firstname.title()
        lastname = username.split(".")[-1].title()
        username = re.sub("[^a-zA-Z]+", "", username)
        username = username.lower()

        try:
            ipauser = client.user_add(
                username,
                firstname,
                lastname,
                form.first_name.data + " " + lastname,
                display_name=form.display_name.data,
                mail=user.email,
                preferred_language="EN",
                random_pass=True,
            )
        except exceptions.DuplicateEntry:
            flash("Account already exists.")
            return render_template("layout.html")
        print(ipauser["randompassword"])
        client.change_password(username, form.password.data, ipauser["randompassword"])
        user.account_created = True
        db.session.commit()

        createHomeDir(username)

        msg = Message("Welcome to Freeside", recipients=[user.email])
        msg.html = render_template(
            "emails/welcome.html", firstname=firstname, username=username
        )
        with app.app_context():
            mail.send(msg)
        flash("Account created! Your username is: " + username)
        return redirect(url_for("accounts.home"))
    else:
        if user.account_created is True:
            flash("Account already verified!")
            return redirect(url_for("accounts.home"))
        else:
            return render_template("complete_registration.html", form=form)


def createHomeDir(username):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        "storage.freeside.co.uk",
        username=app.config["IPA_USERNAME"],
        password=app.config["IPA_PASSWORD"]
    )
    ssh.exec_command("sudo /usr/bin/userdir.sh {}".format(username))
