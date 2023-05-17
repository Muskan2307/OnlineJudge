from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboardPage,name='dashboardPage'),
    path('add/',views.addProblem,name='add'),
    path('delete/', views.deleteProblem, name='delete'),
    path('modify/',views.modifyProblem,name='modify'),
]