
## do we need to import resources??
from flask import Flask, g, render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash

import models
import forms

app = Flask(__name__)

app.secret_key = ""
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


@app.route("/register", method = ("GET", "POST"))
def register():
    form = forms.registerForm()
    if form.validate_on_submit():
        flash("Congrats, You registered successfully")
        models.User.create_user(
            #these are the field we have now, might have to modify later
            username = form.username.data,
            email = form.email.data,
            password = form.password.data
            ## confirm_password = form.confirm_password.data
            )
        return redirect(url_for("index"))
    return render_template("register.html", form = form)
    # need to make sure register.html is the right file


@app.route("/")
def hello_world():
    return "hello world"

if __name__ == '__main__':
    models.initialize()

    app.run(debug = True, port = 8000)