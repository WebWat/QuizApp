"""
URL configuration for Main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from django.views.static import serve
from Auth import views as auth
from Web import views as web
from Tests import views as tests
from Questions import views as questions
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = [
    # Auth
    path("login", auth.login),
    path("register", auth.register),
    path("logout", auth.logout),
    path("change_password", auth.change_password),
    path("change_login", auth.change_login),

    # Web
    path("", web.index),
    path("error", web.error),
    path("history", web.history),
    path("about/<int:id>/", web.about),
    path("result/<unique_id>/", web.result),
    path("test_run/<int:test_id>/", web.test_run),
    path("test_run/<int:test_id>/<unique_id>/", web.test_run),

    # Tests
    path("profile", tests.profile),
    path("create_test", tests.create_test),
    path("edit_test/<int:id>/", tests.edit_test),
    path("add_tag/<int:test_id>/", tests.add_tag),
    path("delete_test/<int:id>/", tests.delete_test),
    path("user_tests/<username>/", tests.user_tests),
    path("publish_test/<int:id>/", tests.publish_test),

    # Questions
    path("questions/<int:test_id>/", questions.questions),
    path("create_question/<int:test_id>/", questions.create_question),
    path("delete_image/<int:test_id>/<int:question_id>/", questions.delete_image),
    path("edit_question/<int:test_id>/<int:question_id>/", questions.edit_question),
    path("delete_question/<int:test_id>/<int:question_id>/", questions.delete_question),
    path("set_true/<int:test_id>/<int:question_id>/<int:answer_id>", questions.set_true),
    path("create_answer/<int:test_id>/<int:question_id>/", questions.create_answer),
    path("edit_answer/<int:test_id>/<int:question_id>/<int:answer_id>/", questions.edit_answer),
    path("delete_answer/<int:test_id>/<int:question_id>/<int:answer_id>/", questions.delete_answer),

    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, 
                          document_root = settings.MEDIA_ROOT)
