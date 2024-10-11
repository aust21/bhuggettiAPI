from flask import render_template, Blueprint, request
from .models import TechnicalQuestion, CultureFitQuestion, User
from flask_login import login_required, current_user

admin = Blueprint("admin", __name__)


@admin.route("/dashboard")
@login_required
def admin_dash():
    culture_questions = CultureFitQuestion.query.all()
    tech_qustions = TechnicalQuestion.query.all()
    posts = culture_questions + tech_qustions

    return render_template("control_panel.html", posts=posts)

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