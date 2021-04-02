import argparse

parser = argparse.ArgumentParser()
parser.add_argument("equation", type=str)
parser.add_argument("-p")

args = parser.parse_args()
print(args)