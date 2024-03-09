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

from django.urls import path
from Auth import views as auth
from Web import views as web
 
urlpatterns = [
    path("login", auth.login),
    path("register", auth.register),
    path("logout", auth.logout),
    path("", web.index),
    path("profile", web.profile),
    path("create_test", web.create_test),
    path("edit_test/<int:id>/", web.edit_test),
    path("delete_test/<int:id>/", web.delete_test),
    path("publish_test/<int:id>/", web.publish_test),
    path("questions/<int:test_id>/", web.questions),
    path("create_question/<int:test_id>/", web.create_question),
    path("edit_question/<int:test_id>/<int:id>/", web.edit_question),
    path("delete_question/<int:test_id>/<int:id>/", web.delete_question),
    path("set_true/<int:test_id>/<int:question_id>/<int:id>", web.set_true),
    path("create_answer/<int:test_id>/<int:question_id>/", web.create_answer),
    path("edit_answer/<int:test_id>/<int:question_id>/<int:id>/", web.edit_answer),
    path("delete_answer/<int:test_id>/<int:question_id>/<int:id>/", web.delete_answer),
]
