# Python script to act as the launch point to our Flask web application

# Import the required modules
from flask import Flask, render_template, request, url_for, flash
import secrets

from registration import RegistrationForm
from login import LoginForm

# Declare and create/instantiate a flask object
app = Flask(__name__)

# Application configurations
# 1. Create the application's secret key to protect our site from CSRF attacks
app.config['SECRET_KEY'] = secrets.token_urlsafe(32) # app_key = secrets.token_hex(18)

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
@app.route('/register', methods=['GET','POST'])
@app.route('/sign-up', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Process the form data(e.g., save to a database and so on)
        flash("Registration or Sign-up successful","success")
        return redirect(url_for('success')) # Redirect to a success page
    else:
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form,field).label.text}: {error}","danger")
    return render_template('registration.html',form=form)

# Route to the login/sign-in page
@app.route('/login', methods=['GET','POST'])
@app.route('/sign-in', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Process the form data (e.g. redirect to inbox, checkout, view post or friend profile & so on)
        flash("Login or Sign-in Successful","success")
        return redirect(url_for('success')) # Redirect to the success page
    else:
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", "danger")
    return render_template('login.html', form=form)

# Route to success page
@app.route('/success')
def success():
    return render_template('success.html')

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