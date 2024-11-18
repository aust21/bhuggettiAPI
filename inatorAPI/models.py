from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import date

from . import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    speciality = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.Date, default=date.today)
    is_admin = db.Column(db.Boolean, default=False)
    culture_fit_questions = db.relationship('CultureFitQuestion', backref='user', passive_deletes=True)
    technical_questions = db.relationship('TechnicalQuestion', backref='user', passive_deletes=True)
    profile_image = db.Column(db.String(100), default='default.png') 
    cormfirm_code = db.Column(db.String(7), default="0000000")
    account_confirmed = db.Column(db.Boolean, default=False)

    @property
    def total_submissions(self):
        return len(self.culture_fit_questions) + len(self.technical_questions)

class CultureFitQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    domain = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.Date, default=date.today)
    field = db.Column(db.String(500), nullable=False)


class TechnicalQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    domain = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.Date, default=date.today)
    field = db.Column(db.String(500), nullable=False)

class QuestionFields(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_field = db.Column(db.String(1000), nullable=False)