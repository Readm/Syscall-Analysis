#! /usr/bin/python
# coding:utf-8

class Instruction(str):
    '''
    Simple instruction class, format sensitive
    >>> a = Instruction('0x00007ff31c44e7ce   mov rax, qword ptr [rsp+0x8]\\n')
    >>> a.split()
    ['0x00007ff31c44e7ce', 'mov', 'rax,', 'qword', 'ptr', '[rsp+0x8]']
    >>> hex(a.ip)
    '0x7ff31c44e7ce'
    >>> a.ins
    'mov'
    >>> a.in_order
    True
    >>> a.disas
    'mov rax, qword ptr [rsp+0x8]'
    >>> a.dest
    'rax'
    >>> a.full_src
    'qword ptr [rsp+0x8]'
    >>> a.src
    '[rsp+0x8]'
    >>> b = Instruction('0x00007ff31c4502d2   jz 0x7ff31c450291')
    >>> b.type
    'jmp'
    >>> b.in_order
    False
    '''

    def __init__(self, str):
        super(Instruction, self).__init__()

    @property
    def ip(self):
        return int(self.split()[0],16)
    @property
    def eip(self):
        return self.ip
    @property
    def rip(self):
        return self.ip

    @property
    def disas(self):
        return self.split(' ',1)[1].strip()

    @property
    def ins(self):
        if len(self.split())<2: return ''
        return self.split()[1]

    @property
    def type(self):
        if self.ins.startswith('j'):
            return 'jmp'
        elif self.ins.startswith('mov'):
            return 'mov'
        else:
            return self.ins

    @property
    def in_order(self):
        return not self.type in ['jmp','call','ret']

    @property
    def full_src(self):
        if ',' in self.disas:
            return self.split(',')[-1].strip()
    @property
    def full_dest(self):
        if ',' in self.disas:
            return ' '.join(self.disas.split(',')[0].split()[1:])

    @property
    def src(self):
        if ',' in self.disas:
            return self.split(',')[-1].split()[-1]
    @property
    def dest(self):
        if ',' in self.disas:
            return self.disas.split(',')[0].split()[-1]



if __name__=='__main__':
    import doctest
    doctest.testmod()