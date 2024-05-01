# Возвращает средний процент правильных ответов среди всех пользователей
def get_average_all(total_user_answers):
    total_user_answers_count = total_user_answers.count()
    if total_user_answers_count == 0:
        return 0
    
    correct_rate_all = 0
    for answer in total_user_answers:
        correct_rate_all += answer.correct_answer_rate
    return correct_rate_all / total_user_answers_count

# Возвращает средний процент выборов для данного вопроса с одиночным ответом
def get_average_for_single(total_user_answers_count, question, answer_id):
    answer = question.singlechoice.singlechoiceanswers_set.get(id = answer_id)
    if total_user_answers_count == 0:
        return 0
    else:
        return answer.count * 100 / total_user_answers_count

# Возвращает средний процент выборов для данного вопроса с множественным выбором
def get_average_for_multiple(question, answer_id):
    total = question.multiplechoice.total_count
    answer = question.multiplechoice.multiplechoiceanswers_set.get(id = answer_id)
    if total == 0:
        return 0
    else:
        return answer.count * 100 / total


