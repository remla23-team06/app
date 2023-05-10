from os import getenv, urandom
import requests
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import validators, TextAreaField, RadioField
from remlaverlib.version_util import VersionUtil

app = Flask(__name__)

app.config['SECRET_KEY'] = urandom(32)
server_url = getenv('MODEL_SERVICE_URL', "http://0.0.0.0:8000/predict")
validation_url = getenv('MODEL_SERVICE_VALIDATION_URL', "http://0.0.0.0:8000/validate")


class ReviewForm(FlaskForm):
    """
    Create text area field for review
    """
    review = TextAreaField('Review', validators=[validators.DataRequired()])


class ValidationForm(FlaskForm):
    """
    Create radio button field for validating the prediction
    """
    is_correct = RadioField('Correct prediction', validators=[validators.DataRequired()], choices=['yes', 'no'])


@app.route("/validate", methods=['POST'])
def validate():
    smiley_emoji = None
    review_form = ReviewForm()
    validation_form = ValidationForm()
    if validation_form.validate_on_submit():

        # Show a thank you message and redirect the user to the home page
        return render_template("thanks.html")
    return render_template("index.html", review_form=review_form, smiley_emoji=smiley_emoji,
                           current_version=VersionUtil.get_version(), validation_form=validation_form)


@app.route("/submit", methods=['POST'])
def submit():
    smiley_emoji = None
    review_form = ReviewForm()
    validation_form = None
    if review_form.validate_on_submit():
        json_response: dict = requests.post(server_url, {"data": review_form.review.data}).json()
        is_positive = json_response.get('sentiment', 0) == 1
        smiley_emoji = "&#128578;" if is_positive else "&#128577;"
        validation_form = ValidationForm()
    return render_template("index.html", review_form=review_form, smiley_emoji=smiley_emoji,
                           current_version=VersionUtil.get_version(), validation_form=validation_form)


@app.route("/", methods=['GET'])
def hello():
    review_form = ReviewForm()
    return render_template("index.html", review_form=review_form, validation_form=None,
                           current_version=VersionUtil.get_version())
