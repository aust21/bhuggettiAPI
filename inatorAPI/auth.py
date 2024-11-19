from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
import sys, os, requests, json, random
from .models import User
from . import db, mail
from .views import views
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from oauthlib.oauth2 import WebApplicationClient
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

sys.path.append(os.getcwd())


auth = Blueprint("auth", __name__)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


client = WebApplicationClient(GOOGLE_CLIENT_ID)

# --------------------------Reset password-------------------------- #

@auth.route("/forgot-password")
def forgot():
    return render_template("forgot_password.html")

# Initialize serializer with your app's secret key
def get_reset_token_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

# Route for requesting password reset
@auth.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate secure token
            serializer = get_reset_token_serializer()
            reset_token = serializer.dumps(user.email, salt='password-reset-salt')
            
            # Create reset link
            reset_url = url_for(
                'auth.reset_password',
                token=reset_token,
                _external=True
            )
            
            # Send email
            msg = Message('Password Reset Request',
                        sender=current_app.config['MAIL_USERNAME'],
                        recipients=[user.email])
            msg.html = render_template('email/reset_email.html', reset_url=reset_url)
            mail.send(msg)
            
        # Always show this message even if email doesn't exist (prevents email enumeration)
        flash('If an account exists with that email, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
        
    return redirect(url_for('auth.login'))


# Route for resetting password with token
@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    try:
        # Verify token (expires after 3600 seconds = 1 hour)
        serializer = get_reset_token_serializer()
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Invalid or expired reset link', 'error')
            return redirect(url_for('auth.login'))
            
        if request.method == 'POST':
            password = request.form.get('password')
            confirm_password = request.form.get('confirmPassword')
            
            if not password or not confirm_password:
                flash('Please fill in all fields', 'error')
                return render_template('reset_password.html')
                
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('reset_password.html')
                
            if len(password) < 8:
                flash('Password must be at least 8 characters long', 'error')
                return render_template('reset_password.html')
                
            # Update password
            user.password = generate_password_hash(password)
            db.session.commit()
            
            flash('Your password has been updated!', 'success')
            return redirect(url_for('auth.login'))
            
        return render_template('reset_password.html')
        
    except:
        flash('Invalid or expired reset link', 'error')
        return redirect(url_for('auth.login'))


# --------------------------login-------------------------- #

@auth.route("/login/google")
def login_with_google():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    # Use url_for with _external=True to get the full URL
    redirect_uri = url_for('auth.google_callback', _external=True)
    print(f"Redirect URI: {redirect_uri}")  # For debugging
    print(f"Generated redirect URI: {url_for('auth.google_callback', _external=True)}")
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@auth.route("/login/google/callback")
def google_callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    # Use the same url_for as above
    redirect_uri = url_for('auth.google_callback', _external=True)
    
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=redirect_uri,
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
        login_user(user, remember=True)
        return redirect(url_for('auth.complete_profile'))

    login_user(user)
    return redirect(url_for("views.home"))

@auth.route("/complete-profile", methods=["GET", "POST"])
@login_required
def complete_profile():
    if request.method == "POST":
        
        speciality = request.form.get("speciality")
        password = request.form.get("password")
        company = request.form.get("company")
        try:
            current_user.speciality = speciality
            current_user.password = generate_password_hash(password, method="pbkdf2:sha256")
            current_user.company = company
            db.session.commit()
            return redirect(url_for("views.home"))
        except Exception as e:
            db.session.rollback()
               
    return render_template("complete_profile.html", user=current_user)


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                
                if user.is_admin:
                    return redirect(url_for("admin.admin_dash"))
                return redirect(url_for("views.home"))
            else:
                flash("Password is incorrect", category="error")
        else:
            flash("Account not found", category="error")
            redirect(url_for("sign_up"))

    return render_template("login.html")

@auth.route("/reset-password")
def reset():
    return render_template("reset.html")

# --------------------------verify account-------------------------- #

def generate_code():
    code = set()

    while len(code) < 7:
        num = random.randint(0, 9)
        code.add(str(num))
    return "".join(code)

# 

@auth.route("/confirm-account", methods=["GET", "POST"])
def update_account():
    if request.method == "POST":
        code = request.form.get("code")
        if current_user.cormfirm_code == code:
            current_user.account_confirmed = True
            db.session.commit()
            flash("Account verified")
            return redirect(url_for('views.settings', id=current_user.id))
        flash("Account could not be confirmed")
        return redirect(url_for('views.settings', id=current_user.id))
    flash("An error has occured, please try again")
    return redirect(url_for('views.settings', id=current_user.id))


@auth.route("/verify", methods=["GET", "POST"]) 
def verify():
    code = generate_code() 
    current_user.cormfirm_code = code
    db.session.add(current_user)
    db.session.commit()
    
    msg = Message('bhuggettiAPI | Email Verification',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[current_user.email])
    
    msg.html = render_template('email/verification.html', 
                             user=current_user, 
                             code=code)
    
    mail.send(msg)
    flash('Verification code has been sent to your email.', 'success')
    return redirect(url_for('views.settings', id=current_user.id))

# --------------------------sign up-------------------------- #


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():

    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password=generate_password_hash(os.urandom(24).hex())
        speciality="Not specified"
        company="Not specified"

        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash('Email exists', category='error')
        else:
            new_user = User(email=email, name=name, speciality=speciality, 
            password=generate_password_hash(password, method="pbkdf2:sha256"), company=company,
            cormfirm_code="0000000",
            account_confirmed=False)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            
            return redirect(url_for('auth.complete_profile'))

    return render_template("sign-up.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))