from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required
from models import db, Customer, MenuItem, Order

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/record_order')
@login_required
def record_order():
    return render_template('record_order.html', 
                           menu_items=MenuItem.query.filter_by(is_active=True).all(), 
                           customers=Customer.query.order_by(Customer.name).all())

@admin_bp.route('/add_customer', methods=['POST'])
@login_required
def add_customer():
    name = request.form.get('customer_name')
    if name:
        db.session.add(Customer(name=name, balance=0.0))
        db.session.commit()
    return redirect(url_for('main.dashboard'))

@admin_bp.route('/add_menu_item', methods=['POST'])
@login_required
def add_menu_item():
    name, price = request.form.get('item_name'), request.form.get('item_price')
    if name and price:
        db.session.add(MenuItem(name=name, price=float(price)))
        db.session.commit()
    return redirect(url_for('main.dashboard'))

@admin_bp.route('/add_order', methods=['POST'])
@login_required
def add_order():
    c_id, m_id = request.form.get('customer_id'), request.form.get('menu_item_id')
    qty = int(request.form.get('quantity', 1))
    if c_id and m_id:
        item = MenuItem.query.get(m_id)
        customer = Customer.query.get(c_id)
        customer.balance += (item.price * qty)
        db.session.add(Order(customer_id=c_id, menu_item_id=m_id, quantity=qty))
        db.session.commit()
    return redirect(url_for('main.dashboard'))