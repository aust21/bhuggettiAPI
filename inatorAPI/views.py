from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user, logout_user
from .models import CultureFitQuestion, TechnicalQuestion
from werkzeug.utils import secure_filename
from . import db
import os
from PIL import Image

views = Blueprint("views", __name__)


@views.route('/upload_profile_image', methods=['POST'])
@login_required
def upload_profile_image():
    if 'profile_image' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('views.settings'))
    
    file = request.files['profile_image']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('views.settings', id=current_user.id))
    
    if file and allowed_file(file.filename):
        name = f"user_{current_user.id}"

        new_filename = f"{name}.png"
        image = Image.open(file)
        image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename))
        
        current_user.profile_image = new_filename
        db.session.commit()
        
        flash('Profile image updated successfully', 'success')
        return redirect(url_for('views.settings', id=current_user.id))
    
    flash('Invalid file type', 'error')
    return redirect(url_for('views.settings', id=current_user.id))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@views.route('/update_settings', methods=['POST'])
@login_required
def update_settings():
    # Get the form data
    name = request.form.get('name')
    email = request.form.get('email')
    company = request.form.get('company')
    
    # Update the current user's details
    current_user.name = name
    current_user.email = email
    current_user.company = company
    
    
    # Commit the updates to the database
    db.session.commit()

    flash('Account details updated successfully', 'success')
    return redirect(url_for('views.settings', id=current_user.id))

@views.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user_id = current_user.id

    # Optionally delete any related data (posts, files, etc.)
    # Example: Delete user's posts if you have a Post model
    # Post.query.filter_by(user_id=user_id).delete()

    # Delete the user's account
    db.session.delete(current_user)
    db.session.commit()

    # Log the user out
    logout_user()

    flash('Your account has been deleted.', 'info')
    return redirect(url_for('auth.login'))


@views.route("/")
@login_required
def home():
    view = request.args.get('view', 'all')

    cult = CultureFitQuestion.query.filter_by(user_id=current_user.id).all()
    tech = TechnicalQuestion.query.filter_by(user_id=current_user.id).all()
    all = cult + tech

    if view == 'culture-fit':
        posts = cult
    elif view == 'technical':
        posts = tech
    else:
        posts = all

    return render_template("dashboard.html", user=current_user, posts=posts, view=view, cult=len(cult), all=len(all), tech=len(tech))

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


@views.route("/settings<id>")
@login_required
def settings(id):
    return render_template("settings.html", user=current_user)

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