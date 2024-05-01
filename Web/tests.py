from .models import Test, UserAnswers
from .helpers import get_average_all
from django.test import TestCase
from django.contrib.auth.models import User

class HelpersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create()
        test = Test.objects.create(user_id = user.id)

        UserAnswers.objects.create(id = "1", correct_answer_rate = 1.0, test_id = test.id)
        UserAnswers.objects.create(id = "2", correct_answer_rate = 0.5, test_id = test.id)
        UserAnswers.objects.create(id = "3", correct_answer_rate = 0.3, test_id = test.id)
        UserAnswers.objects.create(id = "4", correct_answer_rate = 0.1, test_id = test.id)

    def test_get_average_all(self):
        user_answers = UserAnswers.objects.all()
        self.assertEqual(round(get_average_all(user_answers), 3), 0.475)
        self.assertEqual(get_average_all(user_answers.none()), 0)

