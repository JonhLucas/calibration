import numpy as np
from pin import pinLabel


class  linePoints():
    list = []
    size = 10
    mask = np.zeros((size,1), np.int32)
    count = 1
    begin = None
    end = None

    def __init__(self, mw, i = 10) -> None:
        self.size = i
        self.mask = np.zeros((self.size, 1), np.int32)
        for j in range(0, self.size):
            l1 = pinLabel(mw)
            l1.setup(j)
            self.list.append(l1)
            
        self.begin = self.list[0]
        self.end = self.list[-1]
    
    
    def getMask(self):
        return self.mask