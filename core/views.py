import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.generic import ListView, DeleteView, FormView, CreateView, TemplateView
from django.views.generic.edit import FormMixin, UpdateView

from core.forms import RegistrationForm, AuthorizationForm, DataSetForm
from core.models import *

from django.forms import inlineformset_factory

from core.tasks import generate_data_task
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
    template_name = "create_scheme.html"

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

class DataSetView(LoginRequiredMixin, ListView, FormMixin):
    model = DataSet
    template_name = "datasets.html"
    form_class = DataSetForm

    def dispatch(self, request, *args, **kwargs):
        self.scheme_id = kwargs["pk"]
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(DataSetView, self).get_queryset()
        return queryset.filter(scheme_id=self.scheme_id)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.scheme_id = self.scheme_id
        form.instance.status = STATUS_CHOICES[0][1]
        dataset = form.save()
        generate_data_task.delay(dataset.id)
        return super(DataSetView, self).form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DataSetView, self).get_context_data(**kwargs)
        context["scheme"] = Scheme.objects.get(id=self.scheme_id)
        return context

    def get_success_url(self):
        return self.request.path




class DownloadCSVView(LoginRequiredMixin, TemplateView):
    template_name = "datasets.html"

    def get(self, requets, *args, **kwargs):
        filepath = os.path.join(MEDIA_ROOT, f"dataset-{kwargs['pk_ds']}.csv")
        try:
            with open(filepath, "rb") as file:
                response = HttpResponse(file.read(), content_type='application/CSV')
                response["Content-Disposition"] = f'inline; filename={os.path.basename(filepath)}'
                return response
        except FileNotFoundError:
            raise Http404("File not found")



class SchemeUpdateView(LoginRequiredMixin, UpdateView):
    model = Scheme
    fields = ["title", "column_separator", "string_character"]
    success_url = "/schemes"
    template_name = "create_scheme.html"
    pk_url_kwarg = "scheme_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["columns"] = column_formset(self.request.POST, instance=self.object)
        else:
            context["columns"] = column_formset(instance=self.object)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        context = self.get_context_data()
        columns = context["columns"]
        if not columns.is_valid():
            return super().form_valid(form)

        self.object = form.save()
        columns.instance = self.object
        columns.save()
        return super().form_valid(form)
