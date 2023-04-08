import sys
import re

def print_help():
    help_string = """
    Interpret pro jazyk IPPcode23.
    Autor: Jakub Kurka, xkurka06
    Date: 08.04.2023
    Usage:
        --help              =>  vypise tuhle zpravu
        --source=file       =>  vstupni soubor s XML reprezentaci zdrojoveho kodu v jazyce IPPcode23
        --input=file        =>  soubor se vstupy pro samotnou interpretaci zadaneho zdrojoveho kodu  
    """
    print(help_string)
    return 0

#argumenty 
args_list = sys.argv

if len(args_list) > 3:
    print("Max number of arguments is 2")

for myArg in args_list:
    if myArg == "--help":
        print_help()
        exit(0)
    elif re.match("^--file=[a-zA-z0-9\.]+$", myArg):
        #xml file
        print("found xml file")
    elif re.match("^--input=[a-zA-z0-9\.]*$", myArg):
        #input file, nebo rovnou prikazy
        print("found input file")


