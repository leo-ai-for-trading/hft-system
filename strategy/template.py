import collections

########### TEMPLATE CLASSES #################################
class Graph:
    def __init__(self):
        self.neighbors = []
        self.name2node = {}
        self.node2name = []
        self.weight = []
    
    def __len__(self):
        return len(self.node2name)
    def __getitem__(self,v):
        return self.neighbors[v]
    
    def add_node(self,name):
        assert name not in self.name2node
        self.name2node[name] = len(self.name2node)
        self.node2name.append(name)
        self.neighbors.append([]) 
        self.weight.append({})
        return self.name2node[name]
    
    def add_edge(self,name_u,name_v,weight_uv=None):
        self.add_arc(name_u, name_v, weight_uv) 
        self.add_arc(name_v, name_u, weight_uv)

    def add_arc(self,name_u,name_v,weight_uv=None):
        u = self.name2node[name_u]
        v = self.name2node[name_v] 
        self.neighbors[u].append(v)
        self.weight[u][v] = weight_uv

    def bellman_ford(self, weight, source=0):
        graph = self
        n = len(graph)
        dist = [float('inf')] * n
        prec = [None]*n
        dist[source] = 0
        for nb_iterations in range(n):
            changed = False
            for node in range(n):
                for neighbor in graph[node]:
                    alt = dist[node] + weight[node][neighbor]
                    if alt < dist[neighbor]:
                        dist[neighbor] = alt
                        prec[neighbor] = node
                        changed = True
                if not changed:
                    return dist,prec,False
        return dist, prec, True
#######################################################