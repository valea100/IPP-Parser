import xml.etree.ElementTree as ET
import argparse
from sys import stdin, stderr
import re
from fllib import Frame, Label

types = 'string', 'int', 'bool', 'var'



class Interpret:
    def __init__(self, source, input_f):
        self.labels = Label()
        self.dataTypess = 'string', 'int', 'bool', 'nil', 'var'
        self.to_execute = {}
        self.source = source
        self.input_file = input_f
        self.input = None
        self.frame_stack = []
        self.data_stack = []
        self.frames = {'GF': Frame(), 'LF': None, 'TF': None}
        self.current_order = 1
        self.call_stack = []
    def parse_source_file(self):
        try:
            tree = ET.parse(self.source)
        except ET.ParseError:
            stderr.write('Spatny XML soubor\n')
            exit(31)
        root = tree.getroot()
        language = root.get('language')
        if not language == 'IPPcode23':
            stderr.write('Spatna hlavicka\n')
            exit(32)

        for instruction in root.findall('instruction'):
            self.parse_instruction(instruction)

        if self.input_file is not stdin:
            with open(self.input_file, 'r') as input_file:
                self.input = input_file.read().splitlines()

    def parse_instruction(self, instruction):
        if 'order' in instruction.attrib and 'opcode' in instruction.attrib \
                and len(instruction.attrib) == 2:
            args = {'arg1': None, 'arg2': None, 'arg3': None}
            for arg in instruction:
                if not (len(arg.keys()) == 1 and 'type' in arg.keys()):
                    stderr.write('Spatne atributy argumentu\n')
                    exit(32)
                try:
                    if args[arg.tag] is None:
                        '''text = arg.text.strip()
                        special_char = text.find("\\")
                        if special_char != -1:
                            index = special_char + 1
                            character = ""
                            while text[index] <= '9' and text[index] >= '0':
                                character += text[index]
                                text = text[:index] + text[index+1:]
                            print("found: " + character)
                            character = int(character)
                            character = chr(character)
                            print("znak: +" + character + "+")
                            text[special_char] = character
                            arg.text = text
                         '''       
                        args[arg.tag] = (arg.get('type'), arg.text.strip())
                    else:
                        stderr.write('opakovana definice argumentu\n')
                        exit(32)
                except:
                    stderr.write('spatny prvek\n')
                    exit(32)
            if args['arg3'] is not None:
                if args['arg2'] is not None:
                    if args['arg1'] is None:
                        stderr.write('Spatne poradi argumentu\n')
                        exit(32)
                else:
                    stderr.write('Spatne poradi argumentu\n')
                    exit(32)
            if args['arg2'] is not None and args['arg1'] is None:
                stderr.write('Spatne poradi argumentu\n')
                exit(32)

            key = instruction.attrib['order']
            to_execute = (instruction.attrib['opcode'], args)
            if key in self.to_execute:
                stderr.write('vice instrukci se stejnym ORDER\n')
                exit(32)
            self.to_execute[key] = to_execute
        else:
            stderr.write('spatne atributy instrukce\n')
            exit(31)

    def check_execute_order(self):
        orders = []
        for key in self.to_execute.keys():
            orders.append(key)
        for i in range(0,len(orders)-1):
            if int(orders[i]) >= int(orders[i+1]):
                stderr.write('spatne poradi instrukci\n')
                exit(32)
            else:
                self.to_execute[str(i+1)] = self.to_execute.pop(orders[i])
        self.to_execute[str(len(orders))] = self.to_execute.pop(orders[-1])
        
    def execute(self):
        self.check_execute_order()
        for i in range(2):
            self.current_order = 1
            while self.current_order <= len(self.to_execute):
                opcode = self.to_execute[str(self.current_order)][0]
                opcode = opcode.upper()
                if i == 0:
                    if not opcode == 'LABEL':
                        self.current_order += 1
                        continue
                else:
                    if opcode == 'LABEL':
                        self.current_order += 1
                        continue
                args = [value for key, value in self.to_execute[str(self.current_order)][1].items() if value is not None]

                try:
                    func = getattr(self, opcode)
                except AttributeError:
                    print("opcode: " + opcode)
                    stderr.write('Spatny OPCODE\n')
                    exit(32)
                if not args:
                    try:
                        func()
                    except TypeError:
                        stderr.write('Špatný počet argumentů\n')
                        exit(52)
                else:
                    try:
                        func(*args)
                    except TypeError:
                        stderr.write('Špatný počet argumentů\n')
                        exit(52)
                self.current_order += 1


    @staticmethod
    def push(stack, value):
        stack.append(value)

    @staticmethod
    def pop(stack):
        #kontrola jestli existuje
        if stack:
            return stack.pop()
        else:
            return None

    @staticmethod
    def symbol_check(expected_type, var, err=True):
        varType = var[0]
        varType = varType.strip()
        ret = None
        if varType not in expected_type:
            stderr.write('Spatny typ symbolu\n')
            exit(53)
        variable = var[1]
        variable = variable.strip()
        if varType == 'var':
            ret = re.match(
                r'[ ]*(GF|LF|TF)@([_\-$&%*!?a-zA-Z]+[_\-$&%*!?a-zA-Z0-9]*[ ]*)', variable)
            if ret is None:
                print(variable)
                stderr.write('spatny format var\n')
                exit(32)
            frame = ret.group(1)
            value = ret.group(2)
            return frame, value
        else:
            if varType == 'bool':
                ret = re.match(r'true$|false$', variable, re.IGNORECASE)
            elif varType == 'string':
                ret = re.match(r'(\S)*', variable)
            elif varType == 'int':
                ret = re.match(r'-?[0-9]+', variable)
            elif varType == 'label':
                ret = re.match(r'(\S)+', variable)
            elif varType == 'nil':
                ret = re.match(r'nil$', variable)
            
            else:
                print(varType)
                stderr.write('Spatny typ symbolu\n')
                exit(53)

            if ret is None:
                if err:
                    stderr.write('spatny format var\n')
                    exit(32)
                else:
                    return varType, ""
            else:
                value = ret.string
                return varType, value

    @staticmethod
    def top(stack):
        idk = stack[-1]
        return idk
    


    @staticmethod
    def check_bool(val):
        if re.match(r'true$', val, re.IGNORECASE):
            return True
        elif re.match(r'false$', val, re.IGNORECASE):
            return False
        else:
            return val

    def kalkul(self, var, symb1, symb2):
        frameVar, varVal = self.symbol_check('var', var)
        frame1, val1 = self.symbol_check(('var', 'int'), symb1)
        type1, val1 = self.check_var(
            frame1, val1, 'int')
        frame2, val2 = self.symbol_check(('var', 'int'), symb2)
        type2, val2 = self.check_var(
            frame2, val2, 'int')
        return val1, val2, frameVar, varVal

    def operatory(self, var, symb1, symb2, label):
        if label:
            frameVar, varVal = self.symbol_check('label', var)
        else:
            frameVar, varVal = self.symbol_check('var', var)
        frame1, val1 = self.symbol_check(types, symb1)
        frame2, val2 = self.symbol_check(types, symb2)
        type1 = frame1
        type2 = frame2
        if frame1 not in types:
            if self.frames[frame1] is None:
                stderr.write('neexistujici frame\n')
                exit(55)
            type1, val1 = self.frames[frame1].get_val(
                val1)
        if frame2 not in types:
            if self.frames[frame2] is None:
                stderr.write('neexistujici frame\n')
                exit(55)
            type2, val2 = self.frames[frame2].get_val(
                val2)
        if not type1 == type2:
            stderr.write('spatny datovy typ\n')
            exit(53)
        if type1 == 'bool':
            val1 = self.check_bool(val1)
        if type2 == 'bool':
            val2 = self.check_bool(val2)

        return val1, val2, frameVar, varVal

    def bool_operatory(self, var, symb1, symb2):
        frameVar, varVal = self.symbol_check('var', var)
        frame1, val1 = self.symbol_check(('bool', 'var'), symb1)
        frame2, val2 = self.symbol_check(('bool', 'var'), symb2)
        type1 = frame1
        type2 = frame2
        if not frame1 == 'bool':
            if self.frames[frame1] is None:
                stderr.write('Frame neexistuje\n')
                exit(55)
            type1, val1 = self.frames[frame1].get_val(
                val1)
        if not frame2 == 'bool':
            if self.frames[frame2] is None:
                stderr.write('Frame neexistuje\n')
                exit(55)
            type2, val2 = self.frames[frame2].get_val(
                val2)
        if not type1 == 'bool' or not type2 == 'bool':
            stderr.write('Neni boolean\n')
            exit(53)
        val1 = self.check_bool(val1)
        val2 = self.check_bool(val2)
        return val1, val2, frameVar, varVal

    def check_var(self, frame, value, type_to_check):
        my_type = type_to_check
        if frame not in type_to_check:
            if self.frames[frame] is None:
                stderr.write('Frame neexistuje\n')
                exit(55)
            my_type, value = self.frames[frame].get_val(value)
            if not my_type == type_to_check:
                stderr.write('spatny datovy typ\n')
                exit(53)
        return my_type, value

    def MOVE(self, var, symb):
        frameVar, varVal = self.symbol_check('var', var)
        assign_frame,  assign_value = self.symbol_check(self.dataTypess, symb)
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)

        if assign_frame in self.dataTypess:
            self.frames[frameVar].set_val(
                varVal, (assign_frame, assign_value))
        else:
            value_to_set = self.frames[assign_frame].get_val(assign_value)
            self.frames[frameVar].set_val(varVal, value_to_set)
    
    
    def AND(self, var, symb1, symb2):
        val1, val2, frameVar, varVal = self.bool_operatory(var, symb1, symb2)
        final_value = val1 and val2
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('bool', final_value))

    def OR(self, var, symb1, symb2):
        val1, val2, frameVar, varVal = self.bool_operatory(var, symb1, symb2)
        final_value = val1 or val2
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('bool', final_value))

    def CREATEFRAME(self):
        self.frames['TF'] = Frame()

    def PUSHFRAME(self):
        if self.frames['TF'] is not None:
            self.push(self.frame_stack, self.frames['TF'])
            self.frames['LF'] = self.top(self.frame_stack)
            self.frames['TF'] = None
        else:
            stderr.write('Pushing not defined frame\n')
            exit(55)

    def POPFRAME(self):
        if self.frame_stack:
            self.frames['TF'] = self.pop(self.frame_stack)
            if self.frame_stack:
                self.frames['LF'] = self.top(self.frame_stack)
            else:
                self.frames['LF'] = None
        else:
            stderr.write('Pop from empty stack\n')
            exit(55)

    def DEFVAR(self, var):
        frame, value = self.symbol_check('var', var)
        if self.frames[frame] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frame].def_var(value)

    def CALL(self, label):
        self.push(self.call_stack, self.current_order)
        order = self.labels.get_val(label[1])
        self.current_order = order

    def RETURN(self):
        self.current_order = self.pop(self.call_stack)
        if self.current_order is None:
            stderr.write('pop z prazdneho stacku')
            exit(56)

    def PUSHS(self, symb):
        frame, varVal = self.symbol_check(self.dataTypess, symb)
        if frame in self.dataTypess:
            self.push(self.data_stack, (frame, varVal))
        else:
            if self.frames[frame] is None:
                stderr.write('Frame neexistuje\n')
                exit(55)
            to_push_value = self.frames[frame].get_val(varVal)
            self.push(self.data_stack, to_push_value)

    def POPS(self, var):
        frame, varVal = self.symbol_check('var', var)
        to_assign_value = self.pop(self.data_stack)
        if self.frames[frame] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frame].set_val(varVal, to_assign_value)

    def ADD(self, var, symb1, symb2):
        val1, val2, frameVar, varVal = self.kalkul(var, symb1, symb2)
        final_value = int(val1) + int(val2)
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('int', final_value))

    def SUB(self, var, symb1, symb2):
        val1, val2, frameVar, varVal = self.kalkul(var, symb1, symb2)
        final_value = int(val1) - int(val2)
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('int', final_value))

    def MUL(self, var, symb1, symb2):
        val1, val2, frameVar, varVal = self.kalkul(var, symb1, symb2)
        final_value = int(val1) * int(val2)
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('int', final_value))

    def IDIV(self, var, symb1, symb2):
        val1, val2, frameVar, varVal = self.kalkul(var, symb1, symb2)
        if int(val2) == 0:
            stderr.write('Division by 0\n')
            exit(57)
        final_value = int(val1) // int(val2)
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('int', final_value))

    def LT(self, var, symb1, symb2):
        val1, val2, frameVar, varVal = self.operatory(var, symb1, symb2, False)
        
        final_value = val1 < val2

        if self.frames[frameVar] is None:
            stderr.write('neexistujici frame\n')
            exit(55)

        self.frames[frameVar].set_val(varVal, ('bool', final_value))

    def GT(self, var, symb1, symb2):
        val1, val2, frameVar, varVal = self.operatory(var, symb1, symb2, False)
        final_value = val1 > val2
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('bool', final_value))

    def EQ(self, var, symb1, symb2):
        val1, val2, frameVar, varVal = self.operatory(var, symb1, symb2, False)
        final_value = val1 == val2
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('bool', final_value))

    def NOT(self, var, symb):
        val1, val2, frameVar, varVal = self.bool_operatory(
            var, symb, symb)
        final_value = not val1
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('bool', final_value))

    def INT2CHAR(self, var, symb):
        frameVar, varVal = self.symbol_check('var', var)
        frame1, val1 = self.symbol_check(('int', 'var'), symb)
        type1, val1 = self.check_var(
            frame1, val1, 'int')
        try:
            val1 = int(val1)
            final_value = chr(val1)
        except OverflowError:
            stderr.write('Nepovolena hodnota\n')
            exit(58)
        except ValueError:
            stderr.write('Nepovolena hodnota\n')
            exit(58)
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('string', final_value))

    def STRI2INT(self, var, symb1, symb2):
        frameVar, varVal = self.symbol_check('var', var)
        frame1, val1 = self.symbol_check(('string', 'var'), symb1)
        type1, val1 = self.check_var(
            frame1, val1, 'string')
        frame2, val2 = self.symbol_check(('int', 'var'), symb2)
        type2, val2 = self.check_var(
            frame2, val2, 'int')
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        val2 = int(val2)
        if val2 < 0 or val2 > (len(val1) - 1):
            stderr.write('Index mimo rozsah\n')
            exit(58)

        final_value = ord(val1[val2])
        self.frames[frameVar].set_val(varVal, ('int', final_value))

    def LABEL(self, label):
        label, value = self.symbol_check('label', label)
        value = value.strip()
        self.labels.def_var([value, self.current_order])

    def JUMP(self, label):
        order = self.labels.get_val(label[1])
        self.current_order = order

    def JUMPIFEQ(self, label, symb1, symb2):
        val1, val2, frameVar, varVal = self.operatory(
            label, symb1, symb2, True)
        final_value = val1 == val2
        if final_value:
            self.current_order = self.labels.get_val(label[1])

    def JUMPIFNEQ(self, label, symb1, symb2):
        val1, val2, frameVar, varVal = self.operatory(
            label, symb1, symb2, True)
        final_value = val1 == val2
        if not final_value:
            self.current_order = self.labels.get_val(label[1])

    def READ(self, var, my_type):
        frameVar, varVal = self.symbol_check('var', var)
        type_type, type_value = my_type
        if not type_type == 'type':
            stderr.write('Spatny typ symbolu\n')
            exit(53)
        if not self.input_file == stdin:
            my_input = self.input[0]
            self.input = self.input[1:]
        else:
            try:
                my_input = input()
            except EOFError:
                my_input = ""

        type_type, type_value = self.symbol_check(
            type_value, (type_value, my_input), False)
        if type_value == "":
            if type_type == 'int':
                type_value = 0
            if type_type == 'bool':
                type_value = 'false'
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)

        self.check_bool(type_value)
        self.frames[frameVar].set_val(varVal, (type_type, type_value))

    def WRITE(self, symb):
        frame, value = self.symbol_check(self.dataTypess, symb)
        if frame not in self.dataTypess:
            if self.frames[frame] is None:
                stderr.write('Frame neexistuje\n')
                exit(55)
            frame, value = self.frames[frame].get_val(value)
        if frame == 'nil':
            print('', end='')
        if frame == 'bool':
            if value:
                print('true', end='')
            else:
                print('false', end='')
        else:
            text = value
            special_char = text.find("\\")
            while special_char != -1:
                index = special_char + 1
                character = ""
                while text[index] <= '9' and text[index] >= '0':
                    character += text[index]
                    if index+1 != len(text):
                        text = text[:index] + text[index+1:]
                    else:
                        text = text[:-1]
                        index -= 1
                character = int(character)
                character = chr(character)
                text = text[:special_char] + character + text[special_char + 1:]
                special_char = text.find("\\")
                
            print(text, end='')

    def CONCAT(self, var, symb1, symb2):
        frameVar, varVal = self.symbol_check('var', var)
        frame1, val1 = self.symbol_check(('string', 'var'), symb1)
        type1, val1 = self.check_var(
            frame1, val1, 'string')
        frame2, val2 = self.symbol_check(
            ('string', 'var'), symb2)
        type2, val2 = self.check_var(
            frame2, val2, 'string')

        final_value = val1 + val2
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('string', final_value))

    def STRLEN(self, var, symb):
        frameVar, varVal = self.symbol_check('var', var)
        frame1, val1 = self.symbol_check(('string', 'var'), symb)
        type1, val1 = self.check_var(
            frame1, val1, 'string')

        final_value = len(val1)
        if self.frames[frameVar] is None:
            stderr.write('STRLEN: Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('int', final_value))

    def GETCHAR(self, var, symb1, symb2):
        frameVar, varVal = self.symbol_check('var', var)
        frame1, val1 = self.symbol_check(('string', 'var'), symb1)
        type1, val1 = self.check_var(
            frame1, val1, 'string')
        frame2, val2 = self.symbol_check(('int', 'var'), symb2)
        type2, val2 = self.check_var(
            frame2, val2, 'int')

        val2 = int(val2)
        if val2 < 0 or val2 > (len(val1) - 1):
            stderr.write('Index mimo rozsah\n')
            exit(58)

        final_value = val1[val2]
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        self.frames[frameVar].set_val(varVal, ('string', final_value))

    def SETCHAR(self, var, symb1, symb2):
        frameVar, varVal = self.symbol_check('var', var)
        frame1, val1 = self.symbol_check(('int', 'var'), symb1)
        type1, val1 = self.check_var(
            frame1, val1, 'int')
        frame2, val2 = self.symbol_check(
            ('string', 'var'), symb2)
        type2, val2 = self.check_var(
            frame2, val2, 'string')

        val1 = int(val1)
        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        final_type, final_value = self.frames[frameVar].get_val(varVal)
        if not final_type == 'string':
            stderr.write('Wrong operand type\n')
            exit(53)
        if val1 < 0 or val1 > (len(final_value) - 1):
            stderr.write('Index mimo rozsah\n')
            exit(58)
        if val2 == "":
            stderr.write('Empty string\n')
            exit(58)
        final_value = final_value[:val1] + \
            val2[0] + final_value[val1 + 1:]
        self.frames[frameVar].set_val(varVal, ('string', final_value))

    def TYPE(self, var, symb):
        frameVar, varVal = self.symbol_check('var', var)
        frame1, val1 = self.symbol_check(self.dataTypess, symb, False)

        if self.frames[frameVar] is None:
            stderr.write('Frame neexistuje\n')
            exit(55)
        if frame1 in self.dataTypess:
            self.frames[frameVar].set_val(varVal, frame1)
        else:
            if self.frames[frame1] is None:
                stderr.write('Frame neexistuje\n')
                exit(55)
            final_frame, final_value = self.frames[frame1].get_val(
                val1)
            self.frames[frameVar].set_val(
                varVal, ('string', final_frame))

    def DPRINT(symb):
        stderr.write('DPRINT: {}\n'.format(symb))

    #TODO EXIT

    #TODO BREAK






argparser = argparse.ArgumentParser()
argparser.add_argument('--source', dest='source_file', default=stdin, help='Path to XML file with source code')
argparser.add_argument('--input', dest='input_file',default=stdin, help='Path to file with user input')
args = argparser.parse_args()
if args.source_file == stdin and args.input_file == stdin:
    stderr.write('chybejici argumenty\n')
    exit(10)



interpret = Interpret(args.source_file, args.input_file)
interpret.parse_source_file()
interpret.execute()


