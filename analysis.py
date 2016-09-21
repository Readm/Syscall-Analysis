#! /usr/bin/python
# coding:utf-8
from instruction import Instruction
from collections import Counter
from syscall_list.syscall_list import SysCall

__all__ = ['CodeBlock']
syscalls = []


class CodeBlock(list):
    def __init__(self, codes, syscall_num=-1):
        '''codes should be list of str, each for a line'''
        self.syscall_num = syscall_num
        self.path = ''
        for i in codes:
            self.append(Instruction(i))
            if self[-1].unresolved:
                if self[-1].disas:
                    print "warn: unresolved instruction", self[-1].disas
                else:
                    print "warn: unresolved instruction Empty", self[-1]

    @property
    def last_not_order_type(self):
        for i in range(1,len(self)):
            if not self[-i - 1].in_order or self[-i-1].type in ['syscall']:
                return self[-i - 1].type
        return None

    @property
    def last_order_len(self):  # Last_order_block_length include syscall
        for i in range(1,len(self)):
            if not self[-i - 1].in_order or self[-i-1].type in ['syscall']:
                return i
        return None

    @property
    def last_instruction(self):
        return self[-1].ins

    @property
    def rax_source(self):
        return Instruction.data_type(self.trace_back('rax')[0])

    @property
    def rax_data(self):
        eax = self.trace_back('eax')[0]
        if Instruction.data_type(eax)!='immediate': return Instruction.data_type(eax)
        if int(eax,16)!=self.syscall_num:
            print 'Warn: wrong eax trace back. eax:', eax,'real:', self.syscall_num
            print self
        return self.trace_back('eax')[0]

    @property
    def rax_source_distance(self):  # from 1, eg: mov eax, 1; syscall; return 1
        return self.trace_back('rax')[1]

    @property
    def rax_last_assignment(self):
        return self.last_assignment('rax')

    def trace_back(self, reg, fuzzy=True):  # only in regs route
        origin = reg
        i = -1
        if fuzzy:
            for i in range(len(self)):
                if Instruction.reg_type(self[-1 - i].dest) == Instruction.reg_type(reg):
                    reg = self[-1 - i].src
                    if Instruction.data_type(reg) in ['stack', 'immediate', 'memory']:
                        return reg, i
                    if reg == None:
                        print "Error: reg=", reg, self, i, origin
                        break
            return reg, i
        else:
            for i in range(len(self)):
                if self[-1 - i].dest == reg:
                    reg = self[-1 - i].src
                    if Instruction.data_type(reg) in ['stack', 'immediate', 'memory']:
                        return reg
                    if reg == None:
                        print "Error: reg", self, i
            return reg, i

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
        global syscalls
        if not syscalls:
            syscalls = SysCall.read_json('./syscall_list/syscalls.json')
        num = self.rax_data
        if Instruction.data_type(num) == 'immediate':
            try:
                return syscalls[int(num, 16)]
            except:
                return SysCall(int(num, 16), name= 'Unknown')
        else:
            return SysCall(-1, name= 'Unknown')

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

    @property
    def not_order_after_rax_assignment(self):
        _n = 0
        for i in range(self.rax_last_assignment):
            if not self[-1-i].in_order:
                _n += 1
        return _n

    @classmethod
    def read_file(cls, path):
        Blocks = []
        with open(path, 'r') as f:

            tmp = []
            syscall_num = -1
            line_number=0
            while True:
                line_number+=1
                line = f.readline()
                if line and not (line.startswith('ip') or line.startswith('0x')):
                    print "warring: wrong line:"
                    print 'file:', path
                    print 'line:', line_number
                if line.startswith('ip'):
                    Blocks.append(CodeBlock(tmp))
                    Blocks[-1].syscall_num = syscall_num
                    syscall_num = int(line.split(':')[-1])
                    tmp = []
                elif line == '':
                    Blocks.append(CodeBlock(tmp))
                    Blocks[-1].syscall_num = syscall_num
                    break
                else:
                    tmp.append(line)
            del Blocks[0]
        for i in Blocks:
            i.path = path
        return Blocks


class Record(object):
    def __init__(self, path):
        self.path = path
        self.Blocks = CodeBlock.read_file(path)

    def test_good(self):
        print "Sample: ", self.path
        print 'Block numbers',len(self.Blocks)
        print ''

        print 'Rax source\n',Counter([i.rax_source for i in self.Blocks])
        print 'Syscall name\n',Counter([i.syscall.name for i in self.Blocks])
        print 'Args source distance(max)\n',Counter([i.args_source_distance for i in self.Blocks])


    def analysis(self):
        print "Sample: ", self.path
        print 'Block numbers',len(self.Blocks)
        print ''

        print 'Last not order type\n',Counter([i.last_not_order_type for i in self.Blocks])
        print 'Last order length\n',Counter([i.last_order_len for i in self.Blocks])
        print 'Rax source\n',Counter([i.rax_source for i in self.Blocks])
        print 'Rax source distance\n',Counter([i.rax_source_distance for i in self.Blocks])
        print 'Rax last assignment\n',Counter([i.rax_last_assignment for i in self.Blocks])
        print 'Not order after rax assignment\n',Counter([i.not_order_after_rax_assignment for i in self.Blocks])
        print 'Rax data\n',Counter([i.rax_data for i in self.Blocks])
        print 'Syscall name\n',Counter([i.syscall.name for i in self.Blocks])
        print 'Args source distance(max)\n',Counter([i.args_source_distance for i in self.Blocks])
        print 'Args source last assignment(max)\n',Counter([i.args_last_assignment for i in self.Blocks])

def fix_202_problem_in_fail():
    import os
    for i in os.listdir('data/fail'):
        with open('data/fail/'+str(i), 'r') as f:
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
                    a = Record(select_path+str(i))
                    a.test_good()
                    c = raw_input('>>>>>Good(Enter)? Ins? Fail? Delete? Remain?')
                    if not c:
                        shutil.move(select_path+str(i),'data/good/'+str(i))
                        print "Good!"
                    elif c.startswith('i'):
                        shutil.move(select_path+str(i),'data/ins/'+str(i))
                        print "Ins!"
                    elif c.startswith('f'):
                        shutil.move(select_path+str(i),'data/fail/'+str(i))
                        print "Fail!"
                    elif c.startswith('d'):
                        os.remove(select_path+str(i))
                        print "Delete!"
                    else:
                        print "Remain!"
                except:
                    shutil.move(select_path+str(i),'data/fail/'+str(i))

def move_map_to(path):
    import os, shutil
    for i in os.listdir(path):
        map_file = '.'.join(str(i).split('.')[:-1])+'.outmap.out'
        if map_file in os.listdir('data'):
            shutil.move('data/'+map_file, path)

if __name__ == '__main__':
    import os, shutil

    move_map_to('data/good/')
