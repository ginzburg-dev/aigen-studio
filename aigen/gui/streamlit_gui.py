import streamlit as st
from pyvis.network import Network

def visualize_streamlit(nodes, edges):
    net = Network(height="600px", width="100%", directed=True)
    for n in nodes:
        net.add_node(n['id'], label=n.get('label', n['id']), shape="box")
    for e in edges:
        net.add_edge(e['src'], e['dst'])
    net.save_graph("graph.html")
    st.components.v1.html(open("graph.html").read(), height=600)

st.title("Pipeline Viewer")
nodes = [{"id":"A","label":"Prompt"},{"id":"B","label":"Plan"},{"id":"C","label":"Render"}]
edges = [{"src":"A","dst":"B"},{"src":"B","dst":"C"}]
visualize_streamlit(nodes, edges)
