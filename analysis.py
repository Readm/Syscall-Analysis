#! /usr/bin/python
# coding:utf-8
from instruction import Instruction
from counter import Counter
from syscall_list.syscall_list import SysCall

syscalls = []


class CodeBlock(list):
    def __init__(self, codes):
        '''codes should be list of str, each for a line'''
        for i in codes:
            self.append(Instruction(i))
            if self[-1].unresolved: print "warn: unresolved instruction", self[-1].disas

    @property
    def last_not_order_type(self):
        for i in range(len(self)):
            if not self[-i - 1].in_order:
                return self[-i - 1].type
        return None

    @property
    def last_order_len(self):  # Last_order_block_length include syscall
        for i in range(len(self)):
            if not self[-i - 1].in_order:
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
        return self.trace_back('eax')[0]

    @property
    def rax_source_distance(self):  # from 1, eg: mov eax, 1; syscall; return 1
        return self.trace_back('rax')[1]

    @property
    def rax_last_assignment(self):
        return self.last_assignment('rax')

    def trace_back(self, reg, fuzzy=True):  # only in regs route
        origin = reg
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
            print 'Loading syscall list...'
            syscalls = SysCall.read_json('./syscall_list/syscalls.json')
        if Instruction.data_type(self.rax_data) == 'immediate':
            return syscalls[int(self.rax_data, 16)]

    @property
    def args_source_distance(self):
        return max([self.trace_back(i[0][1:])[1] for i in self.syscall.args])

    @property
    def args_last_assignment(self):
        return max([self.last_assignment(i[0][1:]) for i in self.syscall.args])


Blocks = []

with open('statisticsyscall.out', 'r') as f:
    tmp = []
    while True:
        line = f.readline()
        if line.startswith('ip'):
            Blocks.append(CodeBlock(tmp))
            tmp = []
        elif line == '':
            Blocks.append(CodeBlock(tmp))
            break
        else:
            tmp.append(line)
del Blocks[0]

print len(Blocks)

print Counter([i.last_not_order_type for i in Blocks])
print Counter([i.last_order_len for i in Blocks])
print Counter([i.rax_source for i in Blocks])
print Counter([i.rax_source_distance for i in Blocks])
print Counter([i.rax_last_assignment for i in Blocks])
print Counter([i.rax_data for i in Blocks])
print Counter([i.syscall.name for i in Blocks])
print Counter([i.args_source_distance for i in Blocks])
print Counter([i.args_last_assignment for i in Blocks])
