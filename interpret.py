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

    def print_error(self, text, errorCode):
        print(text)
        print("exiting Interpret...")
        exit(errorCode)

    def print_help(self):
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

        elif len(args_list) == 1:
            self.print_help()
            exit(0)
        
        for myArg in args_list:
            if myArg == "--help":
                self.print_help()
                exit(0)
            elif re.match("^--file=[a-zA-z0-9\.]+$", myArg):
                # xml file
                print("found xml file")
                self.xmlFile = re.split("=", myArg)[1]
            elif re.match("^--input=[a-zA-z0-9\.]*$", myArg):
                # input file, nebo rovnou prikazy
                print("found input file")
                self.inputFile = re.split("=", myArg)[1]

            
    def parse_source_file(self):
        xmlRoot, inputFile = None, None
        if (self.xmlFile == None) and (self.inputFile == None):
            self.print_error("Sorry neni zadan xml soubor, ani input file.", 30) #TODO zmenit na spravny error code
        if self.xmlFile != None:
            try:
                xmlTree = ET.parse(self.xmlFile)
            except FileNotFoundError:
                self.print_error("XML file not found.", 30)
            xmlRoot = xmlTree.getroot()
        if self.inputFile != None:
            try:
                inputFile = open(self.inputFile, "r")
            except FileNotFoundError:
                self.print_error("Input file not found.", 30)
        #test vypis
        for child in xmlRoot:
            print(child.tag, child.attrib)
        
        #kontrola language typu
        if xmlRoot.get('language') != 'IPPcode23':
            self.print_error("spatny typ jazyka", 32)

        #parsovani instrukci
        for instruction in xmlRoot.findall('instruction'):
            self.parse_instruction(instruction)
        return

    def parse_instruction(self, instruction):
            if 'order' in instruction.attrib and 'opcode' in instruction.attrib and len(instruction.attrib) == 2:
                arguments = {'arg1': None, 'arg2': None, 'arg3': None}
                for arg in instruction:
                    #TODO kontrola atributu ve funkci do urcite miry
                    pass
#testing
myInterpret = Interpret()
myInterpret.parse_arguments()
myInterpret.parse_source_file()