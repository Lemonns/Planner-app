from time import time
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, EmailField, DateField, TimeField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")
    #recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class EditForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    time = StringField("Time", validators=[DataRequired()])
    submit = SubmitField("Submit")