from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from models.models import db
from routes.auth_routes import auth_routes
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traffic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(auth_routes, url_prefix='/auth')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)