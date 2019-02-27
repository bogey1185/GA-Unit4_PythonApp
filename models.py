import datetime
from peewee import *
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
import config

DATABASE = config.DATABASE

class User(UserMixin, Model):
  username      = CharField(unique=True)
  email         = CharField(unique=True)
  password      = CharField()

  class Meta:
    database = DATABASE

  @classmethod
  def create_user(cls, username, email, password):
    #sanitize email address
    email = email.lower()
    
    try: #see if user exists by querying email
      cls.select().where(cls.email == email).get() 
    
    except cls.DoesNotExist: #if user doesn't exist, create user
      user = cls(username=username, email=email)
      user.password = generate_password_hash(password)
      user.save()
      return user

    else: #if user does exist already
      raise Exception('Email address already in use.')

class Poll(Model):
  created_by  = ForeignKeyField(User, backref='user') #ref to author of poll
  date        = DateTimeField(default=datetime.datetime.now) #the date and time the poll was created
  expiration  = DateTimeField() #the date and time the poll expires. default set to 24 hours or so?
  hashcode    = CharField() #invite code used to access poll directly
  question    = TextField() #the poll question
  active      = BooleanField(default=True) #whether poll is active based on expiration date
  private     = BooleanField(default=False) #if true, poll won't be viewable by public. Will only be accessible through invite code.

  class Meta: 
    database = DATABASE

class Response(Model):       
  poll_id = ForeignKeyField(Poll, backref='poll') #each response belongs to a poll question
  text    = TextField() #each poll response has text

  class Meta: 
    database = DATABASE

class Vote(Model):                        
  user_id     = ForeignKeyField(User, backref='voter') # each vote is cast by a user, which is stored here
  response_id = ForeignKeyField(Response, backref='response') # each vote is applied to a particular response, which itself is tied to a particlar poll

  class Meta: 
    database = DATABASE

class Membership(Model): #this model links users to polls so that a user's homepage can list all polls they are related to. User can add more polls by clicking "follow" on a poll's show page
  user_id = ForeignKeyField(User, backref='user')
  poll_Id = ForeignKeyField(Poll, backref='poll')

  class Meta: 
    database = DATABASE

def initialize():
  DATABASE.connect()
  DATABASE.create_tables([User, Poll, Response, Vote, Membership], safe=True)
  DATABASE.close()


