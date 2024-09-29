from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuring the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///questions.db'
db = SQLAlchemy(app)

# Define the Question model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=True)

# Create the database
with app.app_context():
    db.create_all()

# API route to post a new question
@app.route('/questions', methods=['POST'])
def add_question():
    data = request.get_json()
    new_question = Question(question_text=data['question_text'], category=data.get('category', 'General'))
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Question added successfully!'}), 201

# API route to get all questions
@app.route('/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    return jsonify([{'id': q.id, 'question_text': q.question_text, 'category': q.category} for q in questions]), 200

if __name__ == '__main__':
    app.run(debug=True)
