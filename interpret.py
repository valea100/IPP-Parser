import sys
import re
import xml.etree.ElementTree as ET

class Frame:
    def __init__(self) -> None:
        self.local_vars = {}

    def define_variable(self, variable):
        if variable not in self.local_vars:
            self.local_vars[variable] = None  # vytvoreni promenne
        else:
            print("predefinovani promenne chyba 52")
            exit(52)


class Interpret:

    def __init__(self):
        self.vars = set()

        # interpret variables
        self.frames = []
        self.xmlFile = None
        self.inputFile = None


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

    # argumenty
    def parse_arguments(self):
        args_list = sys.argv

        if len(args_list) > 3:
            print("Max number of arguments is 2")
            exit(30)  # TODO zmenit na spravnej error code
        pass

        for myArg in args_list:
            if myArg == "--help":
                self.print_help()
                exit(0)
            elif re.match("^--file=[a-zA-z0-9\.]+$", myArg):
                # xml file
                print("found xml file")
                filename = re.split("=", myArg)[1]
                self.xmlFile = open(filename, "r")
            elif re.match("^--input=[a-zA-z0-9\.]*$", myArg):
                # input file, nebo rovnou prikazy
                print("found input file")
                filename = re.split("=", myArg)[1]
                self.inputFile = open(filename, "r")
    
    def parse_source_file(self):
        pass


#testing
myInterpret = Interpret()
myInterpret.parse_arguments()