from flask import Blueprint, render_template, request, session, jsonify
from flask_login import login_required, current_user

views = Blueprint("views", __name__)

@views.route("/")
@login_required
def home():
    return render_template("dashboard.html", user=current_user)

# Add this context processor to make current_user available in all templates
@views.context_processor
def inject_user():
    return dict(current_user=current_user)