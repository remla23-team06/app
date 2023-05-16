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
countHello = 0
countValidate = 0
countSubmit = 0


class ReviewForm(FlaskForm):
    """
    Create text area field for review
    """
    review = TextAreaField('Review', validators=[validators.DataRequired()], render_kw={"rows": 5, "cols": 12})
    
    # Make the text are larger
    review.rows = 15


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
    global CORRECT_PREDICTIONS, FALSE_PREDICTIONS, countValidate
    countValidate += 1
    validation_form = ValidationForm()
    if validation_form.validate_on_submit():
        prediction_is_correct = (validation_form.is_correct.data ==
                                 validation_form.thumbs_up)
        if prediction_is_correct:
            CORRECT_PREDICTIONS += 1
        else:
            FALSE_PREDICTIONS += 1
        requests.post(server_url + "/validate",
                      {"validation": json.dumps(prediction_is_correct)})
        # Show a thank you message and redirectthe user to the home page
        return render_template("thanks.html")
    return redirect("/", 301)


@app.route("/submit", methods=['POST'])
def submit():
    """Send the data from the text field to the server."""
    global ALL_PREDICTIONS, countSubmit
    countSubmit += 1

    review_form = ReviewForm()
    if review_form.validate_on_submit():
        response: dict = requests.post(
            server_url + "/predict",
            {"data": review_form.review.data}).json()
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
    global countHello
    countHello += 1
    review_form = ReviewForm()
    return render_template("index.html",
                           review_form=review_form,
                           validation_form=None,
                           current_version=VersionUtil.get_version())


@app.route('/metrics', methods=['GET'])
def metrics():
    """Send metrics for monitoring to Prometheus."""
    global ALL_PREDICTIONS, CORRECT_PREDICTIONS, FALSE_PREDICTIONS, countHello, countSubmit, countValidate

    m = "# HELP predictions The number of predictions.\n"
    m += "# TYPE predictions counter\n"
    m += "predictions{{correct=\"None\"}} {}\n".format(ALL_PREDICTIONS)
    m += "predictions{{correct=\"True\"}} {}\n".format(CORRECT_PREDICTIONS)
    m += "predictions{{correct=\"False\"}} {}\n".format(FALSE_PREDICTIONS)
    
    m += "# HELP num_requests The number of requests.\n"
    m += "# TYPE num_requests counter\n"
    m += "num_requests{{page=\"index\"}} {}\n".format(countHello)
    m += "num_requests{{page=\"validate\"}} {}\n".format(countValidate)
    m += "num_requests{{page=\"submit\"}} {}\n".format(countSubmit)
        

    return Response(m, mimetype="text/plain")
