__metaclass__ = type
import pylab as py

from Flow import Flow
from Simulator import Simulator
from Packet import PacketFactory
from Queues import Queues,ShadowQueues,SPQueues,NewQueues,TestQueues,TestSquareQueues
from NetworkFactory import GridNetworkFactory
from LinkRateGenerator import ConstLinkRateGenerator
from Node import makeSimpleNode,makeMNode,makeOMNode,makeCNode,makePNode,SPNode,makeNewNode

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

        factory.constructNetwork(6,6)\
            .setFlow(Flow((0,0),(0,5),injectRate))\
            .setFlow(Flow((5,0),(5,5),injectRate))\
            .setFlow(Flow((2,0),(3,5),injectRate))

        network = factory.getNetwork()

        self.packetFactory = PacketFactory()
        self.simulator = \
            Simulator(network,maxStep,ConstLinkRateGenerator(linkRate),self.packetFactory)

    def run(self):
        self.simulator.run(flag = False)

    def getStaticsInfo(self):
        return self.simulator.getStaticsInfo()


def rateVsDelayTest():
    for m in [0,2,6,10]:
        factory = GridNetworkFactory(makeMNode(m),Queues)
        result = mainProcessCtrl(factory=factory,rateList = gobalRateList,threadNum=3)
        py.plot(gobalRateList,result,label = 'm=%d'%m)
    py.legend(loc=0)
    py.show()

def differentOMNodeModeTest():
    for m in [0,2,4,10]:
        factory = GridNetworkFactory(makeOMNode(m),Queues)
        result = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
        py.plot(gobalRateList,result,label ='om=%d'%m)
    py.legend(loc=0)
    py.show()
    

def OMNodeVSMNodeTest():
    factory = GridNetworkFactory(makeOMNode(0),Queues)
    result = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
    py.plot(gobalRateList,result,label ='bp')
    for m in [2,4]:
        factory = GridNetworkFactory(makeOMNode(m),Queues)
        result = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
        py.plot(gobalRateList,result,'--',label ='om=%d'%m)

        factory = GridNetworkFactory(makeMNode(m),Queues)
        result = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
        py.plot(gobalRateList,result,label ='m=%d'%m)
    py.legend(loc=0)
    py.show()

def Test():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    result = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
    #print result
    py.plot(gobalRateList,result,'-o',label ='bp')

    #factory = GridNetworkFactory(makeSimpleNode(),ShadowQueues)
    #result = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
    #py.plot(gobalRateList,result,'-v',label ='sq')

    #factory = GridNetworkFactory(makeOMNode(1),Queues)
    #result = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
    #py.plot(gobalRateList,result,'-+',label ='om')

    #factory = GridNetworkFactory(makeMNode(2),Queues)
    #result = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
    #py.plot(gobalRateList,result,'-*',label ='mm=2')
    

    #factory = GridNetworkFactory(makeMNode(4),ShadowQueues)
    #result = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
    #py.plot(gobalRateList,result,'-s',label ='ms=4')
    
    py.legend(loc=0)
    py.show()


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
    return statDict
    return [statDict[key]['aveDRate'] for key in rateList]

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

def onePassLearningVsPressure():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    resultBP = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeCNode(1),Queues)
    resultLQ = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeCNode(10),Queues)
    resultLQ2 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
    
    for item in ['aveDelay','aveDRate']:
        
        entry = [resultBP[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-o',label ='bp')
    
        entry = [resultLQ[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-v',label ='lq=1')
        
        entry = [resultLQ2[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-x',label ='lq=10')
        

        py.legend(loc=0)
        py.savefig('onePassLearning_'+item)
        py.close()

def PerodicPossiblityLearningVsPressure():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    resultBP = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makePNode(0.9),Queues)
    resultLQ = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makePNode(0.5),Queues)
    resultLQ2 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
    
    for item in ['aveDelay','aveDRate']:
        
        entry = [resultBP[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-o',label ='bp')
    
        entry = [resultLQ[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-v',label ='a=0.9')
        
        entry = [resultLQ2[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-x',label ='a=0.5')
        

        py.legend(loc=0)
        py.savefig('PerodicPossiblityLearning_with_redo_add_'+item)
        py.close()

def newTest():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    resultBP = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makePNode(0.5),Queues)
    resultLQ = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(SPNode,SPQueues)
    resultLQ2 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeMNode(2),Queues)
    resultLQ3 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
    
    #factory = GridNetworkFactory(makeCNode(1),Queues)
    #resultLQ4 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
    
    for item in ['aveDelay','aveDRate']:
        
        entry = [resultBP[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-o',label ='bp')
    
        entry = [resultLQ[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-v',label ='pl=0.5')
        
        entry = [resultLQ2[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-x',label ='sp=1')
        
        entry = [resultLQ3[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-p',label ='mm=2')

        #entry = [resultLQ4[key][item] for key in gobalRateList]
        #py.plot(gobalRateList,entry,'-+',label ='ol=1')
        
        py.legend(loc=0)
        py.savefig('newTest_'+item)
        py.close()

def NewQueuesTest():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    resultBP = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeNewNode(1),NewQueues)
    resultLQ = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(SPNode,SPQueues)
    resultLQ2 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeNewNode(0.8),NewQueues)
    resultLQ3 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
    
    for item in ['aveDelay','aveDRate']:
        
        entry = [resultBP[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-o',label ='bp')
    
        entry = [resultLQ[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-v',label ='nq=1')

        entry = [resultLQ3[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-p',label ='nq=0.7')
        
        entry = [resultLQ2[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-x',label ='sp=1')


        
        
        py.legend(loc=0)
        py.savefig('newQueuesTest_'+item)
        py.close()

def NewQueuesWithLimitsTest():

    results = []
    for rate in [0.2,0.4,0.8,1]:
        factory = GridNetworkFactory(makeNewNode(rate),NewQueues)
        result = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
        results.append((rate,result))
    
    for item in ['aveDelay','aveDRate']:
        for rate,result in results:
            entry = [result[key][item] for key in gobalRateList]
            py.plot(gobalRateList,entry,label ='nq=%.1f'%rate)
   
        
        py.legend(loc=0)
        py.savefig('newQueuesTest_differentLimits_'+item)
        py.close()

def paperOneTestSA():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    resultBP = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)


    factory = GridNetworkFactory(makeMNode(2),Queues)
    resultLQ3 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeMNode(4),Queues)
    resultLQ4 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeMNode(6),Queues)
    resultLQ5 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    labels = {'aveDelay':'Average end-to-end delay',\
                  'aveDRate':'Delivery rate',\
                  'aveHop':'Average hop count',\
                  'aveBacklog':'Per-node queue lengths'}

    for item in ['aveDelay','aveDRate','aveHop','aveBacklog']:
        
        entry = [resultBP[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-o',label ='bp')
    
        
        entry = [resultLQ3[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-p',label ='M=2')
        
        entry = [resultLQ4[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-x',label ='M=4')

        entry = [resultLQ5[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-x',label ='M=6')
        
        py.xlabel("$\lambda$")
        py.ylabel(labels[item])
        py.legend(loc=0)
        py.savefig('PaperOneTest_sameAlgorithms_'+labels[item])
        py.close()


def paperOneTestDA():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    resultBP = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)


    factory = GridNetworkFactory(SPNode,SPQueues)
    resultLQ2 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeMNode(4),Queues)
    resultLQ3 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    labels = {'aveDelay':'Average end-to-end delay',\
                  'aveDRate':'Delivery rate',\
                  'aveHop':'Average hop count',\
                  'aveBacklog':'Per-node queue lengths'}

    for item in ['aveDelay','aveDRate','aveHop','aveBacklog']:
        
        entry = [resultBP[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-o',label ='bp')
    
        
        entry = [resultLQ2[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-x',label ='K=10')
        
        entry = [resultLQ3[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-p',label ='M=4')

        
        py.xlabel("$\lambda$")
        py.ylabel(labels[item])
        py.grid
        py.legend(loc=0)
        py.savefig('PaperOneTest_differentAlgorithms_other_'+labels[item])
        py.close()


def PaperTwoTest_onePassLearningVsPressure():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    resultBP = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeCNode(2),Queues)
    resultLQ = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    labels = {'aveDelay':'Average end-to-end delay',\
                  'aveDRate':'Delivery rate',\
                  'aveHop':'Average hop count',\
                  'aveBacklog':'Per-node queue lengths'}
    for item in ['aveDelay','aveDRate','aveHop','aveBacklog']:
        
        entry = [resultBP[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-o',label ='bp')
    
        entry = [resultLQ[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-v',label ='M=2')
        
        
        py.xlabel("$\lambda$")
        py.ylabel(labels[item])
        py.legend(loc=0)
        py.savefig('PaperTwo_onePassLearning_'+item)
        py.close()

def PaperTwoTest_PerodicPossiblityLearningVsPressure():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    resultBP = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makePNode(0.9),Queues)
    resultLQ = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makePNode(0.5),Queues)
    resultLQ2 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    labels = {'aveDelay':'Average end-to-end delay',\
                  'aveDRate':'Delivery rate',\
                  'aveHop':'Average hop count',\
                  'aveBacklog':'Per-node queue lengths'}
    
    for item in ['aveDelay','aveDRate','aveHop','aveBacklog']:
        
        entry = [resultBP[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-o',label ='bp')
    
        entry = [resultLQ[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-v',label ='r=0.9')
        
        entry = [resultLQ2[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-x',label ='r=0.5')
        
        py.xlabel("$\lambda$")
        py.ylabel(labels[item])
        py.legend(loc=0)
        py.savefig('PaperTwoTest_PerodicPossiblityLearning_with_redo_add_'+item)
        py.close()
def PaperTwoTest_DA():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    resultBP = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(SPNode,SPQueues)
    resultLQ = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makePNode(0.5),Queues)
    resultLQ2 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    labels = {'aveDelay':'Average end-to-end delay',\
                  'aveDRate':'Delivery rate',\
                  'aveHop':'Average hop count',\
                  'aveBacklog':'Per-node queue lengths'}
    
    for item in ['aveDelay','aveDRate','aveHop','aveBacklog']:
        
        entry = [resultBP[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-o',label ='bp')
    
        entry = [resultLQ[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-v',label ='K=10')
        
        entry = [resultLQ2[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-x',label ='r=0.5')
        
        py.xlabel("$\lambda$")
        py.ylabel(labels[item])
        py.legend(loc=0)
        py.savefig('PaperTwoTest_DA_'+item)
        py.close()


def PaperThree_NewQueuesTest_DA():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    resultBP = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)


    factory = GridNetworkFactory(SPNode,SPQueues)
    resultLQ2 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeNewNode(0.8),NewQueues)
    resultLQ3 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)


    labels = {'aveDelay':'Average end-to-end delay',\
                  'aveDRate':'Delivery rate',\
                  'aveHop':'Average hop count',\
                  'aveBacklog':'Per-node queue lengths'}
    
    for item in ['aveDelay','aveDRate','aveHop','aveBacklog']:
        
        entry = [resultBP[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-o',label ='bp')
    

        entry = [resultLQ3[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-p',label ='r=0.8')
        
        entry = [resultLQ2[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-x',label ='K=10')


        
        py.xlabel("$\lambda$")
        py.ylabel(labels[item])
        py.legend(loc=0)
        py.savefig('PaperThree_newQueuesTest_DA_'+item)
        py.close()


def PaperThree_NewQueuesWithLimitsTest_SA():

    results = []
    for rate in [0.2,0.4,0.8,1]:
        factory = GridNetworkFactory(makeNewNode(rate),NewQueues)
        result = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)
        results.append((rate,result))
    

    labels = {'aveDelay':'Average end-to-end delay',\
                  'aveDRate':'Delivery rate',\
                  'aveHop':'Average hop count',\
                  'aveBacklog':'Per-node queue lengths'}
    
    for item in ['aveDelay','aveDRate','aveHop','aveBacklog']:
        for rate,result in results:
            entry = [result[key][item] for key in gobalRateList]
            py.plot(gobalRateList,entry,label ='r=%.1f'%rate)
   
        py.xlabel("$\lambda$")
        py.ylabel(labels[item])
        py.legend(loc=0)
        py.savefig('PaperThree_SA_'+item)
        py.close()

def CounterTest(step = 10000):
    injectRate = 1
    factory = GridNetworkFactory(makeCNode(0),Queues)
    factory.constructNetwork(8,8)\
        .setFlow(Flow((0,0),(0,7),injectRate))\
        .setFlow(Flow((7,0),(7,7),injectRate))
                                
    network = factory.getNetwork()

    packetFactory = PacketFactory()
    simulator = \
    Simulator(network,step,ConstLinkRateGenerator(1),packetFactory)
    simulator.run()
    #simulator.printNetwork()
    stat = simulator.getStaticsInfo()
    print stat



def otherTest():
    factory = GridNetworkFactory(makeSimpleNode(),Queues)
    resultBP = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeNewNode(0.8),NewQueues)
    resultLQ = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeNewNode(0.8),TestQueues)
    resultLQ2 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    factory = GridNetworkFactory(makeNewNode(0.8),TestSquareQueues)
    resultLQ3 = mainProcessCtrl(factory=factory,rateList=gobalRateList,threadNum=3)

    labels = {'aveDelay':'Average end-to-end delay',\
                  'aveDRate':'Delivery rate',\
                  'aveHop':'Average hop count',\
                  'aveBacklog':'Per-node queue lengths'}
    
    for item in ['aveDelay','aveDRate','aveHop','aveBacklog']:
        
        entry = [resultBP[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-o',label ='bp')
    
        entry = [resultLQ[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-v',label ='original')
        
        entry = [resultLQ2[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-x',label ='doubleRule')

        entry = [resultLQ3[key][item] for key in gobalRateList]
        py.plot(gobalRateList,entry,'-+',label ='squareRule')
        
        py.xlabel("$\lambda$")
        py.ylabel(labels[item])
        py.grid(True)
        py.legend(loc=0)
        py.savefig('otherTest_'+item)
        py.close()

if __name__ == "__main__":
 

    #mainProcessCtrl([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1],3)
    #rateVsDelayTest()
    #differentOMNodeModeTest()
    #OMNodeVSMNodeTest()
    #Test()

    #CounterTest()
    #PerodicPossiblityLearningVsPressure()
    #learningVsPressure()

    #newTest()

    #NewQueuesTest()

    
    #NewQueuesWithLimitsTest()

    #paperOneTestSA()
   #PaperThree_NewQueuesWithLimitsTest_SA()
    #otherTest()
    paperOneTestDA()
    #PaperTwoTest_DA()
    #PaperThree_NewQueuesTest_DA()
    #Test()
