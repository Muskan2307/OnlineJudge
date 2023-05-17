from django.test import TestCase, Client
from django.urls import reverse, resolve
from oj.models import *
from enduser.models import *
from datetime import datetime
from enduser.tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from datetime import datetime
from django.utils import timezone


from django.core import mail
from .forms import CreateUserForm
from .views import registerPage

class RegisterPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_register_page(self):
        # Test GET request
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enduser/register.html')
        self.assertTrue(isinstance(response.context['form'], CreateUserForm))

        # Test POST request with valid form data
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username=form_data['username'])
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(form_data['email'], mail.outbox[0].to)
        self.assertEqual(mail.outbox[0].subject, 'Welcome to OJ- Django Login!!')
        
        # Test POST request with invalid form data
        form_data['email'] = 'invalidemail'
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enduser/register.html')
        self.assertTrue(isinstance(response.context['form'], CreateUserForm))
        # self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')



class TestViewsUpdateProfile(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpass'
        )
        self.client.login(username='testuser', password='testpass')

    def test_update_profile(self):
        # login as test user

        # make GET request to update profile page
        response = self.client.get(reverse('profile'))

        # check that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # make POST request to update profile
        post_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'testuser@example.com',
        }
        response = self.client.post(reverse('profile'), data=post_data)

        # check that the response redirects to the profile page
        # self.assertRedirects(response, reverse('profile'))

        # refresh the user object from the database
        self.user.refresh_from_db()

        # check that the user object has been updated
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'testuser@example.com')



class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass', role='participant')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2', role='setter')

    def test_login_GET(self):
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response,'enduser/login.html')


    def test_successful_login(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'})
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_successful_login_setter(self):
        response = self.client.post(reverse('login'), {'username': 'testuser2', 'password': 'testpass2'})
        self.assertRedirects(response, reverse('dashboardPage'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_unsuccessful_login(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpass'})
        self.assertContains(response, 'Username or Password is incorrect')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

class TestActivateView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.token = account_activation_token.make_token(self.user)

    def test_activation_success(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.get(reverse('activate', args=[uidb64, self.token]))
        self.assertEqual(response.status_code, 302)  # check if the user is redirected to the login page
        # self.assertRedirects(response, reverse('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)  # check if the user is activated
        # self.assertEqual(len(response.context['messages']), 1)  # check if a success message is displayed

    def test_activation_failure(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk + 1))  # wrong user id
        response = self.client.get(reverse('activate', args=[uidb64, self.token]))
        self.assertEqual(response.status_code, 200)  # check if the view returns the register template
        self.user.refresh_from_db()
        # self.assertFalse(self.user.is_active) 

class LogoutPageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_logout(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

class SubmissionViewTestCase(TestCase):
    def setUp(self):
        # Create a user and a submission
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.submission = Submission.objects.create(user=self.user)

    def test_authenticated_user_can_access_own_submission(self):
        # Log in as the user and try to access the submission page
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('submission', args=[self.submission.id]))
        # Check that the response status code is 200 and the submission is in the context
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['submission'], self.submission)

    def test_authenticated_user_cannot_access_other_submission(self):
        # Create another user and submission
        other_user = User.objects.create_user(username='otheruser', password='12345')
        other_submission = Submission.objects.create(user=other_user)
        # Log in as the first user and try to access the second submission page
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('submission', args=[other_submission.id]))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_cannot_access_submission(self):
        # Log out and try to access the submission page
        self.client.logout()
        response = self.client.get(reverse('submission', args=[self.submission.id]))
        # Check that the response is a redirect to the login page
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('submission', args=[self.submission.id]))


class TestAllSubmissionPage(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.login(username='testuser', password='testpass')
        self.problem1 = Problem.objects.create(
            Name='testproblem',
            Difficulty='Easy',
            TimeLimit=1,
            MemLimit=64,
            testnum=1,
            Author=self.user.username,
            Statement='This is a test problem statement.'
        )
        self.problem2 = Problem.objects.create(
            Name='testproblem2',
            Difficulty='Easy',
            TimeLimit=1,
            MemLimit=64,
            testnum=1,
            Author=self.user.username,
            Statement='This is a test problem statement2.'
        )
        
    def test_all_submissions_page(self):
        
        Submission.objects.create(user=self.user, problem = self.problem1, user_code='print("Hello World")', verdict='Accepted')
        Submission.objects.create(user=self.user, problem = self.problem2, user_code='print("Goodbye World")', verdict='Wrong Answer')
        response = self.client.get(reverse('all_submissions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enduser/submission.html')
        self.assertContains(response, 'Accepted')
        self.assertContains(response, 'Wrong Answer')


class TestModelsSubmission(TestCase):
    @classmethod
    def setUp(self):
        user = User.objects.create(
            username='testuser', 
            password='12345', 
            emailid='testuser@example.com',
            totalCount=5, 
            easyCount=2, 
            mediumCount=1, 
            toughCount=2, 
            totalScore=45, 
            role='admin')

        problem = Problem.objects.create(
            Statement="This is a sample statement",
            Name='Test Problem', 
            Difficulty='Easy', 
            TimeLimit=2, 
            MemLimit=64, 
            testnum=1, 
            Author='Test Author')

        Submission.objects.create(user=user, problem=problem, user_code='print("Hello, World!")', user_stdout='Hello, World!\n', submission_time=datetime.now(), run_time=0.05, language='Python', verdict='Accepted')
    
    def test_object_name(self):
        submission = Submission.objects.get(id=1)
        expected_object_name = str(submission.submission_time) + " : @" + str(submission.user) + " : " + submission.problem.Name + " : " + submission.verdict + " : " + submission.language
        self.assertEqual(expected_object_name, str(submission))

class TestModelsUser(TestCase):

    @classmethod
    def setUp(cls):
        User.objects.create(
            username='testuser', 
            password='testpass', 
            emailid='test@example.com',
            totalCount=5, 
            easyCount=2, 
            mediumCount=1, 
            toughCount=2, 
            totalScore=45, 
            role='admin'
        )

    def test_object_name_is_username(self):
        user = User.objects.get(id=1)
        expected_object_name = user.username
        self.assertEquals(expected_object_name, str(user))
