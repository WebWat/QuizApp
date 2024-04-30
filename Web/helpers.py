from .models import UserAnswers

# Возвращает средний процент правильных ответов среди всех пользователей
def get_average_all(total_user_answers):
    correct_rate_all = 0
    for answer in total_user_answers:
        correct_rate_all += answer.correct_answer_rate
    return correct_rate_all / total_user_answers.count()

# Возвращает средний процент выборов для данного вопроса с одиночным ответом
def get_average_for_single(total_user_answers, current_question, answer_id):
    average = 0
    for all in total_user_answers:
        if all.questionresult_set.all()[current_question].singlechoiceresult.chose == answer_id:
            average += 1
    return average * 100 / total_user_answers.count()

# Возвращает средний процент выборов для данного вопроса с множественным выбором
def get_average_for_multiple(total_user_answers, current_question, answer_id):
    average = 0
    total_multiple_chose = 0
    for all in total_user_answers:
        total_multiple_chose += all.questionresult_set.all()[current_question].multiplechoiceresult.multiplechoiceanswersresult_set.count()
        for mul_ans in all.questionresult_set.all()[current_question].multiplechoiceresult.multiplechoiceanswersresult_set.all():
            if mul_ans.chose == answer_id:
                average += 1
    return average * 100 / total_multiple_chose



