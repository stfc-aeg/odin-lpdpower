class DataTreeError(Exception):
    pass


class DataTree(object):

    def __init__(self, tree):
        self.__callbacks = []
        self.__tree = self.__recursiveTreeCheck(tree)

    # Expand out lists / child DataTrees
    def __recursiveTreeCheck(self, subtree, path=''):

        # Expand out child DataTree
        if isinstance(subtree, DataTree):
            # Merge callbacks
            for c in subtree.__callbacks:
                self.addCallback(path + c[0], c[1])
            return subtree.__tree

        # Convert lists/tuples to dict
        if isinstance(subtree, list) or isinstance(subtree, tuple):
            subtree = {str(i): subtree[i] for i in range(len(subtree))}

        # Recursively check child elements
        if isinstance(subtree, dict):
            return {k: self.__recursiveTreeCheck(
                v, path=path + k + '/') for k, v in subtree.iteritems()}

        return subtree

    def __recursivePopulateTree(self, node):
        if isinstance(node, dict):
            return {k: self.__recursivePopulateTree(v) for k, v in node.iteritems()}

        # Leaf nodes
        if callable(node):
            return node()
        return node

    def getData(self, path):
        levels = path.split('/')

        subtree = self.__tree

        if levels == ['']:
            return self.__recursivePopulateTree(subtree)

        for l in levels:
            # Check if next level of path is valid
            if isinstance(subtree, dict) and l in subtree:
                subtree = subtree[l]
            else:
                raise DataTreeError("The path %s is invalid" % path)

        return self.__recursivePopulateTree({levels[-1]: subtree})

    # Replaces values in data_tree with values from new_data
    def __recursiveMergeTree(self, data_tree, new_data, cur_path):

        # Functions are read only
        if callable(data_tree):
            raise DataTreeError(
                "Cannot set value of read only path {}".format(cur_path[:-1]))

        # Override value
        if not isinstance(data_tree, dict):
            # Validate type of new node matches existing
            if type(data_tree) is not type(new_data):
                raise DataTreeError('Type mismatch updating {}: got {} expected {}'.format(
                    cur_path[:-1], type(new_data).__name__, type(data_tree).__name__
                ))
            # Check for callbacks
            for c in self.__callbacks:
                if cur_path.startswith(c[0]):
                    c[1](cur_path, new_data)
            return new_data

        try:
            data_tree.update({k: self.__recursiveMergeTree(
                data_tree[k], v, cur_path + k + '/') for k, v in new_data.iteritems()})
            return data_tree
        except KeyError as e:
            raise DataTreeError('Invalid path: {}{}'.format(cur_path, str(e)[1:-1]))

    def setData(self, path, data):

        # Expand out any lists/tuples
        data = self.__recursiveTreeCheck(data)

        # Get subtree from the node the path points to
        levels = path.split('/')
        if levels == ['']:
            levels = []

        merge_point = self.__tree

        for l in levels:
            # Check if next level of path is valid
            if isinstance(merge_point, dict) and l in merge_point:
                merge_point = merge_point[l]
            else:
                raise DataTreeError("Invalid path: {}".format(path))

        # Add trailing / to paths where necessary
        if len(path) and path[-1] != '/':
            path += '/'

        # Merge data with tree
        merged = self.__recursiveMergeTree(merge_point, data, path)

        # Add merged part to tree
        if levels == []:
            self.__tree = merged
            return

        merge_point = self.__tree
        for l in levels[:-1]:
            merge_point = merge_point[l]
        merge_point[levels[-1]] = merged

    # Adds a callback for when a given writable value is changed
    def addCallback(self, path, callback):
        self.__callbacks.append([path, callback])
