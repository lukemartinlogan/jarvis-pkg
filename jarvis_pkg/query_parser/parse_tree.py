class ParseTree:
    def check_node_type(self, root_node, i, type):
        if i >= len(root_node):
            return False
        return root_node[i].type == type

    def check_pattern(self, root_node, i, *types):
        for node_type in types:
            if not self.check_node_type(root_node, i, node_type):
                return False
            i += 1
        return True

    def hide(self, root_node, i):
        x = root_node.pop(i)
        self.hidden.add_node(x)
