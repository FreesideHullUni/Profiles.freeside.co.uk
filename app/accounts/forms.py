
from wtforms import Form, StringField, PasswordField, validators


class EmailForm(Form):
    email = StringField("Email Address", [validators.Length(min=6, max=35)])


class RegisterForm(Form):
    display_name = StringField(
        "Display Name",
        validators=[validators.Length(min=2, max=35), validators.DataRequired()],
    )
    first_name = StringField(
        "Forename",
        validators=[validators.Length(min=2, max=35), validators.DataRequired()],
    )
    password = PasswordField(
        "Password",
        [
            validators.Length(min=8),
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Repeat Password")


class LoginForm(Form):
    username = StringField("Username", validators=[validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])
