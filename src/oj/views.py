from django.shortcuts import render
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from oj.forms import CodeForm
from enduser.models import User
import os
import os.path
import subprocess
import signal
from django.views.decorators.csrf import csrf_protect
# Create your views here.
from datetime import datetime
from time import time
import docker
from oj.models import Problem, TestCases
from enduser.models import Submission
@login_required(login_url='login')
def dashboardPage(request):
    toteasy = len(Problem.objects.filter(Difficulty="Easy"))
    totmedium = len(Problem.objects.filter(Difficulty="Medium"))
    tottough = len(Problem.objects.filter(Difficulty="Tough"))

    user = request.user
    easydone = user.easyCount
    mediumdone = user.mediumCount
    toughdone = user.toughCount

    context = {
        "toteasy":toteasy,
        "totmedium":totmedium,
        "tottough":tottough,
        "easydone":easydone,
        "mediumdone":mediumdone,
        "toughdone":toughdone
    }
    return render(request,'oj/dashboard.html',context)

@login_required(login_url='login')
def leaderboardPage(request):
    leaders = User.objects.all()
    context = {
        'leaders': leaders
    }
    return render(request,'oj/leaderboardpage.html',context)

@login_required(login_url='login')
def ProblemList(request):
    problems = Problem.objects.all()
    context = {
        'problems': problems
    }
    return render(request,'oj/problempage.html', context)

@login_required(login_url='login')
def Detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    form = CodeForm()
    context = {'problem':problem,'code_form':form}
    return render(request,'oj/detail.html', context)

@login_required(login_url='login')
def Verdict(request, problem_id):
    user_stderr = ""
    user_stdout = ""
    if request.method == 'POST':
        # setting docker-client
        docker_client = docker.from_env()
        Running = "running"

        problem = Problem.objects.get(id=problem_id)
        # testcases = TestCases.objects.get(Problem_id=problem_id)
        # #replacing \r\n by \n in original output to compare it with the usercode output
        # testcases.Output = testcases.Output.replace('\r\n','\n').strip() 



        #setting verdict to wrong by default
        verdict = "Wrong Answer" 
        res = ""
        run_time = 0

        # extract data from form
        form = CodeForm(request.POST)
        user_code = ''
        if form.is_valid():
            user_code = form.cleaned_data.get('user_code')
            user_code = user_code.replace('\r\n','\n').strip()
            
        language = request.POST['language']
        submission = Submission(user=request.user, problem=problem, submission_time=datetime.now(), 
                                    language=language, user_code=user_code)
        submission.save()

        filename = str(submission.id)

        # if user code is in C++
        if language == "C++":
            extension = ".cpp"
            cont_name = "oj-cpp"
            compile = f"g++ -o {filename} {filename}.cpp"
            clean = f"{filename} {filename}.cpp"
            docker_img = "gcc:11.2.0"
            exe = f"./{filename}"
            
        elif language == "C":
            extension = ".c"
            cont_name = "oj-c"
            compile = f"gcc -o {filename} {filename}.c"
            clean = f"{filename} {filename}.c"
            docker_img = "gcc:11.2.0"
            exe = f"./{filename}"

        elif language == "Python":
            extension = ".py"
            cont_name = "oj-py"
            compile = "python"
            clean = f"{filename}.py"
            docker_img = "python"
            exe = f"python {filename}.py"

        elif language == "Java":
            filename = "Main"
            extension = ".java"
            cont_name = "oj-java"
            compile = f"javac {filename}.java"
            clean = f"{filename}.java {filename}.class"
            docker_img = "openjdk"
            exe = f"java {filename}"


        file = filename + extension
        filepath = settings.FILES_DIR + "/" + file
        code = open(filepath,"w")
        code.write(user_code)
        code.close()

        # checking if the docker container is running or not
        try:
            container = docker_client.containers.get(cont_name)
            container_state = container.attrs['State']
            container_is_running = (container_state['Status'] == Running)
            if not container_is_running:
                subprocess.run(f"docker start {cont_name}",shell=True)
        except docker.errors.NotFound:
            subprocess.run(f"docker run -dt --name {cont_name} {docker_img}",shell=True)


        # copy/paste the .cpp file in docker container 
        subprocess.run(f"docker cp {filepath} {cont_name}:/{file}",shell=True)
        failedtestcase = 0
        # compiling the code
        cmp = subprocess.run(f"docker exec {cont_name} {compile}", capture_output=True, shell=True)
        if cmp.returncode != 0:
            verdict = "Compilation Error"
            subprocess.run(f"docker exec {cont_name} rm {file}",shell=True)

        else:
            # running the code on given input and taking the output in a variable in bytes
            numtest = problem.testnum
            for i in range(1,numtest+1):
                testcase = TestCases.objects.get(Problem_id=problem_id,testid=i)
                testcase.Output = testcase.Output.replace('\r\n','\n').strip() 
                start = time()
                res = subprocess.run(f"docker exec {cont_name} sh -c \"echo '{testcase.Input}' | timeout --preserve-status {problem.TimeLimit} {exe}\"", capture_output=True, shell=True)
                run_time = time()-start
                if(run_time>problem.TimeLimit and res.returncode != 0):
                    verdict = "Time Limit Exceeded"
                    failedtestcase=i
                    subprocess.run(f"docker container kill {cont_name}", shell=True)
                    subprocess.run(f"docker start {cont_name}",shell=True)
                    subprocess.run(f"docker exec {cont_name} rm {clean}",shell=True)
            
                if res.returncode != 0 and verdict!="Time Limit Exceeded":
                    verdict = "Runtime Error" 
                    failedtestcase = i
                
                truth1=False
                truth2=False
                if verdict=="Wrong Answer" :
                    user_stdout = res.stdout.decode('utf-8')
                    print(user_stdout)
                    if str(user_stdout)!=str(testcase.Output):
                        truth1=True
                    testcase.Output += '\n'
                    if str(user_stdout)!=str(testcase.Output):
                        truth2=True
                    if truth1 and truth2:
                        failedtestcase = i
                    if failedtestcase:
                        break
        if verdict == "Compilation Error":
            user_stderr = cmp.stderr.decode('utf-8')
        elif failedtestcase == 0:
            verdict = "Accepted"
        if problem.Difficulty=="Easy":
            score = 20
        elif problem.Difficulty=="Medium":
            score = 50
        else:
            score = 100
        
        user = User.objects.get(username=request.user)
        previous_verdict = Submission.objects.filter(user=user.id, problem=problem, verdict="Accepted")
        if len(previous_verdict)==0 and verdict=="Accepted":
            user.totalScore += score
            user.totalCount += 1
            if problem.Difficulty == "Easy":
                user.easyCount += 1
            elif problem.Difficulty == "Medium":
                user.mediumCount += 1
            else:
                user.toughCount += 1
            user.save()

        submission.verdict = verdict
        submission.user_stdout = user_stdout
        submission.user_stderr = user_stderr
        submission.run_time = run_time
        submission.save()
        os.remove(filepath)
        context={
            'verdict':verdict,
            'failedtestcase':failedtestcase
            }
        return render(request,'oj/verdict.html',context)


