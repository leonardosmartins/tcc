import networkx as nx
import matplotlib.pyplot as plt
import json
import pprint as p
from networkx.readwrite import json_graph
import os
from jinja2 import Environment, FileSystemLoader

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
        env = Environment(loader=FileSystemLoader(os.path.join('.', 'templates')))
        template1 = env.get_template('s1_commands-template.txt')
        template2 = env.get_template('s5_commands-template.txt')
        arq1 = open("util/s1_commands.txt", "w")
        arq2 = open("util/s5_commands.txt", "w")
        currentSourceCapacity = F.node[source]['demand']
        currentDestinyCapacity = F.node[destiny]['demand']
        F.node[source]['demand'] = currentSourceCapacity+(-flow)
        F.node[destiny]['demand'] = currentDestinyCapacity+(flow)
        flowCost, flowDict = nx.capacity_scaling(F, capacity='current_capacity')
        print(flowDict)
        for i in flowDict:
                for j in flowDict[i]:
                        currentCapacityij = F.edge[i][j]['current_capacity']
                        currentCapacityji = F.edge[j][i]['current_capacity']
                        F.edge[i][j]['current_capacity'] = currentCapacityij-flowDict[i][j]
                        F.edge[j][i]['current_capacity'] = currentCapacityji-flowDict[i][j]
        arq1.write(template1.render(source_ip=F.node[source]['ip'], destination_ip=F.node[destiny]['ip'], first=format(F.edge[2][3]['capacity']-F.edge[2][3]['current_capacity'], '08b'), second=format(F.edge[2][4]['capacity']-F.edge[2][4]['current_capacity'], '08b'), third=format(F.edge[2][5]['capacity']-F.edge[2][5]['current_capacity'], '08b')))
        arq2.write(template2.render(source_ip=F.node[destiny]['ip'], destination_ip=F.node[source]['ip'], first=format(F.edge[2][3]['capacity']-F.edge[2][3]['current_capacity'], '08b'), second=format(F.edge[2][4]['capacity']-F.edge[2][4]['current_capacity'], '08b'), third=format(F.edge[2][5]['capacity']-F.edge[2][5]['current_capacity'], '08b')))
        flows[id] = flowDict		   
        F.node[source]['demand'] = 0
        F.node[destiny]['demand'] = 0
        arq1.close()
        arq2.close()
        return F, flows

def destroyFlow(F, flows, id):
    template = env.get_template('delete_commands-template.txt')
    arq = open("util/delete_commands.txt", "w") 
	if id in flows:
		for i in flows[id]:
			for j in flows[id][i]:
                                currentCapacityij = F.edge[i][j]['current_capacity']
                                currentCapacityji = F.edge[i][j]['current_capacity']
                                F.edge[i][j]['current_capacity'] = currentCapacityij+flows[id][i][j]
                                F.edge[j][i]['current_capacity'] = currentCapacityji+flows[id][i][j]
        arq.write(template.render(handle=id))
        arq.close()
        del flows[id]		
	else:
		print("Invalid id")
	return F, flows

def listId(flows):
	for key, value in flows.items():
		print("ID: ", key, " - Value : ", value)

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
                count=count+1
                os.system("python tools/apply_commands.py")            
        if option == 2:
                print("---------- DESTROYING FLOW ----------")
                id=int(input('Insert id: '))
                F, flows = destroyFlow(F,flows, id)
                os.system("python tools/apply_commands-delete.py")
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
