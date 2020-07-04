from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Profile, Question, Option

password = 1234
username = 'username'


def create(logic):
    user = User.objects.create(username=username, password=password)
    user.set_password(password)
    user.save()
    Profile.objects.create(user=user, taken=logic)
    return user


def create_question(no_of_question, no_of_options):
    for i in range(no_of_question):
        question = Question.objects.create(Q='question {}'.format(i + 1))
        for j in range(no_of_options):
            x = chr(ord('A') + j)
            option = Option.objects.create(question=question, option='option {}'.format(x))
    if no_of_options !=0:
        return option


class QuestionsViewTest(TestCase):
    def test_no_questions(self):
        user = create(False)
        self.client.login(username='username', password=1234)
        response = self.client.get(reverse('exams:questions', args=(user.pk,)))
        self.assertContains(response, 'no question available')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['all_questions'], [])

    def test_one_question(self):
        create_question(1, 0)
        user = create(False)
        response = self.client.get(reverse('exams:questions', args=(user.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['all_questions'], ['<Question: 1 question 1>'])

    def test_question_if_user_has_taken(self):
        user = create(True)
        self.client.login(username=user.username, password=password)
        response = self.client.get(reverse('exams:questions', args=(user.id,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FULL NAME: {} {}'.format(user.first_name, user.last_name) )
        self.assertContains(response, 'Email: {}'.format(user.email) )
        self.assertContains(response, 'Score: {}'.format(user.profile.score))

    def test_two_question_four_option(self):
        user = create(False)
        create_question(2, 4)
        self.client.login(username=user.username, password=password)
        response = self.client.get(reverse('exams:questions', args=(user.pk,)), follow=True)
        self.assertQuerysetEqual(response.context['all_questions'], ['<Question: 1 question 1>',
                                                                     '<Question: 2 question 2>'], ordered=False)
        self.assertContains(response, '2. question' )
        self.assertContains(response, '1. question' )
        self.assertContains(response, 'option A' )
        self.assertContains(response, 'option B' )
        self.assertContains(response, 'option C' )
        self.assertContains(response, 'option D')
        self.assertEqual(response.status_code, 200)


class LoginView(TestCase):
    def test_login_taken(self):
        user = create(True)
        response = self.client.post(reverse('exams:login'), {'username': 'username', 'password': 1234}, follow=True)
        self.assertContains(response, 'FULL NAME: {} {}'.format(user.first_name, user.last_name))
        self.assertContains(response, 'Email: {}'.format(user.email))
        self.assertContains(response, 'Score: {}'.format(0))
        self.assertContains(response, 'Logout')
        self.assertEqual(response.status_code, 200)

    def test_login_not_taken(self):
        create(False)
        response = self.client.post(reverse('exams:login'), {'username': 'username', 'password': 1234}, follow=True)
        self.assertContains(response, 'Logout')
        self.assertContains(response, 'Start')
        self.assertEqual(response.status_code, 200)

    def test_login_wrong_user(self):
        create(False)
        response = self.client.post(reverse('exams:login'), {'username': 'username', 'password': 123}, follow=True)
        self.assertContains(response, 'invalid username or password' )
        self.assertContains(response, 'Username' )
        self.assertContains(response, 'Password' )
        self.assertContains(response, 'Login' )
        self.assertContains(response, 'Sign Up')
        self.assertEqual(response.status_code, 200)

    def test_login_empty_user(self):
        create(False)
        response = self.client.post(reverse('exams:login'), {'username': '', 'password': 123}, follow=True)
        self.assertContains(response, 'invalid username or password')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Sign Up')
        self.assertEqual(response.status_code, 200)

    def test_login_empty_password(self):
        create(False)
        response = self.client.post(reverse('exams:login'), {'username': 'username', 'password': ''}, follow=True)
        self.assertContains(response, 'invalid username or password')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Sign Up')
        self.assertEqual(response.status_code, 200)

    def test_login_form(self):
        response = self.client.get(reverse('exams:login'), follow=True)
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Sign Up')
        self.assertEqual(response.status_code, 200)


class Logout(TestCase):
    def test_logout(self):
        response = self.client.get(reverse('exams:logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Sign Up')


class Answer(TestCase):
    def test_wrong_answer(self):
        user = create(False)
        question = Question.objects.create(Q='question')
        incorrect_option = Option.objects.create(question=question,  option='option A')
        self.client.login(username=user.username, password=password)
        response = self.client.post(reverse('exams:answer', args=(user.id,)), {question.id: incorrect_option.id},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FULL NAME: {} {}'.format(user.first_name, user.last_name))
        self.assertContains(response, 'Email: {}'.format(user.email))
        self.assertContains(response, 'Score: {}'.format(0))
        self.assertContains(response, 'Logout')
    def test_right_answer(self):
        user = create(False)
        question = Question.objects.create(Q='question')
        correct_option = Option.objects.create(question=question, option='option A', is_favorite=True)
        self.client.login(username=user.username, password=password)
        response = self.client.post(reverse('exams:answer', args=(user.id,)),
                                    {'form': 'form', question.id: correct_option.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FULL NAME: {} {}'.format(user.first_name, user.last_name))
        self.assertContains(response, 'Email: {}'.format(user.email))
        self.assertContains(response, 'Score: {}'.format(25))
        self.assertContains(response, 'Logout')

    def test_answer_if_user_has_taken_exam(self):
        user = create(True)
        self.client.login(username=user.username, password=password)
        response = self.client.post(reverse('exams:answer', args=(user.id,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'FULL NAME: {} {}'.format(user.first_name, user.last_name))
        self.assertContains(response, 'Email: {}'.format(user.email))
        self.assertContains(response, 'Score: {}'.format(0))
        self.assertContains(response,'Logout' )

    def test_answer_get_request(self):
        user = create(True)
        self.client.login(username=user.username, password=password)
        response = self.client.get(reverse('exams:answer', args=(user.id,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'FULL NAME: {} {}'.format(user.first_name, user.last_name))
        self.assertContains(response, 'Email: {}'.format(user.email))
        self.assertContains(response, 'Score: {}'.format(0))
        self.assertContains(response,'Logout' )


class Index(TestCase):
    def test_index_if_logged_out(self):
        response = self.client.get(reverse('exams:index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login' )
        self.assertContains(response, 'Sign Up')

    def test_index_if_logged_in_has_taken_exam(self):
        user = create(True)
        self.client.login(username=user.username, password=password)
        response = self.client.get(reverse('exams:index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'FULL NAME: {} {}'.format(user.first_name, user.last_name))
        self.assertContains(response, 'Email: {}'.format(user.email))
        self.assertContains(response, 'Score: {}'.format(0))
        self.assertContains(response,'Logout' )

    def test_index_if_logged_in_and_has_not_taken(self):
        user = create(False)
        self.client.login(username=user.username, password=password)
        response = self.client.get(reverse('exams:index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logout')
        self.assertContains(response,'Start')


class UserFormViewTest(TestCase):
    def test_get_form(self):
        response = self.client.get(reverse('exams:register'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First name')
        self.assertContains(response, 'Last name')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Email address')
        self.assertContains(response, 'Password')

    def test_post_empty_form(self):
        response = self.client.post(reverse('exams:register'), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_post_filled_form(self):
        response = self.client.post(reverse('exams:register'),
                                    {'first_name': ['modesta'],
                                     'last_name': ['okeke'],
                                     'username': ['username'],
                                     'email': ['test@gmail.com'],
                                     'password': ['test']}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FULL NAME: Modesta Okeke')
        self.assertContains(response, 'Email: test@gmail.com')
        self.assertContains(response,'Start')

    def test_username_taken(self):
        self.client.post(reverse('exams:register'),
                         {'first_name': ['modesta'], 'last_name': ['okeke'], 'username': ['username'],
                          'email': ['test@gmail.com'],
                          'password': ['test']}, follow=True)
        response = self.client.post(reverse('exams:register'),
                         {'first_name': ['modesta'], 'last_name': ['okeke'], 'username': ['username'],
                          'email': ['test@gmail.com'],
                          'password': ['test']}, follow=True)
        self.assertContains(response, 'A user with that username already exists.')


class ModelStr(TestCase):
    def test_option_str(self):
        option = create_question(1, 1)
        self.assertEqual(str(option), option.option)

    def test_profile_str(self):
        user = User.objects.create(first_name='modesta', last_name='okeke', password=1234, username=username)
        profile = Profile.objects.create(user=user)
        self.assertEqual(str(profile), 'modesta okeke')