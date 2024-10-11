from flask import Blueprint, render_template, redirect, url_for, request, flash
import sys, os, requests, json
from .models import User
from . import db
from .views import views
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from oauthlib.oauth2 import WebApplicationClient

sys.path.append(os.getcwd())


auth = Blueprint("auth", __name__)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@auth.route("/login/google/callback")
def google_callback():
    # Get authorization code from Google
    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    user_info = userinfo_response.json()

    user = User.query.filter_by(email=user_info["email"]).first()

    if not user:
        user = User(
            email=user_info["email"],
            name=user_info["name"],
            password=generate_password_hash(os.urandom(24).hex()),
            speciality="Not specified",
            company="Not specified"
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)  # Log in the new user
        return redirect(url_for('auth.complete_profile'))

    login_user(user)
    return redirect(url_for("views.home"))

@auth.route("/complete-profile", methods=["GET", "POST"])
@login_required
def complete_profile():
    # logger.debug(f"Current user: {current_user}")
    # logger.debug(f"Current user is authenticated: {current_user.is_authenticated}")
    # logger.debug(f"Current user attributes: {vars(current_user)}")

    if request.method == "POST":
        speciality = request.form.get("speciality")
        password = request.form.get("password")
        company = request.form.get("company")
        # logger.debug(f"Received speciality: {speciality}")

        
        try:
            current_user.speciality = speciality
            current_user.password = generate_password_hash(password, method="pbkdf2:sha256")
            current_user.company = company
            # logger.debug(f"Updated current_user: {vars(current_user)}")
            db.session.commit()
            # flash("Profile updated successfully!", category="success")
            return redirect(url_for("views.home"))
        except Exception as e:
            db.session.rollback()
               

    return render_template("complete_profile.html", user=current_user)


@auth.route("/login/google")
def login_with_google():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )

    return redirect(request_uri)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Password is incorrect", category="error")
        else:
            redirect(url_for("sign_up"))

    return render_template("login.html")


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        speciality = request.form.get("speciality")
        name = request.form.get("name")
        company = request.form.get("company")

        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash('Email exists', category='error')
        else:
            new_user = User(email=email, name=name, speciality=speciality, 
                            password=generate_password_hash(password, method="pbkdf2:sha256"), company=company)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created')
            return redirect(url_for("views.home"))

    return render_template("sign-up.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))