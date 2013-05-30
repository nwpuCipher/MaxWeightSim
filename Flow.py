__metaclass__= type

class Flow:

    def __init__(self,source,destination,generateRate):
        self.setSourceAndDestination(source, destination)
        self.setGenerateRate(generateRate)
        
    def setSourceAndDestination(self,source,destination):
        assert source != destination,\
            'source should not same as destination'
        self.source, self.destination = \
            source, destination

    def setGenerateRate(self,rate):
        assert rate > 0 and rate <=1,\
            "generate rate should belong in (0,1]"
        self.generateRate = rate

    def getSource(self):
        return self.source

    def getDestination(self):
        return self.destination

    def getGenerateRate(self):
        return self.generateRate

    def __setSource(self,source):
        self.source = source

    def __setDestination(self,destination):
        self.destination = destination

    def __repr__(self):
        return 'flow(%.1f): '%(self.generateRate) +\
            repr(self.source) +\
            '->' + repr(self.destination)

class BigFlow(Flow):

    def __init__(self,source,destination,generateRate):
        super(PacketFlow,self).__init__(source,destination,generateRate)

    def setGenerateRate(self,rate):
        self.generateRate = rate

if __name__ == "main":
    print "ok"
