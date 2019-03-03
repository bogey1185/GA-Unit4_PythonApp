import os
from flask import Flask, g, render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
import datetime
import random
import config
import models
import forms

app = Flask(__name__)

#session key for cookies 
app.secret_key = config.SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
  try:
    return models.User.get(models.User.id == userid)
  except models.DoesNotExist:
    return None

@app.before_request
def before_request():
  """Connect to the database before each request"""
  g.db = models.DATABASE
  g.db.connect()
  g.user = current_user

@app.after_request
def after_request(response):
  """Close the databases connection after each request"""
  g.db.close()
  return response

#################################
#                               #
#        Routes                 #
#                               #
#################################

#need to change the return value on this route, this is just for now.
@app.route("/")
def index():
  return render_template('index.html')

        #################################
        #                               #
        #        Auth Routes            #
        #                               #
        #################################

#register route
@app.route("/register", methods=("GET", "POST"))
def register():
  form = forms.RegisterForm()
  if form.validate_on_submit():
    flash("Congrats, You registered successfully!", "success")
    newUser = models.User.create_user(
      username = form.username.data,
      email = form.email.data,
      password = form.password.data
    )
    login_user(newUser)
    return redirect(url_for("index"))
  return render_template("register.html", form=form)

#login route
@app.route('/login', methods=('GET', 'POST'))
def login():
  form = forms.LoginForm()
  if form.validate_on_submit():
    try:
      user = models.User.get(models.User.email == form.email.data)
    except models.DoesNotExist:
      # need to create model for this
      flash('Your email or password does not match.', 'error')
    else:
      if check_password_hash(user.password, form.password.data):
        login_user(user)
        return redirect(url_for('index'))

      else:
        flash('Your email or password does not match.', 'error')

  return render_template('login.html', form=form)

#logout route
@app.route("/logout")
@login_required
def logout():
  logout_user()
  flash("You have been logged out.", "success")
  return redirect(url_for("index"))

        #################################
        #                               #
        #     Create New Poll route     #
        #                               #
        #################################

# new poll route
@app.route("/new_poll", methods=("GET", "POST"))
@login_required
def new_poll():
  form = forms.PollForm()
  if form.validate_on_submit():

    #generate hash for hash invite code
    hash = ''
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    while len(hash) < 25:
      hash += valid_chars[random.randint(0,len(valid_chars)-1)]

    #make new poll
    new_poll = models.Poll.create(
      created_by      = g.user._get_current_object(),
      created_by_user = g.user._get_current_object().username,
      expiration_date = form.expiration_date.data,
      hashcode        = hash,
      question        = form.question.data.strip(),
      private         = form.private.data,
    )

    #if at time of creation, poll is expired, reset its active status to false
    if new_poll.__data__['expiration_date'] < datetime.date.today():
      new_poll.__data__['active'] = False
    else:
      new_poll.__data__['active'] = True
    new_poll.save()

    #make new membership entry to relate creator with poll
    new_member = models.Membership.create(
      user_id = g.user._get_current_object(),
      poll_id = new_poll.__data__['id']
    )

    #gather field responses
    responses = [form.response1.data, form.response2.data, form.response3.data, form.response4.data]

    print(responses, 'THESE ARE RESPONSES')
    #for any completed responses, create responses in sequence so they can be reconstructed later
    for i in range(1, 5):
      # if responses[i-1] != '':
        new_response = models.Response.create(
          poll_id  = new_poll.__data__['id'],
          text     = responses[i-1],
          sequence = i
        )            
   
    flash('Your poll have been posted', 'success')
    return redirect(url_for('stream'))

  # get route
  return render_template('new_poll.html', form=form)

        #################################
        #                               #
        #        Show routes            #
        #                               #
        #################################

#show all public polls route
@app.route('/stream')
@app.route('/stream/')
def stream():
  #get all active and expired polls that are public
  active_polls = models.Poll.select().where((models.Poll.expiration_date >= datetime.date.today()) & (models.Poll.private == 'public')).order_by(models.Poll.expiration_date)
  expired_polls = models.Poll.select().where((models.Poll.expiration_date < datetime.date.today()) & (models.Poll.private == 'public')).order_by(-models.Poll.date)
  
  #in order to make sure database is continually updating and keeping the active property
  #properly set to True or False depending on whether poll is active, this quick loop runs when
  #the stream route is run. It updates active status for db entries based on date.

  for poll in expired_polls:
    if poll.active:
      poll.active = False
      poll.save()

  return render_template('stream.html', active_polls=active_polls, expired_polls=expired_polls)

#Userpage for specific user
@app.route('/user')
@app.route('/user/')
@login_required
def user_page():

  #get all the memberships that include the current user
  memberships = models.Membership.select().where(models.Membership.user_id == g.user._get_current_object())

  #extract the poll ids from the memberships
  poll_ids = [member.__dict__['__data__']['poll_id'] for member in memberships]    
  
  #query the poll ids into list comprehensions for active and inactive polls.
  polls = [models.Poll.select().where(models.Poll.id == poll).get() for poll in poll_ids]

  #break polls into list of active and expired polls
  active_polls = [poll for poll in polls if poll.__data__['active'] == True]
  expired_polls = [poll for poll in polls if poll.__data__['active'] == False]
  
  return render_template('userpage.html', active_polls=active_polls, expired_polls=expired_polls, user_id=g.user._get_current_object())
  
        #################################
        #                               #
        #        Show poll route        #
        #                               #
        #################################

#show specific poll

@app.route('/stream/<hashcode>')
def show_poll(hashcode):

  #get poll
  poll = models.Poll.select().where(models.Poll.hashcode == hashcode).get()
  
  #current poll id
  pollId = poll.__data__['id']
  
  #current user id
  userId = g.user._get_current_object()
  
  #get responses associated with poll
  responses = models.Response.select().where(models.Response.poll_id == pollId).order_by(models.Response.sequence)

  #grab all votes cast for current poll 
  votes = models.Vote.select().where(models.Vote.poll_id == pollId)

  #how many people voted for each response? Let's see...
  votecount = []
  votetotal = 0

  for response in responses:
    respvotes = models.Vote.select().where(response.id == models.Vote.response_id).count()
    votecount.append(respvotes)
    votetotal += respvotes

  #need to set this in a ternary because before you have your first vote, you will get a divide by zero error 
  # due to the num / votetotal
  vote_percentages = [round((num / votetotal)*100, 2) for num in votecount] if votetotal > 0 else [0, 0, 0, 0]
  
  #if the poll activity is false (meaning expired), or there is no login
  # register it as voted upon so only results show. #No voting allowed!
  if (poll.active == False) or (userId.__dict__ == {}):
    return render_template('/show.html', poll=poll, responses=responses, vote=True, vote_percentages=vote_percentages, votecount=votecount) 

  #loop over votes. If any were cast by current user, set voted to True. Else make it False
  for vote in votes:
    if vote.user_id == userId:
      return render_template('/show.html', poll=poll, responses=responses, vote=True, vote_percentages=vote_percentages, votecount=votecount)

  return render_template('/show.html', poll=poll, responses=responses, vote=False, vote_percentages=vote_percentages, votecount=votecount)

        #################################
        #                               #
        #        Delete route           #
        #                               #
        #################################

#Delete route for polls
@app.route('/user/delete/<id>')
@login_required
def delete_poll(id):
  poll = models.Poll.get(models.Poll.id == id)
  poll.delete_instance(recursive=True)

  return redirect('/user')

        #################################
        #                               #
        #        Edit routes            #
        #                               #
        #################################

#edit route for poll - GET

@app.route('/user/edit/<id>', methods=['GET'])
@login_required
def edit_get(id):

  #get the poll we are going to edit
  poll = models.Poll.get(models.Poll.id == id)
  #get the responses we are going to edit
  responses = models.Response.select().where(models.Response.poll_id == id)
  #make an array of the form data from the responses so it can be injected 
  response_list = ['', '', '', '']
  response_idx = 0
  for response in responses:
    response_list[response_idx] = response.__data__['text']
    response_idx+=1

  #create the form with the values pre-set
  form = forms.PollForm(
    expiration_date = poll.__data__['expiration_date'],
    private = poll.__data__['private'],
    question = poll.__data__['question'],
    response1 = response_list[0],
    response2 = response_list[1],
    response3 = response_list[2],
    response4 = response_list[3]
  ) 

  return render_template('edit.html', form=form)

#edit route for poll - POST/PUT

@app.route('/user/edit/<id>', methods=['POST'])
@login_required
def edit_post(id):

  form = forms.PollForm()

  #if submitted for is valid
  if form.validate_on_submit():

    #update the poll
    poll_update = models.Poll.update({
      models.Poll.expiration_date: form.expiration_date.data,
      models.Poll.private: form.private.data,
      models.Poll.question: form.question.data
    }).where(models.Poll.id == id)
    #execute the update
    poll_update.execute()

    #gather the response changes into an iterable list so each can be updated separately
    #since each response is its own db entry
    response_list = [form.response1.data, form.response2.data, form.response3.data, form.response4.data]
    index = 1
    for response in response_list:
      response_update = models.Response.update({models.Response.text: response}).where((models.Response.poll_id == id) & (models.Response.sequence == index))
      response_update.execute()
      index += 1

    flash('Your poll have been updated', 'success')
    return redirect(url_for('user_page'))

  else:

    return redirect(f'/user/edit/{id}')


        #################################
        #                               #
        #        Vote route             #
        #                               #
        #################################

#cast vote
@app.route('/stream/<hashcode>/vote/<responseid>')
@login_required
def vote(hashcode, responseid):

  poll = models.Poll.select().where(models.Poll.hashcode == hashcode).get()

  vote = models.Vote.create(
    user_id = g.user._get_current_object(),   
    response_id = responseid,
    poll_id = poll.__data__['id']
  )

  return redirect('/stream/' + hashcode)

        #################################
        #                               #
        #   follow/unfollow poll route  #
        #                               #
        #################################

@app.route('/stream/<hashcode>/follow/<poll>')
@login_required
def follow(hashcode, poll):
  #check if already member and following poll
  record = models.Membership.select().where((models.Membership.poll_id == poll) & (models.Membership.user_id == g.user._get_current_object()))
  #if record exists, delete. if not, create it.
  if record.exists():
    models.Membership.delete().where((models.Membership.poll_id == poll) & (models.Membership.user_id == g.user._get_current_object())).execute()
    return redirect('/stream/' + hashcode)
  else:
    created_rec = models.Membership.create(
      poll_id = poll,
      user_id = g.user._get_current_object()
    )
    return redirect('/stream/' + hashcode)

    
if __name__ == '__main__':
  if 'ON_HEROKU' in os.environ:
      print('hitting ')
      models.initialize()
#   models.initialize()
  # app.run(debug = config.DEBUG, port = config.PORT)

