from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
qdb = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)
    from .auth import auth
    from .models import User
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


    return app