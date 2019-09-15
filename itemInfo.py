
class ItemInfo(object):
    
    def __init__(self, name, weight, simprice, toprice, category):
        self.name = name
        self.weight = weight
        self.simprice = simprice
        self.toprice = toprice
        self.category = category

    def getName(self):
        return self.name

    def getSimPrice(self):
        return self.simprice

    def getToPrice(self):
        return self.toprice

    def getWeight(self):
        return self.weight

    def getCategory(self):
        return self.category

    def getTotalInfo(self):
        return self.name, self.simprice, self.toprice, self.weight, self.category