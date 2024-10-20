from flask import render_template, Blueprint, request, flash, redirect, url_for
from .models import TechnicalQuestion, CultureFitQuestion, User
from flask_login import login_required, current_user
from . import db

admin = Blueprint("admin", __name__)


@admin.route("/delete-post/<field>/<id>")
@login_required
def delete_post(id, field):
    
    view = request.args.get('view', 'all')

    if field == "culture-fit":
        post = CultureFitQuestion.query.filter_by(id=id).first()
    else:
        post = TechnicalQuestion.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist", category="error")
    
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted", category="success")

    return redirect(url_for("admin.admin_dash", view=view))


@admin.route("/dashboard")
@login_required
def admin_dash():
    culture_questions = CultureFitQuestion.query.all()
    tech_qustions = TechnicalQuestion.query.all()
    users = len(User.query.all()) - 1
    posts = culture_questions + tech_qustions
    posts.sort(key=lambda x: x.date_created, reverse=True)
    return render_template("control_panel.html", posts=posts, tech=len(tech_qustions), 
                           cult=len(culture_questions), all=len(posts), user = current_user, users=users)

@admin.route("/admin/dashbord/view-posts")
@login_required
def view_posts():

    view = request.args.get('view', 'all')

    if view == 'culture-fit':
        posts = CultureFitQuestion.query.all()
    elif view == 'technical':
        posts = TechnicalQuestion.query.all()
    else:
        culture_fit_posts = CultureFitQuestion.query.all()
        technical_posts = TechnicalQuestion.query.all()
        posts = culture_fit_posts + technical_posts 


    return render_template("posts_view.html", posts=posts, view=view)

@admin.route("/admin/dashbord/user<id>")
def view_user(id):
    return render_template("user.html")