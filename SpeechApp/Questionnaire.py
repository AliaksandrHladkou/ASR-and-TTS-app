import speech_recognition as sr
import subprocess
import sys
import time

from Question import Question
from User import User
from Data import Data
from random import randrange
from playsound import playsound

# Questionnaire
question_prompts = [
    "\nWhich of these is not a core data type?\n(a) Lists\n(b) Dictionary\n(c) Tuples\n(d) Class",
    "\nWhat data type is the object below?\n(a) List\n(b) Dictionary\n(c) Tuple\n(d) Array",
    "\nWhich of the following best defines a class?\n(a) Parent of an object"
    "\n(b) Instance of an object\n(c) Blueprint of an object\n(d) Scope of an object",
    "\nWho invented OOP?\n(a) Alan Kay\n(b) Andrea Ferro\n(c) Dennis Ritchie\n(d) Adele Goldberg",
    "\nWhich of the two features match each other?\n(a) Inheritance and Encapsulation\n(b) Encapsulation and "
    "Polymorphism\n(c) Encapsulation and Abstraction\n(d) Abstraction and Polymorphism"
]

questions = [
    Question(question_prompts[0], "d", "Class"),
    Question(question_prompts[1], "a", "List"),
    Question(question_prompts[2], "b", "Instance of an object"),
    Question(question_prompts[3], "a", "Alan Kay"),
    Question(question_prompts[4], "c", "Encapsulation and Abstraction")
]

users = [
    User("Alexander", "Alex", "ice cream"),
    User("John", "John", "John")
]

no_answer_reply = [
    "I didn't catch that. What was that?",
    "Could you repeat it please?",
    "I'm sorry. What did you say?"
]

MENU_WIDTH = 40
ALLOWED_ATTEMPTS = 3


# check that recognition is correct
def check_user(answer, rec, mic):
    checked = False
    say("Say 'yes' if your answer was: " + str(answer))
    # reply = recognize(rec, mic)
    reply = listen(mic, rec, 3)
    if reply["transcription"]:
        if reply["transcription"] == "yes":
            checked = True
    return checked


# recognition API
def recognize(rec, mic):
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(rec, sr.Recognizer):
        raise TypeError("`rec` must be `Recognizer` instance")

    if not isinstance(mic, sr.Microphone):
        raise TypeError("`mic` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with mic as source:
        playsound('tolisten.wav')
        print("\nListening..")
        rec.adjust_for_ambient_noise(source)
        audio = rec.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = rec.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    if not response["transcription"]:
        response["success"] = False
        print("")
    else:
        print(response["transcription"])
    return response


# Says and prints any string that passed
def say(text):
    print(text)
    subprocess.call(['say', text])


# Listen to user and recognize
def listen(microphone, recognizer, attempt_lim):
    for i in range(attempt_lim):
        answer = recognize(recognizer, microphone)
        if answer["transcription"]:
            if answer["transcription"] == "exit":
                say("Goodbye!")
                sys.exit(0)
            return answer
        else:
            if i == attempt_lim - 1:
                answer["transcription"] = "no answer"
                return answer
            reply = randrange(len(no_answer_reply))
            say(no_answer_reply[reply])


# print menu
def print_menu(q_number, q_total):
    q_info = "\n| Question " + str(q_number) + "/" + str(q_total) + " |"
    for i in range(MENU_WIDTH):
        print("-", end="")
    print(q_info + "|  Repeat  |" + "|   Exit   |")
    for i in range(MENU_WIDTH):
        print("_", end="")
    print()


# print end question line
def print_end_of():
    for i in range(2):
        print("|", end="")
        for j in range(MENU_WIDTH - 2):
            print("-", end="")
        print("|")
    print()


# printing main menu of the program (before login).
def print_main_menu():
    info = "\n|  Login  |" + "| Create new user |" + "|  Exit |" + "|"
    for i in range(MENU_WIDTH):
        print("-", end="")
    print(info)
    for i in range(MENU_WIDTH):
        print("_", end="")
    print()


# printing menu when logged in
def print_user_menu(id):
    info = "\n|   " + str(users[id].nickname) + "   |" + "| Start Test |" + "|   Exit   |" + "|"
    for i in range(MENU_WIDTH):
        print("-", end="")
    print(info)
    for i in range(MENU_WIDTH):
        print("_", end="")
    print()


# add users to data
def init_data():
    data = Data()
    # data.add(0, (User("Admin", "Test", "Administrator"), 0))
    for i in range(len(users)):
        if i not in data.keys():
            data.add(i, (users[i], 0))
    return data


# making sure that a user exist
def check_credentials(microphone, recognizer):
    is_correct = {
        "true": False,
        "id": 0
    }
    say("What is your name?")
    name = listen(microphone, recognizer, 3)
    for i in range(len(users)):
        if name["transcription"] == users[i].name:
            say("What is your keyword?")
            key = listen(microphone, recognizer, 3)
            if key["transcription"] == users[i].key:
                is_correct["true"] = True
                is_correct["id"] = i
                say("Welcome, " + str(users[i].nickname))
                break
    return is_correct


# Main engine of the program
def engine():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    data = init_data()

    attempt_counts = 0
    while True:
        print_main_menu()
        user = login(microphone, recognizer, data)
        if user["isTrue"]:
            # print("Welcome to the questionnaire " + str(users[user["id"]].nickname) + "!")
            print_user_menu(user["id"])
            for i in range(3):
                say("You can now say 'start test' or 'exit'.")
                decision = listen(microphone, recognizer, 3)
                if decision["transcription"] == "start test":
                    run_test(questions, recognizer, microphone)
                    break
        else:
            say("Goodbye!")
            sys.exit(0)
        if attempt_counts == ALLOWED_ATTEMPTS:
            say("Goodbye!")
            break
        attempt_counts += 1


# ask user to login or create new user
def login(microphone, recognizer, data):
    success = {
        "isTrue": False,
        "id": 0
    }
    for i in range(ALLOWED_ATTEMPTS):
        say("Please say 'login' or 'create new user'.")
        input = listen(microphone, recognizer, 3)
        if input["transcription"] == "login":
            credentials = check_credentials(microphone, recognizer)
            if credentials["true"]:
                success["isTrue"] = True
                success["id"] = credentials["id"]
                break
            else:
                if i == 2:
                    say("Please try again later.")
                else:
                    say("I didn't find it. Try again.")
        elif input["transcription"] == "create new user":
            # then create new user and add to the data
            say("What is your name?")
            name = listen(microphone, recognizer, 3)
            if name["success"]:
                say("What is your preferred unique nickname?")
                nickname = listen(microphone, recognizer, 3)
                is_unique = True
                for j in range(ALLOWED_ATTEMPTS):
                    for k in range(len(users)):
                        if nickname["transcription"] == users[k].nickname:
                            say("This nickname is already taken.")
                            is_unique = False
                            break
                    if is_unique:
                        break
                    else:
                        if j != ALLOWED_ATTEMPTS-1:
                            say("Please, provide unique nickname")
                            nickname = listen(microphone, recognizer, 3)
                            is_unique = True

                if nickname["success"] and is_unique:
                    say("What is your keyword?")
                    key = listen(microphone, recognizer, 3)
                    if key["success"]:
                        data.add(len(data),
                                 (User(name["transcription"], nickname["transcription"], key["transcription"]), 0))
                        users.append(User(name["transcription"], nickname["transcription"], key["transcription"]))
                        success["isTrue"] = True
                        success["id"] = len(data)-1
                        say("Welcome, " + str(nickname["transcription"]))
                        break
        else:
            if i == 2:
                say("Please try again later.")
            else:
                say(no_answer_reply[randrange(len(no_answer_reply))])

    return success


# running the test
def run_test(quest, recognizer, microphone):
    score = 0
    quest_num = 0

    for question in quest:
        playsound('sound.wav')
        attempt = 1  # 2 attempt to answer
        quest_num += 1
        print_menu(quest_num, len(quest))

        say("\nQuestion #" + str(quest_num))
        say(question.prompt)
        print_end_of()
        # answer = input()
        answer = listen(microphone, recognizer, 3)

        # Check the user's input
        while True:
            if answer["transcription"]:
                if answer["transcription"] == "repeat":
                    say(question.prompt)
                    answer = listen(microphone, recognizer, 3)
                    if attempt > 0:
                        attempt -= 1
                else:
                    # check to be sure that a user said what he wanted to say.
                    # If it's true check if the answer is correct
                    is_correct = check_user(answer["transcription"], recognizer, microphone)

                    # if a user says Yes
                    if is_correct:
                        if answer["transcription"] == str.lower(question.answer) or \
                                answer["transcription"] == str.lower(question.short_answer):
                            score += 1
                        break
                    else:
                        say("What is your answer then?")
                        answer = listen(microphone, recognizer, 3)
                if attempt >= 2:
                    print("Reached max attempt #: " + str(attempt) + "\n")
                    break
                attempt += 1

        say("Your answer is: " + answer["transcription"])
        print()
        # say("The correct answer is: (" + question.short_answer + ") " + question.answer)
        time.sleep(1)

    output = "You got " + str(score) + " out of " + str(len(quest)) + " correct."
    say(output)


if __name__ == "__main__":
    engine()
