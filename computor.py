import re
import argparse
import logging as log

from customErrors import *

# Bonuses:
# Support of free form
# Output precision parameter [@p precision]
# Result as complex numbers for D<0 [@i]
# Repeating degrees

EQUATION_EXAMPLE = """1 * X + 5X^1 + 9.3 * X^2 = -5"""

MAX_DEGREE = 100
SQRT_MAX_ITER = 70
WARN_INPUT_COEFF_LEN = 11
MAX_OUTPUT_COEFF_LEN = 11
INPUT_PRECISION = 14
outputPrecision = 10

handleComplex = False

powerCoefficients = {0:0.0}

log.basicConfig(format='%(levelname)s: %(message)s', level=log.WARN)

def outputRound(value):
    value = value if not value.is_integer() and outputPrecision != 0 else round(value)
    return round(value, outputPrecision) if len(str(int(value))) <= MAX_OUTPUT_COEFF_LEN and (fabs(value) > 0.1 ** outputPrecision or value == 0) else format(value, ".%de" % outputPrecision)

def inputRound(value):
    value = value if not value.is_integer() else round(value)
    return round(value, INPUT_PRECISION) if len(str(int(value))) <= MAX_OUTPUT_COEFF_LEN and (fabs(value) > 0.1 ** INPUT_PRECISION or value == 0) else format(value, ".%de" % outputPrecision)

def fabs(n):
    return -n if n < 0 else n

def sqrt(n, min=0, max=0, iter=0):
    if n < 0:
        raise ValueError("Cannot solve square root of a negative number.")
    if max == 0 and n != 0:
        max = n // 2 + 1
    middle = (max - min) / 2 + min
    accuracyIncrease = len(str(n))
    if iter > SQRT_MAX_ITER + accuracyIncrease or middle * middle == n:
        return middle
    elif middle * middle > n:
        return sqrt(n, min=min, max=middle, iter=(iter + 1))
    else:
        return sqrt(n, min=middle, max=max, iter=(iter + 1))

# Regex groups indexes
# 0 - full match
# 1 - = or None
# 2 - sign (None = positive)
# 3 - sign (None = positive)
# 4 - coefficient (None = 1)
# 5 - X (None = X^0)
# 6 - power of X (None = 1)

def executeRegex(equation):
    if re.search(r"\d\s+\.?\d", equation):
        raise MalformedEquationError("Equation contains whitespaces inside numeric values.")
    equation = re.sub(r"\s", '', equation)

    r = re.compile(r"(?:(?:(?:^|(=))([+-])?)|([+-]))(?:((?:\d+)(?:\.\d+)?)(?:\*)?)?(?:(X)?(?:\^?(\d+))?)?", re.I)
    unmatched = r.sub('', equation)
    isIncomplete = len(equation) == 0 or equation.find("=") == -1 or equation[0] == '=' or equation[-1] == '='

    if len(unmatched) != 0:
        raise MalformedEquationError("Equation contsins syntax errors.")
    elif isIncomplete:
        raise MalformedEquationError("Equation is empty or incomplete.")

    iterator = r.finditer(equation)
    return iterator

def simplify(iterator):
    isLeft = True
    for match in iterator:
        equal = match.group(1)
        sign1 = match.group(2)
        sign2 = match.group(3)
        coeff = match.group(4)
        isX = match.group(5)
        power = match.group(6)

        if (coeff is None and isX is None) or (coeff is not None and isX is None and power is not None):
            raise MalformedEquationError("A member of the polynomial is invalid.")

        if equal is not None:
            if isLeft:
                isLeft = False
            else:
                raise MalformedEquationError("Equation contains multiple equal signs.")

        sign = sign1 or sign2
        sign = '+' if sign is None else sign
        isPositive = True if (sign == '+' and isLeft == True) or (sign == '-' and isLeft == False) else False

        isFreeCoefficient = True if isX is None else False
        if not isFreeCoefficient:
            powerOfX = int(power) if power is not None else 1
        else:
            powerOfX = 0

        if len(coeff) > WARN_INPUT_COEFF_LEN:
            log.warning("One of provided coefficients is long, solution(s) might be inaccurate.")
        
        coefficient = float(coeff) if coeff is not None else 1.0
        if coefficient == float("inf"):
            raise ValueError("One of provided coefficients is infinity, can't solve.")
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
    degree = getDegree()

    if degree > MAX_DEGREE:
        raise DegreeTooHighError("Degree of provided equation is too high to print reduced form or solve.")

    result = ""
    for power in range(degree + 1):
        coefficient = powerCoefficients[power] if power in powerCoefficients else 0.0
        printedCoefficient = coefficient if coefficient >= 0 else -coefficient
        if coefficient < 0:
            result += " - " if result != "" else "-"
        else:
            result += " + " if result != "" else ""
        result += "%s * X^%d" % (inputRound(printedCoefficient), power)
    result += ' = 0'
    print("Reduced form: " + result)

def solveDegree0():
    if powerCoefficients[0] == 0:
        print("Solution is every real number.")
    else:
        print("Equation has no solution.")

def solveDegree1():
    if powerCoefficients[1] == 0:
        solveDegree0()
        return
    else:
        x = -powerCoefficients[0] / powerCoefficients[1]
    print("The solution is:", outputRound(x), sep="\n")

def solveDegree2():
    if 1 not in powerCoefficients:
        powerCoefficients[1] = 0

    discriminant = (powerCoefficients[1] ** 2) - 4 * powerCoefficients[0] * powerCoefficients[2]
    discriminantString = "Discriminant = %s" % outputRound(discriminant)

    if discriminant > 0:
        sqrtD = sqrt(discriminant)
        x1 = (-powerCoefficients[1] + sqrtD) / (2 * powerCoefficients[2])
        x2 = (-powerCoefficients[1] - sqrtD) / (2 * powerCoefficients[2])
        discriminantString += ", strictly positive, the two solutions are:"
        if x1 == -x2:
            print(discriminantString, "±%s" % outputRound(max(x1, x2)) if x1 != x2 else outputRound(x1), sep="\n")
        else:
            print(discriminantString, outputRound(x1), outputRound(x2), sep="\n")
    elif discriminant == 0:
        discriminantString += ", is zero, one solution:"
        x = -powerCoefficients[1] / (2 * powerCoefficients[2])
        print(discriminantString, outputRound(x), sep="\n")
    else:
        discriminantString += ", strictly negative" + (", no real solutions" if not handleComplex else ". Complex solutions are:")
        if handleComplex:
            sqrtD = sqrt(-discriminant)
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
        raise DegreeTooHighError("The polynomial degree is greater than 2, I can't solve.")

parser = argparse.ArgumentParser(prefix_chars='@')
parser.add_argument("equation", metavar="equation", type=str, help="example: " + EQUATION_EXAMPLE)
parser.add_argument("@i", action="store_true", help="handle complex results")
parser.add_argument("@p", metavar="precision", type=int, help="precision for result output (>=0)")

args = parser.parse_args()

if args.p is not None:
    if args.p < 0:
        parser.error("Precision value cannot be negative")
    outputPrecision = args.p

if args.i is True:
    handleComplex = True

try:
    iterator = executeRegex(args.equation)
    simplify(iterator)
except (MalformedEquationError, ValueError) as e:
    log.error(e)
    exit(1)

try:
    printReducedForm()
    solve()
except DegreeTooHighError as e:
    log.error(e)
    exit(1)
