import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.generic import ListView, DeleteView, FormView, CreateView, TemplateView

from core.forms import RegistrationForm, AuthorizationForm
from core.models import *

from django.forms import inlineformset_factory

from csvgen.settings import MEDIA_ROOT

column_formset = inlineformset_factory(
    Scheme, Column, fields=("title", "type", "range_from", "range_to", "order"),
    labels={"title": "Column name",
            "type": "Type",
            "order": "Order",
            "range_from": "From",
            "range_to": "To",
            },
    extra=0
)

class SchemeView(LoginRequiredMixin, ListView):
    template_name = 'schemes.html'
    model = Scheme

    def get_queryset(self):
        return Scheme.objects.filter(user=self.request.user)


class DeleteSchemeView(LoginRequiredMixin, DeleteView):
    template_name = "confirm_delete.html"
    model = Scheme
    success_url = "/schemes"


class RegistrationView(FormView):
    template_name = "registration.html"
    form_class = RegistrationForm
    success_url = "/authorization"

    def form_valid(self, form):
        form.save()
        return super(RegistrationView, self).form_valid(form)


class CreateSchemeView(LoginRequiredMixin, CreateView):
    model = Scheme
    fields = ["title", "column_separator", "string_character"]
    success_url = "/schemes"
    template_name = "new-schema.html"

    def get_context_data(self, **kwargs):
        context = super(CreateSchemeView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["columns"] = column_formset(self.request.POST)
        else:
            context["columns"] = column_formset()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        context = self.get_context_data()
        columns = context["columns"]
        if not columns.is_valid():
            return super(CreateSchemeView, self).form_valid(form)

        self.object = form.save()
        columns.instance = self.object
        columns.save()
        return super(CreateSchemeView, self).form_valid(form)



class DownloadCSVView(LoginRequiredMixin, TemplateView):
    template_name = "data_set.html"

    def get(self, requets, *args, **kwargs):
        filepath = os.path.join(MEDIA_ROOT, f"dataset-{kwargs['pk-ds']}.csv")
        try:
            with open(filepath, "rb") as file:
                response = HttpResponse(file.read(), content_type='application/CSV')
                response["Content-Disposition"] = f'inline; filename={os.path.basename(filepath)}'
                return response
        except FileNotFoundError:
            raise Http404("File not found")

