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
        if Product.query.count() == 0: # You can also use 'if not Product.query.first()'
            # Variable to hold the records to be inserted/added to the product table
            sample_records = [
                ('01H73QEWMF1KG6QADD', 'Ground beef parties - 25% Fat', 980.0),
                ('01H73QEWMFMWNQPSM', 'Coffee - Hazelnut Cream', 815.0),
                ('01H73QEWMGFSMTWR3X', 'Coffee - Flavoured', 905.0),
                ('01H73QEWMGHCW3PXFR', 'Tequila Rose Cream Liquor', 675.0),
                ('01H73QEWMG9MD4CTB9', 'Split Peas - Yellow, Dry', 820.0),
                ('01H73QEWMGTRXVQYY', 'Wine - Vineland Estate Semi - Dry', 855.0),
                ('01H73QEWMH3GCAA4P', 'Mushroom - Chanterelle, Dry', 585.0),
                ('01H73QEWMHM6WXBGM', 'Butter - KCC Salted', 760.0),
                ('01H73QEWMHPX9KZ2YV', 'Olives - Black, Pitted', 450.0),
                ('01H73QEWMHQ7T5R6WX', 'Pasta - Fettuccine, Egg', 320.0),
                ('01H73QEWMHR4F8S9D2', 'Cheese - Cheddar, Medium', 690.0),
                ('01H73QEWMHS1G3H5J7', 'Chicken - Whole Roasting', 1250.0),
                ('01H73QEWMHT9K8L2P4', 'Tomatoes - Cherry, Yellow', 380.0),
                ('01H73QEWMHV7M6N1Q3', 'Bread - Italian Roll With Herbs', 420.0),
                ('01H73QEWMHW5T9R7Y2', 'Salmon - Fillets', 1980.0),
                ('01H73QEWMHX3V8B6N5', 'Chocolate - Dark, 70% Cocoa', 550.0)
            ]

            # Insert the above sample data into the Product table using a for loop
            for record in sample_records:
                product = Product(id=record[0], name=record[1], price=record[2])
                db.session.add(product)

            # Commit the changes to the database after inserting the sample data
            db.session.commit()