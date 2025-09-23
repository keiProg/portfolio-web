from flask import Flask, render_template, redirect, session, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'helloworld123'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "users.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database = SQLAlchemy(app)

class Users(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(150), unique=True, nullable=False)
    password = database.Column(database.String(150), nullable=False)

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            print('user in database!')
            return redirect(url_for('login'))
        else:
            print('user not in database!')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            hashed_password = generate_password_hash(password)
            new_user = Users(username=username, password=hashed_password)
            database.session.add(new_user)
            database.session.commit()
            print('Signed up succesfully!')
            return redirect(url_for('login'))
        else:
            print('Input information to sign up!')
            return redirect(url_for('signup'))

    return render_template('sign-up.html')

if __name__ == '__main__':
    with app.app_context():
        database.create_all()
    app.run(debug=True)