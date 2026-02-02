# Python file to model the database tables
from email.policy import default
from sys import path_hooks

# Import the required module(s)
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
import bcrypt

# Create the datatbase object/instance
db = SQLAlchemy()

# Define the User Model/Class
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('male', 'female',name='gender_enum'), nullable=False)
    phone = db.Column(db.String(11), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc),
                           onupdate=datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    multi_factor_enabled = db.Column(db.Boolean, default=False)
    password_updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Method to return a string representation of the object
    def __rep__(self):
        return f"Name: {self.full_name}. Email: {self.email}"

    # Method to hash and set the user's encrypted password
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.password_updated_at = datetime.now(timezone.utc)

    # Method to check if the user's email already exists in the database
    @staticmethod
    def check_email_exists_(email):
        return User.query.filter_by(email=email).first() is not None

    # Method to create the user account in the database
    def create_user(self, email,full_name,birth_date,gender,password):
        if User.check_email_exists_(email):
            raise ValueError("Email already exists")

        user = User(email=email, full_name=full_name, birth_date=birth_date,gender=gender,phone=phone)
        user.set_password(password)
        # Addthe default user role of customer
        customer_role = Role.query.filter_by(name='Customer').first()
        if customer_role:
            user_role = UserRole(user=user, role=customer_role, assigned_by=None,is_active=True)
            db.session.add(user)
            db.session.commit()
            return user
    # Method to check whether a user is an admin or manager
    def is_admin_or_manager(self):
        """Checks if the user has an admin or manager role"""
        if not self.is_authenticated:
            return False
        return any(ur.role.name in ['Admin','Manager'] for ur in self.user_roles if ur.is_active)

    # Method to check whether a user is an admin or manager
    def is_admin(self):
        """Checks if the user has an admin role"""
        if not self.is_authenticated:
            return False
        return any(ur.role.name == 'Admin' for ur in self.user_roles if ur.is_active)

# Define the Role model/class
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc),
                           onupdate=datetime.now(timezone.utc))
    is_system_admin = db.Column(db.Boolean, default=False)

    # Method to return string representation of the object
    def __repr__(self):
        return f"Role: {self.name}, Description: {self.description}"

# Define the UserRole model/class
class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Link/create relationships to the users and roles tables
    user = db.relationship('User', foreign_keys=[user_id],backref=db.backref('user_role', lazy=True,
                                                                             cascade='all, delete-orphan'))
    role = db.relationship('Role', backref=db.backref('user_role', lazy=True,
                                                      cascade='all, delete-orphan'))

    # Method to return a string representation of the user-role object
    def __repr__(self):
        return f"UserRole : {self.user.email} - {self.role.name}"

# Define the Product model/class
class Product(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Method to return a string representation of the product
    def __repr__(self):
        return f"Product ID: {self.id}, Name: {self.name}, Price: {self.price}"

# Function to create the Product table in the database and populate it with data
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

        # Populate the product table with data if it's empty
        # if Product.query.count() == 0: # You can also use 'if not Product.query.first()'
