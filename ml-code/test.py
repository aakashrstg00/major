import argparse
parser = argparse.ArgumentParser()
parser.add_argument('pathjson',type=str, help='path to filename')
args = parser.parse_args()
print(args.pathjson)