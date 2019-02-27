from flask import Flask, g, render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash

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

#need to change the return value on this route, this is just for now.
@app.route("/")
def hello_world():
    return "hello world"

#register route
@app.route("/register", methods=("GET", "POST"))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Congrats, You registered successfully!", "success")
        models.User.create_user(
            username = form.username.data,
            email = form.email.data,
            password = form.password.data
        )
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

# new poll-form route
# this whole thing might break up with syntax error, so we need to be 
    #extra careful and double check everything later.
# @app.route("/new_poll", methods = ("GET", "POST"))
# @login_required
# def poll():
#     form = forms.PollForm()
#     if form.validate_on_submit():
#         models.Poll.create(user=g.user._get_current_object(),
#                            content=form.content.data.strip())
#         flash('Your poll have been posted', 'success')
#         return redirect(url_for('index'))

#     # get route
#     return render_template('polls.html', form=form)
# file and forms' names need to be double checked

if __name__ == '__main__':
    models.initialize()
    app.run(debug = config.DEBUG, port = config.PORT)


