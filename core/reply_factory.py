from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST

def generate_bot_responses(message, session):
    bot_responses = []

    # Initialize current question and session data
    current_question_id = session.get("current_question_id")
    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        current_question_id = -1 
        session["answers"] = [] 

    # Process the user's answer if applicable
    if current_question_id >= 0:
        success, error = record_current_answer(message, current_question_id, session)
        if not success:
            return [error] 

    # Get the next question
    next_question, next_question_id = get_next_question(current_question_id)
    if next_question:
        bot_responses.append(next_question)
        session["current_question_id"] = next_question_id
    else:
        bot_responses.append(generate_final_response(session))
        session["current_question_id"] = None

    session.save()
    return bot_responses


def record_current_answer(answer, current_question_id, session):
    if current_question_id < 0 or current_question_id >= len(PYTHON_QUESTION_LIST):
        return False, "Invalid question ID!"

    question = PYTHON_QUESTION_LIST[current_question_id]
    is_correct = question["answer"].strip().lower() == answer.strip().lower()

    if "answers" not in session:
        session["answers"] = []

    session["answers"].append({
        "question_text": question["question_text"],
        "user_answer": answer,
        "is_correct": is_correct
    })
    session.save()

    return is_correct, "" if is_correct else "Incorrect answer! Moving to the next question."


def get_next_question(current_question_id):
    next_question_id = current_question_id + 1
    if next_question_id < len(PYTHON_QUESTION_LIST):
        question = PYTHON_QUESTION_LIST[next_question_id]
        question_text = f"{question['question_text']}\nOptions:\n" + \
                        "\n".join([f"{i + 1}. {opt}" for i, opt in enumerate(question["options"])])
        return question_text, next_question_id

    return None, -1  # No more questions


def generate_final_response(session):
    answers = session.get("answers", [])
    score = sum(1 for answer in answers if answer["is_correct"])

    return f"Quiz completed! Your final score is {score} out of {len(answers)}."
