import csv
import math
import scipy as sp
import matplotlib 
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
import datetime
import networkx as nx

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from modulesTouristLocal import *


#### Loading the databeses from Yelp academic dataset

Business = pd.read_csv('yelp_academic_dataset_business.csv')

Reviews = pd.read_csv('yelp_academic_dataset_review.csv')

#users = pd.read_csv('yelp_academic_dataset_user.csv')

####

B = RemoveDottedAttributes(Business) 

RestaurantsList= in_category(B,['Restaurants']) 

Restaurants = RetainList(B,RestaurantsList)


# montreal
#latMx = 45.8
#latMn = 45.3
#longMx = -73.2
#longMn = -74

# Charlotte
#latMx = 35.5
#latMn = 34.9
#longMx = -80.5
#longMn = -81.3

# Madison
latMx = 43.6
latMn = 42.4
longMx = -88
longMn = -91

X = Restaurants[Restaurants.latitude<latMx]
X = X[X.latitude>latMn]
X = X[X.longitude>longMn]
X = X[X.longitude<longMx]

b_id_List = find_b_id(X)

append_reviewInfo(X,Reviews)

userDict = create_user_dict(X)


ATs,ALs = user_matrices_strict(X,userDict)
#ATl,ALl = user_matrices_lineant(X,userDict)



AL, AT = isolate_T_from_L(ALl,ATl)


Aiimin = 5  # minimum number of likes by locals/tourists 
Aijmin = 2  # minimum number of common local/tourist likers between two businesses


iLocalNetwork, iTouristNetwork, indL, indT = plot_TLnes(AL,AT,X,Aiimin,Aijmin)

GL, GT = get_netXLT(X,AL,AT,Aiimin,Aijmin,indL,indT)


# write json formatted data
dL = json_graph.node_link_data(GL) # node-link format to serialize
# write json
json.dump(dL, open('node_linkGL_Madison.json','w'))

# write json formatted data
dT = json_graph.node_link_data(GT) # node-link format to serialize
# write json
json.dump(dT, open('node_linkGT_Ch.json','w'))


