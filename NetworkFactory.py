__metaclass__ = type
from Node import Node
from Queues import Queues
from Flow import Flow
class NetworkFactory:

    def __init__(self):
        self.network = dict()
        pass

    def getNetWork(self):
        return self.netWork

    def setFlows(self,*flows):
        pass


class GridNetworkFactory(NetworkFactory):

    def __init__(self,makeNodeFunc,queuesType):
        self.queuesType = queuesType
        self.makeNodeFunc = makeNodeFunc
        super(GridNetworkFactory,self).__init__()
    
    
    def getNetwork(self):
        return self.network

    def constructNetwork(self,x,y):
        self.network = dict()
        assert x*y > 0,\
            "node number must > 0"

        # generate all nodes in netWork
        for i in range(x):
            for j in range(y):
                self.network[(i,j)] = self.makeNodeFunc(ID=(i,j),flow=None,\
                                               queuesType=self.queuesType)

        # four possible (x,y) in grid setting,  
        # eg (1,1) -> (2,1), (0,1), (1,2), (1,0)
        # the if make sure that some (x,y) is not in the netWork
        for (x,y),node in self.network.iteritems():         
            for key in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
                if self.network.has_key(key):
                    node.neigbours[key] = self.network[key]

        return self

    def setFlow(self,*flows):
        for flow in flows:
            assert flow.source in self.network and \
                flow.destination in self.network,\
                "source and dest must be in network"
            self.network[flow.source].setFlow(flow)
        return self


if __name__ == "__main__":
    factory = GridNetworkFactory(Node,Queues)
    factory.constructNetwork(3,3).setFlow(Flow((0,0),(2,2),1),
                                          Flow((0,1),(2,1),1))
    network1 = factory.getNetwork()
    
    print network1


    

