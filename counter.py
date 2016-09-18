#! /usr/bin/python
# coding:utf-8

class Counter(dict):
    '''
    Counter from a list to a dict.
    >>> a=Counter(['1',2,2,3,3,3,4,4,4,4])
    >>> print a
    {'1': 1, 2: 2, 3: 3, 4: 4}
    >>> a.total
    10
    '''

    def __init__(self, lst):
        self.total = len(lst)
        while lst:
            a = lst.pop()
            if a not in self.keys():
                self[a] = 1
            else:
                self[a] += 1

    def dump_text(self):
        text = ''
        for (k, v) in self.items():
            text += str(k) + '\t' + str(v) + '\n'
        return text


if __name__ == '__main__':
    import doctest

    doctest.testmod()
