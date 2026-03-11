from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from sqlalchemy import func

# Import the db object and models from models.py
from models import db, Admin, Customer, MenuItem, Order

app = Flask(__name__)
# Secret key is required for form security and session cookies (keeping you logged in)
app.config['SECRET_KEY'] = 'your_super_secret_key_here_change_later' 

# Configure the MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:your_mysql_password@localhost/mamaprogram'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and login manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Where to send users if they aren't logged in

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# --- APP CREATION & INITIAL ADMIN SETUP ---
with app.app_context():
    db.create_all() 
    
    # Check if admin exists. If not, create it.
    if not Admin.query.filter_by(username='admin').first():
        hashed_pw = generate_password_hash('mama123') 
        new_admin = Admin(username='admin', password_hash=hashed_pw)
        db.session.add(new_admin)
        db.session.commit()
        print("Initial admin account created: User='admin', Pass='mama123'")

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin, remember=True) 
            return redirect(url_for('dashboard'))
        else:
            print("Failed login attempt.")
            return redirect(url_for('login'))

    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():

    food_totals = db.session.query(
        MenuItem.name, 
        func.sum(Order.quantity).label('total_qty')
    ).join(Order, MenuItem.id == Order.menu_item_id)\
     .group_by(MenuItem.name).all()
    total_owed = db.session.query(func.sum(Customer.balance)).filter(Customer.balance > 0).scalar() or 0.0
    total_expected = db.session.query(
        func.sum(MenuItem.price * Order.quantity)
    ).join(Order, MenuItem.id == Order.menu_item_id).scalar() or 0.0
    total_collected = total_expected - total_owed

    return render_template('dashboard.html', 
                           food_totals=food_totals,
                           total_owed=total_owed,
                           total_collected=total_collected)

@app.route('/record_order', methods=['GET'])
@login_required
def record_order():
    # Fetch data needed for the form
    menu_items = MenuItem.query.filter_by(is_active=True).all()
    customers = Customer.query.order_by(Customer.name).all()
    
    return render_template('record_order.html', 
                           menu_items=menu_items, 
                           customers=customers)

@app.route('/add_customer', methods=['POST'])
@login_required
def add_customer():
    name = request.form.get('customer_name')
    if name:
        new_customer = Customer(name=name, balance=0.0)
        db.session.add(new_customer)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_menu_item', methods=['POST'])
@login_required
def add_menu_item():
    name = request.form.get('item_name')
    price = request.form.get('item_price')
    if name and price:
        new_item = MenuItem(name=name, price=float(price))
        db.session.add(new_item)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_order', methods=['POST'])
@login_required
def add_order():
    c_id = request.form.get('customer_id')
    m_id = request.form.get('menu_item_id')
    qty = int(request.form.get('quantity', 1))
    
    if c_id and m_id:
        # Create the order
        new_order = Order(customer_id=c_id, menu_item_id=m_id, quantity=qty)
        
        # Update customer balance: price * quantity
        item = MenuItem.query.get(m_id)
        customer = Customer.query.get(c_id)
        customer.balance += (item.price * qty)
        
        db.session.add(new_order)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)