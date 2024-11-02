from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user, logout_user
from .models import CultureFitQuestion, TechnicalQuestion
from werkzeug.utils import secure_filename
from . import db
import os
from PIL import Image
from sqlalchemy import exc

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
    
    old_email = current_user.email
    # Update the current user's details
    current_user.name = name
    current_user.email = email
    current_user.company = company

    if old_email != email:
        current_user.account_confirmed = False
    
    # Commit the updates to the database
    db.session.commit()

    flash('Account details updated successfully', 'success')
    return redirect(url_for('views.settings', id=current_user.id))

@views.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    try:
        user_id = current_user.id
        
        # Delete profile image if it exists
        if current_user.profile_image and current_user.profile_image != 'default.jpg':
            image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], current_user.profile_image)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except OSError as e:
                    current_app.logger.error(f"Error deleting profile image: {e}")
        
        # Begin database transaction
        db.session.begin_nested()
        
        # Delete all associated data using cascade if possible, otherwise manual deletion
        try:

            TechnicalQuestion.query.filter_by(user_id=user_id).delete()
            CultureFitQuestion.query.filter_by(user_id=user_id).delete()
            
            
            db.session.delete(current_user)
            db.session.commit()
            
        except exec.SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error during account deletion: {e}")
            flash('An error occurred while deleting your account. Please try again.', 'error')
            return redirect(url_for('views.settings'))
        
        # Log the user out after successful deletion
        logout_user()
        
        flash('Your account has been successfully deleted.', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error during account deletion: {e}")
        flash('An unexpected error occurred. Please contact support.', 'error')
        return redirect(url_for('views.settings'))


@views.route("/")
@login_required
def home():
    view = request.args.get('view', 'dash')

    cult = CultureFitQuestion.query.filter_by(user_id=current_user.id).all()
    tech = TechnicalQuestion.query.filter_by(user_id=current_user.id).all()
    all = cult + tech

    cult_count = CultureFitQuestion.query.filter_by(user_id=current_user.id).count()
    tech_count = TechnicalQuestion.query.filter_by(user_id=current_user.id).count()
    total_count = cult_count + tech_count

    if view == 'culture-fit':
        posts = cult
    elif view == 'technical':
        posts = tech
    else:
        posts = all

    return render_template("dashboard.html", 
                        user=current_user, 
                        posts=posts, 
                        view=view, 
                        cult=cult, 
                        all=all, 
                        tech=tech,
                        cult_count=cult_count,
                        tech_count=tech_count,
                        total_count=total_count
                            )

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