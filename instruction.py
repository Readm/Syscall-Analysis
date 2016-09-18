#! /usr/bin/python
# coding:utf-8

class Instruction(str):

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
        return self.split(' ',1)[0].strip()

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
        return not self.ins in ['jmp','call','ret']

    @property
    def dest(self):
        if ',' in self.disas:
            return self.split(',')[-1].strip()
    @property
    def src(self):
        if ',' in self.disas:
            return ' '.join(self.disas.split(',')[0].split()[1:])

a = Instruction('0x00007ff31c44e7ce   mov rax, qword ptr [rsp+0x8]')
print a.split()
print hex(a.ip)
print a.ins
print a.in_order
print a.disas
print a.dest
print a.src