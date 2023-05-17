from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse, resolve
from oj2.views import dashboardPage, addProblem, deleteProblem, modifyProblem
from oj.models import *
from enduser.models import *
import json
    
from django.contrib.auth.models import Permission
class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('dashboardPage')
        self.add_url = reverse('add')
        self.delete_url = reverse('delete')
        self.modify_url = reverse('modify')

    def test_dashboardPage_GET(self):
        response = self.client.get(self.dashboard_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'oj2/dashboard.html')

    def test_addproblem_GET(self):
        response = self.client.get(self.add_url)
        self.assertEquals(response.status_code, 302)
    
    def test_deleteproblem_GET(self):
        response = self.client.get(self.delete_url)
        self.assertEquals(response.status_code, 302)

    def test_modifyproblem_GET(self):
        response = self.client.get(self.modify_url)
        self.assertEquals(response.status_code, 302)


class ModifyProblemTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user.is_staff = True
        self.user.save()

        self.problem = Problem.objects.create(
            Name='testproblem',
            Difficulty='Easy',
            TimeLimit=1,
            MemLimit=64,
            testnum=1,
            Author=self.user.username,
            Statement='This is a test problem statement.'
        )
        TestCases.objects.create(
            Problem=self.problem,
            Input='1 2\n',
            Output='3\n',
            testid=1
        )

    def test_modify_problem(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('modify'), {
            'name': 'testproblem',
            'tomodify': 'option1',
            'difficulty': 'Medium',
            'time_limit': 2,
            'mem_limit': 128,
            'statement': 'This is a modified test problem statement.'
        })
        self.assertEqual(response.status_code, 302) # Redirect to dashboardPage
        modified_problem = Problem.objects.filter(Name='testproblem').first()
        self.assertEqual(modified_problem.Difficulty, 'Medium')
        self.assertEqual(modified_problem.TimeLimit, 2)
        self.assertEqual(modified_problem.MemLimit, 128)
        self.assertEqual(modified_problem.Statement, 'This is a modified test problem statement.')

    def test_modify_testcase(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('modify'), {
            'name': 'testproblem',
            'tomodify': 'option2',
            'testnum': 1,
            'inputtest': '3 4\n',
            'outputtest': '7\n'
        })
        self.assertEqual(response.status_code, 302) # Redirect to dashboardPage
        modified_testcase = TestCases.objects.filter(Problem=self.problem, testid=1).first()
        self.assertEqual(modified_testcase.Input, '3 4\n')
        self.assertEqual(modified_testcase.Output, '7\n')

    def test_add_testcase(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('modify'), {
            'name': 'testproblem',
            'tomodify': 'option3',
            'inputtest': '5 6\n',
            'outputtest': '11\n'
        })
        self.assertEqual(response.status_code, 302) # Redirect to dashboardPage
        modified_problem = Problem.objects.filter(Name='testproblem').first()
        self.assertEqual(modified_problem.testnum, 2)
        new_testcase = TestCases.objects.filter(Problem=self.problem, testid=2).first()
        self.assertEqual(new_testcase.Input, '5 6\n')
        self.assertEqual(new_testcase.Output, '11\n')

    def test_no_such_problem(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('modify'), {
            'name': 'nosuchproblem',
            'tomodify': 'option1',
            'difficulty': 'Medium',
            'time_limit': 2,
            'mem_limit': 128,
            'statement': 'This is a modified test problem statement.'
        })
        self.assertEqual(response.status_code, 200) # Render modify.html
        self.assertContains(response, 'No such problem exists!!')


class TestViewsDeleteProblem(TestCase):
    def setUp(self):
        # create a staff user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user.is_staff = True
        self.user.save()
        
        # create a problem
        self.problem = Problem.objects.create(
            Statement='Test problem statement',
            Name='Test problem',
            Difficulty='Easy',
            TimeLimit=1,
            MemLimit=256,
            testnum=2,
            Author=self.user.username,
        )

    def test_delete_problem_successful(self):
        # log in the user
        client = Client()
        client.login(username='testuser', password='testpass')
        
        # send a POST request to delete the problem
        response = client.post(reverse('delete'), {'name': 'Test problem'})
        
        # check that the problem was deleted and redirected to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboardPage'))
        self.assertFalse(Problem.objects.filter(Name='Test problem').exists())
        
    def test_delete_problem_author_only(self):
        # create another user
        user2 = User.objects.create_user(username='testuser2', password='testpass2')
        
        # log in the new user
        client = Client()
        client.login(username='testuser2', password='testpass2')
        
        # send a POST request to delete the problem
        response = client.post(reverse('delete'), {'name': 'Test problem'})
        
        # check that the problem was not deleted and an error message was displayed
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Problem.objects.filter(Name='Test problem').exists())
        
    def test_delete_problem_nonexistent(self):
        # log in the user
        client = Client()
        client.login(username='testuser', password='testpass')
        
        # send a POST request to delete a nonexistent problem
        response = client.post(reverse('delete'), {'name': 'Nonexistent problem'})
        
        # check that an error message was displayed
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No such problem exists")
        
    def tearDown(self):
        # delete the user and problem objects
        self.user.delete()
        self.problem.delete()



class TestViewsAddProblem(TestCase):
    def setUp(self):
        # create a user with staff permission
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpass'
        )
        self.user.is_staff = True
        self.user.save()
        
        # create a problem
        self.problem = Problem.objects.create(
            Statement='Test problem statement',
            Name='Test problem',
            Difficulty='Easy',
            TimeLimit=1,
            MemLimit=256,
            testnum=2,
            Author=self.user.username,
        )

    def test_add_problem(self):
        # create POST request data
        post_data = {
            'name': 'test problem',
            'difficulty': 'Easy',
            'time_limit': 1,
            'mem_limit': 1024,
            'test_num': 2,
            'input1': '1 2\n',
            'output1': '3\n',
            'input2': '3 4\n',
            'output2': '7\n',
            'statement': 'Test problem statement',
        }

        # login as test user
        self.client.login(username='testuser', password='testpass')

        # make POST request to add problem
        response = self.client.post(reverse('add'), data=post_data)

        # assert that the problem and test cases were created
        problem = Problem.objects.get(Name='test problem')
        self.assertEqual(problem.Difficulty, 'Easy')
        self.assertEqual(problem.Author, 'testuser')
        self.assertEqual(problem.Statement, 'Test problem statement')
        self.assertEqual(problem.TimeLimit, 1)
        self.assertEqual(problem.MemLimit, 1024)
        self.assertEqual(problem.testnum, 2)
        test_cases = TestCases.objects.filter(Problem=problem).order_by('testid')
        self.assertEqual(len(test_cases), 2)
        self.assertEqual(test_cases[0].Input, '1 2\n')
        self.assertEqual(test_cases[0].Output, '3\n')
        self.assertEqual(test_cases[1].Input, '3 4\n')
        self.assertEqual(test_cases[1].Output, '7\n')

        # assert that the response redirects to the dashboard page
        self.assertRedirects(response, reverse('dashboardPage'))

    def test_add_problem_unauthorized(self):
        # create POST request data
        post_data = {
            'name': 'test problem',
            'difficulty': 'Easy',
            'time_limit': 1,
            'mem_limit': 1024,
            'test_num': 2,
            'input1': '1 2\n',
            'output1': '3\n',
            'input2': '3 4\n',
            'output2': '7\n',
            'statement': 'Test problem statement',
        }

        # login as a user without staff permission
        self.client.login(username='testuser2', password='testpass2')
        # make POST request to add problem
        response = self.client.post(reverse('add'), data=post_data)
        # assert that the user is redirected to the login page
        self.assertRedirects(response, '/login/?next=/oj2/add/')

        # assert that the problem was not created
        self.assertFalse(Problem.objects.filter(Name='test problem').exists())

    def tearDown(self):
        # delete the user and problem objects
        self.user.delete()
        self.problem.delete()



class TestUrls(SimpleTestCase):

    def test_dashboardPage_url_resolves(self):
        url = reverse('dashboardPage')
        self.assertEquals(resolve(url).func,dashboardPage )
        
    def test_add_url_resolves(self):
        url = reverse('add')
        self.assertEquals(resolve(url).func,addProblem )
        
    def test_delete_url_resolves(self):
        url = reverse('delete')
        self.assertEquals(resolve(url).func,deleteProblem )
        
    def test_modify_url_resolves(self):
        url = reverse('modify')
        self.assertEquals(resolve(url).func,modifyProblem)
# Create your tests here.
