#!/usr/bin/python3

""" Filip Dobrovolny (c) 2015 GNU GPL 3.0 https://github.com/BrnoPCmaniak/turing_simulator"""
import sys

""" 
Usage: turing.py prog.txt
Example of code 
# sum two bin on 0,1 to bits 2,3
1 1 # initial tape
$A: # state A
0 -> 0 1r B # if 0 under head then write 0 and move head one to right and move to state B
1 -> 1 1r C
$B:
0 -> 0 2r Zero
1 -> 1 2r One
$C:
0 -> 1 2r One
1 -> 1 1r One
$Zero:
* -> 0 0r HALT
$One:
* -> 1 0r HALT
$HALT: # End of program State 
HALT # End of Program Instruction

"""

class instruction(object):
    def __init__(self, symbol, write, move, nextState):
        self.other = False
        if symbol == "*":
            self.other = True
            self.symbol = None
        else:
            self.symbol = int(symbol)
        self.write = int(write)
        self.move = int(move[:-1])
        self.direction = move[-1]
        self.strNextState = nextState
        self.nextState = None

    def has_occoured(self, symbol):
        return symbol == self.symbol or self.other

    def execute(self, tape):
        tape.write(self.write)
        tape.move(self.move, self.direction)
        return self.nextState

    def linkState(self, dict):
        try:
            self.nextState = dict[self.strNextState]
        except:
            print("ERROR: State \"" + self.strNextState + "\" does not exists")
            sys.exit(1)

class State(object):
    def __init__(self, text):
        rows = text.split("\n")
        self.name = rows[0][:rows[0].find(":")].strip()
        self.is_halt = False
        self.instructions = []
        for row in rows[1:]:
            self.parseRow(row)

    def parseRow(self, row):
        row = row.strip()
        if row == "":
            return
        if row == "HALT":
            self.is_halt = True
        else:
            inst = row.split(" ")
            if inst[1] != "->":
                return
            else:
                self.instructions.append(instruction(inst[0], 
                                                     int(inst[2]),
                                                     inst[3],
                                                     inst[4]))
    def execute(self, symbol, tape):
        if self.is_halt: return False
        inst = None
        for i in self.instructions:
            if i.has_occoured(symbol):
                inst = i
        if inst == None:
            print("ERROR: instraction is not defined for this symbol")
            sys.exit(1)
        return inst.execute(tape)

    def linkInst(self, dict):
         for i in self.instructions:
             i.linkState(dict)


class Tape(object):
    def __init__(self, tape=[0]):
        self.tape = tape
        self.len = len(self.tape) - 1
        self.pos = 0

    def moveRight(self):
        self.pos += 1
        if self.pos > self.len:
            self.tape.append(0)
            self.len = len(self.tape) - 1

    def moveLeft(self):
        self.pos -= 1
        if self.pos < 0:
            print("ERROR: Out of tape")
            sys.exit(1)

    def move(self, dist, dir):
        if dir == "l":
            for i in range(dist):
                self.moveLeft()
        elif dir == "r":
            for i in range(dist):
                self.moveRight()
        else:
            print("ERROR: Invalid move \"" + dir + "\"")
            sys.exit(1)

    def write(self, symbol):
        self.tape[self.pos] = symbol

    def read(self):
        return self.tape[self.pos]

    def __str__(self):
        return str(self.tape)

# Arguments
if len(sys.argv) == 1:
    print("  usage: ./turing.py FILE\n\nInterpreter for Turing machine\nFilip Dobrovolny (c) 2015 GNU GPL 3.0 https://github.com/BrnoPCmaniak/turing_simulator")
    sys.exit(0)
if len(sys.argv) > 2:
    print("ERROR: Too much arguments")
    sys.exit(1)
with open(sys.argv[1], "r") as f:
    plain = f.read()


# split states

plain = plain.replace("\t", " ") # tabs -> spaces

while(plain.find("  ") != -1): # multiple spaces -> space
    plain = plain.replace("  ", " ")

while(plain.find("\n\n") != -1): #multiple empty lines -> line
    plain = plain.replace("\n\n", "\n")

#Crop comments
plain = plain.split("\n")
del_list = []
for i in range(len(plain)):
    if "#" in plain[i]:
        plain[i] = plain[i][:plain[i].find("#")]
    if plain[i].strip() == "":
        del_list.append(plain[i])

for i in del_list:
    plain.remove(i)

plain = "\n".join(plain)

if "$" in plain[:plain.find("\n")] or plain[:plain.find("\n")].strip() == "":
    init_tape = [0]
else:
    init_tape = plain[:plain.find("\n")].split(" ")

del_list = []
for i in range(len(init_tape)):
    try:
        init_tape[i] = int(init_tape[i])
    except:
        del_list.append(init_tape[i])

for i in del_list:
    init_tape.remove(i)

if len(init_tape) == 0:
    init_tape = [0]
states = plain[plain.find("\n")+1:].split("$")

statesObjs = []
MainDict = {"HALT" : False}
tape = Tape(init_tape)
for i in states:
    if i != "":
        obj = State(i)
        MainDict[obj.name] = obj
        statesObjs.append(obj)

for i in statesObjs:
    i.linkInst(MainDict)

curr = statesObjs[0]
print("START:", tape)
while curr != False:
    print(curr.name, end=": ")
    curr = curr.execute(tape.read(), tape)
    print(tape)

