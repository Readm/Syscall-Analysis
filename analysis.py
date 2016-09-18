#! /usr/bin/python
# coding:utf-8


class Code_Block(dict):
    def __init__(self, codes):
        '''codes should be list of str, each for a line'''
        for i in range(len(codes)):
            self[i]=codes[i]





a=Code_Block(['jiljsdif\n','lfjisdjfsld\n'])
print a[0]
