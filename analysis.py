#! /usr/bin/python
# coding:utf-8

from collections import Counter

from instruction import Instruction
from syscall_list.syscall_list import SysCall

__all__ = ['CodeBlock']
syscalls = SysCall.read_json('./syscall_list/syscalls.json')


class CodeBlock(list):
    def __init__(self, codes, syscall_num=-1, path='', func_name='', image=''):
        '''codes should be list of str, each for a line'''
        self.syscall_num = syscall_num
        self.path = path
        self.func_name = func_name
        self.image = image
        for i in codes:
            self.append(Instruction(i))
            if self[-1].unresolved:
                if self[-1].disas:
                    print "warn: unresolved instruction", self[-1].disas
                else:
                    print "warn: unresolved instruction Empty", self[-1]

        #for speed
        self.rax_data, self.rax_source_distance = self.get_rax_data_distance

    @property
    def entry(self):
        try:
            if self[-1].disas != 'syscall':
                with open('reports/exceptions/entry.txt', 'a+') as f:
                    f.write('path:' + self.path + '\n')
                    f.writelines(self)
            return self[-1].disas
        except:
            with open('reports/exceptions/entry.txt', 'a+') as f:
                f.write('path:' + self.path + '\n')
                f.writelines(self)
            return None

    @property
    def entry_type(self):
        try:
            return self[-1].type
        except:
            with open('reports/exceptions/entry.txt', 'a+') as f:
                f.write('path:' + self.path + '\n')
                f.writelines(self)
            return None

    def last_not_order_type(self):
        for i in range(1, len(self)):
            if not self[-i - 1].in_order or self[-i - 1].type in ['syscall']:
                return self[-i - 1].type
        return None

    def last_order_len(self):  # Last_order_block_length include syscall
        for i in range(1, len(self)):
            if not self[-i - 1].in_order or self[-i - 1].type in ['syscall']:
                return i
        return None

    @property
    def last_instruction(self):
        return self[-1].ins

    @property
    def rax_source(self):
        return Instruction.data_type(self.trace_back('rax')[0])

    @property
    def get_rax_data_distance(self):  # from 1, eg: mov eax, 1; syscall; return 1
        eax, distance = self.trace_back('eax')
        if Instruction.data_type(eax) != 'immediate': return Instruction.data_type(eax), distance
        if int(eax, 16) != self.syscall_num:
            if not self.rax_not_match_recorded:
                with open('reports/exceptions/rax_not_match_syscall.txt', 'a+') as f:
                    f.write('path=' + self.path + '\n')
                    f.write('real:' + str(self.syscall_num) + 'trace:' + str(int(eax, 16)) + '\n')
                    f.writelines(self)
                print 'Warn: wrong eax trace back. eax:', eax, 'real:', self.syscall_num
                self.rax_not_match_recorded = True
        return eax, distance

    def rax_last_assignment(self):
        return self.last_assignment('rax')

    def trace_back(self, reg, fuzzy=True, only_reg=True):  # only in regs route

        origin = reg
        i = -1
        if only_reg:
            end_list = ['stack', 'immediate', 'memory']
        else:
            end_list = ['immeidate']

        if fuzzy:
            def match(a, b):
                return Instruction.reg_type(a) == Instruction.reg_type(b)
        else:
            def match(a, b):
                return a == b
        for i in range(len(self)):
            if match(self[-1 - i].dest, reg):
                reg = self[-1 - i].src
                if Instruction.data_type(reg) in end_list:
                    return reg, i
                if reg is None:
                    print "Error: reg=", reg, self, i, origin
                    break
        return reg, -1

    def last_assignment(self, reg, fuzzy=True):  # from 1, eg: mov eax, 1; syscall; return 1
        for i in range(len(self)):
            if fuzzy:
                if Instruction.reg_type(self[-1 - i].dest) == Instruction.reg_type(reg):
                    return i
            else:
                if self[-1 - i].dest == reg:
                    return i

    @property
    def syscall(self):  # try to find out which syscall
        num = self.rax_data
        if Instruction.data_type(num) == 'immediate':
            try:
                return syscalls[int(num, 16)]
            except:
                with open('reports/exceptions/unknown_syscall.txt', 'a+') as f:
                    f.write('path:' + self.path + '\n')
                    f.write('sysnum:'+str(self.rax_data)+'\n')
                    f.writelines(self)
                return SysCall(int(num, 16), name='Unknown', args=[])
        else:
            return SysCall(-1, name='Unknown', args=[])

    @property
    def args_source_distance(self):
        a = [self.trace_back(i[0][1:])[1] for i in self.syscall.args]
        if a:
            return max(a)
        else:
            return None

    @property
    def args_last_assignment(self):
        a = [self.last_assignment(i[0][1:]) for i in self.syscall.args]
        if a:
            return max(a)
        else:
            return None

    def not_order_after_rax_assignment(self):
        _n = 0
        if self.rax_last_assignment is not None:
            for i in range(self.rax_last_assignment):
                if not self[-1 - i].in_order:
                    _n += 1
        return _n

    @classmethod
    def read_file(cls, path, only_syscall = True):
        Blocks = []
        with open(path, 'r') as f:

            wrong_block = set([])

            tmp = []
            syscall_num = -1
            func = ''
            image = ''
            line_number = 0

            while True:
                line_number += 1
                line = f.readline()

                # mark wrong line.
                if line and not (line.startswith('ip') or line.startswith('0x')):
                    with open('reports/exceptions/wrong_line.txt', 'a+') as fn:
                        fn.write('path=' + path + '\n')
                        fn.write('line=' + str(line_number) + '\n')
                    print "warring: wrong line:"
                    print 'file:', path
                    print 'line:', line_number
                    wrong_block.add(len(Blocks))

                if line.startswith('ip'):
                    if tmp:
                        Blocks.append(CodeBlock(tmp, syscall_num, path, func, image))
                        if only_syscall:
                            if Blocks[-1].entry != 'syscall':
                                del Blocks[-1]
                    syscall_num = int(line.split(':')[-1])
                    try:
                        func , _ , image = line.split('#')[2:5]
                    except:
                        func = ''
                        image = ''
                        print 'wrong func name and image', line
                    tmp = []
                elif line == '':
                    Blocks.append(CodeBlock(tmp, syscall_num, path, func, image))
                    if only_syscall:
                        if Blocks[-1].entry != 'syscall':
                            del Blocks[-1]
                    break
                else:
                    tmp.append(line)


            # delete wrong block.
            wrong_block = list(wrong_block)
            for i in range(len(wrong_block)):
                del Blocks[wrong_block[0]]
                wrong_block.remove(wrong_block[0])
                for j in range(len(wrong_block)):
                    wrong_block[j] = wrong_block[j] - 1

        return Blocks


Clnot   = Counter()
Clol    = Counter()
Crs     = Counter()
Crsd    = Counter()
Crla    = Counter()
Cnoara  = Counter()
Crd     = Counter()
Csy     = Counter()
Casla   = Counter()
Ce      = Counter()
Cet     = Counter()
Cfn     = Counter()
Ci      = Counter()


class Record(object):
    def __init__(self, path):
        self.path = path
        self.Blocks = CodeBlock.read_file(path)

    def test(self):
        print "Sample: ", self.path
        print 'Block numbers', len(self.Blocks)
        print ''

        print 'Rax source\n', Counter([i.rax_source for i in self.Blocks])
        print 'Syscall name\n', Counter([i.syscall.name for i in self.Blocks])
        print 'Args source distance(max)\n', Counter([i.args_source_distance for i in self.Blocks])

    def analysis(self):
        print 'Sample:', self.path
        print 'Block numbers', len(self.Blocks)
        print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        Clnot.update(Counter([i.last_not_order_type for i in self.Blocks]))
        Clol.update(Counter([i.last_order_len for i in self.Blocks]))
        Crs.update(Counter([i.rax_source for i in self.Blocks]))
        Crsd.update(Counter([i.rax_source_distance for i in self.Blocks]))
        Crla.update(Counter([i.rax_last_assignment for i in self.Blocks]))
        Cnoara.update(Counter([i.not_order_after_rax_assignment for i in self.Blocks]))
        Crd.update(Counter([i.rax_data for i in self.Blocks]))
        Csy.update(Counter([i.syscall.name for i in self.Blocks]))
        Casla.update(Counter([i.args_last_assignment for i in self.Blocks]))
        Ce.update(Counter([i.entry for i in self.Blocks]))
        Cet.update(Counter([i.entry_type for i in self.Blocks]))
        Cfn.update(Counter([i.func_name for i in self.Blocks]))
        Ci.update(Counter([i.image for i in self.Blocks]))


        # print 'Last not order type\n',Counter([i.last_not_order_type for i in self.Blocks])
        # print 'Last order length\n',Counter([i.last_order_len for i in self.Blocks])
        # print 'Rax source\n',Counter([i.rax_source for i in self.Blocks])
        # print 'Rax source distance\n',Counter([i.rax_source_distance for i in self.Blocks])
        # print 'Rax last assignment\n',Counter([i.rax_last_assignment for i in self.Blocks])
        # print 'Not order after rax assignment\n',Counter([i.not_order_after_rax_assignment for i in self.Blocks])
        # print 'Rax data\n',Counter([i.rax_data for i in self.Blocks])
        # print 'Syscall name\n',Counter([i.syscall.name for i in self.Blocks])
        # print 'Args source last assignment(max)\n',Counter([i.args_last_assignment for i in self.Blocks])
        # print 'Last instruction location\n', Counter([i.last_instruction_location for i in self.Blocks])
        # print 'Entry\n',Counter([i.entry for i in self.Blocks])

    def analysis_key_syscall_source(self):
        #print 'Sample:', self.path
        #print 'Block numbers', len(self.Blocks)
        #print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        global key_list_counter

        for block in self.Blocks:
            if block.syscall.name in [i[0].name for i in key_list_counter]:
                for arg in block.syscall.args:
                    source, _ = block.trace_back(arg[0][1:], only_reg = False)
                    source_type = Instruction.data_type(source)
                    for i in key_list_counter:
                        if i[0].name == block.syscall.name:
                            i[1][block.syscall.args.index(arg)].update(Counter({source_type:1}))





def print_txt(counter):
    for (k, v) in counter.items():
        print str(k), '\t', str(v)

def fix_202_problem_in_fail():
    import os
    for i in os.listdir('data/fail'):
        with open('data/fail/' + str(i), 'r') as f:
            lines = f.readlines()
            for j in lines:
                if j.startswith('ip') and 'x' in j.split(':')[-1]:
                    print 'file', i, 'line', lines.index(j)

def select_and_move(path):
    import os, shutil
    select_path = path
    for i in os.listdir(select_path):
        if not str(i).endswith('outmap.out'):
            if str(i) not in ['good', 'ins', 'fail']:
                print '================================================================================'
                print 'Testing...', str(i)
                try:
                    a = Record(select_path + str(i))
                    a.test()
                    c = raw_input('>>>>>Good(Enter)? Ins? Fail? Delete? Remain?')
                    if not c:
                        shutil.move(select_path + str(i), 'data/good/' + str(i))
                        print "Good!"
                    elif c.startswith('i'):
                        shutil.move(select_path + str(i), 'data/ins/' + str(i))
                        print "Ins!"
                    elif c.startswith('f'):
                        shutil.move(select_path + str(i), 'data/fail/' + str(i))
                        print "Fail!"
                    elif c.startswith('d'):
                        os.remove(select_path + str(i))
                        print "Delete!"
                    else:
                        print "Remain!"
                except:
                    shutil.move(select_path + str(i), 'data/fail/' + str(i))


if __name__ == '__main__':
    import os, shutil

    key_list_counter = []

    with open('syscall_list/key_syscall.txt') as f:
        for line in f.readlines():
            for i in syscalls:
                if i.name == line.strip():
                    key_list_counter.append((i, []))
                    break
            else:
                key_list_counter.append((None,[]))

    #prepare
    for (a, b) in key_list_counter:
        if a:
            for _ in range(len(a.args)):
                b.append(Counter())

    for i in os.listdir('data/new/'):
        a = Record('data/new/' + i)
        a.analysis_key_syscall_source()

    for (a, b) in key_list_counter:
        print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        print 'syscall name:', a.name
        for n in range(len(b)):
            for i in a.args[n]:
                print i,
            print ''
            print_txt(b[n])







''' full analysis
    for i in os.listdir('data/new/'):
        a = Record('data/new/' + i)
        a.analysis()

    print 'Total:', sum(Clnot.values())
    print '\nLast not order type\n'
    print_txt(Clnot)
    print '\nLast order length\n'
    print_txt(Clol)
    print '\nRax source\n'
    print_txt(Crs)
    print '\nRax source distance\n'
    print_txt(Crsd)
    print '\nRax last assignment\n'
    print_txt(Crla)
    print '\nNot order after rax assignment\n'
    print_txt(Cnoara)
    print '\nRax data\n'
    print_txt(Crd)
    print '\nSyscall name\n'
    print_txt(Csy)
    print '\nArgs source last assignment(max)\n'
    print_txt(Casla)
    print '\nEntry\n'
    print_txt(Ce)
    print '\nEntry_type\n'
    print_txt(Cet)
    print '\nFunction name\n'
    print_txt(Cfn)
    print '\nImage\n'
    print_txt(Ci)
'''