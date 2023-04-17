from checkpoints import *

magenta_checkpoints = [(2, 1), (3, 2), (4, 3), (5, 4), (6, 5)]
green_checkpoints = [(5, 6), (4, 5), (3, 4), (2, 3), (1, 2)]


class CheckPoints2(CheckPoints):
    def checkpoints(self):
        return magenta_checkpoints if self.magenta else green_checkpoints