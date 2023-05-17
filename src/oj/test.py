from oj.models import Problem, TestCases
from django.test import TestCase, Client
from django.urls import reverse
from enduser.models import User, Submission
from oj.forms import CodeForm
import tempfile
import os

class TestVerdictView(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.problem_id = 1
        self.url = reverse('verdict', args=[self.problem_id])
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next=' + self.url)


class DetailTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.problem = Problem.objects.create(Name='Test Problem',  Difficulty='Easy', Statement='This is a test problem statement.', TimeLimit = 2, MemLimit = 64, testnum = 1, Author = 'testuser')
        
    def test_detail_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('detail', args=(self.problem.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'oj/detail.html')
        self.assertContains(response, 'Test Problem')
        self.assertContains(response, 'This is a test problem statement.')
        self.assertIsInstance(response.context['problem'], Problem)
        self.assertIsInstance(response.context['code_form'], CodeForm)
        
    def tearDown(self):
        self.user.delete()
        self.problem.delete()


class ProblemListTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('problems')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.problem1 = Problem.objects.create(Name='Problem 1', Difficulty='Easy', Statement='Problem statement 1', TimeLimit = 2, MemLimit = 64, testnum = 1, Author = 'me')

    def test_problemspage_GET(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'oj/problempage.html')
        self.assertQuerysetEqual(response.context['problems'], ['<Problem: Problem 1>'])

    def test_problems_page_GET(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next=/oj/problems/', status_code=302, target_status_code=200)


class TestViewsleaderboard(TestCase):

    def setUp(self):
        self.client = Client()
        self.leaderboard_url = reverse('leaderboard')
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_leaderboard_page_GET(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.leaderboard_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'oj/leaderboardpage.html')
        self.assertQuerysetEqual(response.context['leaders'], ['<User: testuser>'])

    def test_leaderboard_page_GET_not_logged_in(self):
        response = self.client.get(self.leaderboard_url)
        self.assertRedirects(response, '/login/?next=/oj/leaderboard/', status_code=302, target_status_code=200)



class TestModelsTestCases(TestCase):
    @classmethod
    def setUpTestData(cls):
        problem = Problem.objects.create(
            Statement="This is a sample statement",
            Name="Sample Problem",
            Difficulty="Easy",
            TimeLimit=5,
            MemLimit=1024,
            testnum=1,
            Author="John Doe"
        )
        TestCases.objects.create(
            Input="2\n4 2\n1 2\n3 4\n3 2\n2 3\n1 2\n",
            Output="1\n1\n",
            Problem=problem,
            testid=1
        )

    def test_problem_foreign_key(self):
        test_case = TestCases.objects.get(id=1)
        problem = Problem.objects.get(id=1)
        self.assertEquals(test_case.Problem, problem)

    def test_object_name(self):
        test_case = TestCases.objects.get(id=1)
        expected_object_name = f"{test_case.Problem} {test_case.testid}"
        self.assertEquals(expected_object_name, str(test_case))

class TestModelsProblem(TestCase):

    @classmethod
    def setUpTestData(cls):
        Problem.objects.create(
                Statement="This is a sample statement",
                Name="Sample Problem",
                Difficulty="Easy",
                TimeLimit=5,
                MemLimit=1024,
                testnum=1,
                Author="John Doe"
            )

    def test_object_name_is_name(self):
        problem = Problem.objects.get(id=1)
        expected_object_name = problem.Name
        self.assertEquals(expected_object_name, str(problem))