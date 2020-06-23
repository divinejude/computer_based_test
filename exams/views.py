from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from .forms import UserForm, LoginForm
from .models import *


# Create your views here.
def index(request):
    return render(request, 'exams/index.html')


def answer(request, user_id):
    user = User.objects.get(pk=user_id)
    profile = user.profile
    i = 0
    if request.method == 'POST':
        if profile.taken:
            return redirect('exams:index')
        else:
            for key, value in request.POST.items():

                if i == 0:
                    i = 1
                else:
                    question = Question.objects.get(pk=key)
                    option = question.option_set.get(pk=value)
                    if option.is_favorite:
                        profile.score += 25
                        profile.save()
            profile.taken = True
            profile.save()
            return redirect('exams:index')
    else:
        return redirect('exams:index')


def questions(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user.profile.taken:
        return redirect('exams:index')
    else:
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
            last_name = form.cleaned_data['last_name']
            first_name = form.cleaned_data['first_name']
            password = form.cleaned_data['password']
            user.set_password(password)
            first_name = str(first_name).capitalize()
            last_name = str(last_name).capitalize()
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            profile = Profile(user=user)
            profile.save()

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('exams:index')
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
                return redirect('exams:index')
        messages.error(request, 'invalid username or password')
        return render(request, self.template_name, {'form': form})


def logout1(request):
    logout(request)
    return redirect("exams:index")
