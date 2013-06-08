__metaclass__ = type

class Packet:
    def __init__(self,packetID=0,createTime=0,hopNum=0,src=None,dst=None):
        self.id = packetID
        self.createTime = createTime
        self.hopNum = hopNum

        self.src = src
        self.dst = dst

        self.remainHopNum = 0

    def setCreateTime(self,time):
        self.createTime = time
        return self

    def getID(self):
        return self.id

    def getCreateTime(self):
        return self.createTime

    def setHopNum(self,hopNum):
        self.hopNum = hopNum
        return self

    def addHopNum(self,i=1):
        self.hopNum += 1
        return self

    def getHopNum(self):
        return self.hopNum

    def setDst(self,dst):
        self.dst = dst
        return self

    def getDst(self):
        return self.dst

    def setSrc(self,src):
        self.src = src
        return self

    def getSrc(self):
        return self.src

    def setDelay(self,currentTime):
        self.arrivalTime = currentTime
        self.delay = currentTime - self.createTime
        return self

    def getDelay(self):
        return self.delay

    def getArrivalTime(self):
        return self.arrivalTime

    def setRemainHopNum(self,num):
        assert num >= 1, 'remaining hop num >= 1 at least'
        self.remainHopNum = num
        return self

    def getRemainHopNum(self):
        return self.remainHopNum

    def decreaseRemainHopNum(self):
        assert self.remainHopNum > 0, 'this should not happen'
        self.remainHopNum -= 1
        return self

    def __repr__(self):
        return "<id:%d ctime:%d hnum:%d"\
            % (self.id, self.createTime, self.hopNum) +' s:'+ repr(self.src)\
            + ' d:' + repr(self.dst)+'>'

class PacketFactory:
    def __init__(self):
        self.id = 0
    def getPacket(self,currentTime,src,dst):       
        packet = Packet(self.id,createTime=currentTime,\
                            src=src,dst=dst)
        self.id += 1
        return packet


if __name__ == "__main__":
    factory = PacketFactory()
    packet = factory.getPacket(currentTime=1,src=(0,0),dst=(1,1))

    print packet
    
