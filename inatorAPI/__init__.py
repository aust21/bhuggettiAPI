from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from sqlalchemy import func
from oauthlib.oauth2 import WebApplicationClient

db = SQLAlchemy()
DB_NAME = "database.db"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)
    from .auth import auth
    from .models import User, QuestionModel
    from .views import views

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(views, url_prefix="/dash")


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

        questions = QuestionModel.query.order_by(func.random()).limit(count).all()

        questions_data = [
            {
                "id": question.id,
                "question": question.question,
                "user_id": question.user_id,
                "domain": question.domain,
            }
            for question in questions
        ]

        return jsonify({"data": questions_data})


    return app