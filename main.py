from flask import Flask, render_template, request, send_from_directory

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_ckeditor import CKEditorField, CKEditor
from wtforms.fields.html5 import EmailField

from flask_bootstrap import Bootstrap

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib
import os

app = Flask(__name__)
Bootstrap(app)
ckeditor = CKEditor(app)


email = os.environ.get("EMAIL")
password = os.environ.get("EMAIL_PASSWORD")

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    message = CKEditorField("Your Message", validators=[DataRequired()])
    submit = SubmitField("Send Message")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/schedule')
def schedule():
    return render_template("schedule.html")


@app.route('/contact', methods=["GET", "POST"])
def contact(*args):
    form = ContactForm()
    alert = False

    if form.validate_on_submit():
        print("Trying to send an email...")
        name = request.form.get("name")
        contact_email = request.form.get("email")
        message = request.form.get("message")
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "New Message for Blades Lawn Care"
            msg['From'] = email
            msg['To'] = "chris.oreilly97@gmail.com"
            connection.login(user=email, password=password)
            html = f"""\
            <html>
              <head></head>
              <body>
                <p>New message from {name}:<br>
                   {message}
                   <br>
                   Sender's email: {contact_email}
                </p>
              </body>
            </html>
            """
            message_html = MIMEText(html, 'html')
            msg.attach(message_html)
            connection.sendmail(from_addr=email, to_addrs="chris.oreilly97@gmail.com", msg=msg.as_string())
        alert = True
        form.name.data = ""
        form.email.data = ""
        form.message.data = ""
        return render_template('contact.html', alert=alert, form=form)
    return render_template('contact.html', alert=alert, form=form)


@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == "__main__":
    app.run(debug=True)
