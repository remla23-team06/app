from os import getenv

import requests
from django.shortcuts import render

from webservice.forms import SentimentForm

from dotenv import load_dotenv

load_dotenv()


# Create your views here.
def home_view(request):
    server_url = getenv('SERVER_URL')
    form = SentimentForm(request.POST or None)
    smiley_emoji = "&#128577;"  # ""

    if form.is_valid():
        # response = requests.post(server_url).json()

        is_positive = True # TODO: needs to be equal to a boolean constraint on the response

        smiley_emoji = "&#128578;" if is_positive else "&#128577;"
    context = {
        'form': form,
        'server_url': server_url,
        'smiley_emoji': smiley_emoji

    }
    return render(request, "webservice/index.html", context)
