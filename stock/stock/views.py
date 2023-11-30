from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotFound
from django.urls import reverse, reverse_lazy


#
class HelloWorldView(View):

	#
	def get(self, requests):
		msg = requests.GET['name'] if 'name' in requests.GET.keys() else 'World'

		return HttpResponse(f"<h1>Hello, {msg}!</h1>")