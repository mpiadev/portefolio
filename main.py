from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash, send_file
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, form 
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms.fields import StringField, EmailField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder="assets/templates",
    static_folder="assets/static",
    instance_path=BASE_DIR
)
app.config["SECRET_KEY"] = "top-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

db = SQLAlchemy(app)
admin = Admin(app, name="Admin", template_mode="bootstrap4")

class Contact(db.Model):
    __tablename__ = "contacts"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    date = db.Column(db.DateTime(), default=datetime.utcnow())

    def __str__(self):
        return self.name
    

class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    image = db.Column(db.Unicode(128))

    def __str__(self):
        return self.name
    

class ProjectAdminView(ModelView):
    form_overrides = {"image": form.ImageUploadField}
    form_args = {
        "image": {
            "label": "Image",
            "base_path": BASE_DIR / "assets",
            "relative_path": "static/uploads/"
        }
    }


class ContactAdminView(ModelView):
    pass


admin.add_views(
    ProjectAdminView(Project, db.session),
    ContactAdminView(Contact, db.session)
)


class ContactForm(FlaskForm):
    name = StringField(
        label="Votre nom",
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    email = EmailField(
        label="Votre adresse mail",
        validators=[DataRequired(), Email()],
        render_kw={"class": "form-control"}
    )
    message = TextAreaField(
        label="Votre message",
        validators=[DataRequired()],
        render_kw={"class": "form-control", "style": "height: 180px;"}
    )
    submit = SubmitField(label="Envoyer")


class IndexView(MethodView):
    template_name = "index.html"
    form_class = ContactForm

    def get(self):
        projects = Project.query.all()
        form = self.form_class()
        return render_template(self.template_name, projects=projects, form=form)
    
    def post(self):
        projects = Project.query.all()
        form = self.form_class()

        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            message = form.message.data

            new_contact = Contact(
                name=name,
                email=email,
                message=message
            )
            db.session.add(new_contact)
            db.session.commit()

            flash("Votre message a été envoyé avec succès.", "success")

            return redirect(url_for("index_url"))
        
        elif form.errors:
            flash(form.errors, "warning")

        return render_template(self.template_name, projects=projects, form=form)
    

@app.route("/download")
def download_file():
    path = BASE_DIR / "assets/static/cv/cv.pdf"
    return send_file(path, as_attachment=True)

    

app.add_url_rule(
    "/",
    view_func=IndexView.as_view(name="index_url")
)
    

if __name__ == "__main__":
    app.run(debug=True)

