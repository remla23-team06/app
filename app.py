import json
from os import getenv, urandom
import requests
from flask import Flask, render_template, redirect, request, make_response
from flask_wtf import FlaskForm
from wtforms import validators, TextAreaField, RadioField
from remlaverlib.version_util import VersionUtil

app = Flask(__name__)

app.config['SECRET_KEY'] = urandom(32)
server_url = "http://localhost:8000"  # getenv('MODEL_SERVICE_URL', "http://0.0.0.0:8000")


class ReviewForm(FlaskForm):
    """Create text area field for review."""

    review = TextAreaField('Review',
                           validators=[validators.DataRequired()],
                           render_kw={"rows": 5, "cols": 36})


@app.route("/validate", methods=['POST'])
def validate():
    """Process the feedback from the validation form in `index.html`."""
    review = ReviewForm().review
    rating_value = request.form.get('rating')  # Updated to 'rating' instead of 'ratingValue'

    response = requests.post(
        server_url + "/validate",
        {"validation": json.dumps({'rating': rating_value, 'review': review.data}), "sender": "with-emojis"},
        timeout=20)

    # Check the response status code
    if response.status_code == 200:
        # Show a thank you message and redirect the user to the home page
        return make_response(render_template("thanks.html"))
    else:
        # Handle the error case
        return make_response("Validation request failed.", 500)


@app.route("/submit", methods=['POST'])
def submit():
    """Send the data from the text field to the server."""
    review_form = ReviewForm()
    if review_form.validate_on_submit():

        response = requests.post(
            server_url + "/predict",
            {"data": review_form.review.data, "sender": "with-emojis"},
            timeout=20).json()

        is_positive = response.get('sentiment', 0) == 1
        smiley_emoji = "&#128578;" if is_positive else "&#128577;"

        # Call the validate function and get the response
        validation_response = validate()

        if validation_response.status_code == 200:
            # Show a thank you message and redirect the user to the home page
            return render_template("index.html",
                                   review_form=review_form,
                                   smiley_emoji=smiley_emoji,
                                   current_version=VersionUtil.get_version())
        else:
            # Handle the error case
            return "Validation request failed.", 500

    return redirect("/", 301)


@app.route("/", methods=['GET'])
def hello():
    """Home page."""
    review_form = ReviewForm()
    return render_template("index.html",
                           review_form=review_form,
                           validation_form=None,
                           current_version=VersionUtil.get_version())


if __name__ == '__main__':
    app.run(debug=True)
