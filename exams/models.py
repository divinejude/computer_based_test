from django.db import models
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User


# Create your models here.
class Question(models.Model):
    Q = models.CharField(max_length=1000)

    '''def get_absolute_url(self):
        return reverse('exams:index', kwargs={'pk': self.pk})'''

    def __str__(self):
        return str(self.id) + ' ' + self.Q


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.CharField(max_length=1000)
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.option


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    taken = models.BooleanField(default=False)
    score = models.FloatField(default=0)

    def __str__(self):
        return str(self.user.first_name) + ' ' + self.user.last_name
