from flask import Flask, render_template, session, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'helloworld123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db', 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f'<product {self.name}>'

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Fields are empty!')
            return render_template('signup.html')
        
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            flash('Username taken!')
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)
        new_user = Users(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_valid = Users.query.filter_by(username=username).first()
        
        if user_valid and check_password_hash(user_valid.password, password):
            session['user_id'] = user_valid.id
            session['username'] = user_valid.username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!')
            return render_template('signin.html')
            

    return render_template('signin.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    products = Products.query.limit(8).all()
    return render_template('home.html', products=products)

@app.route('/products', methods=['POST', 'GET'])
def create_products():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        image_url = request.form.get('image_url')

        if not name or not price or not description or not image_url:
            flash('Fields are empty!', 'error')
            return render_template('products.html')
        
        try:
            price = float(price)
        except ValueError:
            flash('Price must be a number!', 'error')
            return render_template('products.html')

        new_product = Products(
            name=name,
            price=price,
            description=description,
            image_url=image_url
        )
        db.session.add(new_product)
        db.session.commit()

        flash('Product added!', 'success')
        return redirect(url_for('home'))

    return render_template('products.html')

@app.route('/product/<int:product_id>')
def product_details(product_id):
    product = Products.query.get_or_404(product_id)
    return render_template('product_details.html', product=product)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/clear_products')
def clear_products():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    Products.query.delete()
    db.session.commit()
    return "✅ All products deleted!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)