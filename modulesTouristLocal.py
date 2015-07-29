import csv
import math
import scipy as sp
import numpy as np
import pandas as pd 
import datetime

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import networkx as nx
from networkx.readwrite import json_graph
import json 
import geopandas as gpd


from dateutil import parser



def RemoveDottedAttributes(Business):
    needed = []
    for i in range(len(Business.columns)):
        if '.' not in Business.columns[i]:
            needed.append(i)
    B = Business[Business.columns[needed]]
    return B



def find_types_name(Data,name):
    list = []
    for i in range(len(Data)):
        if Data[name][Data.index[i]] not in list:
            list.append(Data[name][Data.index[i]])
    return list

def in_category(Data,cat):
    list = []
    l_cat = find_types_name(Data,'categories')
    for i in l_cat:
        for icat in cat:
            if icat in eval(i) and i not in list:
                list.append(i)
    return list


def RetainList(B,sdf):
    B_new = B
    todrop= []
    for i in range(len(B)):
        if B.categories[i] not in sdf:
            todrop.append(i)
    B_new.drop(B_new.index[todrop],axis=0, level=None, inplace=True, errors='raise')
    return B_new

def find_b_id(B):
    list=[]
    for i in B.business_id:
        list.append(i)
    return list


def get_all_reviews(R, b_id):
    R_new = R
    todrop= []
    for i in range(len(R)):
        if R.business_id[R.index[i]] not in b_id:
            todrop.append(i)
    R_new.drop(R_new.index[todrop],axis=0, level=None, inplace=True, errors='raise')
    return R_new          

def add_emp_list(B,name):
    ls = []
    for i in range(len(B)):
        ls.append([])
    B[name] = pd.Series(ls, index=B.index)

def append_reviewInfo(B,R):
    add_emp_list(B,'RvDate')
    add_emp_list(B,'RvStar')
    add_emp_list(B,'RvUserID')
    for i in range(len(B)):
        print i*1./len(B)
        B.RvStar[B.index[i]]=[]
        B.RvDate[B.index[i]] = []
        B.RvUserID[B.index[i]] = []
        LsInx = R.index[R.business_id==B.business_id[B.index[i]]]
        for j in LsInx:
            B.RvStar[B.index[i]].append(R.stars[j])
            B.RvDate[B.index[i]].append(R.date[j])
            B.RvUserID[B.index[i]].append(R.user_id[j])
    
    return 1



def create_user_dict(V): 
    user = {}
    user_idL = []
    for i in range(len(V)):
        j=0
        while j <len(V.RvUserID[V.index[i]]):
            usrID = V.RvUserID[V.index[i]][j]
            if usrID in user_idL:
                user[usrID]['business_id'].append(V.business_id[V.index[i]])
                user[usrID]['rate'].append(V.RvStar[V.index[i]][j])
                user[usrID]['date'].append(parser.parse(V.RvDate[V.index[i]][j]).toordinal())
            
            else:
                user_idL.append(usrID)
                user[usrID] = {}
                user[usrID]['business_id'] = []
                user[usrID]['business_id'].append(V.business_id[V.index[i]])
                user[usrID]['rate'] = []
                user[usrID]['rate'].append(V.RvStar[V.index[i]][j])
                user[usrID]['date'] = []
                user[usrID]['date'].append(parser.parse(V.RvDate[V.index[i]][j]).toordinal());
                user[usrID]['dateSpan'] = 0
                user[usrID]['stdDatesDiff'] =  0
                user[usrID]['meanDatesDiff'] = 0
                user[usrID]['firstRevDate'] = 0
                user[usrID]['isLocal'] = 'n/a'
                user[usrID]['isTourist'] = 'n/a'
            j=j+1
        print i*1./len(V)
    for i in user_idL:
        lsD = np.sort(np.asarray(user[i]['date']))
        user[i]['dateSpan'] = max(lsD)-min(lsD)
        diff = sorted(list(lsD[1:]-lsD[0:-1]),reverse = True)
        user[i]['isLocal'] = 'n/a'
        user[i]['isTourist'] = 'n/a'
        if len(diff)>0:
            while diff[-1]==0 and len(diff)>1:
                popped = diff.pop()
            user[i]['stdDatesDiff'] =  np.sqrt(np.std(diff))
            user[i]['meanDatesDiff'] = np.mean(diff)
            user[i]['firstRevDate'] = min(lsD)
            if max(lsD)-min(lsD)>30:
                user[i]['isLocal'] = 'maybe'
                if np.sqrt(np.std(diff))/np.mean(diff) < 2 or len(diff)>30:
                    user[i]['isLocal'] = 'yes'
                    user[i]['isTourist']='no'
            else:
                user[i]['isTourist'] = 'maybe'
                if diff[0] < 5:
                    user[i]['isTourist'] = 'yes'
                    user[i]['isLocal']='no'
    return user


def user_matrices_strict(B,user):
    
    AT = np.zeros((len(B),len(B)))
    AL = np.zeros((len(B),len(B)))
    
    for i in range(len(B)-1):
        list1 = B.RvUserID[B.index[i]]
        listL = []
        listT = []
        likedL = 0
        likedT = 0
        k=0
        for l in list1:
            if user[l]['isLocal'] == 'yes' :
                listL.append(l)
                if B.RvStar[B.index[i]][k] > 3:
                    likedL = likedL +1
            if user[l]['isTourist'] == 'yes':
                listT.append(l)
                if B.RvStar[B.index[i]][k] > 3:
                    likedT = likedT +1
            k=k+1
        j=i+1
        AT[i,i] = likedT
        AL[i,i] = likedL
        while j<len(B):
            list2 = B.RvUserID[B.index[j]]
            aijT = len(set(listT).intersection(list2))
            AT[i,j]= aijT
            AT[j,i] = aijT
            aijL = len(set(listL).intersection(list2))
            AL[i,j]= aijL
            AL[j,i] = aijL
            j=j+1
        print i*1./len(B)
    return AT, AL



def user_matrices_lineant(B,user):
    
    AT = np.zeros((len(B),len(B)))
    AL = np.zeros((len(B),len(B)))
    
    for i in range(len(B)-1):
        list1 = B.RvUserID[B.index[i]]
        listL = []
        listT = []
        likedL = 0
        likedT = 0
        k=0
        for l in list1:
            if user[l]['isLocal'] == 'yes' or user[l]['isLocal'] == 'maybe':
                listL.append(l)
                if B.RvStar[B.index[i]][k] > 3:
                    likedL = likedL +1
            if user[l]['isTourist'] == 'yes' or user[l]['isTourist'] == 'maybe':
                listT.append(l)
                if B.RvStar[B.index[i]][k] > 3:
                    likedT = likedT +1
            k=k+1
        j=i+1
        AT[i,i] = likedT
        AL[i,i] = likedL
        while j<len(B):
            list2 = B.RvUserID[B.index[j]]
            aijT = len(set(listT).intersection(list2))
            AT[i,j]= aijT
            AT[j,i] = aijT
            aijL = len(set(listL).intersection(list2))
            AL[i,j]= aijL
            AL[j,i] = aijL
            j=j+1
        print i*1./len(B)
    
    return AT, AL

def isolate_T_from_L(ALs,ATs):
    AL_new = np.zeros((len(ALs),len(ALs)))
    AT_new = np.zeros((len(ALs),len(ALs)))
    for i in range(len(ALs)):
        j=i+1
        if ALs[i][i] > 20*ATs[i][i]:
            AL_new[i][i] = ALs[i][i]
            while j< (len(ALs)):
                if ALs[i][j] !=0 and ATs[i][j] ==0:
                    AL_new[i][j] = ALs[i][j]
                    AL_new[j][i] = ALs[i][j]
                j = j+1
        if ATs[i][i] > 0.2*ALs[i][i]:
            AT_new[i][i] = ATs[i][i]
            while j< (len(ATs)):
                if ATs[i][j] !=0:
                    AT_new[i][j] = ATs[i][j]
                    AT_new[j][i] = ATs[i][j]
                j = j+1
        print i*1./len(ALs)
    return AL_new, AT_new



################


def plot_TLnes(AL_new,AT_new,B,Aiimin,Aijmin):
    
    A = AL_new;
    clrin = 'blue'
    iLocalNetwork = []
    indL = []
    for i in range(len(A)):
        j=i+1
        if A[i][i] > Aiimin:
            while j<len(A):
                if A[i][j] > Aijmin and A[j][j] > Aiimin:
                    #wth = 4.*A[i][j]/A.max()
                    #plt.plot([B.longitude[B.index[i]],B.longitude[B.index[j]]],[B.latitude[B.index[i]],B.latitude[B.index[j]]],linewidth = wth,color = clrin)
                    if i not in indL:
                        iLocalNetwork.append(B.index[i])
                        indL.append(i)
                    print i
                j=j+1
    A = AT_new;
    clrin = 'red'
    iTouristNetwork = []
    indT = []
    for i in range(len(A)):
        j=i+1
        if A[i][i] > Aiimin:
            while j<len(A):
                if A[i][j] > Aijmin and A[j][j] > Aiimin:
                     #  plt.plot([B.longitude[B.index[i]],B.longitude[B.index[j]]],[B.latitude[B.index[i]],B.latitude[B.index[j]]],linewidth = wth,color = clrin)
                    if i not in indT:
                        iTouristNetwork.append(B.index[i])
                        indT.append(i)
                    print i
                j=j+1   
    return iLocalNetwork, iTouristNetwork, indL, indT


############




def get_netXLT(B,AL,AT,Aiimin,Aijmin,indL,indT):
    A = AL
    GL = nx.Graph()
    for i in indL:
        GL.add_node(i,labels = B.name[B.index[i]], pos = [B.longitude[B.index[i]],B.latitude[B.index[i]]], node_size = A[i][i])
        print GL.node[i]
    for i in indL:
        for j in indL:
            if j>i and A[i][j]>Aijmin:                
                GL.add_edge(i,j,width = A[i][j])
    A = AT
    GT = nx.Graph()
    for i in indT:
        GT.add_node(i,labels = B.name[B.index[i]], pos = [B.longitude[B.index[i]],B.latitude[B.index[i]]], node_size = A[i][i])
        print GT.node[i]
    for i in indT:
        for j in indT:
            if j>i and A[i][j]>Aijmin:                
                GT.add_edge(i,j,width = A[i][j])
    return GL, GT




##############



def plot_connections(GL,GT):
    labelsGL = {}
    node_sizeGL = []
    posGL = {}
    node_colorL = 'b'
    for i in GL:
        labelsGL[i] = GL.node[i]['labels']
        posGL[i] = GL.node[i]['pos']
        node_sizeGL.append(GL.node[i]['node_size'])
    M= max(node_sizeGL)
    for i in range(len(node_sizeGL)):
        node_sizeGL[i] = node_sizeGL[i]*250./M
    weightsL = [GL[u][v]['width'] for u,v in GL.edges()]
    Mw = max(weightsL)
    for i in range(len(weightsL)):
        weightsL[i] = weightsL[i]/Mw
    nx.draw_networkx(GL, pos=posGL, node_size = node_sizeGL , labels = labelsGL, with_labels=True,font_size = 20, node_color = node_colorL,width = weightsL, edge_color = node_colorL ,alpha = 0.5)
    labelsGT = {}
    node_sizeGT = []
    posGT = {}
    node_colorT = 'r'
    for i in GT:
        labelsGT[i] = GT.node[i]['labels']
        posGT[i] = GT.node[i]['pos']
        node_sizeGT.append(GT.node[i]['node_size'])
    M= max(node_sizeGT)
    for i in range(len(node_sizeGT)):
        node_sizeGT[i] = node_sizeGT[i]*250./M
    weightsT = [GT[u][v]['width'] for u,v in GT.edges()]
    Mw = max(weightsT)
    for i in range(len(weightsT)):
        weightsT[i] = weightsT[i]/Mw
    nx.draw_networkx(GT, pos=posGT, node_size = node_sizeGT , labels = labelsGT, with_labels=True,font_size = 20,node_color = node_colorT, width = weightsT , edge_color = node_colorT, alpha = 0.5)
    
    return 1

"""
    df = gpd.read_file('phoneix_arizona_roads_gen1.geojson')
    df.plot(color = '#4C4C4C', alpha = 0.1)
    
    nx.draw_networkx(GT, pos=posGT, node_size = node_sizeGT , labels = labelsGT, with_labels=True,font_size = 20,node_color = node_colorT, width = weightsT , edge_\
    color = node_colorT, alpha = 1.0)
    
    nx.draw_networkx(GL, pos=posGL, node_size = node_sizeGL , labels = labelsGL, with_labels=True,font_size = 20, node_color = node_colorL,width = weightsL, edge_c\
    olor = node_colorL ,alpha = 1.0)

    
    # write json formatted data                                                                                                                                     
    d = json_graph.node_link_data(GL) # node-link format to serialize                                                                                               
    # write json                                                                                                                                                    
    json.dump(d, open('node_linkGL.json','w'))
    
    d = json_graph.adjacency_data(GL) # node-link format to serialize                                                                                               
    # write json                                                                                                                                                    
    json.dump(d, open('adjacencyGL.json','w'))
    
    
    # write json formatted data                                                                                                                                     
    d = json_graph.node_link_data(GT) # node-link format to serialize                                                                                               
    # write json                                                                                                                                                    
    json.dump(d, open('node_linkGT.json','w'))
    
    d = json_graph.adjacency_data(GT) # node-link format to serialize                                                                                               
    # write json                                                                                                                                                    
    json.dump(d, open('adjacencyGT.json','w'))

    """

