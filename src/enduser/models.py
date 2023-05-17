from django.db import models
from django.contrib.auth.models import AbstractUser
from oj.models import Problem, TestCases
# Create your models here.

class User(AbstractUser):
    emailid = models.EmailField( default="")
    totalCount = models.IntegerField(default=0)
    easyCount = models.IntegerField(default=0)
    mediumCount = models.IntegerField(default=0)
    toughCount = models.IntegerField(default=0)
    totalScore = models.IntegerField(default=0)
    role = models.CharField(max_length=30)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def __str__(self):
        return self.username

class Submission(models.Model):
    LANGUAGES = (("C++", "C++"), ("C", "C"), ("Python", "Python"), ("Java", "Java"))
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    problem = models.ForeignKey(Problem, null=True, on_delete=models.SET_NULL)
    user_code = models.TextField(max_length=10000, default="")
    user_stdout = models.TextField(max_length=10000, default="")
    user_stderr = models.TextField(max_length=10000, default="")
    submission_time = models.DateTimeField(auto_now_add=True, null=True)
    run_time = models.FloatField(null=True, default=0)
    language = models.CharField(max_length=10, choices=LANGUAGES, default="C++")
    verdict = models.CharField(max_length=100, default="Wrong Answer")

    class Meta:
        ordering = ['-submission_time']

    def __str__(self):
        return str(self.submission_time) + " : @" + str(self.user) + " : " + self.problem.Name + " : " + self.verdict + " : " + self.language
