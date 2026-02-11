# Python file to create a new user in the system/app. Only accessible by admin users

# Import the required modules
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, RadioField, EmailField
from wtforms import TelField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from wtforms.widgets import TextArea


# Define the user form
class UserForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email address must be 120 characers or less'),
    ],
                        render_kw={'placeholder': 'me@email.com',
                                   'title': "Please enter the  employee's email",
                                   'tabindex': 10}
                        )

    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=150, message='Full name must be between 2 and 150 characers'),
    ],
                        render_kw={'placeholder': 'Employee Jane Doe',
                                   'title': "Please enter the employee's full name",
                                   'tabindex': 20}
                        )

    birth_date = DateField('Birth Date', validators=[
        DataRequired(message='Birth Date is required'),
    ],format="%Y-%m-%d", render_kw={'placeholder': 'YYYY-MM-DD',
                                   'title': "Please enter the employee's birthe date",
                                   'tabindex': 30}
                        )

    gender = RadioField('Gender',
                         choices=[('Male', 'Male'), ('Female', 'Female')],
                         validators=[DataRequired(message='Gender is required')],
                         render_kw={'title': "Please select the employee's gender",
                                    'tabindex': 40})

    phone = StringField("Phone Number", validators=[
        DataRequired('Phone number is required'),
        Length(min=0, max=11, message='Phone number must be 10 or 11 digits'),
        Regexp(r'\d{10,11}', message='Phone number must contain only digits')
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=18, message='Password must be between 8 and 18 characters'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
               message="Password must be between 8 to 18 characters, contain at least one uppercase, "
                            "one lowercase, one digit and one special character")
    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Confirm password is required'),
        EqualTo('password', message='Passwords must match')
    ])

    role = SelectField('Role', choices=[
        ('Admin','Admin'),
        ('Manager','Manager'),
        ('Staff','Staff'),
        ('Customer','Customer')
    ], validators=[DataRequired(message='Role is required')])