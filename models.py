class User(UserMixin, Model):
  username      = CharField(unique=True)
  email         = CharField(unique=True)
  password      = CharField()

class Poll(Model):
  question = CharField() #the poll question
  date = DateTimeField(default=datetime.datetime.now) #the date and time the poll was created
  expiration = DateTimeField() #the date and time the poll expires. default set to 24 hours or so?
  created_by = ForeignKeyField(User, backref='author') #ref to author of poll
  active = BooleanField(default=True) #whether poll is active based on expiration date
  hashcode = CharField() #invite code used to access poll directly
  private = BooleanField(default=False) #if true, poll won't be viewable by public. Will only be accessible through invite code.

class Response(Model):
  poll_id = ForeignKeyField(Poll, backref='poll') #each response belongs to a poll question
  text = TextField() #each poll response has text

class Vote(Model):
  user_id = ForeignKeyField(User, backref='voter') # each vote is cast by a user, which is stored here
  response_id = ForeignKeyField(Response, backref='response') # each vote is applied to a particular response, which itself is tied to a particlar poll




