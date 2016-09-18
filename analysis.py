#! /usr/bin/python
# coding:utf-8
from instruction import Instruction
from counter import Counter


class Code_Block(list):
    def __init__(self, codes):
        '''codes should be list of str, each for a line'''
        for i in codes:
            self.append(Instruction(i))
            if self[-1].unresolved: print "warn: unresolved instruction", self[-1].disas

    @property
    def last_not_order_type(self):
        for i in range(len(self)):
            if not self[-i-1].in_order:
                return self[-i-1].type
        return None

    @property
    def last_order_len(self):       #Last_order_block_length not include syscall
        for i in range(len(self)):
            if not self[-i-1].in_order:
                return i
        return None

    @property
    def last_instruction(self):
        return self[-1].ins

    @property
    def rax_source(self):
        return self.trace_back('rax')[0]

    @property
    def rax_source_distance(self):      # from 1, eg: mov eax, 1; syscall; return 1
        return self.trace_back('rax')[1]

    @property
    def rax_last_assignment(self):
        return self.last_assignment('rax')

    def trace_back(self, reg, fuzzy = True):
        if fuzzy:
            for i in range(len(self)):
                if Instruction.reg_type(self[-1-i].dest) == Instruction.reg_type(reg):
                    reg = self[-1-i].src
                    if Instruction.data_type(reg) in ['stack', 'immediate', 'memory']:
                        return Instruction.data_type(reg),i
                    if reg == None:
                        print "Error: reg", self, i
            return Instruction.reg_type(reg),i
        else:
            for i in range(len(self)):
                if self[-1-i].dest == reg:
                    reg = self[-1-i].src
                    if Instruction.data_type(reg) in ['stack', 'immediate', 'memory']:
                        return Instruction.data_type(reg),i
                    if reg == None:
                        print "Error: reg", self, i
            return reg,i

    def last_assignment(self, reg, fuzzy = True):   # from 1, eg: mov eax, 1; syscall; return 1
        for i in range(len(self)):
            if fuzzy:
                if Instruction.reg_type(self[-1-i].dest) == Instruction.reg_type(reg):
                    return i
            else:
                if self[-1-i].dest == reg:
                    return i



Blocks=[]

with open('statisticsyscall.out','r') as f:
    tmp = []
    while True:
        line = f.readline()
        if line.startswith('ip'):
            Blocks.append(Code_Block(tmp))
            tmp = []
        elif line == '':
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
