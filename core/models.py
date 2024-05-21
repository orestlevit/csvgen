from django.contrib.auth.models import User
from django.db import models

# Create your models here.


from core.choices import *



class Scheme(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=60)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    column_separator = models.CharField(max_length=5, choices=SEPARATOR_CHOICES, default=",")
    string_character = models.CharField(max_length=5, choices=CHARACTER_CHOICES, default="\"")

    def __str__(self):
        return f'{self.user.username} -> {self.title}'


class Column(models.Model):
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)
    title = models.CharField(max_length=30, )
    type = models.IntegerField(choices=DATA_TYPE_CHOICES, default=0)
    range_from = models.IntegerField(blank=True, null=True)
    range_to = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return f'{self.scheme} -> {self.title}'


class DataSet(models.Model):
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    rows = models.IntegerField(null=True, blank=True)
    download_url = models.URLField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=0)

    def __str__(self):
        return f'{self.scheme} -> {self.status}({self.rows})'


