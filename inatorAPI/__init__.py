from flask import Flask, request, jsonify, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from sqlalchemy import func
from oauthlib.oauth2 import WebApplicationClient
from flask_mail import Mail, Message

db = SQLAlchemy()
DB_NAME = "database.db"
mail = Mail() 
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'profile_pics')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'bhuggettiapi@gmail.com'  # Your email
    app.config['MAIL_PASSWORD'] = 'qfzk bhzz wjlc vryz'     # Your app password
    mail.init_app(app)
    db.init_app(app)
    from .auth import auth
    from .models import User, TechnicalQuestion, CultureFitQuestion
    from .views import views
    from .admin import admin

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(views, url_prefix="/dash")
    app.register_blueprint(admin, url_prefix="/admin")


    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.route("/")
    def index():
        flash("We're excited to have you here! This site is currently in development and testing, but feel free to sign up and take a look around.", category="info")
        return render_template("index.html")
    
    @app.route("/login")
    def login():
        return render_template("login.html")
    
    @app.route("/sign-up")
    def sign_up():
        return render_template("sign-up.html")
    
    @app.route("/docs")
    def docs():
        return render_template("docs.html")
    
    @app.route("/about")
    def about():
        return render_template("about.html")
    
    @app.route('/search')
    def search():
        query = request.args.get('q')
        # Perform your search logic here
        return render_template('search_results.html')

    @app.route("/api/questions", methods=["GET"])
    def get_question():

        # in the future, select random id's first and return the questions from them
        count = request.args.get('count', default=1, type=int)
        q_type = request.args.get('type', default="technical", type=str)
        q_field = request.args.get('field', default="not relevant", type=str).lower()

        print(q_field)
        if q_field == "not relevant":
            if q_type.lower() == "technical":
                questions = TechnicalQuestion.query.order_by(func.random()).limit(count).all()
            elif q_type.lower() == "culture":
                questions = CultureFitQuestion.query.order_by(func.random()).limit(count).all()
            else:
                return jsonify({"data":"invalid question type. Please refer to the docs"})
            
        elif q_field != "not relevant":
            if q_type.lower() == "technical":
                questions = TechnicalQuestion.query.filter(TechnicalQuestion.domain == q_field).order_by(func.random()).limit(count).all()
            elif q_type.lower() == "culture":
                questions = CultureFitQuestion.query.filter(CultureFitQuestion.domain == q_field).order_by(func.random()).limit(count).all()
                print(f"questions {questions}")
            else:
                return jsonify({"data":"invalid question type. Please refer to the docs"})
        
        
        if len(questions) == 0:
            return jsonify({"data": "there are no questions yet for this field"})

        questions_data = [
            {
                "question": question.question,
                "domain": question.domain,
            }
            for question in questions
        ]

        return jsonify({"data": questions_data})


    return app