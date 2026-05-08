from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='index'),
    path('contact/', views.contact_view, name='contact'),
    path('review/', views.submit_review, name='submit_review'),
    path('testimonials/', views.testimonials_view, name='testimonials'),
]