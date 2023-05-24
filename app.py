"""This module contains the flask server running the web-app."""
import json
from os import getenv, urandom
import requests
from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import validators, TextAreaField, RadioField
from remlaverlib.version_util import VersionUtil

app = Flask(__name__)

app.config['SECRET_KEY'] = urandom(32)
server_url = getenv('MODEL_SERVICE_URL', "http://0.0.0.0:8000")


class ReviewForm(FlaskForm):
    """Create text area field for review."""

    review = TextAreaField('Review',
                           validators=[validators.DataRequired()],
                           render_kw={"rows": 5, "cols": 36})


class ValidationForm(FlaskForm):
    """Create radio button field for validating the prediction."""

    thumbs_up = "Correct"
    thumbs_down = "Incorrect"
    is_correct = RadioField('Correct prediction',
                            validators=[validators.DataRequired()],
                            choices=[thumbs_up, thumbs_down])


@app.route("/validate", methods=['POST'])
def validate():
    """Process the feedback from the validation form in `index.html`."""
    validation_form = ValidationForm()
    if validation_form.validate_on_submit():
        prediction_is_correct = (validation_form.is_correct.data ==
                                 validation_form.thumbs_up)
        requests.post(server_url + "/validate",
                      {"validation": json.dumps(prediction_is_correct)},
                      timeout=1.5)
        # Show a thank you message and redirect the user to the home page
        return render_template("thanks.html")
    return redirect("/", 301)


@app.route("/submit", methods=['POST'])
def submit():
    """Send the data from the text field to the server."""
    review_form = ReviewForm()
    if review_form.validate_on_submit():
        response: dict = requests.post(
            server_url + "/predict",
            {"data": review_form.review.data},
            timeout=1.5).json()
        is_positive = response.get('sentiment', 0) == 1
        smiley_emoji = "You are happy!" if is_positive else "You are sad."
        validation_form = ValidationForm()
        return render_template("index.html",
                               review_form=review_form,
                               smiley_emoji=smiley_emoji,
                               current_version=VersionUtil.get_version(),
                               validation_form=validation_form)
    return redirect("/", 301)


@app.route("/", methods=['GET'])
def hello():
    """Home page."""
    review_form = ReviewForm()
    return render_template("index.html",
                           review_form=review_form,
                           validation_form=None,
                           current_version=VersionUtil.get_version())
