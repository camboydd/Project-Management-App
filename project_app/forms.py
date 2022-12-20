from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, TextAreaField
from wtforms.validators import Length, Regexp, DataRequired, EqualTo, Email
from wtforms import ValidationError
from models import User
from database import db


class RegisterForm(FlaskForm):
    class Meta:
        csrf = False

    firstname = StringField('First Name', validators=[Length(1, 10)])

    lastname = StringField('Last Name', validators=[Length(1, 20)])

    email = StringField('Email', [
        Email(message='Not a valid email address.'),
        DataRequired()])

    password = PasswordField('Password', [
        DataRequired(message="Please enter a password."),
        EqualTo('confirmPassword', message='Passwords must match and be between 6 and 10 characters')
    ])

    confirmPassword = PasswordField('Confirm Password', validators=[
        Length(min=6, max=10),
        Regexp('(?=.*[A-Z])(?=.*[!,@,#,$,%,^,&,*,(,),?])(?=.*\d).+', message="Password must contain at least 1 capital letter, special character, and number") 
        #search for at least 1 capital letter, special character, and number
        #cases:
            #num,cap,spec   a1bAc!
            #num,spec,cap   ab1!Aa
            #cap,num,spec   aAb1!a
            #cap,spec,num   aAb!1a
            #spec,num,cap   ab!1Aa
            #spec,cap,num   ab!Ac1
    ])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).count() != 0:
            raise ValidationError('Username already in use.')


class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    email = StringField('Email', [
        Email(message='Not a valid email address.'),
        DataRequired()])

    password = PasswordField('Password', [
        DataRequired(message="Please enter a password.")])

    submit = SubmitField('Submit')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).count() == 0:
            raise ValidationError('Incorrect username or password.')


class CommentForm(FlaskForm):
    class Meta:
        csrf = False

    comment = TextAreaField('Comment')

    submit_comment = SubmitField('Add Comment/User')

    username = TextAreaField('Username')