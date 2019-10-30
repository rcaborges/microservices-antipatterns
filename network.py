import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
from collections import Counter
import networkx as nx
#import powerlaw
import operator

def write_dict(d,file_name):
    with open(file_name, 'w') as f:  # Just use 'w' mode in 3.x
        for k, v in d.items():
            f.write(str(k) + ','+ str(v) + '\n')
        #w = csv.DictWriter(f, d.keys())
        #w.writeheader()
        #w.writerow(d)
    f.close()

def write_list(l, file_name):
    with open(file_name, 'w') as fp:
            fp.write('\n'.join('%s,%s,%s' % x for x in l))

def build_network(df, edges, nodes):

    ##### BUILDING NETWORK ######
    
    column_edge = edges
    column_ID = nodes
    
    data_to_merge = df[[column_ID, column_edge]].dropna(subset=[column_edge]).drop_duplicates() # select columns, remove NaN
    #data_to_merge = df[[column_ID, column_edge]]
    
    # To create connections between people who have the same number,
    # join data with itself on the 'ID' column.
    data_to_merge = data_to_merge.merge(
        data_to_merge[[column_ID, column_edge]].rename(columns={column_ID:column_ID+"_2"}), 
        on=column_edge
    )
    
    # By joining the data with itself, people will have a connection with themselves.
    # Remove self connections, to keep only connected people who are different.
    d = data_to_merge[~(data_to_merge[column_ID]==data_to_merge[column_ID+"_2"])] \
        .dropna()[[column_ID, column_ID+"_2", column_edge]]
        
    # To avoid counting twice the connections (person 1 connected to person 2 and person 2 connected to person 1)
    # we force the first ID to be "lower" then ID_2
    d.drop(d.loc[d[column_ID+"_2"]<d[column_ID]].index.tolist(), inplace=True)
    print('pre pro done...')
    
    #########################
    
    G = nx.from_pandas_edgelist(df=d, source=column_ID, target=column_ID+'_2', edge_attr=column_edge)
    G.add_nodes_from(nodes_for_adding=df.class_name.tolist())
    #G.add_nodes_from(nodes_for_adding=list(df[nodes].values()))
    print('#nodes:', len(G.nodes()), 'and', '#edges:', len(G.edges()))
    
    degrees = [val for (node, val) in G.degree()]
    np.save("data/degrees.npy",degrees)
    degree_values = sorted(set(degrees))
    histogram = [degrees.count(i)/float(nx.number_of_nodes(G)) for i in degree_values]
    
    fig, ax = plt.subplots()
    # the histogram of the data
    n, bins, patches = plt.hist(degrees, 50)
    #plt.bar(range(len(histogram)),histogram)
    #plt.xticks(range(len(histogram)), degree_values)
    plt.xlabel('Degree')
    plt.ylabel('Fraction of Nodes')
    plt.xlim(0,max(degree_values))
    #plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig("plot/nodes_degress.pdf")
    
    fig, ax = plt.subplots()
    plt.plot(range(len(histogram)),sorted(histogram, reverse=True),'o')
    plt.xticks(range(len(histogram)), degree_values)
    plt.xlabel('Degree')
    plt.ylabel('Fraction of Nodes')
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig("plot/power_law.pdf")
   

    closeness_centrality = nx.closeness_centrality(G)
    #print(closeness_centrality)
    write_dict(closeness_centrality,"data/closeness_centrality.csv")
    print('closeness done...')
    
    betweenness_centrality = nx.betweenness_centrality(G)
    #print(betweenness_centrality)
    write_dict(betweenness_centrality,"data/betweenness_centrality.csv")
    print('betweenness done...')
    
    degree_centrality = nx.degree_centrality(G)
    #print(degree_centrality)
    write_dict(degree_centrality,"data/degree_centrality.csv")
    print('centrality done...')
    
    fig, ax = plt.subplots()
    # the histogram of the data
    nx.draw(G)
    #plt.bar(range(len(histogram)),histogram)
    #plt.xticks(range(len(histogram)), degree_values)
    plt.tight_layout()
    #plt.show()
    plt.savefig("plot/net.pdf")
    
