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
        template = env.get_template('commands-template.txt')
        currentSourceCapacity = F.node[source]['demand']
        currentDestinyCapacity = F.node[destiny]['demand']
        F.node[source]['demand'] = currentSourceCapacity+(-flow)
        F.node[destiny]['demand'] = currentDestinyCapacity+(flow)
        flowCost, flowDict = nx.capacity_scaling(F, capacity='current_capacity')
        #print(flowDict)
        for i in flowDict:
                for j in flowDict[i]:
                        currentCapacityij = F.edge[i][j]['current_capacity']
                        F.edge[i][j]['current_capacity'] = currentCapacityij-flowDict[i][j]
        F.node[source]['demand'] = 0
        F.node[destiny]['demand'] = 0
        currentSourceCapacity2 = F.node[destiny]['demand']
        currentDestinyCapacity2 = F.node[source]['demand']
        F.node[source]['demand'] = currentSourceCapacity2+(flow)
        F.node[destiny]['demand'] = currentDestinyCapacity2+(-flow)
        flowCost2, flowDict2 = nx.capacity_scaling(F, capacity='current_capacity')
        #print(flowDict2)
        for i in flowDict2:
            for j in flowDict2[i]:
                currentCapacityij = F.edge[i][j]['current_capacity']
                F.edge[i][j]['current_capacity'] = currentCapacityij-flowDict2[i][j]
        F.node[source]['demand'] = 0
        F.node[destiny]['demand'] = 0
        for i in flowDict:
            if F.node[i]['isHost'] != 1:
                pathGo = [0] * F.node[i]['numPorts']
                pathBack = [0] * F.node[i]['numPorts']
                for j in flowDict[i]:
                    pathGo[F.edge[i][j]['porigem']] = flowDict[i][j]
                    pathBack[F.edge[i][j]['porigem']] = flowDict2[i][j]
                arq = open("util/"+str(i)+"-commands.txt", 'w')
                arq.write(template.render(source_ip=F.node[source]['ip'], destination_ip=F.node[destiny]['ip'], numP = F.node[i]['numPorts'], listPath=pathGo)+"\n" )
                arq.write(template.render(source_ip=F.node[destiny]['ip'], destination_ip=F.node[source]['ip'], numP = F.node[i]['numPorts'], listPath=pathBack))    
                arq.close()
        flows[id] = flowDict
        flows[id+1] = flowDict2		   
        return F, flows

def destroyFlow(F, flows, id):
    env = Environment(loader=FileSystemLoader(os.path.join('.', 'templates')))
    template = env.get_template('delete_commands-template.txt')
    arq = open("util/delete_commands.txt", "w") 
    if id%2 == 0:
        if id in flows:
            for i in flows[id]:
                for j in flows[id][i]:
                    currentCapacityij = F.edge[i][j]['current_capacity']
                    currentCapacityji = F.edge[i][j]['current_capacity']
                    F.edge[i][j]['current_capacity'] = currentCapacityij+flows[id][i][j]
                    F.edge[j][i]['current_capacity'] = currentCapacityji+flows[id][i][j]
            del flows[id]		
        else:
            print("Invalid id")

        if id+1 in flows:
            for i in flows[id+1]:
                for j in flows[id+1][i]:
                    currentCapacityij = F.edge[i][j]['current_capacity']
                    currentCapacityji = F.edge[i][j]['current_capacity']
                    F.edge[i][j]['current_capacity'] = currentCapacityij+flows[id+1][i][j]
                    F.edge[j][i]['current_capacity'] = currentCapacityji+flows[id+1][i][j]
            del flows[id+1]       
        else:
            print("Invalid id")
        
        arq.write(template.render(handle=id)+"\n")
        arq.write(template.render(handle=id+1)+"\n")
        arq.close()
                

    else:
        if id in flows:
            for i in flows[id]:
                for j in flows[id][i]:
                    currentCapacityij = F.edge[i][j]['current_capacity']
                    currentCapacityji = F.edge[i][j]['current_capacity']
                    F.edge[i][j]['current_capacity'] = currentCapacityij+flows[id][i][j]
                    F.edge[j][i]['current_capacity'] = currentCapacityji+flows[id][i][j]
            del flows[id]       
        else:
            print("Invalid id")

        if id-1 in flows:
            for i in flows[id-1]:
                for j in flows[id-1][i]:
                    currentCapacityij = F.edge[i][j]['current_capacity']
                    currentCapacityji = F.edge[i][j]['current_capacity']
                    F.edge[i][j]['current_capacity'] = currentCapacityij+flows[id-1][i][j]
                    F.edge[j][i]['current_capacity'] = currentCapacityji+flows[id-1][i][j]
            del flows[id-1]       
        else:
            print("Invalid id")
        
        arq.write(template.render(handle=id)+"\n")
        arq.write(template.render(handle=id-1)+"\n")
        arq.close()  

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
                count=count+2
                #os.system("python tools/apply_commands.py")            
        if option == 2:
                print("---------- DESTROYING FLOW ----------")
                id=int(input('Insert id: '))
                F, flows = destroyFlow(F,flows, id)
                #os.system("python tools/apply_commands-delete.py")
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
