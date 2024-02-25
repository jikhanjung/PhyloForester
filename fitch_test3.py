import PfUtils as pu


taxa_list = ["A", "B", "C", "D"]
morphological_data = [
    [0, 1, 0],  # Character states for taxon A
    [1, 1, 0],  # Character states for taxon B
    [0, 1, 1],  # Character states for taxon C
    [1, 1, 1]   # Character states for taxon D 
]

tree_str = "((A:0.1,B:0.2):0.3,(C:0.4,D:0.5):0.6);"
from Bio import Phylo
from io import StringIO
tree = Phylo.read(StringIO(tree_str), "newick")
Phylo.draw_ascii(tree)
print("tree:", tree)

ancestral_states = pu.reconstruct_ancestral_states(tree, morphological_data, taxa_list)
for node in tree.find_clades():
    #node.confidence = [None] * len(morphological_data[0])
    print("final node confidence:", node.name, node.character_states)
#print(ancestral_states)

# Example usage:
#reconstruct_ancestral_states_for_all_characters(tree, morphological_data)
    
print("tree:", tree)
def print_character_states(node, depth=0):
    print(" "*4*depth,node.name, node.character_states, node.changed_characters, len(node.changed_characters) )
    for child in node:
        print_character_states(child, depth + 1)

        
print_character_states(tree.root)