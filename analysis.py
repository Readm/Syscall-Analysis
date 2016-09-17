#! /usr/bin/python
# coding:utf-8
from instruction import Instruction
from counter import Counter


class Code_Block(list):
    def __init__(self, codes):
        '''codes should be list of str, each for a line'''
        for i in codes:
            self.append(Instruction(i))
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
        return self.[-1].ins

    @property
    def rax_sorce(self):
        pass

    #def trace_back(self, reg, ):


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
