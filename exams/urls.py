from django.conf.urls import url
from . import views

app_name = 'exams'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.UserFormView.as_view(), name='register'),
    url(r'^logout$', views.logout1, name='logout'),
    url(r'^login$', views.LoginFormView.as_view(), name='login'),
    url(r'^(?P<user_id>[0-9]+)/questions/$', views.questions, name='questions'),
    url(r'^(?P<user_id>[0-9]+)/$', views.answer, name='answer'),

]
