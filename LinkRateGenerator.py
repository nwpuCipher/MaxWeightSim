__metaclass__ = type
class LinkRateGenerator:
    def __init__(self):
        pass
    def getRate(self):
        pass

class ConstLinkRateGenerator(LinkRateGenerator):
    def __init__(self,rate):
        super(ConstLinkRateGenerator,self).__init__()
        assert int(rate) > 0, "link rate should above 0"
        self.rate = int(rate)
    def getRate(self):
        return self.rate
    def setRate(self,rate):
        self.rate = int(rate)
        return self
