from flask import Flask, session, render_template, flash, url_for, redirect, request
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'helloworld123321'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db', 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('landing-page.html', username=session.get('username'))

@app.route('/signin', methods=['POST', 'GET'])
def sign_in():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        valid_user = Users.query.filter_by(username=username).first()

        if not username or not password:
            flash('Input empty fields!', 'error')
            return render_template('login.html')

        if valid_user and check_password_hash(valid_user.password, password):
            session['username'] = valid_user.username
            session['user_id'] = valid_user.id
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
            return render_template('login.html')
        
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Input empty fields!', 'error')
            return redirect(url_for('sign_up'))

        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            flash('username already taken!', 'warning')
            return redirect(url_for('sign_up'))

        hashed_password = generate_password_hash(password)
        new_user = Users(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('sign_in'))

    return render_template('signup.html')

@app.route('/services', methods=['POST', 'GET'])
def service():
    return render_template('service.html', username=session.get('username'))

@app.route('/aboutme', methods=['POST', 'GET'])
def aboutme():
    return render_template('aboutme.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)