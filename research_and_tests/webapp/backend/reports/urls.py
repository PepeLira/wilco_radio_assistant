from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.reports, name='reports'),
    # Other URL patterns...
]
