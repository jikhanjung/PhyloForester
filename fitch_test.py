from collections import defaultdict

def modified_fitch(tree, char_data):
    """Performs modified Fitch algorithm with bottom-up and top-down passes.
    Handles polymorphic characters represented as sets of states.

    Args:
        tree: A Biopython Tree object.
        char_data: A dictionary mapping taxa names to sets of character states.

    Returns:
        A dictionary representing ancestral reconstructions (keys = nodes, 
        values = sets of possible states).
    """

    ancestral_states = defaultdict(set)

    # Bottom-up pass
    def _fitch_bottom_up(node):
        if node.is_terminal():
            ancestral_states[node] = char_data[node.name]
        else:
            for child in node.clades:
                _fitch_bottom_up(child)
            ancestral_states[node] = set().union(*[ancestral_states[child] for child in node.clades])

    # Top-down pass
    def _fitch_top_down(node):
        if node.is_root(): 
            return  
        parent_states = ancestral_states[node.up] 
        intersection = parent_states & ancestral_states[node] 

        # Optimization: Minimize changes
        if intersection:
            ancestral_states[node] = intersection 
        else:
            # Resolve ambiguity (you can customize this based on your chosen strategy)
            ancestral_states[node] = parent_states 


    def _fitch_top_down(node):
        for child in node.clades:  # Traverse children
            parent_states = ancestral_states[node.up] 
            intersection = parent_states & ancestral_states[node] 

            # Optimization: Minimize changes
            if intersection:
                ancestral_states[node] = intersection 
            else:
                # Resolve ambiguity (you can customize this based on your chosen strategy)
                ancestral_states[node] = parent_states 

            _fitch_top_down(child)  # Recurse on children

    _fitch_bottom_up(tree.root)
    _fitch_top_down(tree.root)

    return ancestral_states


from Bio.Phylo.TreeConstruction import _Matrix

# Function to reconstruct ancestral states for all characters in the data matrix
def reconstruct_ancestral_states_for_all_characters(tree, morphological_data):
    # Initialize ancestral states for each character
    for character in range(len(morphological_data[0])):
        for node in tree.find_clades():
            node.confidence[character] = None

    clade_list = [ c for c in tree.find_clades() ]
    root = clade_list[0]
    # Perform the first pass (bottom-up traversal)
    bottom_up_pass(root, morphological_data)

    # Perform the second pass (top-down traversal)
    top_down_pass(root, morphological_data)

# Function to perform the first pass of the Fitch algorithm (bottom-up traversal)
def bottom_up_pass(node, morphological_data):
    if node.is_terminal():
        taxon_idx = taxa_list.index(node.name)
        for character, state in enumerate(morphological_data[taxon_idx]):
            node.confidence[character] = state
    else:
        for character in range(len(morphological_data[0])):
            for child in node:
                bottom_up_pass(child, morphological_data)
            children_states = [child.confidence[character] for child in node]
            left_states = set(node[0].confidence[character])
            right_states = set(node[1].confidence[character])
            node.confidence[character] = left_states.intersection(right_states)

# Function to perform the second pass of the Fitch algorithm (top-down traversal)
def top_down_pass(node, morphological_data):
    if not node.is_terminal():
        for character in range(_Matrix.get_dimension(morphological_data)):
            if len(node.confidence[character]) == 0:
                for child in node.clades:
                    for state in child.confidence[character]:
                        node.confidence[character].add(state)

    for child in node.clades:
        top_down_pass(child, morphological_data)

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
for node in tree.find_clades():
    node.confidence = [None] * len(morphological_data)

ancestral_states = reconstruct_ancestral_states_for_all_characters(tree, morphological_data)
print(ancestral_states)
# Example usage:
#reconstruct_ancestral_states_for_all_characters(tree, morphological_data)