from os import getenv

from django.shortcuts import render

from webservice.forms import SentimentForm

from dotenv import load_dotenv

load_dotenv()


# Create your views here.
def home_view(request):
    server_url = getenv('SERVER_URL')
    form = SentimentForm(request.POST or None)
    if form.is_valid():
        form.save()
    context = {
        'form': form,
        'url': server_url
    }
    return render(request, "webservice/index.html", context)
