__metaclass__ = type
import pylab as py

from Flow import Flow
from Simulator import Simulator
from Packet import PacketFactory
from Queues import Queues,ShadowQueues,SPQueues
from NetworkFactory import GridNetworkFactory
from LinkRateGenerator import ConstLinkRateGenerator
from Node import makeSimpleNode,makeMNode,makeOMNode,makeCNode,makePNode,SPNode

gobalRateList = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
gobalGridNetworkFactory = GridNetworkFactory(makeMNode(1),Queues)
gobalMaxStep = 10000
gobalFlow = 'Flow((2,0),(2,7),injectRate),Flow((4,0),(4,7),injectRate),\
                     Flow((0,2),(7,2),injectRate),Flow((0,4),(7,4),injectRate),\
                     Flow((1,1),(5,1),injectRate),Flow((6,1),(6,6),injectRate),\
                     Flow((5,6),(1,6),injectRate),Flow((1,5),(1,2),injectRate)'

class DifferentInjectRateTest:
    def __init__(self,linkRate=1,maxStep=gobalMaxStep,injectRate=0.5,\
                     factory=gobalGridNetworkFactory):
        factory.constructNetwork(8,8)\
            .setFlow(Flow((2,0),(2,7),injectRate),Flow((4,0),(4,7),injectRate),
                     Flow((0,2),(7,2),injectRate),Flow((0,4),(7,4),injectRate),
                     Flow((1,1),(5,1),injectRate),Flow((6,1),(6,6),injectRate)
                     ,Flow((5,6),(1,6),injectRate),Flow((1,5),(1,2),injectRate))
        network = factory.getNetwork()

        self.packetFactory = PacketFactory()
        self.simulator = \
            Simulator(network,maxStep,ConstLinkRateGenerator(linkRate),self.packetFactory)

    def run(self):
        self.simulator.run(flag = False)

    def getStaticsInfo(self):
        return self.simulator.getStaticsInfo()


from multiprocessing import Process, Lock, Queue
class OneProcess(Process):
    def __init__(self,threadID, rateList,statDict, lock, queue,factory):
        super(OneProcess,self).__init__();
        self.threadID = threadID
        self.rateList = rateList

        self.factory = factory
        self.lock = lock
        self.queue = queue
    def run(self):
        for rate in self.rateList:
            print rate
            test =\
                DifferentInjectRateTest(injectRate=rate,linkRate=1,maxStep=gobalMaxStep,factory=self.factory)
            test.run()

            self.lock.acquire()
            statDict = self.queue.get()
            statDict[rate] = test.getStaticsInfo()
            self.queue.put(statDict)
            self.lock.release()
                    


def mainProcessCtrl(rateList,threadNum,factory):
    statDict = {}
    q = Queue()
    q.put(statDict)
    lock = Lock()
    

    step = int(round(len(rateList) / float(threadNum)))
    #for i in range(0,len(rateList),step):
        #print len(rateList[i:i+step])

    threads = [OneProcess(i,rateList[i:i+step],statDict,lock,q,factory=factory) \
                   for i in range(0,len(rateList),step)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    statDict = q.get()
    return [statDict[key]['aveDelay'] for key in rateList]

def plainOldWay():
    delays = []
    for iRate in [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]: 
        print iRate
        test = DifferentInjectRateTest(injectRate=iRate,linkRate=1,maxStep=gobalMaxStep)
        test.run()
        static = test.getStaticsInfo()
        delays.append(static['aveDelay'])
    py.plot([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1],delays)
    py.show()

def OrdTest():
    injectRate = 0.5
    factory = GridNetworkFactory(makeMNode(1),ShadowQueues)
    factory.constructNetwork(8,8)\
        .setFlow(Flow((2,0),(2,7),injectRate),Flow((4,0),(4,7),injectRate),\
                     Flow((0,2),(7,2),injectRate),Flow((0,4),(7,4),injectRate),\
                     Flow((1,1),(5,1),injectRate),Flow((6,1),(6,6),injectRate),\
                     Flow((5,6),(1,6),injectRate),Flow((1,5),(1,2),injectRate))
    network = factory.getNetwork()

    packetFactory = PacketFactory()
    simulator = \
    Simulator(network,gobalMaxStep,ConstLinkRateGenerator(1),packetFactory)
    simulator.run()
    stat = simulator.getStaticsInfo()
    print stat


def CounterTest(step = 10000):
    injectRate = 0.5
    factory = GridNetworkFactory(makePNode(0.6),Queues)
    factory.constructNetwork(6,6)\
        .setFlow(Flow((0,0),(0,5),injectRate))\
        .setFlow(Flow((5,0),(5,5),injectRate))\
        .setFlow(Flow((2,0),(3,5),injectRate))

    network = factory.getNetwork()

    packetFactory = PacketFactory()
    simulator = \
        Simulator(network,step,ConstLinkRateGenerator(1),packetFactory)
    simulator.run()
    #simulator.printNetwork()
    stat = simulator.getStaticsInfo()
    print stat



if __name__ == "__main__":
 
    #mainProcessCtrl([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1],3)
    #rateVsDelayTest()
    #differentOMNodeModeTest()
    #OMNodeVSMNodeTest()
    #Test()

    CounterTest()
    #learningVsPressure()

