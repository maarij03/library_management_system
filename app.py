from flask import Flask
from flask_jwt_extended import JWTManager
from controller.admin import admin_bp
from controller.customer import customer_bp
from model.db import init_db
from datetime import timedelta
app = Flask(__name__)

# Configuration for JWT
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_ALGORITHM"] = "HS256"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

jwt = JWTManager(app)

# Initialize the database
init_db(app)

# Register Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(customer_bp)

if __name__ == "__main__":
    app.run(debug=True, port=3000)
