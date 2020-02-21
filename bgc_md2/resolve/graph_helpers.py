
from functools import lru_cache,reduce
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import CSS4_COLORS,BASE_COLORS,TABLEAU_COLORS
from pygraphviz.agraph import AGraph
from typing import List,Set,Tuple,Callable
from copy import deepcopy
from frozendict import frozendict
from testinfrastructure.helpers import pp,pe

from .non_graph_helpers import  (
    #computable_mvars
	#,directly_computable_mvars
	input_mvars
	#,output_mvar
	,arg_set
	#,arg_set_set
	,all_mvars
	#,applicable_computers
	,all_computers_for_mvar
    ,pretty_name
)
def compset_2_string(compset):
    return '{'+",".join([pretty_name(c) for c in compset])+'}'

def node_2_string(node):
    return '{'+",".join([pretty_name(v) for v in node])+'}'

def nodes_2_string(node):
    return '[ '+",".join([node_2_string(n) for n in node])+' ]'

def edge_2_string(e):
    return "("+node_2_string(e[0])+','+node_2_string(e[1])+')'

def immutable_edge(edge):
    s,d,dat=edge
    return (s,d,frozendict(dat))

def graphs_equal(
        g1:nx.MultiDiGraph
        ,g2:nx.MultiDiGraph
    )->bool:
    s1=set(immutable_edge(e) for e in g1.edges(data=True)) 
    s2=set(immutable_edge(e) for e in g2.edges(data=True))
    return s1==s2

@lru_cache(maxsize=None) 
def arg_set_graph( 
        mvar :type,
        allComputers:Set[Callable]
    )->nx.MultiGraph:
    # return the subgraph of arg_name_sets for all computers that
    # return this mvar
    target=frozenset({mvar})
    g = nx.MultiDiGraph()
    g.add_node(target)
    for c in all_computers_for_mvar(mvar,allComputers):
        g.add_edge(arg_set(c), target,computers=frozenset({c}))
    return g

def product_graph(
        *graphs:Tuple[nx.MultiDiGraph]
    )->nx.MultiDiGraph:
    return reduce(lambda u,v:product_graph_2(u,v),graphs)

def product_graph_2(
        g1:nx.MultiDiGraph
        ,g2:nx.MultiDiGraph
    )->nx.MultiDiGraph:
    cp=nx.cartesian_product(g1,g2)
    prod=nx.MultiDiGraph()


    for edge in cp.edges(data=True):
        s_tup,d_tup,data=edge
        prod.add_edge(
            reduce(lambda acc,n :acc.union(n), s_tup)
            ,reduce(lambda acc,n :acc.union(n), d_tup)
            ,computers=data['computers'])
        
    return prod

def initial_sparse_powerset_graph(computers:Set[Callable])->nx.MultiDiGraph:
    spsg=nx.MultiDiGraph()
    allMvars = all_mvars(computers) 
    for v in allMvars:
        spsg.add_edges_from(arg_set_graph(v,computers).edges(data=True))
    return spsg

def update_step(
        spsg:nx.MultiDiGraph,
        computers:Set[Callable]
    )->nx.MultiDiGraph:
    spsg=deepcopy(spsg)
    start_nodes= [n for n in spsg.nodes() if len(spsg.in_edges(n))==0]
    #print(nodes_2_string(start_nodes)) 
    for node in start_nodes:
        print(tuple(v for v in node))
        pg=product_graph(*[arg_set_graph(v,computers) for v in node])
        spsg.add_edges_from(pg.edges(data=True))
        #spsg=nx.compose(spsg,pg)
    
    return spsg

def sparse_powerset_graph(
        computers:Set[Callable]
    )->nx.MultiDiGraph:
    spsg=initial_sparse_powerset_graph(computers)
    spsg_new=update_step(spsg,computers)
    while not(graphs_equal(spsg,spsg_new)):
        spsg_new=update_step(spsg,computers)
        spsg=spsg

    return spsg_new
class SequenceOfUpdates:
    def __iter__(self):
        self.a=1
        return self
    def __next__(self):
        x=self.a
        self.a+=1
        return x
    
def update_sequence(
        computers:Set[Callable]
        ,max_it:int
    )->List[nx.MultiDiGraph]:
    start_list=[initial_sparse_powerset_graph(computers)]
    def add_to_list(acc,_):
        last=acc[-1]
        new=update_step(last,computers)
        return acc+[new] if not(graphs_equal(last,new)) else []

    result_list=reduce(
        add_to_list(acc,x)
        ,range(max_int)
    )
    return result_list







def minimal_startnodes_for_single_var(
         spg:nx.Graph
        ,targetVar:type
    ):
    ''' spg is a sparse powerset Graph, which means that it only contains all one element sets as targets.'''
    # We first create a graph with the direction of the edges reversed
    targetSet=frozenset({targetVar})
    GR=spg.reverse()
    res=[p for p in nx.all_pairs_shortest_path(GR) if p[0]==targetSet]
    possible_startnodes=frozenset([n for n in res[0][1].keys()])
    print("possible_startnodes for",node_2_string(targetSet)," including supersets:",[node_2_string(n) for n in possible_startnodes])
    minimal_startnodes=remove_supersets(possible_startnodes)
    minimal_startnodes=[n for n in filter(lambda n: not(n.issuperset(targetSet)),minimal_startnodes)]
    return frozenset(minimal_startnodes)
    

def minimal_startnodes_for_node(
         spg:nx.Graph
        ,targetNode:Set[type]
    ):
    single_sets=[
            minimal_startnodes_for_single_var(spg,var) for var in targetNode
    ]
    possible_startnodes=cartesian_union(single_sets)
    minimal_startnodes=remove_supersets(possible_startnodes)
    return frozenset(minimal_startnodes)
    
    def filter_func(n):
        # remove every set that contains one of the variables we are looking for ...
        return not(any([ (v in n) for v in targetNode]))

    minimal_startnodes=[n for n in filter(filter_func,minimal_startnodes)]


def draw_multigraph_graphviz(allMvars,allComputers):
    # build initial multigraph
    # for visualization draw the directed Multigraph with the MVars as nodes
    # unfortunately it is not useful for connectivity computations
    # since all 'edges' defined by a computer c are misleading in the sense that 
    # we need the union of all the source variables of c to go to the target Mvar of c 
    # while the arrows suggest ways from any of the arguments...
    # for visualization it would helpful to draw all arcs belonging to the same computer
    # in the same color.
    # Since we do not compute anything from this graph we actually do not need a 
    # graph library
    # but can visualize it immediately with graphviz
    # We use a uniqud .draw('Multigraph.svg',prog="circo") # draw using circo
    colordict=TABLEAU_COLORS
    color_names=[n for n in colordict.keys()]
    computer_colors={c.__name__:color_names[i] for i,c in enumerate(allComputers)}
    A=AGraph(directed=True)
    A.node_attr['style']='filled'
    A.node_attr['shape']='circle'
    A.node_attr['fixedsize']='false'
    A.node_attr['fontcolor']='#FFFFFF'
    A.node_attr['color']='black'
    A.add_nodes_from([pretty_name(v) for v in allMvars])
    cols=['blue','red','green','orange'] 
    for v in allMvars:
        for c in all_computers_for_mvar(v,allComputers):
            ans=input_mvars(c)
            edges=[(pretty_name(an),pretty_name(v))  for an in ans]
            for e in edges:
                A.add_edge(e)
                Ae=A.get_edge(e[0],e[1])
                Ae.attr['color']=colordict[computer_colors[c.__name__]]
                Ae.attr['fontcolor']=colordict[computer_colors[c.__name__]]
                Ae.attr['label']=c.__name__
    #print(A.string()) # print to screen
    A.draw('Multigraph.svg',prog="circo") # draw using circo




def draw_multigraph_matplotlib(allMvars,allComputers):
    # only for visualization draw the connections of the mvars via computers
    # note that this is not a graph we can query for connectivity
    colordict=TABLEAU_COLORS
    color_names=[n for n in colordict.keys()]
    computer_colors={c.__name__:color_names[i] for i,c in enumerate(allComputers)}
    G=create_multigraph(allMvars,allComputers)
    # possibly create new Graph with text nodes
    g=G
    # create a colorlist for the edges using the computer attribute 
    edgelist=[e for e in g.edges]
    computers=[g[e[0]][e[1]]['computer'] for e in edgelist]
    edge_color=[computer_colors[c.__name__] for c in computers]
    fig=plt.figure(figsize=(5,5))
    axes=fig.add_subplot(1,1,1)
    nx.draw_networkx(
            g
            ,edgelist=edgelist
            ,edge_color=edge_color
            ,ax=axes)
    fig.savefig("Multigraph_matplotlib.pdf")

def create_multigraph(allMvars,allComputers):
    G=nx.DiGraph()
    for v in allMvars:
        for c in all_computers_for_mvar(v,allComputers):
            ans=input_mvars(c)
            for an in ans:
                G.add_edge(
                     pretty_name(an)
                    ,pretty_name(v)
                    ,computer=c
                )
    return G


def draw_SetMultiDiGraph(spsg,ax,**kwargs):
    pos=nx.spring_layout(spsg)
    nx.draw(
        spsg
        ,labels={n:node_2_string(n) for n in spsg.nodes()}
        ,ax=ax
        ,node_size=1000
        ,node_shape='s'
        ,pos=pos
        ,**kwargs
    )
    # at the moment it is not possible to draw
    # more than one edge (egde_lables) between nodes
    # directly (no edgelabels for MultiDiGraphs)
    # therefore we draw only one line for all computersets
    # and assemble the label from the different edges 
    def edgeDict_to_string(ed):
        target='computers'
        comp_sets=[v[target] for v in ed.values() if target in v.keys()]
        comp_set_strings=[compset_2_string(cs) for cs in comp_sets]
        res="\n".join(comp_set_strings)
        print(res)
        return res
    
    edge_labels={e:edgeDict_to_string(spsg.get_edge_data(*e)) for e in spsg.edges()}  

    nx.draw_networkx_edge_labels(
        spsg 
        ,ax=ax
        ,edge_labels=edge_labels
        ,pos=pos
    )

def draw_Graph_with_computers_svg(spsg,file_name_trunk):
    # the next line is the standard translation 
    # We could do this using the attributes of the edges to
    # make much niceer pictures representing the different computers in different
    # colors or annotate them....
    allComputers=reduce(
        lambda acc,edge:acc.union(edge[2]['computers'],acc)
        ,spsg.edges(data=True)
        ,set()
    )
    colordict=TABLEAU_COLORS
    color_names=[n for n in colordict.keys()]
    computer_colors={c.__name__:color_names[i] for i,c in enumerate(allComputers)}
    A=nx.nx_agraph.to_agraph(spsg)
    A=AGraph(directed=True)
    A.node_attr['style']='filled'
    A.node_attr['shape']='rectangle'
    A.node_attr['fixedsize']='false'
    A.node_attr['fontcolor']='black'
    
    for node in spsg.nodes:
        A.add_node(node_2_string(node))
    edges=spsg.edges(data=True)
    for edge in edges:
        s,t,data_dict=edge
        computer_set=data_dict['computers']
        print('computer_set')
        print(computer_set)
        ss,st=tuple(map(node_2_string,(s,t)))
        A.add_edge(ss,st)
        Ae=A.get_edge(ss,st)
        #Ae.attr['color']=colordict[computer_colors[c.__name__]]
        #Ae.attr['fontcolor']=colordict[computer_colors[c.__name__]]
        Ae.attr['label']="\n".join([c.__name__ for c in computer_set]) 
    #print(A.string()) # print to screen
    #A.draw(file_name_trunk+'.png',prog="circo") # draw to png using circo
    A.draw(file_name_trunk+'.svg',prog='circo') 

