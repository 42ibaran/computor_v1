import re
import sys
import math
import argparse

from customErrors import *
from messages import *

# TODO
# 1. Manage floats without extra decimal places

powerCoefficients = {}

# Regex groups indexes
# 0 - full match
# 1 - = or None
# 2 - sign (None = positive)
# 3 - sign (None = positive)
# 4 - coefficient (None = 1)
# 5 - decimal point (None = Int)
# 6 - X (None = X^0)
# 7 - power of X (None = 1)

def executeRegex(equation):
    r = re.compile(r"(?:(?:(?:^|(=))([+-])?)|([+-]))(?:((?:\d+)(\.\d+)?)(?:\*)?)?(?:(X)?(?:\^([+-]?\d+))?)?", re.I)
    argument = equation.replace(' ', '')
    unmatched = r.sub('', argument)
    halfIsMissing = (argument[0] == '=' or argument[-1] == '=')

    if len(unmatched) != 0 or halfIsMissing:
        raise MalformedEquationError()

    iterator = r.finditer(argument)
    return iterator

def simplify(iterator):
    isLeft = True
    for match in iterator:
        equal = match.group(1)
        sign1 = match.group(2)
        sign2 = match.group(3)
        coeff = match.group(4)
        decimal = match.group(5)
        isX = match.group(6)
        power = match.group(7)

        if coeff == None and isX == None:
            raise MalformedEquationError()

        if equal != None:
            if isLeft:
                isLeft = False
            else:
                raise MalformedEquationError()

        sign = sign1 or sign2
        sign = '+' if sign == None else sign
        isPositive = True if sign == '+' and isLeft == True else False

        isFreeCoefficient = True if isX == None else False
        if not isFreeCoefficient:
            powerOfX = int(power) if power != None else 1 # TODO handle float power
        else:
            powerOfX = 0
        
        if coeff == None:
            coefficient = 1
        elif decimal != None:
            coefficient = float(coeff)
        else:
            coefficient = int(coeff)

        if powerOfX not in powerCoefficients:
            powerCoefficients[powerOfX] = 0
        powerCoefficients[powerOfX] += coefficient if isPositive else -coefficient

def printReducedForm():
    if len(powerCoefficients) == 1 and powerCoefficients[0] == 0:
        result = "0"
    else:
        result = ""
    for power, coefficient in powerCoefficients.items():
        if coefficient != 0.0:
            printedCoefficient = coefficient if coefficient > 0 else -coefficient
            if result != "":
                result += ' + ' if coefficient >= 0.0 else ' - '
            result += "%s * X^%d" % (printedCoefficient, power)
    result += ' = 0'
    print("Reduced form: " + result)

def getDegree():
    degrees = powerCoefficients.keys()
    return max(degrees)

def solveDegree0():
    if powerCoefficients[0] == 0:
        print(SOLUTION_IS_ALL)
    else:
        print(SOLUTION_IS_NONE)

def solveDegree1():
    x = -powerCoefficients[0] / powerCoefficients[1]
    print("The solution is:", x, sep="\n")

def solveDegree2():
    if 1 not in powerCoefficients:
        powerCoefficients[1] = 0
    discriminant = (powerCoefficients[1] ** 2) - 4 * powerCoefficients[0] * powerCoefficients[2]
    discriminantString = "Discriminant = %s" % (discriminant)
    if discriminant > 0:
        discriminantString += ", strictly positive, the two solutions are:"
        sqrtD = math.sqrt(discriminant)
        x1 = (-powerCoefficients[1] + sqrtD) / (2 * powerCoefficients[2])
        x2 = (-powerCoefficients[1] - sqrtD) / (2 * powerCoefficients[2])
        print(discriminantString, x1, x2, sep="\n")
    elif discriminant == 0:
        discriminantString += ", is zero, one solution:"
        x = - powerCoefficients[1] / (2 * powerCoefficients[2])
        print(discriminantString, x, sep="\n")
    else:
        discriminantString += ", strictly negative, no real solutions"
        print(discriminantString)

def solve():
    degree = getDegree()
    print("Polynomial degree: %d" % (degree))
    if degree == 0:
        solveDegree0()
    elif degree == 1:
        solveDegree1()
    elif degree == 2:
        solveDegree2()
    else:
        print(DEGREE_TOO_HIGH)

parser = argparse.ArgumentParser()
parser.add_argument("equation", metavar="Equation", type=str)
parser.add_argument("-p", metavar="Precision", type=int)

args = parser.parse_args()

try:
    iterator = executeRegex(args.equation)
    simplify(iterator)
except MalformedEquationError:
    print(MALFORMED_EQUATION)
    exit(1)

printReducedForm()
solve()
