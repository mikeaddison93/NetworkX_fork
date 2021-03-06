#-*- coding: utf-8 -*-
from collections import defaultdict
import networkx as nx
#-*- coding: utf-8 -*-
#    Copyright (C) 2011 by 
#    Jordi Torrents <jtorrents@milnou.net>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """\n""".join(['Jordi Torrents <jtorrents@milnou.net>',
                            'Aric Hagberg (hagberg@lanl.gov)'])
__all__ = ["average_neighbor_degree",
           "average_neighbor_in_degree",
           "average_neighbor_out_degree",
           'average_degree_connectivity',
           'average_in_degree_connectivity',
           'average_out_degree_connectivity',
           'k_nearest_neighbors']

def _average_nbr_deg(G, degree_method, nodes=None, weighted=False):
    avg_nbr_deg = {}
    for n in G.nbunch_iter(nodes):
        nbrdeg = degree_method(G[n])
        if weighted:
            nbrv = [G[n][nbr].get('weight',1)*d for nbr,d in nbrdeg.items()]
        else:
            nbrv = nbrdeg.values()
        norm = degree_method(n,weighted=weighted)
        avg_nbr_deg[n] = float(sum(nbrv))
        if norm > 0:
            avg_nbr_deg[n] /= norm
    return avg_nbr_deg

def average_neighbor_degree(G, nodes=None, weighted=False):
    """Returns the average degree of the neighborhood of each node.

    The average degree of a node :math:`i` is:

    .. math::

        k_{nn,i} = \\frac{1}{|N(i)|} \\sum_{j \in N(i)} k_j

    where :math:`N(i)` are the neighbors of node :math:`i` and :math:`k_j` is
    the degree of node :math:`j` which belongs to :math:`N(i)`. For weighted 
    graphs, an analogous measure can be defined [1]_,

    .. math::

        k_{nn,i}^{w} = \\frac{1}{s_i} \sum_{j \in N(i)} w_{ij} k_j

    where :math:`s_i` is the weighted degree of node :math:`i`, :math:`w_{ij}`
    is the weight of the edge that links :math:`i` and :math:`j` and
    :math:`N(i)` are the neighbors of node :math:`i`.


    Parameters
    ----------
    G : NetworkX graph

    nodes: list or iterable (optional)
        Compute neighbor connectivity for these nodes. The default is all nodes.

    weighted: bool (default=False)
        Compute weighted average nearest neighbors degree.

    Returns
    -------
    d: dict
       A dictionary keyed by node with average neighbors degree value.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> G.edge[0][1]['weight'] = 5
    >>> G.edge[2][3]['weight'] = 3
    >>> average_neighbor_degree(G)
    {0: 2.0, 1: 1.5, 2: 1.5, 3: 2.0}
    >>> average_neighbor_degree(G, weighted=True)
    {0: 2.0, 1: 1.1666666666666667, 2: 1.25, 3: 2.0}

    >>> G=nx.DiGraph()
    >>> G.add_path([0,1,2,3])
    >>> average_neighbor_in_degree(G)
    {0: 1.0, 1: 1.0, 2: 1.0, 3: 0.0}
    >>> average_neighbor_out_degree(G)
    {0: 1.0, 1: 1.0, 2: 0.0, 3: 0.0}
 
    Notes
    -----
    For directed graphs you can also specify in-degree or out-degree 
    by calling the relevant functions.  

    See Also
    --------
    average_neighbor_out_degree, average_neighbor_in_degree, 
    average_degree_connectivity 
    
    References
    ----------    
    .. [1] A. Barrat, M. Barthélemy, R. Pastor-Satorras, and A. Vespignani, 
       "The architecture of complex weighted networks". 
       PNAS 101 (11): 3747–3752 (2004).
    """
    degree_method = G.degree
    return _average_nbr_deg(G, degree_method, nodes=nodes, weighted=weighted)

def average_neighbor_in_degree(G, nodes=None, weighted=False):
    if not G.is_directed():
        raise nx.NetworkXError("Not defined for undirected graphs.")
    degree_method = G.in_degree
    return _average_nbr_deg(G, degree_method, nodes=nodes, weighted=weighted)
average_neighbor_in_degree.__doc__=average_neighbor_degree.__doc__

def average_neighbor_out_degree(G, nodes=None, weighted=False):
    if not G.is_directed():
        raise nx.NetworkXError("Not defined for undirected graphs.")
    degree_method = G.out_degree
    return _average_nbr_deg(G, degree_method, nodes=nodes, weighted=weighted)
average_neighbor_out_degree.__doc__=average_neighbor_degree.__doc__

def _avg_deg_conn(G, degree_method, nodes=None, weighted=False):
    # "k nearest neighbors, or neighbor_connectivity
    if nodes is None:
        node_iter = G
    else:
        node_iter = G.nbunch_iter(nodes)
    dsum = defaultdict(float)
    dnorm = defaultdict(float)
    for n,k in degree_method(node_iter).items():
        nbrdeg = degree_method(G[n])
        if weighted:
            nbrv = [G[n][nbr].get('weight',1)*d for nbr,d in nbrdeg.items()]
            dnorm[k] += degree_method(n, weighted=weighted)
        else:
            nbrv = nbrdeg.values()
            dnorm[k] += k
        dsum[k] += float(sum(nbrv))

    dc = {}
    for k,avg in dsum.items():
        dc[k]=avg
        if avg > 0:
            dc[k]/=dnorm[k]
    return dc

def average_degree_connectivity(G, nodes=None, weighted=False):
    """Compute the average degree connectivity of graph.

    The average degree connectivity is the average nearest neighbor degree of
    nodes with degree k. For weighted graphs, an analogous measure can 
    be computed using the weighted average neighbors degree defined in 
    [1]_, for a node :math:`i`, as:

    .. math::

        k_{nn,i}^{w} = \\frac{1}{s_i} \sum_{j \in N(i)} w_{ij} k_j

    where :math:`s_i` is the weighted degree of node :math:`i`, :math:`w_{ij}`
    is the weight of the edge that links :math:`i` and :math:`j` and
    :math:`N(i)` are the neighbors of node :math:`i`.

    Parameters
    ----------
    G : NetworkX graph

    nodes: list or iterable (optional)
        Compute neighbor connectivity for these nodes. The default is all nodes.

    weighted: bool (default=False)
        Compute weighted average nearest neighbors degree.

    Returns
    -------
    d: dict
       A dictionary keyed by degree k with the value of average neighbor degree.
    
    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> G.edge[1][2]['weight'] = 3
    >>> k_nearest_neighbors(G)
    {1: 2.0, 2: 1.5}
    >>> k_nearest_neighbors(G, weighted=True)
    {1: 2.0, 2: 1.75}

    See also
    --------
    neighbors_average_degree

    Notes
    -----
    This algorithm is sometimes called "k nearest neighbors'.

    References
    ----------    
    .. [1] A. Barrat, M. Barthélemy, R. Pastor-Satorras, and A. Vespignani, 
       "The architecture of complex weighted networks". 
       PNAS 101 (11): 3747–3752 (2004).
    """
    degree_method = G.degree
    return _avg_deg_conn(G, degree_method, nodes=nodes, weighted=weighted)

def average_in_degree_connectivity(G, nodes=None, weighted=False):
    if not G.is_directed():
        raise nx.NetworkXError("Not defined for undirected graphs.")
    degree_method = G.in_degree
    return _avg_deg_conn(G, degree_method, nodes=nodes, weighted=weighted)
average_in_degree_connectivity.__doc__=average_degree_connectivity.__doc__

def average_out_degree_connectivity(G, nodes=None, weighted=False):
    if not G.is_directed():
        raise nx.NetworkXError("Not defined for undirected graphs.")
    degree_method = G.out_degree
    return _avg_deg_conn(G, degree_method, nodes=nodes, weighted=weighted)
average_out_degree_connectivity.__doc__=average_degree_connectivity.__doc__


k_nearest_neighbors=average_degree_connectivity
neighbor_connectivity=average_degree_connectivity
