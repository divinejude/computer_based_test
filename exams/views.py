from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.generic import View

from .forms import UserForm, LoginForm
from .models import *


# Create your views here.
def index(request):

    return redirect('exams:logout')


def answer(request, user_id):
    template_name = 'exams/index.html'
    user = User.objects.get(pk=user_id)
    profile = user.profile_set.get(user=user)
    i = 0
    if request.method == 'POST':
        for key, value in request.POST.items():

            if i == 0:
                i = 1
            else:
                question = Question.objects.get(pk=key)
                option = question.option_set.get(pk=value)
                if option.is_favorite:
                    profile.score += 25
                    profile.save()
        score = profile.score
        profile.taken = True
        profile.save()
        taken = profile.taken
        context = {'score': score, 'taken': taken}
        return redirect(template_name, context)
    else:
        score = profile.score
        taken = profile.taken
        context = {'score': score, 'taken': taken}
        return render(request, template_name, context)


def questions(request):
    all_questions = Question.objects.all()
    context = {'all_questions': all_questions}
    template_name = 'exams/questions.html'
    return render(request, template_name, context)


class UserFormView(View):
    form_class = UserForm
    template_name = 'exams/registration-form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            profile = Profile(user=user)
            profile.save()

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return render(request, 'exams/index.html')
        return render(request, self.template_name, {'form': form})


class LoginFormView(View):
    form_class = LoginForm
    template_name = 'exams/login.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(None)
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                profile = Profile.objects.get(user=user)
                taken = profile.taken
                score = profile.score
                context = {'taken': taken, 'score': score}
                return render(request, 'exams/index.html', context)
        messages.error(request, 'invalid username or password')
        return render(request, self.template_name, {'form': form})


def logout1(request):
    logout(request)
    return render(request, 'exams/index.html')
