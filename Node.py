__metaclass__ = type
import numpy as np
import random as rd
from Flow import Flow
from Queues import Queues

class Node:
    def __init__(self,ID,flow=None, queuesType=Queues):
        self.id = ID
        self.setFlow(flow)

        self.neigbours = dict()

        self.queues = queuesType()


    def setQueues(self,**args):
        #print args
        args['neighbours'] = self.neigbours
        self.queues.setQueues(args)

    def hasFlow(self):
        return self.flow is not None

    def setFlow(self,flow):
        if flow is not None:
            assert flow.source == self.id,\
                "flow's source must same with node id"
            assert flow.destination != self.id,\
                "flow's destination must different with node id"
        self.flow = flow

    def injectNewFlow(self,currentStep,getPacket):
        packets = [getPacket(currentStep,src=self.flow.getSource(),\
                         dst=self.flow.getDestination())\
               for i in range(np.random.poisson(self.flow.getGenerateRate()))]
        self.queues.putPacket(packets,\
                                  {'dst':self.flow.getDestination(),\
                                  'nbr':self.flow.getSource()} )



    def calcNeighbourWeight(self):
        weightEdges = dict()
        for neigbour,node in self.neigbours.iteritems():
            dstAndWeight = self.__calcDstAndWeightWith(node)
            if dstAndWeight is not None:    
                weightEdges[neigbour] = dstAndWeight

        return weightEdges


    def sendPackets(self,**paramDict):
        return self.queues.getPacket(paramDict)

    def receivePackets(self,packets,**params):
        self.queues.putPacket(packets,params)

    def callbackFunc(self,**param):
        self.queues.callbackFunc(param)


    def __calcDstAndWeightWith(self,node):
        assert node != self \
            and node.id != self.id, \
            "A node cant calc Weith with itself"
        weightList = self.queues.calcWeightWith(node.queues)

        
        # all the algorithm goes to this func
        return self.__getBestDstAndWeightIn(weightList =weightList,\
                                                src=self.id,nbr=node.id)

    def __getBestDstAndWeightIn(self,weightList,**params):
        if len(weightList) != 0:
            rd.shuffle(weightList)
            weightList.sort(key=lambda x:x[1], reverse=True)
            return weightList.pop(0)
        else:
            return None

    
    def __repr__(self):
        return '<'+'id: '+ repr(self.id) + \
            ' with ' + str(len(self.neigbours)) + ' neighbours ' + \
            repr(self.flow) + '>'

def makeSimpleNode():
    def makeNode(ID,flow,queuesType):
        return Node(ID=ID, flow=flow, queuesType=queuesType)
    return makeNode


class MNode(Node):
    def __init__(self,ID,flow,queuesType,mValue):
        self.mValue = mValue
        super(MNode,self).__init__(ID,flow,queuesType)



    # over loard
    def calcNeighbourWeight(self):
        weightEdges = dict()
        for neigbour,node in self.neigbours.iteritems():
            dstAndWeight = self.__calcDstAndWeightWith(node)
            if dstAndWeight is not None:    
                weightEdges[neigbour] = dstAndWeight

        return weightEdges

    def __calcDstAndWeightWith(self,node):
        assert node != self \
            and node.id != self.id, \
            "A node cant calc Weith with itself"
        weightList = self.queues.calcWeightWith(node.queues)

        return self.__getBestDstAndWeightIn(weightList =weightList,\
                                                src=self.id,nbr=node.id)


    def __getBestDstAndWeightIn(self,weightList,**params):
        src = params['src']
        nbr = params['nbr']

        def __calc(pair):
            mark = 0
            dst = pair[0]
            weight = pair[1]
            if  abs(src[0] - dst[0])+abs(src[1]-dst[1]) -\
                    (abs(nbr[0]-dst[0])+abs(nbr[1]-dst[1])) < 0:
                mark = -1
            weight += self.mValue * mark
            return (dst, weight)

        if len(weightList) != 0:
            weightList = map(__calc,weightList)
            rd.shuffle(weightList)
            weightList.sort(key=lambda x:x[1], reverse=True)
            return weightList.pop(0)
        else:
            return None

def makeMNode(mValue):
    def makeNode(ID,flow,queuesType):
        return MNode(ID,flow,queuesType,mValue)
    return makeNode



class OMNode(Node):
    def __init__(self,ID,flow,queuesType,mValue):
        self.mValue = mValue
        super(OMNode,self).__init__(ID,flow,queuesType)

    # over loard
    def calcNeighbourWeight(self):
        weightEdges = dict()
        for neigbour,node in self.neigbours.iteritems():
            dstAndWeight = self.__calcDstAndWeightWith(node)
            if dstAndWeight is not None:    
                weightEdges[neigbour] = dstAndWeight

        return weightEdges

    def __calcDstAndWeightWith(self,node):
        assert node != self \
            and node.id != self.id, \
            "A node cant calc Weith with itself"
        weightList = self.queues.calcWeightWith(node.queues)

        return self.__getBestDstAndWeightIn(weightList =weightList,\
                                                src=self.id,nbr=node.id)


    def __getBestDstAndWeightIn(self,weightList,**params):
        src = params['src']
        nbr = params['nbr']

        def __calc(pair):
            dst = pair[0]
            weight = pair[1]
            weight += self.mValue* (-1)
            return (dst, weight)

        if len(weightList) != 0:
            weightList = map(__calc,weightList)
            rd.shuffle(weightList)
            weightList.sort(key=lambda x:x[1], reverse=True)
            return weightList.pop(0)
        else:
            return None
def makeOMNode(mValue):
    def makeNode(ID,flow,queuesType):
        return OMNode(ID,flow,queuesType,mValue)
    return makeNode



class CNode(Node):
    def __init__(self,ID,flow,queuesType,m):
        super(CNode,self).__init__(ID,flow,queuesType)
        self.m = m
        self.isLearn = False
        self.counterTable = dict()
        self.mValue = dict()

    def sendPackets(self,**paramDict):
        nbr = paramDict['nbr']
        dst = paramDict['dst']

        self.counterTable[dst] = self.counterTable.get(dst,dict())
        self.counterTable[dst][nbr] = self.counterTable[dst].get(nbr,0)


        packets = self.queues.getPacket(paramDict)

        for packet in packets:
            self.counterTable[dst][nbr] += 1
        return packets
        
    def callbackFunc(self,**paramDict):
        if self.isLearn == True:
            return 
        else: self.isLearn = True
        for dst, neigbours in self.counterTable.iteritems():

            sortedList =\
                sorted([(link,num) for link,num in neigbours.iteritems()],\
                              key=lambda x:x[1],reverse=True)
            item = None
            if len(sortedList) >= 2:
                item = sortedList[1]
            else:
                item = sortedList[0]
            tempDict = dict()
            for link,num in neigbours.iteritems():
                if num >= item[1]:
                    tempDict[link] = 0
                else:
                    tempDict[link] = -1*self.m
            self.mValue[dst] = tempDict
        #print self.mValue
            
    def calcNeighbourWeight(self):
        weightEdges = dict()
        for neigbour,node in self.neigbours.iteritems():
            dstAndWeight = self.__calcDstAndWeightWith(node)
            if dstAndWeight is not None:    
                weightEdges[neigbour] = dstAndWeight

        return weightEdges


    def __calcDstAndWeightWith(self,node):
        assert node != self \
            and node.id != self.id, \
            "A node cant calc Weith with itself"
        weightList = self.queues.calcWeightWith(node.queues)
        

        def func(item):
            return (item[0],item[1]+self.mValue.get(item[0],{}).get(node.id,0))
        weightList = map(func,weightList)



        return self.__getBestDstAndWeightIn(weightList =weightList,\
                                                src=self.id,nbr=node.id)


    def __getBestDstAndWeightIn(self,weightList,**params):
        if len(weightList) != 0:
            rd.shuffle(weightList)
            weightList.sort(key=lambda x:x[1], reverse=True)
            return weightList.pop(0)
        else:
            return None



        
    def __repr__(self):
        return super(CNode,self).__repr__() + '\n' +\
            'CTable: ' + repr(self.counterTable)


def makeCNode(mValue):
    def makeNode(ID,flow,queuesType):
        return CNode(ID,flow,queuesType,mValue)
    return makeNode


class PNode(Node):
    def __init__(self,ID,flow,queuesType,a):
        super(PNode,self).__init__(ID,flow,queuesType)
        self.a = a
        
        self.counterTable = dict()
        self.pValue = dict()

        self.callbackCounter = 0

    def sendPackets(self,**paramDict):
        nbr = paramDict['nbr']
        dst = paramDict['dst']

        self.counterTable[dst] = self.counterTable.get(dst,dict())
        self.counterTable[dst][nbr] = self.counterTable[dst].get(nbr,0)


        packets = self.queues.getPacket(paramDict)

        for packet in packets:
            self.counterTable[dst][nbr] += 1
        return packets
        
    def callbackFunc(self,**paramDict):
        p = np.exp(-1*self.callbackCounter / 30.0)
        self.callbackCounter += 1
        if np.random.random() > p:
            self.pValue.clear()
            self.callbackCounter = 0;
        else:
            
            for dst, neigbours in self.counterTable.iteritems():
                no = sum(neigbours[key] for key in neigbours.iterkeys())
                tempDict = dict()
                for nbr,value in neigbours.iteritems():
                    tempDict[nbr] = \
                        (1-self.a)*self.pValue.get(dst,{}).get(nbr,1/float(len(self.neigbours)))\
                        +self.a*(value/float(no))
                self.pValue[dst] = tempDict

        self.counterTable.clear()
            
    def calcNeighbourWeight(self):
        weightEdges = dict()
        for neigbour,node in self.neigbours.iteritems():
            dstAndWeight = self.__calcDstAndWeightWith(node)
            if dstAndWeight is not None:    
                weightEdges[neigbour] = dstAndWeight

        return weightEdges


    def __calcDstAndWeightWith(self,node):
        assert node != self \
            and node.id != self.id, \
            "A node cant calc Weith with itself"
        weightList = self.queues.calcWeightWith(node.queues)
        

        def func(item):
            return (item[0],item[1]+self.pValue.get(item[0],{}).get(node.id,1/float(\
                        len(self.neigbours))))
        weightList = map(func,weightList)



        return self.__getBestDstAndWeightIn(weightList =weightList,\
                                                src=self.id,nbr=node.id)


    def __getBestDstAndWeightIn(self,weightList,**params):
        if len(weightList) != 0:
            rd.shuffle(weightList)
            weightList.sort(key=lambda x:x[1], reverse=True)
            return weightList.pop(0)
        else:
            return None



        
    def __repr__(self):
        return super(PNode,self).__repr__() + '\n' +\
            'PTable: ' + repr(self.pValue)


def makePNode(a):
    def makeNode(ID,flow,queuesType):
        return PNode(ID,flow,queuesType,a)
    return makeNode



class SPNode:
    def __init__(self,ID,flow=None, queuesType=Queues):
        self.id = ID
        self.setFlow(flow)

        self.neigbours = dict()

        self.queues = queuesType()


    def setQueues(self,**args):
        #print args
        args['neighbours'] = self.neigbours
        self.queues.setQueues(args)

    def hasFlow(self):
        return self.flow is not None

    def setFlow(self,flow):
        if flow is not None:
            assert flow.source == self.id,\
                "flow's source must same with node id"
            assert flow.destination != self.id,\
                "flow's destination must different with node id"
        self.flow = flow

    def injectNewFlow(self,currentStep,getPacket):
        packets = [getPacket(currentStep,src=self.flow.getSource(),\
                         dst=self.flow.getDestination())\
               for i in range(np.random.poisson(self.flow.getGenerateRate()))]


        dst = self.flow.getDestination()
        nbr = self.flow.getSource()
        hop = self.queues.distance(self.flow.getDestination(),\
                                       self.flow.getSource())
        tempList = sorted([((dst,h),10*h +len(self.queues.get((dst,h),[])))\
                    for h in range(hop,36)],\
                          key=lambda x:x[1])

        dstIDandQueue = tempList[0][0]



        self.queues.putPacket(packets,\
                                  {'dst':self.flow.getDestination(),\
                                  'nbr':self.flow.getSource(),\
                                       'dstHopPair':dstIDandQueue} )



    def calcNeighbourWeight(self):
        weightEdges = dict()
        for neigbour,node in self.neigbours.iteritems():
            dstAndWeight = self.__calcDstAndWeightWith(node)
            if dstAndWeight is not None:    
                weightEdges[neigbour] = dstAndWeight

        return weightEdges


    def sendPackets(self,**paramDict):
        return self.queues.getPacket(paramDict)

    def receivePackets(self,packets,**params):
        self.queues.putPacket(packets,params)

    def callbackFunc(self,**param):
        self.queues.callbackFunc(param)


    def __calcDstAndWeightWith(self,node):
        assert node != self \
            and node.id != self.id, \
            "A node cant calc Weith with itself"
        weightList = self.queues.calcWeightWith(node.queues,nbr=node.id)

        
        # all the algorithm goes to this func
        return self.__getBestDstAndWeightIn(weightList =weightList,\
                                                src=self.id,nbr=node.id)

    def __getBestDstAndWeightIn(self,weightList,**params):
        if len(weightList) != 0:
            rd.shuffle(weightList)
            weightList.sort(key=lambda x:x[-1], reverse=True)
            return weightList.pop(0)
        else:
            return None

    
    def __repr__(self):
        return '<'+'id: '+ repr(self.id) + \
            ' with ' + str(len(self.neigbours)) + ' neighbours ' + \
            repr(self.flow) + '>' + ' '+ repr(self.queues)




class NewNode:
    def __init__(self,ID,flow=None, queuesType=Queues,shortRate=0.8):
        self.id = ID
        self.setFlow(flow)
        self.shortPathRate = shortRate
        self.neigbours = dict()

        self.queues = queuesType()


    def setQueues(self,**args):
        #print args
        args['neighbours'] = self.neigbours
        self.queues.setQueues(args)

    def hasFlow(self):
        return self.flow is not None

    def setFlow(self,flow):
        if flow is not None:
            assert flow.source == self.id,\
                "flow's source must same with node id"
            assert flow.destination != self.id,\
                "flow's destination must different with node id"
        self.flow = flow

    def injectNewFlow(self,currentStep,getPacket):
        tSrc = self.flow.getSource()
        tDst = self.flow.getDestination()
        packets = [getPacket(currentStep,src=tSrc,\
                         dst=tDst)\
               for i in range(np.random.poisson(self.flow.getGenerateRate()))]
        shortestHopNum = self.queues.distance(tSrc,tDst)
        num = int(np.ceil(shortestHopNum / self.shortPathRate))
        for p in packets:
            p.setRemainHopNum(num)
        self.queues.putPacket(packets,\
                                  {'dst':tDst,\
                                       'nbr':tSrc} )



    def calcNeighbourWeight(self):
        weightEdges = dict()
        for neigbour,node in self.neigbours.iteritems():
            dstAndWeight = self.__calcDstAndWeightWith(node)
            if dstAndWeight is not None:    
                weightEdges[neigbour] = dstAndWeight

        return weightEdges


    def sendPackets(self,**paramDict):

        return self.queues.getPacket(paramDict)

    def receivePackets(self,packets,**params):
        self.queues.putPacket(packets,params)

    def callbackFunc(self,**param):
        self.queues.callbackFunc(param)


    def __calcDstAndWeightWith(self,node):
        assert node != self \
            and node.id != self.id, \
            "A node cant calc Weith with itself"
        weightList = self.queues.calcWeightWith(node.queues,self.id,node.id)

        #print weightList
        # all the algorithm goes to this func
        return self.__getBestDstAndWeightIn(weightList =weightList,\
                                                src=self.id,nbr=node.id)

    def __getBestDstAndWeightIn(self,weightList,**params):
        nbr = params['nbr']

        if len(weightList) != 0:
            for pair in weightList:
                if pair[0] == nbr:
  
                    return pair
        else:
            return None

    
    def __repr__(self):
        return '<'+'id: '+ repr(self.id) + \
            ' with ' + str(len(self.neigbours)) + ' neighbours ' + \
            repr(self.flow) + '>\n' +repr(self.queues)


def makeNewNode(rate):
    def makeNode(ID,flow,queuesType):
        return NewNode(ID,flow,queuesType,rate)
    return makeNode



if __name__ == "__main__":
    flow1 = Flow((1,2),(2,2),1)
    node = Node((1,2),flow1)
    node.queues[(2,2)] = [1,2,3,4]
    
    flow2 = Flow((2,4),(3,5),1)
    node2 = Node((2,4),None)
    node2.queues[(2,2)] = [3,3,3]

    node.neigbours[node2.id] = node2

    node.calcNeighbourWeight()
    print node
