def fitch_pass_down(tree, node, parent_state=None):
    if "state" in tree[node] and isinstance(tree[node]["state"], set):
        # If the node has multiple possible states, choose the one that matches the parent state if possible
        if parent_state in tree[node]["state"]:
            tree[node]["chosen_state"] = parent_state
        else:
            # Arbitrarily choose one of the possible states
            tree[node]["chosen_state"] = next(iter(tree[node]["state"]))
    elif "state" in tree[node]:  # Leaf node, simply carry the state
        tree[node]["chosen_state"] = tree[node]["state"]

    # Proceed to children if this is not a leaf
    if "children" in tree[node]:
        for child in tree[node]["children"]:
            fitch_pass_down(tree, child, tree[node]["chosen_state"])


def fitch_pass_up(tree, node):
    if "state" in tree[node]:  # Leaf node, base case
        return {tree[node]["state"]}

    left_child, right_child = tree[node]["children"]
    left_states = fitch_pass_up(tree, left_child)
    right_states = fitch_pass_up(tree, right_child)

    possible_states = (
        left_states & right_states if left_states & right_states else left_states | right_states
    )
    tree[node]["state"] = possible_states  # Store possible states
    return possible_states


# Example tree structure, slightly modified for clarity
tree = {
    "root": {"children": ["node1", "node2"]},
    "node1": {"children": ["leaf1", "leaf2"]},
    "node2": {"children": ["leaf3", "leaf4"]},
    "leaf1": {"state": 0},
    "leaf2": {"state": 0},
    "leaf3": {"state": 1},
    "leaf4": {"state": 1},
}


taxa_list = ["A", "B", "C", "D"]
morphological_data = [
    [0, 1, 0],  # Character states for taxon A
    [1, 1, 0],  # Character states for taxon B
    [0, 1, 1],  # Character states for taxon C
    [1, 1, 1],  # Character states for taxon D
]

# Run the Fitch algorithm on the example tree
fitch_pass_up(tree, "root")
fitch_pass_down(tree, "root")

# Display the chosen states for each node
for node, attributes in tree.items():
    if "chosen_state" in attributes:
        print(f"{node}: chosen state = {attributes['chosen_state']}")
    else:  # For leaf nodes, the chosen state is the original state
        print(f"{node}: state = {attributes['state']}")


"""
This line of code is used during the second phase of the Fitch algorithm, where a specific state is chosen for an internal node based on the set of possible states determined during the first phase. Here's a breakdown of what it does:

- `tree[node]['state']` is a set of possible states for the node. During the first phase, this set was filled with all the states that could exist at this node without increasing the total number of state changes across the tree. This set could contain one or multiple states, depending on the character states of the node's descendants.

- `iter(tree[node]['state'])` creates an iterator over the set of possible states. In Python, an iterator is an object that allows you to traverse through all the elements of a collection (such as a list, set, or dictionary) without needing to use indexing.

- `next(iter(tree[node]['state']))` takes the iterator created in the previous step and gets the next element from it. Since sets in Python are unordered collections, you cannot directly access elements by an index. Using `next()` on an iterator of the set gives you one element from the set. In this context, since the specific ordering of elements in a set is not guaranteed, the `next()` function essentially picks an arbitrary (but consistent) element from the set.

This approach is used when the algorithm needs to choose a specific state for an internal node, but there is no clear choice based on the parent's state (either because we are at the root, which has no parent, or because the parent's state is not among the possible states for this node). By arbitrarily choosing one of the possible states, the algorithm ensures that every node in the tree has a specific state assigned to it, completing the ancestral state reconstruction process.

In summary, the line `tree[node]['chosen_state'] = next(iter(tree[node]['state']))` assigns an arbitrary state from the set of possible states to the internal node as its "chosen state" for the second phase of the Fitch algorithm. This is a necessary step to resolve cases where there's more than one possible state for a node, allowing the algorithm to proceed with a specific state assignment for the downward pass.
"""
