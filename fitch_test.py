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
            ancestral_states[node] = set().union(
                *[ancestral_states[child] for child in node.clades]
            )

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


# Function to reconstruct ancestral states for all characters in the data matrix
def reconstruct_ancestral_states_for_all_characters(tree, morphological_data):
    # Initialize ancestral states for each character
    print("morphological_data:", morphological_data, len(morphological_data[0]))
    for node in tree.find_clades():
        node.confidence = [None] * len(morphological_data[0])
        node.changed_characters = []
        # for character in range(len(morphological_data[0])):
        #    node.confidence[character] = None

    clade_list = [c for c in tree.find_clades()]
    root = clade_list[0]
    # Perform the first pass (bottom-up traversal)
    bottom_up_pass(root, morphological_data)
    print("bottom up done, root.confidence:", root.confidence)

    # Perform the second pass (top-down traversal)
    top_down_pass(root, morphological_data)


# Function to perform the first pass of the Fitch algorithm (bottom-up traversal)
def bottom_up_pass(node, morphological_data):
    if node.is_terminal():
        taxon_idx = taxa_list.index(node.name)
        print("taxon:", node.name, morphological_data[taxon_idx])
        # print("node.confidence:", node.confidence)
        for character, state in enumerate(morphological_data[taxon_idx]):
            node.confidence[character] = set([state])
            print(character, state)
        # print("node.confidence:", node.confidence)
    else:
        for child in node:
            bottom_up_pass(child, morphological_data)
        for character in range(len(morphological_data[0])):
            children_states = [child.confidence[character] for child in node]
            print("children_states:", children_states)
            children_sets = [s for s in children_states if isinstance(s, set)]
            print("children_sets:", children_sets)
            intersection = set.intersection(*children_sets) if children_sets else set()
            print("intersection:", intersection)
            # check if intersection is empty
            if not intersection:
                union = set.union(*children_sets) if children_sets else set()
                node.confidence[character] = union
                print("union:", union)
            else:
                node.confidence[character] = intersection
            node.confidence[character] = set.union(*children_sets) if children_sets else set()
        print("node.confidence:", node.confidence)

        # left_states = set(children_states[0])
        # right_states = set(children_states[1])
        # left_states = set(node[0].confidence[character])
        # right_states = set(node[1].confidence[character])
        # node.confidence[character] = left_states.intersection(right_states)


# Function to perform the second pass of the Fitch algorithm (top-down traversal)
def top_down_pass(node, morphological_data, parent_state=None):
    if not node.is_terminal():
        # print("topdown node.confidence:", node.name, node.confidence, "parent confidence:", parent_state)
        for character_index in range(len(morphological_data[0])):
            if parent_state and parent_state[character_index] in node.confidence[character_index]:
                node.confidence[character_index] = parent_state[character_index]
            else:
                node.confidence[character_index] = min(node.confidence[character_index])
            if parent_state and parent_state[character_index] != node.confidence[character_index]:
                print(
                    "changed character:",
                    character_index,
                    "parent:",
                    parent_state[character_index],
                    "node:",
                    node.confidence[character_index],
                )
                node.changed_characters.append(character_index)
    else:
        # print("topdown terminal node.confidence:", node.name, node.confidence)
        for character_index in range(len(morphological_data[0])):
            final_state = min(node.confidence[character_index])
            node.confidence[character_index] = final_state
            if parent_state and parent_state[character_index] != node.confidence[character_index]:
                print(
                    "changed character:",
                    character_index,
                    "parent:",
                    parent_state[character_index],
                    "node:",
                    node.confidence[character_index],
                )
                node.changed_characters.append(character_index)
            # print("node.confidence:", node.confidence)
    #            if len(node.confidence[character_index]) == 0:
    #                for child in node.clades:
    #                    for state in child.confidence[character_index]:
    #                        node.confidence[character_index].add(state)

    for child in node.clades:
        top_down_pass(child, morphological_data, node.confidence)


taxa_list = ["A", "B", "C", "D"]
morphological_data = [
    [0, 1, 0],  # Character states for taxon A
    [1, 1, 0],  # Character states for taxon B
    [0, 1, 1],  # Character states for taxon C
    [1, 1, 1],  # Character states for taxon D
]

tree_str = "((A:0.1,B:0.2):0.3,(C:0.4,D:0.5):0.6);"
from io import StringIO

from Bio import Phylo

tree = Phylo.read(StringIO(tree_str), "newick")
Phylo.draw_ascii(tree)
print("tree:", tree)

ancestral_states = reconstruct_ancestral_states_for_all_characters(tree, morphological_data)
for node in tree.find_clades():
    # node.confidence = [None] * len(morphological_data[0])
    print("final node confidence:", node.name, node.confidence)
# print(ancestral_states)

# Example usage:
# reconstruct_ancestral_states_for_all_characters(tree, morphological_data)

print("tree:", tree)


def print_character_states(node, depth=0):
    print(
        " " * 4 * depth,
        node.name,
        node.confidence,
        node.changed_characters,
        len(node.changed_characters),
    )
    for child in node:
        print_character_states(child, depth + 1)


print_character_states(tree.root)
