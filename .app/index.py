# Python script to act as the launch point to our Flask web application

# From crypt import methods

# Import the required modules
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify, session
from flask_login import current_user,LoginManager
from flask_login import login_user, logout_user, login_required # For application authentication & authorization
from datetime import datetime, timezone
import secrets
import string

# Import the registration, login and product form modules
from register import RegistrationForm
from login import LoginForm
from user_form import UserForm
from product_form import ProductForm

# Import the database models
from models import Product, init_db, db, User, Role, UserRole
from seed_products_users_and_roles import seed_all

# Get the list of tasks from the tasks API (tasks.py file)
from tasks import tasks

# Declare and create/instantiate a flask object
app = Flask(__name__)

# Application configurations
# 1. Create the application's secret key to protect our site from CSRF attacks
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)  # app_key = secrets.token_hex(18)

# 2. Specfy the path/URI to the sqlite database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ds2505.db'
# Improve th application's performance by not tracking all database modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#Initialise the database
init_db(app)
seed_all(app)

# Setup Flask_login for the applicaion's login functionality
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create a guest user to access out unprotected site areas anonymously (unauthenticated access)
class GuestUser:
    def __init__(self):
        self.full_name = "Guest"
        self.is_authenticated = False
        self.is_active = False
        self.is_anonymous = True

    def is_admin_or_manager(self):
        return False

    def get_id(self):
        return None

# Function to get the user object for the current user, if the current user is authenticated, else
# it returns a Guest subject
@app.context_processor
def inject_user():
    if current_user.is_authenticated:
        return {"current_user": current_user}
    else:
        return {"current_user": GuestUser}

# Function to generate the prefix for the product ids when adding new products in the product's table
def generate_product_id():
    prefix = '01H73QEWM'
    alphabet = string.ascii_uppercase + string.digits
    while True:
        suffix = "".join(secrets.choice(alphabet) for _ in range(8))
        candidate = prefix + suffix
        if Product.query.get(candidate) is None: # when the product id doesn't exist in the 'product' table
            return candidate


# Set the route to the index/home page
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    # Get the user's browser and store it in the browser variable
    browser = request.headers.get('User-Agent')

    # Determine the browser based on the browser string
    if 'Firefox' in browser:
        user_agent = 'Firefox'
    elif 'Opera' in browser:
        user_agent = 'Opera'
    elif 'Chrome' in browser:
        user_agent = 'Chrome'
    elif 'Safari' in browser:
        user_agent = 'Safari'
    elif 'Edge' in browser:
        user_agent = 'Edge'
    else:
        user_agent = 'Unknown'

    # Display the home page and pass the user_agent variable to it
    return render_template('index.html', user_agent=user_agent)


# Set the route to the user's page
@app.route('/user')
@app.route('/user/<username>')
def user(username=None):
    return render_template('user.html', username=username)


# Route to the register/sign-up page
@app.route('/register', methods=['GET', 'POST'])
@app.route('/sign-up', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Process the form data(e.g., save to a database and so on)
        try:
            # check whether the user's email already exists in the database
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already exists. Please use a different email or login.', 'danger')
                return render_template('rgister.html', form=form)
            # check if tje phone number already exists in the database
            if User.query.filter_by(phone=form.phone.data).first():
                flash('Phone number already exists. Please use a different phone number', 'danger')
                return render_template('register.html', form=form)

            # Create a new user in the database
            new_user = User(
                email=form.email.data,
                full_name=form.names.data,
                birth_date=form.birth_date.data,
                gender=form.gender.data.lower(), # Convert to lowercase to match enum
                phone=form.phone.data,
                is_active=True
            )

            # Set the user's password
            new_user.set_password(form.password.data)

            #Add the new_user's details to the database
            db.session.add(new_user)
            db.session.flush() # Get the user ID

            # Assign the new user the default role of customer
            customer_role = Role.query.filter_by(name='Customer').first()
            if customer_role:
                user_role = UserRole(
                    user_id=new_user.id,
                    role_id=customer_role.id,
                    assigned_by=None, # Self registration has no assigned by
                    is_active=True
                )
                db.session,add(user_role)
            db.session.commit()
            flash("Registration or Sign-up successful, you can now login", "success")
            # return redirect(url_for('success'))  # Redirect to a success page
            return redirect(url_for('login'))  # Redirect to a login page
        except Exception as e:
            db.session.rollback()
            flash(f"Sorry there was an error during registration:\n{str(e)}", "danger")
            return render_template('register.html', form=form)
    else:
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", "danger")
    return render_template('register.html', form=form)


# Route to the login/sign-in page
@app.route('/login', methods=['GET', 'POST'])
@app.route('/sign-in', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Process the form data (e.g. redirect to inbox, checkout, view post or friend profile & so on)

        # Get the next page from the query parameter or session
        next_page = request.args.get('next') or session.pop('next', None)

        if form.validate_on_submit():
            # Find the user by their email address
            user = User.query.filter_by(email=form.email.data).first()

            if user and user.check_password(form.password.data):
                #Log in/sign in the user
                login_user(user,remember=True)
                user.last_login = datetime.now(timezone.utc)
                db.session.commit()

                flash("Welcome back, {user.full_name}!", "success")

                # Redirect the user to the intended page or index
                if next_page and next_page != url_for('login'):
                    return redirect(next_page)
                else:
                    return redirect(url_for('index'))
            else:
                flash("Invalid email or password", 'danger')
        # flash("Login or Sign-in Successful", "success")
        # return redirect(url_for('success'))  # Redirect to the success page
    else:
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", "danger")

    # Store the next page in session for after successful login
    if request.args.get('next'):
        session['next'] = request.args.get('next')
    return render_template('login.html', form=form)

# Route to logout/sign out the user
@app.route('/logout')
@login_required # requires the user to be logged in
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

# Route to add the new user (will br accessed by admins only)
@app.route("/add_user", methods=['GET','POST'])
def add_user():
    form = UserForm()
    return render_template('add-user.html', form=form)

# Route to success page
@app.route('/success')
def success():
    return render_template('success.html')

#Route to the product's page (used t display all products in the table)
@app.route('/products')
def products():
    # Get all te products from the products table in the ds2505 database
    products = Product.query.all()
    return render_template('products.html', products=products)

# Route to add product page (usedto add an item/product to the product table)
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            id=form.name.data.replace(' ', '').upper(),
            name=form.name.data,
            price=form.price.data
        )
        # Add and persist the new product to the data base
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('add-products.html', form=form)

# Route to the edit product page (used to modify/change an item in the product list/catalogue)
@app.route("/edit_product/<string:id>", methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get(id)
    if product is None:
        return redirect(url_for('products'))
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('edit-products.html', form=form)

# Route to delete product detail from the product catalogue and subsequently from the product's table
@app.route("/delete_product/<string:id>", methods=['GET', 'POST'])
def delete_product(id):
    product = Product.query.get(id)
    if product is None:
        return redirect(url_for('products'))
    else:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('products'))


# Route to get or fetch the list of to do items/tasks
@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

# Route to display the table and their status (done or not done)
@app.route('/tasks', methods=['GET'])
def view_tasks():
    return render_template('tasks.html')

# Pages to handle site errors
# 1. Handle bad request error (400 error)
@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400


# 2. Handle when authentication is required and has not been provided or failed (401 error)
@app.errorhandler(401)
def unauthorised(e):
    return render_template('401.html'), 401


# 3. Handle when user is authenticated but does'nt have permission to access a resource/page (403 error)
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


# 4. Handle page not found (404 error)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 5. Handle internal server error (500 error)
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# Codr to simulate an internal server error by raising an exception
# @app.route('/trigger-500')
# def trigger_500():
#     # Deliberately raise an error in our server
#     raise Exception("Deliberate internal exception")

# 6. Handle bad gateway error (502 error)
@app.errorhandler(502)
def bad_gateway(e):
    return render_template('502.html'), 502


# 7. Handle when the website is overloaded or temporarily down for upgrades/maintenance (503 error)
@app.errorhandler(503)
def service_unavailable(e):
    return render_template('503.html'), 503


# Set the entry point to our web application
if __name__ == "__main__":
    app.run(debug=True)
