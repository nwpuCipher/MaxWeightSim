import random as rd
from Flow import Flow
from Node import Node
from Queues import Queues
from Packet import Packet, PacketFactory
from NetworkFactory import GridNetworkFactory
from LinkRateGenerator import ConstLinkRateGenerator


class Simulator:
    def __init__(self,network,maxStep,linkRateGenerator,packetFactory):
        self.network = network

        self.maxStep = maxStep
        self.currentStep = 0

        self.linkRateGenerator = linkRateGenerator
        self.packetFactory = packetFactory

        self.weightNetwork = dict()
        self.packetPool = list()

        self.callbacks = list()

    def run(self,flag=False):
        self.networkInit()
        while self.currentStep < self.maxStep:
            self.currentStep += 1
            self.calcMaxWeight()
            self.schedule()
            self.injectNewFlow()
            #self.printNetwork()
            self.__invokeCallbacks()
            if flag:
                print self.currentStep

    def networkInit(self):
        for nId,node in self.network.iteritems():
            node.setQueues(network=self.network)
            self.callbacks.append(node.callbackFunc)

    def calcMaxWeight(self):
        self.weightNetwork.clear()
        for nID,node in self.network.iteritems():
            self.weightNetwork[nID] = node.calcNeighbourWeight()

    def schedule(self):
        routeRule = self.__getScheduleRule()
        self.__scheduleWithRouteRule(routeRule)

    def injectNewFlow(self):
        for nID,node in self.network.iteritems():
            if node.hasFlow():
                node.injectNewFlow(self.currentStep,self.packetFactory.getPacket)

    def getStaticsInfo(self):
        aveDelay = sum(packet.getDelay() for packet in self.packetPool)/float(len(self.packetPool))
        aveDRate = len(self.packetPool) / float(self.packetFactory.id)
        aveHop = sum(packet.getHopNum() for packet in self.packetPool)/float(len(self.packetPool))
        statics = {'aveDelay':aveDelay,'aveDRate':aveDRate,'aveHop':aveHop,\
                       'recPktNbr':len(self.packetPool),'gntPtkNbr':self.packetFactory.id}
        return statics
    

    def __invokeCallbacks(self):
        if self.currentStep % 1000 == 0:
            for func in self.callbacks:
                func()
            #while self.callbacks:
                #self.callbacks.pop(0)()

    def printNetwork(self):
        for nID,node in self.network.iteritems():
            print node
    
    def __getScheduleRule(self):
        edgeSet = self.__getEdgeSet()
        routeRule = self.__getRouteRule(edgeSet)
        return routeRule
        
    def __getEdgeSet(self):
        edgeSet = []
        tempDict = dict()
        for nID,entry in self.weightNetwork.iteritems():

            for neighbour,item in entry.iteritems():
                # sysmtrical edge
                weight = \
                    max(item[-1],\
                            self.weightNetwork[neighbour].get(nID,[0,0])[-1])
                # multipy by rate
                linkRate = self.linkRateGenerator.getRate()
                weight *= linkRate


                if weight is not 0:
                    if ((neighbour,nID),weight) not in edgeSet:
                        edgeSet.append(\
                            ((nID,neighbour),weight,linkRate)\
                                )

        return edgeSet

    def __getRouteRule(self,edgeSet):
        linkSet = []
        while len(edgeSet):
            rd.shuffle(edgeSet)
            edgeSet.sort(key=lambda x:x[1],reverse=True)
            elem = edgeSet.pop(0)
            #((n1,n2),rate)
            linkSet.append((elem[0],elem[2]))
            conflictEdge = [item for item in edgeSet\
                                if elem[0][0] in item[0] \
                                or elem[0][1] in item[0]]
            for edge in conflictEdge:
                edgeSet.remove(edge)

        return linkSet

    def __scheduleWithRouteRule(self,routeRule):
        for edge in routeRule:
            self.__sendAndRecive(edge[0][0],\
                                     edge[0][1],edge[1])

    def __sendAndRecive(self,srcID,nbrID,linkRate):
        if self.weightNetwork[srcID].get(nbrID,(0,0))[-1] < \
                self.weightNetwork[nbrID].get(srcID,(0,0))[-1]:
            srcID,nbrID = nbrID,srcID

        if nbrID not in self.weightNetwork[srcID]:
            srcID,nbrID = nbrID,srcID
        dstID = self.weightNetwork[srcID].get(nbrID)[0]

        dstIDandQueue = self.weightNetwork[srcID].get(nbrID)[1]

        packets = self.network[srcID].sendPackets(src=srcID,nbr=nbrID,dst=dstID,rate=linkRate,)
        self.__statProcess(packets,src=srcID,dst=dstID,nbr=nbrID)
        self.network[nbrID].receivePackets(packets,src=srcID,nbr=nbrID,dst=dstID,rate=linkRate,\
                                               dstHopPair=dstIDandQueue)
        

    def __statProcess(self,packets,**params):
        for packet in packets:
            packet.addHopNum()
            
            if packet.getDst() == params['nbr']:
                self.packetPool.append(packet.setDelay(self.currentStep))




            
if __name__ == "__main__":
    factory = GridNetworkFactory(Node,Queues)
    factory.constructNetwork(8,8)\
        .setFlow(Flow((0,0),(2,2),1),\
                     Flow((0,1),(2,1),1))
    network = factory.getNetwork()
    packetFactory = PacketFactory()


    network[(0,0)].queues[(1,1)] = \
        [packetFactory.getPacket(currentTime=0, src=(0,0),dst=(1,1)),\
             packetFactory.getPacket(currentTime=0, src=(0,0),dst=(1,1)),\
             packetFactory.getPacket(currentTime=0, src=(0,0),dst=(1,1))]
    network[(0,1)].queues[(0,2)] = \
        [packetFactory.getPacket(currentTime=0,src=(0,1),dst=(0,2)),\
             packetFactory.getPacket(currentTime=0,src=(0,1),dst=(0,2))]
    
    simulator = Simulator(network,100,ConstLinkRateGenerator(1),packetFactory)
    simulator.run()
