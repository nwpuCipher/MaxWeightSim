__metaclass__ = type
import sys
import random as rd

class Queues:
    def __init__(self):
        self.innerQueue = dict()

    def __getitem__(self,key):
        return self.innerQueue[key]

    def __setitem__(self,key,value):
        self.innerQueue[key] = value

    def __repr__(self):
        return repr(self.innerQueue)

    def setQueues(self,args):
        #print 'Queues:here'
        pass

    def clear(self):
        self.innerQueue.clear()

    def get(self,key,value=None):
        return self.innerQueue.get(key,value)

    
    def calcWeightWith(self,queues):
        weightList = [(dst,len(queue) - len(queues.get(dst,[]))) \
                          for dst,queue in self.innerQueue.iteritems()]
        
        newList = [pair for pair in weightList \
                       # if 1) weight not equal 0, 
                       # and when 1) cant ensure \
                       # 2) make the queue for destination is not empty
                       if pair[1] != 0 or len(self.innerQueue[pair[0]])]

        return newList

    def getPacket(self,paramDict):
        dst = paramDict['dst']
        rate = paramDict['rate']
        packet = []
        while len(self.innerQueue[dst]) > 0 and rate > 0:
            rate -= 1
            packet.append(self.innerQueue[dst].pop(0))
        return packet

    def putPacket(self,packets,paramDict):
        dst = paramDict['dst']
        nbr = paramDict['nbr']

        for packet in packets:
            if packet.getDst() == nbr:
                pass
                #print 'node received'
            else:
                self.innerQueue[dst] = self.innerQueue.get(dst,list())
                self.innerQueue[dst].append(packet)

    def callbackFunc(self,paramDict):
        pass


class ShadowQueues:
    def __init__(self):
        self.neigbourQueue = dict()
        self.shadowQueue = dict()
        self.bucket = dict()
    
    def __getitem__(self,key):
        return self.shadowQueue[key]
    
    def __setitem__(self,key,value):
        self.shadowQueue[key] = value
    
    def __repr__(self):
        return repr(self.shadowQueue)

    def setQueues(self,args):
        for key in args['neighbours'].iterkeys():
            self.neigbourQueue[key] = []

    def clear(self):
        self.neigbourQueue.clear()
        self.shadowQueue.clear()
        self.bucket.clear()

    def get(self,key,value=0):
        return self.shadowQueue.get(key,value)


    def calcWeightWith(self,queues):
        weightList = [(dst, counter-queues.get(dst,0)) \
                          for dst,counter in self.shadowQueue.iteritems()]
        
        newList = [pair for pair in weightList \
                       if pair[1] != 0 or self.shadowQueue[pair[0]]]
        return newList

    def getPacket(self,paramDict):
        nbr = paramDict['nbr']
        rate = paramDict['rate']
        packets = []
        while len(self.neigbourQueue[nbr]) > 0 and rate > 0:
            rate -= 1

            p = self.neigbourQueue[nbr].pop()
            dst = p.getDst()
            self.shadowQueue[dst] -= 1
            self.bucket[dst][nbr] -= 1
            packets.append(p)
        
        return packets

    def putPacket(self,packets,paramDict):
        nbr = paramDict['nbr']

        for packet in packets:
            if packet.getDst() == nbr:
                pass
            else:
                dst = packet.getDst()

                self.shadowQueue[dst] = self.shadowQueue.get(dst,0) + 1


                defaultTokenTable = dict(zip((nID for nID in self.neigbourQueue.iterkeys()),\
                                                 (sys.maxint/2 for i in range(len(self.neigbourQueue)))\
                                                 )\
                                             )
                self.bucket[dst] = self.bucket.get(dst,defaultTokenTable)

                                        


                tempList = [(link,value) for link,value in self.bucket[dst].iteritems()]
                rd.shuffle(tempList)
                tempList.sort(key=lambda x:x[1],reverse=False)
                link = tempList.pop(0)[0]

                self.bucket[dst][link] += 1
                self.neigbourQueue[link].append(packet)
                #print self.bucket




class SPQueues:
    def __init__(self):
        self.innerQueue = dict()

    def __getitem__(self,key):
        return self.innerQueue[key]

    def __setitem__(self,key,value):
        self.innerQueue[key] = value

    def __repr__(self):
        return repr(self.innerQueue)

    def setQueues(self,args):
        #print 'Queues:here'
        pass

    def clear(self):
        self.innerQueue.clear()

    def get(self,key,value=None):
        return self.innerQueue.get(key,value)

 
    def distance(self,src,dst):
        return abs(src[0]-dst[0])+abs(src[1]-dst[1])
   
    def calcWeightWith(self,queues,**paramDict):
        nbr = paramDict['nbr']
        weightList = []
        for dstAndHop, queue in self.innerQueue.iteritems():
            dst,currentHop = dstAndHop

            minHop = self.distance(nbr,dst)
            weightList.extend( [((dst,currentHop),(dst,hop),len(queue)-len(queues.get((dst,hop),[])))\
                 for hop in range(minHop,currentHop)] )
        
        
        newList = [pair for pair in weightList \
                       # if 1) weight not equal 0, 
                       # and when 1) cant ensure \
                       # 2) make the queue for destination is not empty
                       if pair[-1] != 0 or len(self.innerQueue[pair[0]])]

        return newList

    def getPacket(self,paramDict):
        dst = paramDict['dst']
        rate = paramDict['rate']
        packet = []
        while len(self.innerQueue[dst]) > 0 and rate > 0:
            rate -= 1
            packet.append(self.innerQueue[dst].pop(0))
        return packet

    def putPacket(self,packets,paramDict):

        dst = paramDict['dst']
        nbr = paramDict['nbr']
        dstHopPair = paramDict['dstHopPair']
        for packet in packets:
            if packet.getDst() == nbr:
                pass
                #print 'node received'
            else:
                self.innerQueue[dstHopPair] = self.innerQueue.get(dst,list())
                self.innerQueue[dstHopPair].append(packet)

    def callbackFunc(self,paramDict):
        pass




if __name__ == "__main__":
    queues = Queues()
    print queues 
    queues[2] = 45
    print queues
    
