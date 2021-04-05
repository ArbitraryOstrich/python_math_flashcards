import numpy as np
import pandas as pd 
import calplot 
import matplotlib.pyplot as plt
import pickle
import os.path
from os import path
from random import randrange
# from tabulate import tabulate
from prettytable import PrettyTable 
from argparse import ArgumentParser
## https://stackoverflow.com/questions/3756278/timing-recording-input-in-python-3-1
import time

def timed_input(prompt):
    start = time.time()
    s = input(prompt)
    return s, time.time() - start

def gen_date_str():
    ## When does your day end?
    dayend_offset_hours = '3'
    from datetime import datetime, timedelta
    datestr = datetime.now()
    datestr = datestr - timedelta(hours = int(dayend_offset_hours)) 
    datestr = str(datestr)
    datestr = datestr[0:-7]
    return datestr

def rand_num_by_len(length=2):
    top = 10**length
    return randrange(1,top)

## Ideally this program will produce various math problems to work on.
## Addition
## Subtraction
## Multiplication
## Division

## It will then Keep track of those problems in some data base and provide Report cards based on the answers provided by the user.
## Also have two different game types. First being based on the number of problems, second being a rush mode x problems in amount of time.



parser = ArgumentParser()
parser.add_argument(
    "-n",
    "--number_of_problems",
    dest="number_of_problems",
    action="store",
    type=int,
    default=2,
    help="How many problems would you like to see",
)
parser.add_argument(
    "-d",
    "--number_of_digits",
    default=2,
    dest="number_of_digits",
    action="store",
    type=int,
    help="How many digits in each number",
)
parser.add_argument(
    "-t",
    "--type_of_problem",
    dest="type_of_problem",
    action="store",
    type=int,
    default=3,
    help="1 = Addition, 2 = Subtraction, 3 = Multiplication, 4 = Division",
)
# parser.add_argument(
#     "-r",
#     "--problem_rush",
#     dest="problem_rush",
#     action="store",
#     type="int",
#     help="How many answers can you give without getting 3 wrong in X amount of time",
# )


x = PrettyTable()
x.field_names =  [ "problem_number","first","second","Answer","Input","Time Taken","Result" ]



problem_index = {}
args = parser.parse_args()
correct = 0
total_time = 0

datestr = gen_date_str()


if args.type_of_problem == 3:
    print("Game type: Multiplication")
    
elif args.type_of_problem == 4:
    print("Game type: Division")
    print("No decimal places at the moment, will add later.")

elif args.type_of_problem == 1:
    print("Game type: Addition")

elif args.type_of_problem == 2:
    print("Game type: Subtraction")




for problem_number in range(0,args.number_of_problems):
    numbers = [rand_num_by_len(args.number_of_digits),rand_num_by_len(args.number_of_digits)]
    ## This is ugly but it allows for us to get zero padded digits.
    print(f'{numbers[0]}'.zfill(args.number_of_digits) + '\n' + f'{numbers[1]}'.zfill(args.number_of_digits) )

    if args.type_of_problem == 3:
        correct_answer = numbers[0]*numbers[1]
    elif args.type_of_problem == 4:
        correct_answer = int(numbers[0]/numbers[1])
    elif args.type_of_problem == 1:
        correct_answer =  numbers[0]+numbers[1]
    elif args.type_of_problem == 2:
        correct_answer =  numbers[0]-numbers[1]




    s, thetime = timed_input('Answer?: ')

    if int(s) == correct_answer:
        print('Correct!')
        mark = "Correct"
        correct += 1
    else:
        print('Incorrect! Answer was: {}'.format(correct_answer))
        mark = "Incorrect"
    problem_index[problem_number] = [problem_number,numbers[0],numbers[1],correct_answer,s,str(thetime)[0:5],mark ]
    x.add_row([problem_number,numbers[0],numbers[1],correct_answer,s,str(thetime)[0:5],mark ])


    total_time += thetime
problem_index['summary']= f'Got {correct} out of {args.number_of_problems}. in {total_time:02.2f} Seconds, which is {total_time/60:02.2f} minutes total and {(total_time)/args.number_of_problems:02.2f} seconds per problem  {(correct/args.number_of_problems)*100}%'
print(x)
print(problem_index['summary'])

pickle.dump(problem_index[problem_number], open(datestr + ".p", "wb" ) )


