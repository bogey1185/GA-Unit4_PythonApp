from flask_wtf import FlaskForm as Form

from models import User, Poll, Response, Vote, Membership

from wtforms import StringField, PasswordField, TextAreaField, BooleanField, DateTimeField

from wtforms.validators import (DataRequired, Regexp, ValidationError, Email, Length, EqualTo)

#####################################
#                                   #
#     Custom validators             #
#                                   #
#####################################

def name_exists(form, field):
  if User.select().where(User.username == field.data).exists():
    raise ValidationError('Username is already taken. Please try again.')

def email_exists(form, field):
  if User.select().where(User.email == field.data).exists():
    raise ValidationError('Email is already taken. Please try again.')

#####################################
#                                   #
#     Forms                         #
#                                   #
#####################################

class RegisterForm(Form):
  username = StringField(
    'Username',
    validators=[
      DataRequired(),
      Regexp(
        r'^[a-zA-Z0-9_]+$',
        message=("Username should be one word, letters, numbers, and underscores only.")
      ),
      name_exists
    ]
  )
  email = StringField(
    'Email',
    validators=[
      DataRequired(),
      Email(),
      email_exists
    ]
  )
  password = PasswordField(
    'Password',
    validators=[
      DataRequired(),
      Length(min=8),
      EqualTo('password2', message='Passwords must match. Try again.')
    ]
  )
  password2 = PasswordField(
    'Confirm Password',
    validators=[DataRequired()]
  )

class LoginForm(Form):
  email = StringField(
    'Email',
    validators=[
      DataRequired(),
      Email()
    ]
  )
  password = PasswordField(
    'Password', 
    validators=[DataRequired()]
  )

# class CreatePoll(Form):
