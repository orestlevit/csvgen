from django.contrib import admin


from core.models import Scheme, Column, DataSet
models = Scheme, Column, DataSet

for model in models:
    admin.site.register(model)

