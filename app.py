"""This module contains the flask server running the web-app."""
import json
from os import getenv, urandom
import requests
from flask import Flask, render_template, redirect, Response
from flask_wtf import FlaskForm
from wtforms import validators, TextAreaField, RadioField
from remlaverlib.version_util import VersionUtil

app = Flask(__name__)

app.config['SECRET_KEY'] = urandom(32)
server_url = getenv('MODEL_SERVICE_URL', "http://0.0.0.0:8000")

ALL_PREDICTIONS = 0
CORRECT_PREDICTIONS = 0
FALSE_PREDICTIONS = 0
COUNT_HELLO = 0
COUNT_VALIDATE = 0
COUNT_SUBMIT = 0


class ReviewForm(FlaskForm):
    """Create text area field for review."""

    review = TextAreaField('Review',
                           validators=[validators.DataRequired()],
                           render_kw={"rows": 5, "cols": 36})


class ValidationForm(FlaskForm):
    """Create radio button field for validating the prediction."""

    thumbs_up = "&#x1F44D;"
    thumbs_down = "&#x1F44E;"
    is_correct = RadioField('Correct prediction',
                            validators=[validators.DataRequired()],
                            choices=[thumbs_up, thumbs_down])


@app.route("/validate", methods=['POST'])
def validate():
    """Process the feedback from the validation form in `index.html`."""
    global CORRECT_PREDICTIONS, FALSE_PREDICTIONS, COUNT_VALIDATE
    COUNT_VALIDATE += 1
    validation_form = ValidationForm()
    if validation_form.validate_on_submit():
        prediction_is_correct = (validation_form.is_correct.data ==
                                 validation_form.thumbs_up)
        if prediction_is_correct:
            CORRECT_PREDICTIONS += 1
        else:
            FALSE_PREDICTIONS += 1
        requests.post(server_url + "/validate",
                      {"validation": json.dumps(prediction_is_correct)},
                      timeout=1.5)
        # Show a thank you message and redirect the user to the home page
        return render_template("thanks.html")
    return redirect("/", 301)


@app.route("/submit", methods=['POST'])
def submit():
    """Send the data from the text field to the server."""
    global ALL_PREDICTIONS, COUNT_SUBMIT
    COUNT_SUBMIT += 1

    review_form = ReviewForm()
    if review_form.validate_on_submit():
        response: dict = requests.post(
            server_url + "/predict",
            {"data": review_form.review.data},
            timeout=1.5).json()
        ALL_PREDICTIONS += 1
        is_positive = response.get('sentiment', 0) == 1
        smiley_emoji = "&#128578;" if is_positive else "&#128577;"
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
    global COUNT_HELLO
    COUNT_HELLO += 1
    review_form = ReviewForm()
    return render_template("index.html",
                           review_form=review_form,
                           validation_form=None,
                           current_version=VersionUtil.get_version())


@app.route('/metrics', methods=['GET'])
def metrics():
    """Send metrics for monitoring to Prometheus."""
    global ALL_PREDICTIONS, CORRECT_PREDICTIONS, FALSE_PREDICTIONS
    global COUNT_HELLO, COUNT_SUBMIT, COUNT_VALIDATE

    m = "# HELP predictions The number of predictions.\n" # pylint: disable=snake_case
    m += "# TYPE predictions counter\n" # pylint: disable=snake_case
    m += "predictions{{correct=\"None\"}} {}\n".format(ALL_PREDICTIONS) # pylint: disable=snake_case
    m += "predictions{{correct=\"True\"}} {}\n".format(CORRECT_PREDICTIONS) # pylint: disable=snake_case
    m += "predictions{{correct=\"False\"}} {}\n".format(FALSE_PREDICTIONS) # pylint: disable=snake_case

    m += "# HELP num_requests The number of requests.\n" # pylint: disable=snake_case
    m += "# TYPE num_requests counter\n" # pylint: disable=snake_case
    m += "num_requests{{page=\"index\"}} {}\n".format(COUNT_HELLO) # pylint: disable=snake_case
    m += "num_requests{{page=\"validate\"}} {}\n".format(COUNT_VALIDATE) # pylint: disable=snake_case
    m += "num_requests{{page=\"submit\"}} {}\n".format(COUNT_SUBMIT) # pylint: disable=snake_case

    return Response(m, mimetype="text/plain")
