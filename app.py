from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from chatbot import get_response, detect_mood
from config import SQLALCHEMY_DATABASE_URI, HF_API_KEY
import bcrypt
from datetime import datetime



app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile = db.relationship('UserProfile', backref='user', uselist=False)

# User Profile Model
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    preferences = db.Column(db.Text)

# Chat History Model
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password', 'error')  # Flash error message
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=username, password=hashed_password.decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        preferences = request.form.get('preferences')
        profile = UserProfile(user_id=current_user.id, full_name=full_name, age=age, gender=gender, preferences=preferences)
        db.session.add(profile)
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('profile.html', profile=profile)

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        user_input = request.json.get("message")
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        
        # Detect user mood
        mood = detect_mood(user_input)
        
        # Get response from the chatbot
        response = get_response(user_input, mood)
        
        # Save chat history to the database
        chat_entry = ChatHistory(user_id=current_user.id, message=user_input, response=response, mood=mood)
        db.session.add(chat_entry)
        db.session.commit()
        
        return jsonify({"response": response, "mood": mood})
    
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/chat_history')
@login_required
def chat_history():
    try:
        history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).all()
        return jsonify([{"message": h.message, "response": h.response, "mood": h.mood, "timestamp": h.timestamp} for h in history])
    except Exception as e:
        print(f"Error in /chat_history endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/mood_tracking')
@login_required
def mood_tracking():
    try:
        moods = db.session.query(ChatHistory.mood, db.func.count(ChatHistory.mood)).filter_by(user_id=current_user.id).group_by(ChatHistory.mood).all()
        return jsonify([{"mood": mood, "count": count} for mood, count in moods])
    except Exception as e:
        print(f"Error in /mood_tracking endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/delete_chat/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    try:
        chat_entry = ChatHistory.query.get(chat_id)
        if chat_entry and chat_entry.user_id == current_user.id:
            db.session.delete(chat_entry)
            db.session.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Chat not found or unauthorized"}), 404
    except Exception as e:
        print(f"Error deleting chat: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    try:
        current_password = request.json.get("currentPassword")
        new_password = request.json.get("newPassword")
        
        user = User.query.get(current_user.id)
        if not bcrypt.checkpw(current_password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({"error": "Current password is incorrect"}), 400
        
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password.decode('utf-8')
        db.session.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error changing password: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)