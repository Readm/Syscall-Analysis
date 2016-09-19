#! /usr/bin/python
# coding:utf-8

from syscall_list import SysCall

with open('syscall.json', 'w'):
    pass  # clear all

with open('raw.txt') as f:
    data = f.readlines()

for i in range(314):  # tested ok
    if not data[i * 3].startswith(str(i)):
        print 'wrong i', i
    if data[i * 3 + 1].startswith(str(i + 1)):
        data.insert(i * 3 + 1, '')
        data.insert(i * 3 + 1, '')
    if data[i * 3 + 2].startswith(str(i + 1)):
        data.insert(i * 3 + 1, '')

print data[0].split()
for j in range(314):
    print j
    rax, name, entry, implement = data[j * 3].split()
    if entry == 'not':
        _sc = SysCall(rax, name, implementation='NULL')
        _sc.dump_json()
        continue

    arglist = zip(data[j * 3 + 1].split(), data[j * 3 + 2].split('\t'))
    arg = []
    if arglist:
        for i in range(len(arglist)):
            reg = arglist[i][0]
            argname = arglist[i][1].split()[-1]
            argtype = ' '.join(arglist[i][1].split()[:-1])
            arg.append([reg, argtype, argname])
    _sc = SysCall(rax, name, entry, implement, arg, architecture='amd64')
    _sc.dump_json()
    print _sc
