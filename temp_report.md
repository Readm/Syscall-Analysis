```
Sample:  data/statisticsyscall(1).out
Block numbers 95

Last not order type
syscall	1
jmp	45
call	47
ret	2

Last order length
2	46
3	9
4	10
6	2
7	3
8	8
10	14
11	2
15	1

Rax source
immediate	95

Rax source distance
1	81
2	4
3	2
4	3
5	5

Rax last assignment
1	88
2	2
3	2
5	3

Not order after rax assignment
0	95

Rax data
0x15	7
0x9	19
0xe7	1
0x4e	2
0x3	11
0x2	9
0x1	2
0x0	7
0x9e	1
0x5	10
0x10	2
0xda	1
0x111	1
0xc	3
0xb	1
0xa	12
0xd	2
0x89	2
0xe	1
0x61	1

Syscall name
set_robust_list	1
rt_sigaction	2
set_tid_address	1
exit_group	1
getdents	2
read	7
mmap	19
rt_sigprocmask	1
access	7
arch_prctl	1
write	2
ioctl	2
munmap	1
brk	3
statfs	2
close	11
getrlimit	1
open	9
fstat	10
mprotect	12

Args source distance(max)
1	1
2	3
3	5
4	5
6	1
7	1
8	11
11	5
12	1
14	7
15	1
16	1
17	3
18	5
19	45

Ares source last assignment(max)
1	1
2	6
3	17
4	11
5	7
6	7
7	23
8	7
9	7
12	1
14	2
15	1
18	3
19	2
```