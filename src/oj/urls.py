from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboardPage,name='dashboard'),
    path('problems/', views.ProblemList, name='problems'),
    path('problems/<int:problem_id>/', views.Detail, name='detail'),
    path('problems/<int:problem_id>/verdict/', views.Verdict, name='verdict'),
    path('leaderboard/', views.leaderboardPage, name='leaderboard'),
]