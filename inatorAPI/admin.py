from flask import current_app, json, render_template, Blueprint, request, flash, redirect, url_for, abort, jsonify
from flask_mail import Message
from .models import TechnicalQuestion, CultureFitQuestion, User
from flask_login import login_required, current_user
from . import db, mail


admin = Blueprint("admin", __name__)


@admin.route("/delete-post/<field>/<int:id>")
@login_required
def delete_post(field, id):
    if not current_user.is_admin:
        abort(403)  # Forbidden

    view = request.args.get('view', 'all')

    if field == "culture-fit":
        post = CultureFitQuestion.query.get_or_404(id)
    elif field == "technical":
        post = TechnicalQuestion.query.get_or_404(id)
    else:
        abort(404)  # Not Found

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully", category="success")

    return redirect(url_for("admin.admin_dash", view=view))


@admin.route("/dashboard")
@login_required
def admin_dash():
    view = request.args.get('view', 'dash')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # For AJAX requests
        # Return JSON data
        data = {
            'view': view,
            'users': len(User.query.all()) - 1,
            'tech_count': len(TechnicalQuestion.query.all()),
            'culture_count': len(CultureFitQuestion.query.all()),
            # Add more data as needed
        }
        return jsonify(data)
    
    # For regular requests (initial page load)
    culture_questions = CultureFitQuestion.query.all()
    tech_questions = TechnicalQuestion.query.all()
    users = len(User.query.all()) - 1
    posts = culture_questions + tech_questions
    posts.sort(key=lambda x: x.date_created, reverse=True)
    user_accounts = User.query.all()
    
    return render_template("control_panel.html", 
                         posts=posts, 
                         tech=len(tech_questions),
                         cult=len(culture_questions), 
                         all=len(posts), 
                         user=current_user, 
                         users=users, 
                         view=view,
                         accounts=user_accounts,
                         )

@admin.route("/send_update", methods=['POST'])
@login_required
def send_update():
    view = request.args.get('view', 'notifications')
    selected_emails = json.loads(request.form.get('selected_emails', '[]'))
    message = request.form.get('message', '')
    subject = request.form.get("subject")
    
    html = render_template('email/webupdates.html', message=message, user=current_user)

    for email in selected_emails:
        # Example using Flask-Mail
        msg = Message(subject,
                     sender=current_app.config['MAIL_USERNAME'],
                     recipients=[email])
        msg.html = html
        mail.send(msg)
    
    flash('Updates sent successfully!', 'success')
    return redirect(url_for('admin.admin_dash', view=view))

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