from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from fnmcode.models import User
from . import db
from . import SIMPLE_CAPTCHA

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    # login code goes here
    name = request.form.get("name")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False
    user = User.query.filter_by(name=name).first()

    if not user:
        flash("User Not found. Kindly signup first.")
        return redirect(url_for("auth.login"))

    # user is inactive
    if not user.is_active:
        flash("User is inactive. Contact Admin")
        return redirect(url_for("auth.login"))

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash("Please check your login details and try again.")
        return redirect(
            url_for("auth.login")
        )  # if the user doesn't exist or password is wrong, reload the page
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for("main.fnmpage"))


@auth.route("/signup")
def signup():
    new_captcha_dict = SIMPLE_CAPTCHA.create()
    return render_template('signup.html', captcha=new_captcha_dict)
    # return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post():
    # code to validate and add user to database goes here
    name = request.form.get("name")
    password = request.form.get("password")

    c_hash = request.form.get('captcha-hash')
    c_text = request.form.get('captcha-text')

    if not SIMPLE_CAPTCHA.verify(c_text, c_hash):
        flash("Failed captcha verification")
        return redirect(url_for("auth.signup"))

    user = User.query.filter_by(
        name=name
    ).first()  # if this returns a user, then the email already exists in database

    if (
        user
    ):  # if a user is found, we want to redirect back to signup page so user can try again
        flash("Email address already exists")
        return redirect(url_for("auth.signup"))

    # Hash the password with a valid method
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

    # Create a new user
    new_user = User(name=name, password=hashed_password)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
