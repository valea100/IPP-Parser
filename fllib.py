from sys import stdin, stderr
class Frame:
    def __init__(self):
        self.local_vars = {}

    def def_var(self, variable):
        if variable not in self.local_vars:
            self.local_vars[variable] = None
        else:
            stderr.write('DEFVAR: Redefinition of variable\n')
            exit(52)

    def set_val(self, variable, value):
        my_type = value[0]
        my_value = value[1]
        if variable in self.local_vars:
            self.local_vars[variable] = (my_type, my_value)
        else:
            stderr.write('Working with not defined variable\n')
            exit(54)

    def get_val(self, variable):
        if variable in self.local_vars:
            if self.local_vars[variable] is None:
                stderr.write('Trying to get value of not declared variable\n')
                exit(56)
            return self.local_vars[variable]
        else:
            stderr.write('Working with not defined variable\n')
            exit(54)


class Label(Frame):
    def __init__(self):
        super().__init__()

    def def_var(self, variable):
        name, order = variable
        if name not in self.local_vars:
            self.local_vars[name] = order
        else:
            stderr.write('Redefinition of label\n')
            exit(52)

    def get_val(self, label):
        if label in self.local_vars:
            return self.local_vars[label]
        else:
            print(label)
            stderr.write('Non existing label\n')
            exit(52)
