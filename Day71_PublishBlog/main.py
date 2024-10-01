from datetime import date
from turtle import title
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreateSheetForm, RegisterForm, LoginForm, NewProjectForm,EditProjectForm 
# Optional: add contact me email functionality (Day 60)
# import smtplib
import os
#from dotenv import load_dotenv

#load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
print(f"envTest:{os.environ.get('envTest')}")
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# For adding profile images to the comment section
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')

db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
class Sheet(db.Model):
    __tablename__ = "sheets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


# Create a User table for all your registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))



class Project(db.Model):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    git_url: Mapped[str] = mapped_column(String(250), unique=True, nullable=True)
    blurb: Mapped[str] = mapped_column(String(250), nullable=True)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=True)
    img_thumb: Mapped[str] = mapped_column(String(250), nullable=True)
    

with app.app_context():
    db.create_all()


# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("sheets"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('sheets'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('sheets'))


@app.route('/resume')
def resume():
    return render_template("resume.html", current_user=current_user)

@app.route('/projects', methods=["GET", "POST"])
def projects():
    form = NewProjectForm()
    result = db.session.execute(db.select(Project))
    projects = result.scalars().all()
    if form.validate_on_submit():
        new_project = Project(
            title=form.title.data,
            date =date.today().strftime("%B %d, %Y")
            )
        db.session.add(new_project)
        db.session.commit()
        flash(f"New Project Entry Created: {form.title.data}")
        new_form = NewProjectForm()
        return render_template("projects.html", all_projects=projects, form=new_form, current_user=current_user)
        

    return render_template("projects.html", all_projects=projects, form=form, current_user=current_user)


@app.route('/')
def home():
    proj_res = db.session.execute(db.select(Project))
    projects= proj_res.scalars().all()

    sheet_res = db.session.execute(db.select(Sheet))
    sheets= sheet_res.scalars().all()

    return render_template("index.html", top_projects = projects, top_sheets = sheets, current_user=current_user)

@app.route('/sheets')
def sheets():
    result = db.session.execute(db.select(Sheet))
    sheets = result.scalars().all()
    return render_template("sheets.html", all_sheets=sheets, current_user=current_user)


@app.route("/sheet/<int:sheet_id>", methods=["GET", "POST"])
def show_sheet(sheet_id):
    requested_sheet = db.get_or_404(Sheet, sheet_id)
    return render_template("sheet.html", sheet=requested_sheet, current_user=current_user)



@app.route("/project/<int:project_id>", methods=["GET", "POST"])
def view_project(project_id):
    requested_project = db.get_or_404(Project, project_id)
    return render_template("project.html", project=requested_project, current_user=current_user)


@app.route("/edit-project/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    project = db.get_or_404(Project, project_id)
    edit_form = EditProjectForm(
         title=project.title,
         blurb=project.blurb,
         git_url=project.git_url,
         img_thumb=project.img_thumb,
         body=project.body
     )
    if edit_form.validate_on_submit():
        project.title = edit_form.title.data
        project.blurb = edit_form.blurb.data
        project.git_url = edit_form.git_url.data
        project.img_thumb = edit_form.img_thumb.data
        project.body = edit_form.body.data
        db.session.commit()
        flash("Project Updated")
        return redirect(url_for("view_project", project_id=project.id))
    return render_template("edit-project.html", form=edit_form, current_user=current_user)





# Use a decorator so only an admin user can create new posts
@app.route("/new-sheet", methods=["GET", "POST"])
@admin_only
def add_new_sheet():
    form = CreateSheetForm()
    if form.validate_on_submit():
        new_sheet = Sheet(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_sheet)
        db.session.commit()
        return redirect(url_for("sheets"))
    return render_template("make-sheet.html", form=form, current_user=current_user)


# Use a decorator so only an admin user can edit a sheet
@app.route("/edit-sheet/<int:sheet_id>", methods=["GET", "POST"])
def edit_sheet(sheet_id):
    sheet = db.get_or_404(Sheet, sheet_id)
    edit_form = CreateSheetForm(
        title=sheet.title,
        subtitle=sheet.subtitle,
        img_url=sheet.img_url,
        body=sheet.body
    )
    if edit_form.validate_on_submit():
        sheet.title = edit_form.title.data
        sheet.subtitle = edit_form.subtitle.data
        sheet.img_url = edit_form.img_url.data
        sheet.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_sheet", sheet_id=sheet.id))
    return render_template("make-sheet.html", form=edit_form, is_edit=True, current_user=current_user)


# Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:sheet_id>")
@admin_only
def delete_sheet(sheet_id):
    sheet_to_delete = db.get_or_404(Sheet, sheet_id)
    db.session.delete(sheet_to_delete)
    db.session.commit()
    return redirect(url_for('sheets'))


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html", current_user=current_user)


if __name__ == "__main__":
    app.run(debug=False, port=5001)
