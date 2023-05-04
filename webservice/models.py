from django.db import models


# Create your models here.
class Review(models.Model):
    review_text = models.CharField(max_length=500)
    no_of_stars = models.PositiveIntegerField()

    def __str__(self):
        return str(self.no_of_stars) + "\n" + self.review_text


class Sentiment(models.Model):
    score = models.FloatField()

    def __str__(self):
        return str(self.score)
