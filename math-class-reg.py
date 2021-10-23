#! LEGEND =====================================================================
'''
If you're using VSCode, it's recommended that you install the `Better Comments` extension
>>> aaron-bond.better-comments
as I'm making full use of the comment highlighting to differentiate between different
types of comments within this file. - IQBAL_18001179

#! [NAME] ============...    : Divider

##* [Description here...]   : Function/Object Description

#? [Comment placed here...] : Comment

'''

#! IMPORTS ====================================================================
import json
import random
import threading
import time
from queue import Queue

import numpy as np
import pandas as pd

#! DECLARATION ================================================================
data = json.load(open("data.json"))
studNames = data["students"]
tutNames = data["tutors"]
questions = data["questions"]
topics = data["topics"]

#? Simulation Variables
##* Feel free to change these
numTutors = 3
maxQuestions = 5
simTime = 0
simEnd = 10
studentQs = []
tutorArr = []

for topic in topics:
    studentQs.append(Queue(maxsize=3))

#! UTIL =======================================================================

##* getRandom() is used to generate random numbers without having to type
##* `random.randint` everytime. Includes further support for returning as
##* int or str (isStr is Falsey btw)
def getRandom (upper, isStr=False, lower=0):
    outNum = random.randint(lower, upper)
    if isStr:
        return str(outNum)
    return outNum

##* getID() used to generate a random ID based on the index of the name from
##* `data.json`. Randomness is emphasized to lessen the chances of creating
##* duplicate IDs.
def getID (numIndex):
    id = str(numIndex)

    if numIndex < 10:
        id += getRandom(10, True)
    if numIndex < 100:
        id += getRandom(10, True)
    if numIndex < 1000:
        id += getRandom(10, True)

    return ''.join(random.sample(id, len(id)))

##* getRandomName() used to pick a random student name and ID
def getRandomName(arr, tutId=False):
    numIndex = getRandom(len(arr) - 1)
    nameId = getID(numIndex)
    if tutId:
        nameId = "T-" + nameId
    else:
        nameId = "S-" + nameId
    return { "name": arr.pop(numIndex), "id": nameId  }

#? ↓↓↓ Uncomment to test this util out! :D
# print(getRandomName(studNames))

##* getRandomQuestion() used to pick a random question
def getRandomQuestion():
    return questions[getRandom(len(questions) - 1)]

##* getRandomTopic() used to pick a random topics
def getRandomTopic():
    return topics[getRandom(len(topics) - 1)]

##* getFormatTime() used to retrieve the time within a set format
def getFormatTime(time):
    return "@ (" + str(time) + ":00) "

##* s_print() Thread-safe printing
def s_print(content):
    print("{0}\n".format(getFormatTime(simTime) + content))

#! OBJECTS ====================================================================

#? Tutor Class
##* This is the definition of the tutor class.
class UniversityTutor(threading.Thread):
    def __init__(self, name, tutID, specialty):
        threading.Thread.__init__(self)
        self.name = name
        self.tutID = tutID
        self.specialty = specialty
        self.busy = False
        self.student = None

    def identify(self):
        return self.name + "(" + self.tutID + "; " + str(self.specialty["title"]) + ")"

    def reset(self):
        self.busy = False
        self.student = None

    def run(self):
        while simTime < simEnd:
            # time.sleep(1) # This was commented due to making the simulation too slow

            if self.busy:
                if self.student.status == UniversityStudent.FINISHED:
                    self.reset()
                else:
                    s_print(self.name + " is still consulting " + self.student.name)
            else:
                if not studentQs[self.specialty["id"]].empty():
                    self.student = studentQs[self.specialty["id"]].get()
                    self.busy = True
                    self.student.status = UniversityStudent.CONSULTING
                    s_print(
                        self.identify() +
                        " called " +
                        self.student.identify() + " into their office"
                    )

#? Student Class
##* This is the definition of the student class.

class UniversityStudent(threading.Thread):
    IN_QUEUE = 0
    CONSULTING = 1
    FINISHED = 2

    def __init__(self, name, studID, topic):
        threading.Thread.__init__(self)
        self.name = name
        self.studID = studID
        self.topic = topic
        self.questions = getRandom(5, False, 1)
        self.status = UniversityStudent.IN_QUEUE
    
    def identify(self):
        return self.name + "(" + self.studID + "; " + self.topic["title"] + ")"

    def run(self):
        while simTime < simEnd:
            if self.status == UniversityStudent.IN_QUEUE:
                time.sleep(1)
                continue
            if self.status == UniversityStudent.CONSULTING:
                s_print(self.name + " has " + str(self.questions) + " questions on " + self.topic["title"])
                for i in range(self.questions):
                    # time.sleep(1) # This was commented due to making the simulation too slow
                    if not simTime < simEnd:
                        s_print("Session has ended and " + self.name + " was turned away\n" + str(i) + " questions were answered")
                        break
                    else:
                        s_print(self.name + ", Q" + str(i + 1) + " (" + self.topic["title"] + "):'" + getRandomQuestion() + "'")
                self.status = UniversityStudent.FINISHED

#! SIMULATION =================================================================
#? Definition
studentTotal = 0
studentTotals = []

#? Simulation Loop + Initialization
s_print("SIMULATION STARTED ===================================")

for tutorNum in range(numTutors):
    tempName = getRandomName(tutNames, True)
    tutorObj = UniversityTutor(tempName["name"], tempName["id"], topics[tutorNum])
    tutorArr.append(tutorObj)
    tutorObj.start()
    s_print("Tutor " + tutorObj.identify() + " is beginning their session...")

s_print("Total number of tutors: " + str(len(tutorArr)))

while simTime < simEnd:
    s_print("@@ TIME ELAPSED : " + str(simTime) + ":00 hrs")
    studentQsCopy = []
    numStudents = random.randint(1, maxQuestions)

    for student in range(numStudents):
        tempName = getRandomName(studNames)
        tempTopic = getRandomTopic()
        studObj = UniversityStudent(tempName["name"], tempName["id"], tempTopic)
        studentQs[tempTopic["id"]].put(studObj)
        studObj.start()
        studentQsCopy = studentQs

    tempArr = []
    for i in range(3):
        tempArr.append(studentQsCopy[i].qsize())
        s_print("Queue length for " + topics[i]["title"] + " is: " + str(studentQsCopy[i].qsize()))
    studentTotals.append(tempArr)
    simTime += 1


for tutor in tutorArr:
    tutor.join()

s_print(str(studentTotal) + " students are still waiting in queue...")
if studentTotal > 0:
    s_print("They had to be turned away")
s_print("SIMULATION ENDED; ALL THREADS KILLED =================")

print(np.sum(studentTotals), "students consulted")

df = pd.DataFrame(studentTotals, columns=["Tutor 1", "Tutor 2", "Tutor 3"])
df.to_csv("StudentConsultation.csv")
print("MADE DATA TO CSV")

#! EOF =======================================================================
