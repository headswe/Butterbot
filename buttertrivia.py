import os
import operator
import random
from os import walk, listdir, remove
from random import randint
from inspect import signature

current_trivia = []
index = 0
score = {}
running = False
commands = None
nr_of_questions = 10

def init_commands():
    global commands
    commands = {
        'start':start_trivia,
        #'add':add_question,
        'list':get_trivias,
        'highscore':get_highscore,
        'stop':stop_trivia,
        #'questions':list_questions,
        #'removequestion':remove_question,
        'setquestions':set_questions,
        'delete':remove_trivia
    }


#Formats the given input so that we run the correct function with
#the correct arguments
def format_input(input):
    keywords = input.split(" ",2)
    if keywords[0] in commands:
        function = commands[keywords[0]]
        function_sig = signature(function)
        if len(function_sig.parameters) == len(keywords) - 1:
            if len(keywords)-1 > 0:
                return function(*keywords[1:])
            else:
                return function() 
        else:
            return "Wrong amount of arguments, expected amount: " + str(len(function_sig.parameters))
    else:
        return "There is no command called " + commands[0].capitalize()


def set_questions(arg_val):
    global nr_of_questions
    nr_of_questions = int(arg_val)
    return "Number of questions has been set to " + str(nr_of_questions)


#Starts a trivia with the given parameter
def start_trivia(trivia):
    global running, nr_of_questions
    question_nr = nr_of_questions
    if not running:
        running = search_trivias(trivia)
        if running:
            set_trivia(trivia, question_nr)
            return "Successfully initialized trivia " + trivia.capitalize() + "\n" + get_question()
        else:
            return "There is no trivia with name: " + trivia.capitalize()
    else:
        return "There is already a trivia running!"


#Opens the given trivia and loads all the questions/answers
def set_trivia(trivia, nr_of_questions):
    nr_of_questions = int(nr_of_questions)
    file_open = open("triviagames/{}.txt".format(trivia.lower()), "r")
    all_lines = file_open.readlines()
    if len(all_lines) < nr_of_questions:
        return "There is only " + str(len(all_lines)) + " lines in " + trivia.capitalize()
    lines = random.sample(all_lines, nr_of_questions)
    for line in lines:
        result_tup = (line.split("$")[0], line.split("$")[1].strip().lower().split(","))
        current_trivia.append(result_tup) 
    print(len(current_trivia))
    file_open.close()


#Gets all files in dir triviagames with the file ending .txt
#then splits each file on . and capitalizes it so we only get
#the filenames capitalized. We then return a list of these filenames
def get_trivias_list():
	directory = os.path.dirname(__file__)
	directory = os.path.join(directory, 'triviagames/')
	return [ str(f).split(".")[0].capitalize() for f in listdir(directory) if f.endswith(".txt") ]


#Returns all trivias as an output string to be viewed in discord.
def get_trivias():
    f = get_trivias_list()
    result = "There is currently " + str(len(f)) + " games:\n"
    result += '\n'.join(f)#e.split(".")[0].capitalize() for e in f)
    return result


#Checks if the given trivia exists
def search_trivias(trivia):
    f = get_trivias_list()
    return True if trivia.capitalize() in get_trivias_list() else False



def load_trivia(trivia):
    return ("Successfully started trivia: " + trivia.capitalize() 
            if search_trivias(trivia) 
            else "There is no trivia with name: " + trivia.capitalize())


#Randomize a number between 0 and end of list, then return the 
#question on the randomed numbers index in the question list
def get_question():
    global current_trivia, index
    index = randint(0,len(current_trivia)-1)
    return current_trivia[index][0]


#If length of list is larger than index there is more questions
#if not we are done
def check_if_more_questions():
    global current_trivia
    return len(current_trivia) > 0


#Removes the current question
def delete_question():
    global current_trivia, index
    del current_trivia[index]


#Checks if the provided answer is an answer in the answer list
#if it is we remove the question from the list and return True
#for a correct answer.
#If the answer is not correct we return false.
def check_answer(answer):
    global current_trivia, index
    try:
        if answer.lower() in current_trivia[index][1]:
            del current_trivia[index]
            return True
        else:
            return False
    except IndexError:
        return False


#Gives the provided person +1 in score
def give_score(person):
    global score
    score[person] = score[person] + 1 if person in score else 1


#Prints the score for everyone who has atleast got 1 answer corrrect
def print_score():
    global score
    return "\n".join("{} has score: {}".format(k, v) for k, v in score.items())


#Gets the highest person(s) in the scorelist as winner for the trivia
#game
def get_winner():
    global score, running
    winner = ""
    prev_val = 0
    for k,v in score.items():
        if prev_val <= v:
            if prev_val == v:
                winner += ", " + k
            else:
                prev_val = v
                winner = k
    score = {}
    running = False
    return winner


#Resets global variables
def exit_trivia():
    global current_trivia, score
    current_trivia = []
    score = {}


#Stops the current triviagame
def stop_trivia():
    global running
    if running:
        update_highscore()
        result = "Trivia stopped!\nCurrent standings:\n" + print_score() + "\nThe winner is: " + get_winner()
        exit_trivia()
        running = False
        return result
    else:
        return "There is currently no trivia running"
    

#Get the highscore
def get_highscore():
    highscore = "Trivia highscore:\n"
    files = open("highscore.txt", "r")
    highscore +=  "".join(line.split(":")[0] + " : " + line.split(":")[1] for line in files)
    return highscore


#Update the highscore based on the last played trivia
def update_highscore():
	global score
	highscore_dir = os.path.dirname(__file__)
	highscore_file = os.path.join(highscore_dir, 'highscore.txt')

	file_list = []
	files = open(highscore_file, "r")
	highscore = { line.split(":")[0]: int(line.split(":")[1]) for line in files }
	files.close()

	open(highscore_file, "w").close()
	files = open(highscore_file, "w")

	highscore = { k: ( int(highscore[k]) if k in highscore else 0 ) + v 
				  for k,v in score.items() }

	highscore = sorted(highscore.items(), key=operator.itemgetter(1))
	highscore.reverse()
	files.writelines([ str(tup[0]) + ":" + str(tup[1]) + "\n" for tup in highscore ])
	files.close()


#Add a question to a trivia, if the trivia doesnt exist, create it 
#and put that question in it.
def add_question(trivia, input_question):
	print(input_question)
	result = ""
	result += input_question.split(",")[0] + "$"
	answers = input_question.split(",")[1:] 
	answers = [ answer.strip() for answer in answers ]
	result += ",".join(answers)
	result += "\n"
	trivia_directory = os.path.dirname(__file__)
	trivia_file = os.path.join(trivia_directory, 'triviagames/'+ trivia.lower() + ".txt")
	with open(trivia_file , "a") as files:
		files.write(result)
	return "Successfully added question to trivia " + trivia.lower()


#Lists all questions for a given trivia
def list_questions(trivia):
	trivia_directory = os.path.dirname(__file__)
	trivia_file = os.path.join(trivia_directory, 'triviagames/'+ trivia.lower() + ".txt")
	if search_trivias(trivia.lower()):
		files_read = open(trivia_file, "r")
		result = "All questions in " + trivia.capitalize() + "\n"
		questions = [ line for line in files_read ]
		files_read.close()
		result += "\n".join("{}. {}".format(i, question.split("$")[0]) 
							for i, question in enumerate(questions))
		if questions == []:
			result = "There is currently no questions in trivia " + trivia.capitalize()
	else:
		result = "There is no trivia with name " + trivia.capitalize()
	return result


#Removes a question on the provided trivia on the provided index
#Get the index from list_questions
def remove_question(trivia, question_nr):
	if search_trivias(trivia.lower()):
		trivia_directory = os.path.dirname(__file__)
		trivia_file = os.path.join(trivia_directory, 'triviagames/'+ trivia.lower() + ".txt")
		files_read = open(trivia_file, "r")
		questions = [ line for line in files_read ]
		try:
			del questions[int(question_nr)]
		except IndexError:
			return "Invalid index for trivia " + trivia.capitalize()
		files_read.close()

		open(trivia_file, "w").close()

		files_write = open(trivia_file, "w")
		files_write.writelines(questions)
		files_write.close()
		return "Successfully removed question " + question_nr + " from trivia " + trivia.capitalize()
	else:
		return "There is no trivia named " + trivia.capitalize()


#Removes the trivia
def remove_trivia(trivia):
	trivia_directory = os.path.dirname(__file__)
	trivia_file = os.path.join(trivia_directory, 'triviagames/'+ trivia.lower() + ".txt")
	try:
		os.remove(trivia_file)
		return "Successfully removed trivia " + trivia.capitalize()
	except OSError:
		return "There is no trivia with name " + trivia.capitalize()
