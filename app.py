from flask import Flask
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from models import db, Admin
import os

# Import Blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:your_mysql_password@localhost/mamaprogram'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)

with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username='admin').first():
        db.session.add(Admin(username='admin', password_hash=generate_password_hash('mama123')))
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)