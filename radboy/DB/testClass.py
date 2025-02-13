class EntryExtras:
    def __add__(self,val):
        return self.Price+val
    def __sub__(self,val):
        return self.Price-val
    def __truediv__(self,val):
        return self.Price/val
    def __mul__(self,val):
        return self.Price*val
    def __pow__(self,val):
        return self.Price**val

