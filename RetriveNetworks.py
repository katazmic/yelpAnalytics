import numpy as np
import pandas as pd 
import datetime
import matplotlib.pyplot as plt
import networkx as nx
from networkx.readwrite import json_graph
import json 

from modulesTouristLocal import *

city = 'Montreal_aij3' # Montreal Phoenix Vegas Montreal_aij3 Charlotte 

GT_filename = 'node_linkGT_%s.json' %(city)
GL_filename  = 'node_linkGL_%s.json' %(city)


with open(GT_filename) as data_file:    
    dataT = json.load(data_file)

GT = json_graph.node_link_graph(dataT)

with open(GL_filename) as data_file:    
    dataL = json.load(data_file)

GL = json_graph.node_link_graph(dataL)

plot_connections(GL,GT)

plt.show()



