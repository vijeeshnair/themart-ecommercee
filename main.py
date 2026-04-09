from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = 'themart-secret-key-2026'
app.permanent_session_lifetime = timedelta(days=7)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///themart.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to continue'

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Database Models - Simplified without gender column
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    image = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    stock = db.Column(db.Integer, default=100)
    badge = db.Column(db.String(50), nullable=True)
    # Using category to determine men/women instead of separate gender column
    # For men: category contains 'Men' or category is 'Jackets', 'Shirts', etc.
    # For women: category contains 'Women' or category is 'Dresses', 'Rings', etc.

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='cart_items')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    payment_status = db.Column(db.String(50), default='Pending')
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()
    
    # Add sample products if none exist
    if Product.query.count() == 0:
        sample_products = [
            Product(id=1, name="MEN Yarn Fleece Full Zip", category="Men's Jackets", price=61.00, old_price=85.00, image="/static/images/73.png", badge="SALE"),
            Product(id=2, name="Relaxed Short Full Sleeve", category="Men's Shirts", price=61.00, old_price=80.00, image="/static/images/67.png"),
            Product(id=3, name="Running & Trekking Shoes", category="Men's Sports", price=45.00, old_price=70.00, image="/static/images/65.png", badge="NEW"),
            Product(id=4, name="Shiny Dress", category="Women's Dresses", price=95.50, old_price=120.00, image="/static/images/89.png", badge="SALE"),
            Product(id=5, name="Long Dress", category="Women's Dresses", price=95.00, old_price=120.00, image="/static/images/90.png"),
            Product(id=6, name="Full Sweater", category="Women's Sweaters", price=95.50, old_price=120.00, image="/static/images/91.png", badge="NEW"),
            Product(id=7, name="Platinum Zircon Ring", category="Women's Jewellery", price=49.00, old_price=99.00, image="/static/images/66.png", badge="BESTSELLER"),
            Product(id=8, name="Men's Perfume", category="Perfume", price=69.99, old_price=99.99, image="/static/images/62.png"),
            Product(id=9, name="Women's Perfume", category="Perfume", price=59.99, old_price=89.99, image="/static/images/62.png"),
            Product(id=10, name="Smart Watch", category="Accessories", price=199.99, old_price=299.99, image="/static/images/62.png", badge="HOT"),
            Product(id=11, name="Designer Sunglasses", category="Accessories", price=89.99, old_price=149.99, image="/static/images/56.jpg", badge="SALE"),
        ]
        for product in sample_products:
            db.session.add(product)
        db.session.commit()
        print("Sample products added!")

# Helper function to filter products by gender
def get_products_by_gender(gender):
    if gender == 'Men':
        return Product.query.filter(Product.category.like('Men\'s%')).all()
    elif gender == 'Women':
        return Product.query.filter(Product.category.like('Women\'s%')).all()
    else:
        return Product.query.all()

# Routes
@app.route('/')
def index():
    products = Product.query.limit(8).all()
    return render_template('index.html', products=products)

@app.route('/categories')
def categories():
    return render_template('categories.html')

@app.route('/mens')
def mens():
    products = Product.query.filter(Product.category.like('Men\'s%')).all()
    return render_template('category_page.html', products=products, title="Men's Collection")

@app.route('/womens')
def womens():
    products = Product.query.filter(Product.category.like('Women\'s%')).all()
    return render_template('category_page.html', products=products, title="Women's Collection")

@app.route('/perfume')
def perfume():
    products = Product.query.filter_by(category='Perfume').all()
    return render_template('category_page.html', products=products, title="Perfume Collection")

@app.route('/jewellery')
def jewellery():
    products = Product.query.filter(Product.category.like('%Jewellery%')).all()
    return render_template('category_page.html', products=products, title="Jewellery Collection")

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/hot-offers')
def hot_offers():
    products = Product.query.filter(Product.badge.isnot(None)).all()
    return render_template('category_page.html', products=products, title="Hot Offers")

@app.route('/shop')
def shop():
    products = Product.query.all()
    return render_template('shop.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=remember)
        flash('Login successful!', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password, phone=phone)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update-cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    quantity = int(request.form.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
    else:
        db.session.delete(cart_item)
    
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/remove-from-cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id == current_user.id:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        
        order = Order(
            order_id=f'ORD{datetime.now().strftime("%Y%m%d%H%M%S")}{current_user.id}',
            user_id=current_user.id,
            total_amount=total,
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode
        )
        db.session.add(order)
        db.session.commit()
        
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity
            )
            db.session.add(order_item)
        
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order_success', order_id=order.id))
    
    return render_template('checkout.html', cart_items=cart_items, total=total, user=current_user)

@app.route('/order-success/<int:order_id>')
@login_required
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return redirect(url_for('index'))
    return render_template('order_success.html', order=order)

@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

@app.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user)

@app.route('/api/cart-count')
@login_required
def cart_count():
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
