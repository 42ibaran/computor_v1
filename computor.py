import re
import math
import argparse

from customErrors import MalformedEquationError
from messages import *

# Bonuses:
# Support of natural form
# Irrational result for special case of second degree
# Output precision parameter

# TODO
# 1. Manage floats without extra decimal places: 1-0.77
# 2. Equation starting with -
# 3. Check if sign parsing is tots ok 
# spaces between numbers = error
# check reduced form again
# think about +- and -+
# complex numbers - VERIFY

INPUT_PRECISION = 12
outputPrecision = 10

handleImaginary = False

powerCoefficients = {0:0.0}

# Regex groups indexes
# 0 - full match
# 1 - = or None
# 2 - sign (None = positive)
# 3 - sign (None = positive)
# 4 - coefficient (None = 1)
# 5 - decimal point (None = Int)
# 6 - X (None = X^0)
# 7 - power of X (None = 1)

def outputRound(value):
    return round(value, outputPrecision) if not value.is_integer() and outputPrecision != 0 else round(value)

def executeRegex(equation):
    r = re.compile(r"(?:(?:(?:^|(=))([+-])?)|([+-]))(?:((?:\d+)(\.\d+)?)(?:\*)?)?(?:(X)?(?:\^([+-]?\d+))?)?", re.I)
    argument = equation.replace(' ', '')
    unmatched = r.sub('', argument)
    isIncomplete = len(argument) == 0 or argument.find("=") == -1 or argument[0] == '=' or argument[-1] == '='

    if len(unmatched) != 0 or isIncomplete:
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
        isPositive = True if (sign == '+' and isLeft == True) or (sign == '-' and isLeft == False) else False

        isFreeCoefficient = True if isX == None else False
        if not isFreeCoefficient:
            powerOfX = int(power) if power != None else 1
        else:
            powerOfX = 0
        
        coefficient = float(coeff) if coeff != None else 1.0
        coefficient *= 1 if isPositive else -1

        if powerOfX not in powerCoefficients:
            powerCoefficients[powerOfX] = 0
        powerCoefficients[powerOfX] += coefficient

    filtered = {x: round(y, INPUT_PRECISION) for x, y in sorted(powerCoefficients.items()) if x == 0 or y != 0}
    powerCoefficients.clear()
    powerCoefficients.update(filtered)

def getDegree():
    degrees = powerCoefficients.keys()
    return max(degrees)

def printReducedForm():
    if len(powerCoefficients) == 1 and powerCoefficients[0] == 0:
        result = "0"
    else:
        result = ""
    for power in range(getDegree() + 1):
        coefficient = powerCoefficients[power] if power in powerCoefficients else 0
        printedCoefficient = coefficient if coefficient >= 0.0 else -coefficient
        if coefficient < 0:
            result += " - " if result != "" else "-"
        else:
            result += " + " if result != "" else ""
        result += "%s * X^%d" % (printedCoefficient, power)
    result += ' = 0'
    print("Reduced form: " + result)

def solveDegree0():
    if powerCoefficients[0] == 0:
        print(SOLUTION_IS_ALL)
    else:
        print(SOLUTION_IS_NONE)

def solveDegree1():
    if powerCoefficients[1] == 0:
        solveDegree0()
        return
    else:
        x = -powerCoefficients[0] / powerCoefficients[1]
    x = outputRound(x)
    print("The solution is:", round(x, outputPrecision), sep="\n")

def solveDegree2Special():
    print(SPECIAL_CASE_DEGREE_2)
    fraction = -powerCoefficients[0] / powerCoefficients[2]
    if fraction < 0:
        print(SOLUTION_IS_NONE)
        return
    x = math.sqrt(fraction)
    print("Solution%s %s:" % (("", "is") if x == 0 else ("s", "are")))
    if not x.is_integer():
        print("±√%s" % outputRound(fraction), "or", sep="\n")
    x = outputRound(x)
    print("%s%s" % (("" if x == 0 else "±"), x))

def solveDegree2():
    if 1 not in powerCoefficients:
        powerCoefficients[1] = 0
        solveDegree2Special()
        return

    discriminant = (powerCoefficients[1] ** 2) - 4 * powerCoefficients[0] * powerCoefficients[2]
    discriminantString = "Discriminant = %s" % outputRound(discriminant)
    if discriminant > 0:
        discriminantString += ", strictly positive, the two solutions are:"
        sqrtD = math.sqrt(discriminant)
        x1 = (-powerCoefficients[1] + sqrtD) / (2 * powerCoefficients[2])
        x2 = (-powerCoefficients[1] - sqrtD) / (2 * powerCoefficients[2])
        x1 = outputRound(x1)
        x2 = outputRound(x2)
        print(discriminantString, x1, x2, sep="\n")
    elif discriminant == 0:
        discriminantString += ", is zero, one solution:"
        x = -powerCoefficients[1] / (2 * powerCoefficients[2])
        x = outputRound(x)
        print(discriminantString, x, sep="\n")
    else:
        discriminantString += ", strictly negative" + (", no real solutions" if not handleImaginary else ". Complex solutions are:")
        if handleImaginary:
            sqrtD = math.sqrt(-discriminant)
            a = -powerCoefficients[1] / (2 * powerCoefficients[2])
            b = sqrtD / (2 * powerCoefficients[2])
            print(discriminantString)
            print(outputRound(a), " ± ", outputRound(b), "i", sep="")
        else:
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

parser = argparse.ArgumentParser(prefix_chars='@')
parser.add_argument("equation", metavar="equation", type=str, help="example: " + EQUATION_EXAMPLE)
parser.add_argument("@p", metavar="precision", type=int, help="precision for result output")
parser.add_argument("@i", action="store_true", help="handle complex results")

args = parser.parse_args()

if args.p is not None:
    outputPrecision = args.p

if args.i is True:
    handleImaginary = True

try:
    iterator = executeRegex(args.equation)
    simplify(iterator)
except MalformedEquationError:
    print(MALFORMED_EQUATION)
    exit(1)

printReducedForm()
solve()
