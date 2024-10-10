from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import CultureFitQuestion, TechnicalQuestion
from . import db

views = Blueprint("views", __name__)

@views.route("/")
@login_required
def home():
    view = request.args.get('view', 'culture-fit')

    if view == 'culture-fit':
        posts = CultureFitQuestion.query.filter_by(user_id=current_user.id).all()
    else:
        posts = TechnicalQuestion.query.filter_by(user_id=current_user.id).all()

    return render_template("dashboard.html", user=current_user, posts=posts, view=view)

@views.route("/submit-question", methods=["GET", "POST"])
@login_required
def submit_question():
    if request.method == "POST":
        form_question = request.form.get("question")
        industry = request.form.get("category")
        field = request.form.get("field")
        if industry == "technical":
            post = TechnicalQuestion(question=form_question, user_id=current_user.id, field=industry, domain=field)
        else:
            post = CultureFitQuestion(question=form_question, user_id=current_user.id, field=industry, domain=field)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('views.home'))
# Add this context processor to make current_user available in all templates
@views.context_processor
def inject_user():
    return dict(current_user=current_user)