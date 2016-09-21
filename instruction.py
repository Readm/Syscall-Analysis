#! /usr/bin/python
# coding:utf-8

__all__ = ['Instruction']
registers = [
    'rax', 'eax', 'ax', 'al',
    'rbx', 'ebx', 'bx', 'bl',
    'rcx', 'ecx', 'cx', 'cl',
    'rdx', 'edx', 'dx', 'dl',
    'rsi', 'esi', 'si', 'sil',
    'rdi', 'edi', 'di', 'dil',
    'rbp', 'ebp', 'bp', 'bpl',
    'rsp', 'esp', 'sp', 'spl',
    'r8', 'r8d', 'r8w', 'r8b',
    'r9', 'r9d', 'r9w', 'r9b',
    'r10', 'r10d', 'r10w', 'r10b',
    'r11', 'r11d', 'r11w', 'r11b',
    'r12', 'r12d', 'r12w', 'r12b',
    'r13', 'r13d', 'r13w', 'r13b',
    'r14', 'r14d', 'r14w', 'r14b',
    'r15', 'r15d', 'r15w', 'r15b'
]

not_move_list = ['cmp', 'test', 'neg', 'or', 'add', 'sar', 'bsr', 'ror', 'rol', 'pxor', 'pshufd']

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
    >>> Instruction.reg_type('spl')
    'rsp'
    >>> c=Instruction('0x00007ff308c780da   xor eax, eax\\n')
    >>> c.src
    '0x0'
    >>> c.dest
    'eax'
    '''

    def __init__(self, string):
        super(Instruction, self).__init__()

    @property
    def unresolved(self):
        _tmp1 = self.type
        if self.type.startswith('p'):
            _tmp0 = self.type[1:]
        else:
            _tmp0 = _tmp1
        solved = {'jmp', 'call', 'mov', 'or', 'xor', 'nop', 'test', 'syscall', 'pop', 'push', 'cld',
                                 'add', 'sub', 'cmp', 'and', 'lea', 'pushfq', 'lahf', 'set', 'shr', 'shl', 'neg', 'ret',
                                 'not', 'mov', 'cdqe', 'cwde', 'cbw', 'dec', 'div', 'sar', 'bsf', 'rep', 'repne',
                                 'xchg', 'sbb', 'scasb', 'vzeroupper', 'mul', 'subb', 'inc', 'pshufd', 'unpcklbw',
                                 'rdtsc', 'ror', 'data16', 'rol', 'xadd'}
        return (_tmp0 not in solved) and (_tmp1 not in solved)

    @property
    def prefix(self):
        if self.disas.split()[0] in ['bnd', 'lock']:
            return self.disas.split()

    @property
    def ip(self):
        return int(self.split()[0], 16)

    @property
    def eip(self):
        return self.ip

    @property
    def rip(self):
        return self.ip

    @property
    def disas(self):
        try:
            return self.split(' ', 1)[1].strip()
        except:
            return ''

    @property
    def ins(self):
        if len(self.split()) < 2: return ''
        if self.prefix:
            return self.split()[2]      #if exception here, a instruction has only prefix, data bug.
        else:
            return self.split()[1]

    @property
    def type(self):
        if self.ins.startswith('j'):
            return 'jmp'
        elif self.ins.startswith('mov') or self.ins[1:].startswith('mov'):
            return 'mov'
        elif self.ins.startswith('set'):
            return 'set'
        elif self.ins.startswith('cmp') or self.ins[1:].startswith('cmp'):
            return 'cmp'
        else:
            return self.ins

    @property
    def in_order(self):
        return not self.type in ['jmp', 'call', 'ret']

    @property
    def dest(self):
        if ',' in self.disas:
            if self.type == 'xchg':
                if Instruction.data_type(self._src) == 'register':
                    return self._src
                else:
                    return self.split(',')[-1].strip()
            else:
                return self.split(',')[-1].strip()

    @property
    def src(self):
        if ',' in self.disas:
            if self.type == 'xchg':
                if not Instruction.data_type(self._src) == 'register':
                    return self._src
                else:
                    return self.split(',')[-1].strip()

            return ' '.join(self.disas.split(',')[0].split()[1:])

        return not self.type in ['jmp', 'call', 'ret']

    @property
    def full_src(self):
        if ',' in self.disas:
            return self.split(',')[-1].strip()

    @property
    def full_dest(self):
        if ',' in self.disas:
            return ' '.join(self.disas.split(',')[0].split()[1:])

    @property
    def _src(self):
        if ',' in self.disas:
            if self.type not in not_move_list:
                return self.split(',')[-1].split()[-1]
        if self.type == 'pop':
            return 'stack'
        if self.type == 'push':
            return self.split()[-1]

    @property
    def src(self):
        if self.type == 'xor' and self._src == self.dest:
            return '0x0'
        else:
            return self._src

    @property
    def dest(self):
        if ',' in self.disas:
            if self.type not in not_move_list:
                return self.disas.split(',')[0].split()[-1]
        if self.type == 'push':
            return 'stack'
        if self.type == 'pop':
            return self.split()[-1]

    @staticmethod
    def data_type(data):
        if data == None:
            return None
        if data in registers:
            return 'register'
        if data in ['stack']:
            return 'stack'
        if '[' in data:
            if 'sp' in data:
                return 'stack'
            else:
                return 'memory'
        try:
            _ = int(data, 16)
            return 'immediate'
        except:
            return None

    @staticmethod
    def reg_type(reg):
        if reg in registers:
            return registers[registers.index(reg) / 4 * 4]


if __name__ == '__main__':
    import doctest

    doctest.testmod()
