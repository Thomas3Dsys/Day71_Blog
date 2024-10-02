from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a Sheet
class CreateSheetForm(FlaskForm):
    title = StringField("Sheet Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired()])
    body = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Create Sheet")


# Create a form to register new users
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class NewProjectForm(FlaskForm):
    title = StringField("Project", validators=[DataRequired()])
    submit = SubmitField("Create New Project")
    

class EditProjectForm(FlaskForm):
    title = StringField("Project Title", validators=[DataRequired()])
    blurb = StringField("Blurb", validators=[DataRequired()])
    git_url = StringField("GitHub Project URL", validators=[DataRequired(), URL()])
    img_thumb = StringField("Thumbnail Image URL", validators=[DataRequired()])
    body = CKEditorField("Project Write Up", validators=[DataRequired()])
    submit = SubmitField("Update Project")


