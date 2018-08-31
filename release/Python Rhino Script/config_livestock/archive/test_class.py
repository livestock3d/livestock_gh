class Top:

    def __init__(self, a, b):
        self.name = a
        self.age = 10
        self.height = 2*b

    def func(self):
        print('Hej', str(self.name))


class Mid(Top):

    def __init__(self, a, c):
        Top.__init__(a, 60)
        self.hat = c

man = Mid('Hans', True)
man.func()
