import networkx as nx
import matplotlib.pyplot as plt
import json
import pprint as p
from networkx.readwrite import json_graph

def load(fileName):
	with open(fileName+'.json') as json_file: 
		topology = json.load(json_file)
	F = json_graph.node_link_graph(topology)	
	return F

def save(topology):
	data = json_graph.node_link_data(topology)	
	with open('topology.json', 'w') as outfile:  
		json.dump(data, outfile)	   


def createFlow(F, source, destiny, flow, flows, id):
	currentSourceCapacity = F.node[source]['demand']
	currentDestinyCapacity = F.node[destiny]['demand']
	F.node[source]['demand'] = currentSourceCapacity+(-flow)
	F.node[destiny]['demand'] = currentDestinyCapacity+(flow)
	flowCost, flowDict = nx.capacity_scaling(F, capacity='current_capacity')
	print(flowDict)
	for i in flowDict:
		for j in flowDict[i]:
			currentCapacity = F.edge[i][j]['current_capacity']
			F.edge[i][j]['current_capacity'] =  currentCapacity-flowDict[i][j]
	flows[id] = flowDict		   
	F.node[source]['demand'] = 0
	F.node[destiny]['demand'] = 0
	return F, flows

def destroyFlow(F, flows, id):
	if id in flows:
		for i in flows[id]:
			for j in flows[id][i]:
				currentCapacity = F.edge[i][j]['current_capacity']
				F.edge[i][j]['current_capacity'] =  currentCapacity+flows[id][i][j]
		del flows[id]		
	else:
		print("Invalid id")
	return F, flows

def listId(flows):
	for key, value in flows.items():
		print("ID: ", key, " - Value : ", value)

# def add(F,):
# 	for i in flowDict:
# 		for j in flowDict[i]:
# 			if not bool(F.node[i]['teste']):

# 			print(F.node[i]['teste'][i][j])

# G=nx.DiGraph()

# G.add_node(0, id=0, teste={}, demand=0, ip='127.0.0.0')
# G.add_node(1, id=1, teste={}, demand=0, ip='127.0.0.1')
# G.add_node(2, id=2, teste={}, demand=0, ip='127.0.0.2')
# G.add_node(3, id=3, teste={}, demand=0, ip='127.0.0.3')

# G.add_edge(0,1, capacity=10, current_capacity=10, weight=1)
# G.add_edge(0,3, capacity=9, current_capacity=9, weight=1)
# G.add_edge(0,2, capacity=8, current_capacity=8, weight=1)
# G.add_edge(1,2, capacity=7, current_capacity=7, weight=1)
# G.add_edge(2,3, capacity=6, current_capacity=6, weight=1)

# save(G)
F = load("topology")
count = 0
flows = {}
while True:
    try:
        option=int(input('1 - Create Flow  2 - Delete Flow  3 - List Valid Ids  4 - Draw  5 - Exit: '))
        if option == 1:
        	print("---------- CREATING FLOW ----------")
        	source=int(input('Insert source: '))
        	destiny=int(input('Insert destiny: '))
        	flow=int(input('Insert flow: '))
        	F, flows = createFlow(F,source,destiny,flow, flows, count)
        	print(flows)
        	count=count+1
        	print(F.edge[0][2])
        	print(F.edge[0][1])
        	print(F.edge[1][2])
        	#(G.edge[1]['teste'])[1]=2
        	# print(G.edges())
        	# print(G.edge[1][teste][1])            
        if option == 2:
        	print("---------- DESTROYING FLOW ----------")
        	id=int(input('Insert id: '))
        	F, flows = destroyFlow(F,flows, id)
        	print(F.edge[0][2])
        	print(F.edge[0][1])
        	print(F.edge[1][2])
        if option == 3:
        	print("---------- LIST ----------")
        	listId(flows)
        if option == 4:
            print("---------- DRAW ----------")
            pos=nx.circular_layout(F)
            nx.draw(F, pos, node_size=3000)
            node_labels = nx.get_node_attributes(F, 'ip')
            n = {}
            for i in node_labels:
            	n[i] = str(i) + "\n" + str(node_labels[i])
            nx.draw_networkx_labels(F, pos, labels=n, font_size=10, font_weight='bold')
            edge_labels = nx.get_edge_attributes(F,'current_capacity')
            edge_labels2 = nx.get_edge_attributes(F,'capacity')
            d = {}
            for i in edge_labels:
            	d[i] = str(edge_labels[i]) + "/" + str(edge_labels2[i])
            nx.draw_networkx_edge_labels(F, pos, edge_labels=d , font_color='blue', font_size=12, font_weight='bold')
            plt.show() 	
        if option == 5:
        	print("---------- EXIT ----------")
        	break	    
    except ValueError:
        print("Not a number")


# nx.draw(F)
# plt.show()