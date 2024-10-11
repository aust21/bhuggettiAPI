from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import CultureFitQuestion, TechnicalQuestion
from . import db

views = Blueprint("views", __name__)

@views.route("/")
@login_required
def home():
    view = request.args.get('view', 'all')

    if view == 'culture-fit':
        posts = CultureFitQuestion.query.filter_by(user_id=current_user.id).all()
    elif view == 'technical':
        posts = TechnicalQuestion.query.filter_by(user_id=current_user.id).all()
    else:
         # view all posts (both culture-fit and technical)
        culture_fit_posts = CultureFitQuestion.query.filter_by(user_id=current_user.id).all()
        technical_posts = TechnicalQuestion.query.filter_by(user_id=current_user.id).all()
        posts = culture_fit_posts + technical_posts 

    return render_template("dashboard.html", user=current_user, posts=posts, view=view)

@views.route("/delete-post/<field>/<id>")
@login_required
def delete_post(id, field):
    
    view = request.args.get('view', 'all')

    if field == "culture-fit":
        post = CultureFitQuestion.query.filter_by(id=id).first()
    else:
        post = TechnicalQuestion.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist", category="error")
    elif current_user.id == post.user_id:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted", category="success")

    return redirect(url_for("views.home", view=view))

@views.route("/submit-question", methods=["GET", "POST"])
@login_required
def submit_question():
    view = request.args.get('view', 'all')

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
        return redirect(url_for('views.home', user=current_user, view=view))
    
# Add this context processor to make current_user available in all templates
@views.context_processor
def inject_user():
    return dict(current_user=current_user)