from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    status = SelectField('Status', choices=[('New tasks', 'New tasks'), ('Backlog', 'Backlog'), ('Todo', 'Todo'), ('In Progress', 'In Progress'), ('Done', 'Done')])
    tags = StringField('Category')  # For non-claim tags
    submit = SubmitField('Submit')

class ClaimTaskForm(FlaskForm):
    submit = SubmitField('Claim Task')

class UnclaimTaskForm(FlaskForm):
    submit = SubmitField('Unclaim Task')