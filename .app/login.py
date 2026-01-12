# Our site's login/sign-in form

# Get the required modules
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length

# Declare the LoginForm class
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()],
                       render_kw={'placeholder':'me@email.com',
                                  'title':'Please enter your email',
                                  'tabindex':10})
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8)],
                             render_kw={'placeholder':'Secret password',
                                        'title':'Please enter your password',
                                        'tabindex':20})
    # Optional remember me checkbox
    remember = BooleanField('Remember me?')

    # Submit and Reset buttons
    submit = SubmitField('Login',
                         render_kw={'title': 'Login/sign-in to the site',
                                    'tabindex':30})