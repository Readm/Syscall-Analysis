#! /usr/bin/python
# coding:utf-8

import json

__all__=['SysCall']


class SysCall(object):
    def __init__(self, rax, name='', entry='', implementation='', args=[], architecture='amd64'):
        '''
        System calls
        :param rax: syscall number  int
        :param name: syscall name   str
        :param entry: entry point   str 'no_entry' for no entry
        :param implementation: implementation   str 'NULL' for not implement
        :param args: args,list of list: [['%rdi','unsigned int', 'fd'],[...]...]
        :param architecture : 'i386' / 'amd64'
        all str will be lower
        '''
        self.rax = rax
        self.name = name.lower()
        self.entry = entry.lower()
        self.implementation = implementation.lower()
        self.args = args
        self.architecture = architecture.lower()

    def __str__(self):
        json_data = {
            'rax': self.rax,
            'name': self.name,
            'entry': self.entry,
            'implementation': self.implementation,
            'args': self.args,
            'architecture': self.architecture
        }
        return json.dumps(json_data)

    def __repr__(self):
        return self.__str__()

    def dump_json(self, path='syscalls.json'):
        '''Add to dump'''
        with open(path, 'a+') as f:
            json_data = {
                'rax': self.rax,
                'name': self.name,
                'entry': self.entry,
                'implementation': self.implementation,
                'args': self.args,
                'architecture': self.architecture
            }
            json.dump(json_data, f)
            f.write('\n')

    @classmethod
    def read_json(cls, path='syscalls.json'):
        try:
            with open(path, 'r') as f:
                return_lst = []
                lst = f.readlines()
                for i in lst:
                    json_data = json.loads(i)
                    _sc = SysCall(json_data['rax'], json_data['name'], json_data['entry'],
                                  json_data['implementation'], json_data['args'], json_data['architecture'])
                    return_lst.append(_sc)
                return return_lst
        except Exception, e:
            print e

    @property
    def args_number(self):
        return len(self.args)

    @property
    def implemented(self):
        return self.implementation != 'NULL'

    @property
    def used_reg(self):
        return [i[0] for i in self.args]


'''
a=SysCall.read_json()
for i in a:
    if i.args_number == 6:
        print i.rax
        print i.used_reg
print 'max regs', max([i.args_number for i in a])
'''
