from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from models import db, Customer, MenuItem, Order

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    food_totals = db.session.query(
        MenuItem.name, func.sum(Order.quantity).label('total_qty')
    ).join(Order, MenuItem.id == Order.menu_item_id).group_by(MenuItem.name).all()

    total_owed = db.session.query(func.sum(Customer.balance)).filter(Customer.balance > 0).scalar() or 0.0
    total_expected = db.session.query(func.sum(MenuItem.price * Order.quantity)).join(Order).scalar() or 0.0
    
    return render_template('dashboard.html', 
                           food_totals=food_totals,
                           total_owed=total_owed,
                           total_collected=total_expected - total_owed)