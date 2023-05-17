from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
from oj.models import Problem
from oj.models import TestCases
from enduser.decorators import *
from django.contrib.auth.decorators import login_required
# Create your views here.
# @login_required(login_url='login')
# @allowed_staff
def dashboardPage(request):
    return render(request,'oj2/dashboard.html')

@login_required(login_url='login')
@allowed_staff
def addProblem(request):
    if request.method == 'POST':
        # process form data here
        name = request.POST.get('name')
        difficulty = request.POST.get('difficulty')
        time_limit = request.POST.get('time_limit')
        mem_limit = request.POST.get('mem_limit')
        test_num = request.POST.get('test_num')
        # author = request.POST.get('author')
        statement = request.POST.get('statement')
        obj = Problem()
        obj.Statement = statement
        obj.Name = name
        obj.Difficulty = difficulty
        obj.TimeLimit = time_limit
        obj.MemLimit = mem_limit
        obj.testnum = test_num
        obj.Author = request.user.username
        obj.save()
        test_cases = []
        for i in range(1, int(test_num) + 1):
            input_key = f"input{i}"
            output_key = f"output{i}"
            input_value = request.POST.get(input_key)
            output_value = request.POST.get(output_key)
            if input_value is not None and output_value is not None:
                obj2 = TestCases()
                obj2.Input = input_value
                obj2.Output = output_value
                obj2.Problem = obj
                obj2.testid = i
                obj2.save()
            

        # do something with the form data
        # for example, save it to a database
        # then redirect the user to the problem list
        return redirect('dashboardPage')
    return render(request,'oj2/add.html')

@login_required(login_url='login')
@allowed_staff
def modifyProblem(request):
    context = {
            'error_message' : '',
        }
    if request.method == 'POST':
        # process form data here
        name = request.POST.get('name')
        objtemp = Problem.objects.all()
        obj = objtemp.filter(Name = name).first()
        
        if obj == None:
            context = {
                    'error_message' : 'No such problem exists!!',
            } 
        else:
            if request.user.username==obj.Author :
                tomodify = request.POST.get('tomodify')
                if tomodify=='option1':
                    difficulty = request.POST.get('difficulty')
                    time_limit = request.POST.get('time_limit')
                    mem_limit = request.POST.get('mem_limit')
                    statement = request.POST.get('statement')
                    if statement is not None:
                        obj.Statement = statement
                    if difficulty is not None:
                        obj.Difficulty = difficulty
                    if time_limit is not None:
                        obj.TimeLimit = time_limit
                    if mem_limit is not None:
                        obj.MemLimit = mem_limit
                    obj.save()
                elif tomodify=='option2':
                    testnum = request.POST.get('testnum')
                    inputtest = request.POST.get('inputtest')
                    outputtest = request.POST.get('outputtest')
                    objtemp2 = TestCases.objects.all()
                    obj2 = objtemp2.filter(Problem = obj , testid = testnum).first()
                    obj2.Input = inputtest
                    obj2.Output = outputtest
                    obj2.save()
                elif tomodify=='option3':
                    inputtest = request.POST.get('inputtest')
                    outputtest = request.POST.get('outputtest')
                    testnum = obj.testnum
                    testnum = testnum + 1
                    obj.testnum = testnum
                    obj.save()
                    obj3 = TestCases()
                    obj3.Input = inputtest
                    obj3.Output = outputtest
                    obj3.testid = testnum
                    obj3.Problem = obj
                    obj3.save()
                return redirect('dashboardPage')

            else:
                context = {
                    'error_message' : 'You don\'t have permission to modify this problem as you are not the author of this problem',
                } 

    return render(request,'oj2/modify.html',context)
                
        
        

@login_required(login_url='login')
@allowed_staff
def deleteProblem(request):
    context = {
            'error_message' : '',
        }
    if request.method == 'POST':
        # process form data here
        name = request.POST.get('name')
        objtemp = Problem.objects.all()
        obj = objtemp.filter(Name = name).first()
        
        if obj == None:
            context = {
                    'error_message' : 'No such problem exists!!',
            } 
            
        else:
            if request.user.username==obj.Author :
                obj.delete()
                return redirect('dashboardPage')
            else:
                context = {
                    'error_message' : 'You don\'t have permission to delete this problem as you are not the author of this problem',
                } 
                
    return render(request,'oj2/delete.html', context)

    