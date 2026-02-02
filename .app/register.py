# Our site's registration/sign-up form

# Get the required modules
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, RadioField
from wtforms import EmailField, PasswordField, TelField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# Declare the RegistrationForm class
class RegistrationForm(FlaskForm):
    names = StringField("Names", validators=[DataRequired()],
                        render_kw={'placeholder': 'Enter names',
                                   'title': 'Please enter your names',
                                   'tabindex': 10})
    birth_date = DateField('Birth date', validators=[DataRequired()],
                           render_kw={'placeholder': 'yyyy/mm/dd',
                                      'title': 'Please enter your birth date',
                                      'tabindex': 20})
    gender = RadioField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')],
                        validators=[DataRequired()],
                        render_kw={'title': 'Please select your gender','tabindex': 30})
    phone = TelField('Phone Number', validators=[DataRequired()],
                     render_kw={'placeholder': '+254 788 123456',
                                'title': 'Please enter your phone number',
                                'tabindex': 40})
    email = EmailField('Email', validators=[DataRequired()],
                       render_kw={'placeholder':'me@email.com',
                                  'title':'Please enter your email',
                                  'tabindex':50})
    password = PasswordField('Password', validators=[DataRequired(),Length(min=0)],
                             render_kw={'placeholder':'Secret password',
                                        'title':'Please enter your password',
                                        'tabindex':60})
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(),
                                                                     EqualTo('password',
                                                                             message='Passwords must match')],
                                     render_kw={'placeholder':'Confirm secret password',
                                                'title':'Please confirm your password',
                                                'tabindex':70})

    # Submit and Reset buttons
    submit = SubmitField('Register',
                         render_kw={'title': 'Submit your registration details',
                                    'tabindex':80})
    reset = SubmitField('Reset',
                        render_kw={'title':'Clear all fields',
                                   'tabindex':90})