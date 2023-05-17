from django.db import models
from froala_editor.fields import FroalaField
# Create your models here.
class Problem(models.Model):
    Statement = FroalaField()
    Name = models.CharField(max_length=100, unique=True)
    Difficulty = models.CharField(max_length=10)
    TimeLimit = models.IntegerField(help_text="in sec")
    MemLimit = models.IntegerField(help_text="in kb")
    testnum = models.IntegerField()
    Author = models.CharField(max_length=30)
    def __str__(self):
        return self.Name

class TestCases(models.Model):
    Input = models.TextField()
    Output = models.TextField()
    Problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    testid = models.IntegerField()
    def __str__(self):
        return (str(self.Problem)+" "+str(self.testid))