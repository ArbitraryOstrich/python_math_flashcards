import numpy as np
import pandas as pd
import calplot
import matplotlib.pyplot as plt
import pickle
import os.path
from os import path
from random import randrange, choice

# from tabulate import tabulate
from prettytable import PrettyTable
from argparse import ArgumentParser

## https://stackoverflow.com/questions/3756278/timing-recording-input-in-python-3-1
import time
import datetime


from tinydb import Query, TinyDB, where
from tinydb.operations import delete
from pathlib import Path
import pandas as pd


## TODO: Fix up database sytem move from pickle to tinydb
## ----- Makes single DB file.
## TODO: Use new database system to generate Progress reports
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
    help="1 = Addition, 2 = Subtraction, 3 = Multiplication, 4 = Division, 5 = mix add/sub",
)
# parser.add_argument(
#     "-r",
#     "--problem_rush",
#     dest="problem_rush",
#     action="store",
#     type="int",
#     help="How many answers can you give without getting 3 wrong in X amount of time",
# )

parser.add_argument(
    "-pa",
    "--averages",
    nargs="*",
    dest="print_averages",
    action="store",
    help="Print the progress for a day",
)

parser.add_argument(
    "-pd",
    "--dates_average",
    nargs=2,
    metavar=("start_date", "end_date"),
    dest="dates_average",
    action="store",
    help="Print the average times between two dates",
)

parser.add_argument(
    "-pr",
    "--report_range",
    nargs="?",
    const="10",
    dest="averages_days",
    action="store",
    help="Print the average time for a x days",
)


def open_db():
    home = str(Path.home())
    local_storage = home + "/.local/share/math_flash"
    try:
        # Create target Directory
        os.mkdir(local_storage)
        # print("Directory ", local_storage, " Created ")
    except FileExistsError:
        # print("Directory ", local_storage, " already exists")
        pass

    db = TinyDB(local_storage + "/db.json")
    db.DEFAULT_TABLE = "math_flash_table"
    d_Query = Query()
    data = db.all()
    return db, d_Query


def timed_input(prompt, start=0):
    if start == 0:
        start = time.time()
    s = input(prompt)
    try:
        s = int(s)
        return s, time.time() - start
    except ValueError:
        print("Please input int's only \n")
        s = ""
        ## .... recursive returns you say?
        return timed_input(prompt, start)


def gen_date_str():
    ## When does your day end?
    dayend_offset_hours = "3"
    from datetime import datetime, timedelta

    datestr = datetime.now()
    datestr = datestr - timedelta(hours=int(dayend_offset_hours))
    datestr = str(datestr)
    timestr = datestr[11:-7]
    datestr = datestr[0:-16]
    return datestr, timestr


def rand_num_by_len(length=2):
    top = 10 ** length
    return randrange(1, top)


def print_day_average(db, d_Query, datestr):

    try:
        days_results = db.get(d_Query.date == datestr)
    except:
        print(f"No data for {datestr}")
        return None

    if days_results is not None:
        print("-------------")
        print(datestr)
        times = {"1": [], "2": [], "3": [], "4": []}
        for a in range(0, len(days_results["iterations"])):
            for b in range(0, len(days_results["iterations"][a]["results"])):
                problem_type = int(days_results["iterations"][a]["results"][f"{b}"][1])
                time_taken = float(days_results["iterations"][a]["results"][f"{b}"][6])
                times[f"{problem_type}"].append(time_taken)

        for a in range(1, 5):
            if len(times[f"{a}"]) != 0:
                avg_time = sum(times[f"{a}"]) / len(times[f"{a}"])
                print(f" Problem type: {a} Average Time: {avg_time}")
    else:
        print(f"{datestr} has no data")


def print_range(db, d_Query, start_date, end_date):
    date_range = pd.date_range(start_date, end_date, freq="d")
    for date in date_range:
        # Format each date
        date = str(date)
        date = date[0:10]
        # date = date.replace('-','')
        print_day_average(db, d_Query, date)


def save_results(db, d_Query, problem_index, datestr, timestr):
    if db.get(d_Query.date == datestr):
        temp_storage = db.get(d_Query.date == datestr)
        temp_storage["iterations"].append(
            {"timestamp": timestr, "results": problem_index}
        )
        db.update(
            {"date": datestr, "iterations": temp_storage["iterations"]},
            d_Query.date == datestr,
        )
    else:
        db.insert(
            {
                "date": datestr,
                "iterations": [{"timestamp": timestr, "results": problem_index}],
            }
        )


## Correct_answer shouldnt be returning the problem type or the numbers?
def correct_answer(typ, num1, num2):
    if typ == 3:
        print("Problem type: Multiplication")
        answer = num1 * num2
    elif typ == 4:
        print("Problem type: Division")
        print("No decimal places at the moment, will add later.")
        answer = int(num1 / num2)
    elif typ == 1:
        print("Problem type: Addition")
        ## Maybe do a reordering such that no negative answers
        answer = num1 + num2
    elif typ == 2:
        print("Problem type: Subtraction")
        answer = num1 - num2
    elif typ == 5:
        print("Problem type: Mixed")
        ## yay recursion
        typ, num1, num2, answer = correct_answer(choice((1, 2)), num1, num2)
    elif typ == 6:
        print("Problem type: base10 to binary")
        answer = format(num1, "b")
    elif typ == 7:
        print("Problem type: binary to base10")
        answer = num1
    return typ, num1, num2, answer


def show_problems(db, d_Query):
    total_time = 0
    correct = 0
    for problem_number in range(0, args.number_of_problems):
        numbers = [
            rand_num_by_len(args.number_of_digits),
            rand_num_by_len(args.number_of_digits),
        ]
        if args.type_of_problem == 6:
            ## This is ugly but it allows for us to get zero padded digits.
            print(f"{numbers[0]}".zfill(args.number_of_digits))

            problem_type, num1, num2, answer = correct_answer(
                args.type_of_problem, numbers[0], 0
            )
        elif args.type_of_problem == 7:
            print(format(numbers[0], "b"))

        else:
            print(
                f"{numbers[0]}".zfill(args.number_of_digits)
                + "\n"
                + f"{numbers[1]}".zfill(args.number_of_digits)
            )

        problem_type, num1, num2, answer = correct_answer(
            args.type_of_problem, numbers[0], numbers[1]
        )

        s, thetime = timed_input("Answer?: ")
        print(s)
        print(answer)
        if int(s) == int(answer):
            print("Correct!")
            mark = "Correct"
            correct += 1
        else:
            print("Incorrect! Answer was: {}".format(answer))
            mark = "Incorrect"

        problem_index[problem_number] = [
            problem_number,
            problem_type,
            numbers[0],
            numbers[1],
            answer,
            s,
            str(thetime)[0:5],
            mark,
        ]

        x.add_row(
            [
                problem_number,
                problem_type,
                num1,
                num2,
                answer,
                s,
                str(thetime)[0:5],
                mark,
            ]
        )
        total_time += thetime

    save_results(db, d_Query, problem_index, datestr, timestr)
    ## Add summary AFTER putting into the database
    problem_index[
        "summary"
    ] = f"Got {correct} out of {args.number_of_problems}. in {total_time:02.2f} Seconds, which is {total_time/60:02.2f} minutes total and {(total_time)/args.number_of_problems:02.2f} seconds per problem  {(correct/args.number_of_problems)*100}%"
    print(x)
    print(problem_index["summary"])


if __name__ == "__main__":
    datestr, timestr = gen_date_str()
    x = PrettyTable()
    x.field_names = [
        "problem_number",
        "problem_type",
        "first",
        "second",
        "Answer",
        "Input",
        "Time Taken",
        "Result",
    ]
    problem_index = {}
    args = parser.parse_args()
    correct = 0
    total_time = 0
    db, d_Query = open_db()

    if args.print_averages:
        print_day_average(db, d_Query, args.print_averages)
    elif args.averages_days:
        ## pr
        start_date = datetime.datetime.now() - datetime.timedelta(
            days=int(args.averages_days)
        )
        start_date = start_date.strftime("%Y-%m-%d")
        print_range(db, d_Query, start_date, datestr)
    elif args.dates_average:
        ## pd
        print_range(db, d_Query, args.print_averages[0], args.print_averages[1])
    else:
        show_problems(db, d_Query)
