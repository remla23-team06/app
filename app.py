"""
This module contains the flask server running the web-app
"""
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
    """
    Create text area field for review
    """
    review = TextAreaField('Review', validators=[validators.DataRequired()])


class ValidationForm(FlaskForm):
    """
    Create radio button field for validating the prediction
    """
    thumbs_up = "&#x1F44D;"
    thumbs_down = "&#x1F44E;"
    is_correct = RadioField('Correct prediction', validators=[validators.DataRequired()],
                            choices=[thumbs_up, thumbs_down])


@app.route("/validate", methods=['POST'])
def validate():
    """
    This method processed the feedback from the validation form in `index.html` and
     shows a thank-you message if the form has been properly validated
    """
    validation_form = ValidationForm()
    if validation_form.validate_on_submit():
        validation_request = validation_form.is_correct.data == validation_form.thumbs_up
        requests.post(server_url + "/validate", {"validation": validation_request})
        # Show a thank you message and redirect the user to the home page
        return render_template("thanks.html")
    return redirect("/", 301)


@app.route("/submit", methods=['POST'])
def submit():
    """
    The `submit` method sends the data from the restaurant review text field to the server.
    """
    review_form = ReviewForm()
    if review_form.validate_on_submit():
        response: dict = requests.post(server_url + "/predict",
                                       {"data": review_form.review.data}).json()
        is_positive = response.get('sentiment', 0) == 1
        smiley_emoji = "&#128578;" if is_positive else "&#128577;"
        validation_form = ValidationForm()
        return render_template("index.html", review_form=review_form, smiley_emoji=smiley_emoji,
                               current_version=VersionUtil.get_version(),
                               validation_form=validation_form)
    return redirect("/", 301)


@app.route("/", methods=['GET'])
def hello():
    """
    This is the route representing the home page.
    """
    review_form = ReviewForm()
    return render_template("index.html", review_form=review_form, validation_form=None,
                           current_version=VersionUtil.get_version())
