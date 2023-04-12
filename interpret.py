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
        self.todo = {}

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
            # TODO zmenit na spravny error code
            self.print_error(
                "Sorry neni zadan xml soubor, ani input file.", 30)
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
        # test vypis
        for child in xmlRoot:
            print(child.tag, child.attrib)

        # kontrola language typu
        if xmlRoot.get('language') != 'IPPcode23':
            self.print_error("spatny typ jazyka", 32)

        # parsovani instrukci
        for instruction in xmlRoot.findall('instruction'):
            self.parse_instruction(instruction)
        return

    def parse_instruction(self, instruction):
        if 'order' in instruction.attrib and 'opcode' in instruction.attrib and len(instruction.attrib) == 2:
            arguments = {'arg1': None, 'arg2': None, 'arg3': None}
            for arg in instruction:
                # TODO kontrola atributu ve funkci do urcite miry
                if not (len(arg.keys()) == 1 and 'type' in arg.keys()):
                    self.print_error("wrong arg attribute", 32)

                try:
                    if arguments[arg.tag] is None:
                        arguments[arg.tag] = (arg.get('type'), arg.text)
                    else:
                        self.print_error("redefinice argumentu", 32)
                except:
                    self.print_error("Spatny subelement instrukce", 32)

            if arguments['arg3'] is not None:
                if arguments['arg2'] is not None:
                    if arguments['arg1'] is None:
                        self.print_error("wrong argument index", 32)
                else:
                    self.print_error("wrong argument index", 32)
            if arguments['arg2'] is not None and arguments['arg1'] is None:
                self.print_error("wrong argument index", 32)

            key = instruction.attrib['order']
            to_execute = (instruction.attrib['opcode'], arguments)

            if key in self.todo:
                self.print_error("vice instrukci se stejnym order", 32)
            self.todo[key] = to_execute
        else:
            self.print_error("Spatne atributy u instrukce", 31)

    def check_execute_order(self):
        for key in self.todo.keys():
            if int(key) not in range(1, len(self.todo)+1):
                self.print_error("spatne poradi Instrukci", 32)
    
    def execute(self):
        self.check_execute_order()
        pass
    

    
    def check_operand(self, expected_type, var, err=True):
        var_type = var[0]
        ret = None
        if var_type not in expected_type:
            self.print_error("Špatný typ operandů", 53)
        variable = var[1]
        if var_type == 'var':
            ret = re.match(r'(GF|LF|TF)@([_\-$&%*!?a-zA-Z]+[_\-$&%*!?a-zA-Z0-9]*)', variable)
            if ret is None:
                self.print_error("Špatný formát <var>", 32)
            frame = ret.group(1)
            value = ret.group(2)
            return frame, value
        
        else:
            if var_type == 'string':
                ret = re.match(r'(\S)*', variable)
            elif var_type == 'int':
                ret = re.match(r'-?[0-9]+', variable)
            elif var_type == 'bool':
                ret = re.match(r'true$|false$', variable, re.IGNORECASE)
            elif var_type == 'nil':
                ret = re.match(r'nil$', variable)
            elif var_type == 'label':
                ret = re.match(r'(\S)+', variable)
            else:
                self.print_error("Špatný typ operandu.", 53)
            
            if ret is None:
                if err:
                    self.print_error("Špatný formát proměnné.", 32)
                else:
                    return var_type, ""     #promenna bez hodnoty
                    
            else:
                value = ret.string
                return var_type, value
    
    @staticmethod
    def check_bool(value):
        if re.match(r'true$', value, re.IGNORECASE):
            return True
        elif re.match(r'false$', value, re.IGNORECASE):
            return False
        else:
            return value
    

# testing
myInterpret = Interpret()
myInterpret.parse_arguments()
myInterpret.parse_source_file()
