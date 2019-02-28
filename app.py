from flask import Flask, g, render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
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
    return render_template('layout.html')

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
    # need to make sure register.html is the right file name

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
        #        Create New Poll        #
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
            expiration_date = form.expiration_date.data,
            expiration_time = form.expiration_time.data,
            hashcode        = hash,
            question        = form.question.data.strip(),
            private         = form.private.data
        )

        #make new membership entry to relate creator with poll
        new_member = models.Membership.create(
            user_id = g.user._get_current_object(),
            poll_id = new_poll.__data__['id']
        )

        #gather field responses
        responses = [form.response1.data, form.response2.data, form.response3.data, form.response4.data]

        #for any completed responses, create responses in sequence so they can be reconstructed later
        for i in range(1, 5):
            if responses[i-1] != '':
                new_response = models.Response.create(
                    poll_id  = new_poll.__data__['id'],
                    text     = responses[i-1],
                    sequence = i
                )            
       
        flash('Your poll have been posted', 'success')
        return redirect(url_for('index'))

    # get route
    return render_template('new_poll.html', form=form)

        #################################
        #                               #
        #        Show pages             #
        #                               #
        #################################

#show all public polls route
@app.route('/stream')
def stream():
    stream = models.Poll.select().where(models.Poll.private == 'public').order_by(models.Poll.date)
    print(stream)
    return render_template('stream.html', stream=stream)

#show specific poll
@app.route('/stream/<hashcode>')
def show_poll(hashcode):

    #get poll
    stream = models.Poll.select().where(models.Poll.hashcode == hashcode).get()
    #get responses associated with poll
    responses = models.Response.select().where(models.Response.poll_id == stream.__data__['id']).order_by(models.Response.sequence)

    return render_template('/show.html', stream=stream, responses=responses)

if __name__ == '__main__':
    models.initialize()
    app.run(debug = config.DEBUG, port = config.PORT)


