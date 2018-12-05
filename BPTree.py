#B+树节点类
class TreeNode:
    def __init__(self, degree, isleaf=False):
        self.count = 0
        self.degree = degree
        self.parent = None
        self.next_leaf_node = None
        self.keys = []
        self.values = []
        self.childs = []
        self.isleaf = isleaf
        for i in range(0, degree):
            self.keys.append(None)
            self.values.append(None)
            self.childs.append(None)
        self.childs.append(None)


    def isroot(self):
        return self.parent is None

    def search(self, key, index):
        if self.count == 0:
            return False, 0
        else:
            if self.keys[self.count - 1] < key:
                return False, self.count
            elif self.keys[0] > key:
                return False, 0
            elif self.count <= 20:
                for i in range(0, self.count):
                    if self.keys[i] == key:
                        return True, i
                    elif self.keys[i] < key:
                        continue
                    elif self.keys[i] > key:
                        return False, i
            elif self.count > 20:
                left = 0
                right = self.count - 1
                pos = 0
                while right > left + 1:
                    pos = int((right + left) / 2)
                    if self.keys[pos] == key:
                        return True, pos
                    elif self.keys[pos] < key:
                        left = pos
                    elif self.keys[pos] > key:
                        right = pos
                if self.keys[left] >= key:
                    return (self.keys[left] == key), left
                elif self.keys[right] >= key:
                    return (self.keys[right] == key), right
                elif self.keys[right] < key:
                    return False, right+1
        return False, index

    def splite(self):
        half = int((self.degree - 1) / 2)
        new_node = TreeNode(self.degree, self.isleaf)
        if new_node is None:
            print("error in allocate memory")
            exit(0)
        if self.isleaf:
            key = self.keys[half + 1]
            for i in range(half+1, self.degree):
                new_node.keys[i-half-1] = self.keys[i]
                new_node.values[i-half-1] = self.values[i]
                self.keys[i] = None
                self.values[i] = None
            new_node.count = self.count - half - 1
            new_node.parent = self.parent
            new_node.next_leaf_node = self.next_leaf_node
            self.count = half + 1
            self.next_leaf_node = new_node
        else:
            key = self.keys[half]
            for i in range(half+1, self.degree):
                new_node.keys[i-half-1] = self.keys[i]
                self.keys[i] = None
            for i in range(half+1, self.degree+1):
                new_node.childs[i-half-1] = self.childs[i]
                new_node.childs[i-half-1].parent = new_node
                self.childs[i] = None
            self.keys[half] = None
            new_node.parent = self.parent
            new_node.count = self.count - half - 1
            self.count = half
        return key, new_node

    def add(self, key):
        if self.count == 0:
            self.keys[0] = key
            self.count += 1
            return 0
        else:
            index = 0
            isfound, index = self.search(key, index)
            if isfound:
                print("key is already in the tree")
                exit(0)
            else:
                for i in range(self.count, index, -1):
                    self.keys[i] = self.keys[i-1]
                self.keys[index] = key
                for i in range(self.count+1, index+1, -1):
                    self.childs[i] = self.childs[i-1]
                self.childs[index+1] = None
                self.count += 1

                return index

    def add_leaf(self, key, value):
        if not self.isleaf:
            print("current node is not a leaf")
            return -1
        if self.count == 0:
            self.keys[0] = key
            self.values[0] = value
            self.count += 1
            return 0
        else:
            index = 0
            isfound, index = self.search(key, index)
            if isfound:
                print("key is already in the tree")
                exit(0)
            else:
                for i in range(self.count, index, -1):
                    self.keys[i] = self.keys[i-1]
                    self.values[i] = self.values[i-1]
                self.keys[index] = key
                self.values[index] = value
                self.count += 1
                return index

    def delete(self, index):
        if self.count < index:
            #print("can't find the node")
            return False
        else:
            if self.isleaf:
                for i in range(index, self.count-1):
                    self.keys[i] = self.keys[i+1]
                    self.values[i] = self.values[i+1]
                self.keys[self.count-1] = None
                self.values[self.count-1] = None
            else:
                for i in range(index, self.count-1):
                    self.keys[i] = self.keys[i+1]
                    self.childs[i+1] = self.childs[i+2]
                self.keys[self.count-1] = None
                self.childs[self.count] = None
            self.count -= 1
            return True

    def print_node(self):
        print("keys:", self.keys[0:self.count])
        if self.isleaf:
            print("values:", self.values[0:self.count])
        else:
            print("childs:", self.childs[0:self.count+1])

#B+树类
class BPTree:
    def __init__(self, name, degree):
        self.filename = name
        self.key_num = 0
        self.level = 1
        self.node_num = 1
        self.degree = degree
        self.root = TreeNode(degree, True)
        self.left_leaf = self.root

    def __del__(self):
        self.drop_tree(self.root)
        self.key_num = 0
        self.root = None
        self.level = 0
        self.left_leaf = None

    def find(self, node, key):
        index = 0
        isfound, index = node.search(key, index)
        if isfound:
            if node.isleaf:
                return node, index, True
            else:
                node = node.childs[index+1]
                while not node.isleaf:
                    node = node.childs[0]
                return node, 0, True
        else:
            if node.isleaf:
                return node, index, False
            else:
                return self.find(node.childs[index], key)

    def search(self, key):
        if not self.root:
            return -1
        node, index, isfound = self.find(self.root, key)
        if isfound:
            return node.values[index]
        else:
            return -1

    def search_index(self, key):
        if not self.root:
            return -1
        node, index, isfound = self.find(self.root, key)
        if isfound:
            return index
        else:
            return -1

    def insert(self, key, value):
        node, index, isfound = self.find(self.root, key)
        if isfound:
            #print("can't insert the key")
            return False
        else:
            node.add_leaf(key, value)
            self.key_num += 1
            if node.count >= self.degree:
                return self.adjust_insert(node)
            return True

    def adjust_insert(self, node):
        new_key, new_node = node.splite()
        self.node_num += 1
        if node.isroot():
            new_root = TreeNode(self.degree, False)
            new_root.add(new_key)
            new_root.childs[0] = node
            new_root.childs[1] = new_node
            self.level += 1
            self.node_num += 1
            self.root = new_root
            node.parent = self.root
            new_node.parent = self.root
            return True
        else:
            new_parent = node.parent
            index = new_parent.add(new_key)
            new_parent.childs[index + 1] = new_node
            new_node.parent = new_parent
            if new_parent.count >= self.degree:
                return self.adjust_insert(new_parent)
            return True

    def delete(self, key):
        if not self.root:
            print("no node in the tree")
            return False
        else:
            node, index, isfound = self.find(self.root, key)
            if isfound:
                if node.isroot():
                    node.delete(index)
                    self.key_num -= 1
                    return self.adjust_delete(node)
                else:
                    if index == 0 and self.left_leaf != node:
                        index_p = 0
                        current_parent = node.parent
                        isfound_p, index_p = current_parent.search(key, index_p)
                        while not isfound_p:
                            if current_parent.parent:
                                current_parent = current_parent.parent
                            else:
                                break
                            isfound_p, index_p = current_parent.search(key, index_p)

                        current_parent.keys[index_p] = node.keys[1]

                        node.delete(index)
                        self.key_num -= 1
                        return self.adjust_delete(node)
                    else:
                        node.delete(index)
                        self.key_num -= 1
                        return self.adjust_delete(node)

            else:
                print("no such key to be deleted in the tree")
                return False

    def adjust_delete(self, node):
        half = int((self.degree - 1) / 2)
        if node.isleaf and node.count > half:
            return True
        elif not node.isleaf and self.degree != 3 and node.count >= half:
            return True

        if node.isroot():
            if node.count > 0:
                return True
            else:
                if self.root.isleaf:
                    self.root = None
                    self.left_leaf = None
                else:
                    self.root = node.childs[0]
                    self.root.parent = None
                self.level -= 1
                self.node_num -= 1
        else:
            parent = node.parent
            brother = None
            if node.isleaf:
                index = 0
                isfound, index = parent.search(node.keys[0], index)
                if parent.childs[0] != node and parent.count == index + 1:
                    brother = parent.childs[index]
                    if brother.count-1 > half:
                        for i in range(node.count, 0, -1):
                            node.keys[i] = node.keys[i-1]
                            node.values[i] = node.values[i-1]
                        node.keys[0] = brother.keys[brother.count-1]
                        node.values[0] = brother.values[brother.count-1]
                        brother.delete(brother.count-1)

                        node.count += 1
                        parent.keys[index] = node.keys[0]
                        return True

                    else:
                        parent.delete(index)

                        for i in range(0, node.count):
                            brother.keys[i+brother.count] = node.keys[i]
                            brother.values[i+brother.count] = node.values[i]
                        brother.count += node.count
                        brother.next_leaf_node = node.next_leaf_node

                        self.node_num -= 1

                        return self.adjust_delete(parent)
                else:
                    if parent.childs[0] == node:
                        brother = parent.childs[1]
                    else:
                        brother = parent.childs[index+2]
                    if brother.count-1 > half:
                        node.keys[node.count] = brother.keys[0]
                        node.values[node.count] = brother.values[0]
                        node.count += 1
                        brother.delete(0)

                        if parent.childs[0] == node:
                            parent.keys[0] = brother.keys[0]
                        else:
                            parent.keys[index+1] = brother.keys[0]
                        return True
                    else:
                        for i in range(0, brother.count):
                            node.keys[node.count+i] = brother.keys[i]
                            node.values[node.count+i] = brother.values[i]
                        if node == parent.childs[0]:
                            parent.delete(0)
                        else:
                            parent.delete(index+1)
                        node.count += brother.count
                        node.next_leaf_node = brother.next_leaf_node
                        self.node_num -= 1

                        return self.adjust_delete(parent)

            else:
                index = 0
                isfound, index = parent.search(node.childs[0].keys[0], index)
                if parent.childs[0] != node and parent.count == index + 1:
                    brother = parent.childs[index]
                    if brother.count-1 >= half:
                        node.childs[node.count+1] = node.childs[node.count]
                        for i in range(node.count, 0, -1):
                            node.childs[i] = node.childs[i-1]
                            node.keys[i] = node.keys[i-1]
                        node.childs[0] = brother.childs[brother.count]
                        node.keys[0] = parent.keys[index]
                        node.count += 1

                        parent.keys[index] = brother.keys[brother.count-1]

                        if brother.childs[brother.count]:
                            brother.childs[brother.count].parent = node
                        brother.delete(brother.count-1)

                        return True
                    else:
                        brother.keys[brother.count] = parent.keys[index]
                        parent.delete(index)
                        brother.count += 1

                        for i in range(0, node.count):
                            brother.childs[brother.count + i] = node.childs[i]
                            brother.childs[brother.count + i].parent = brother
                            brother.keys[brother.count + i] = node.keys[i]
                        brother.childs[brother.count + node.count] = node.childs[node.count]
                        brother.childs[brother.count + node.count].parent = brother

                        brother.count += node.count

                        self.node_num -= 1

                        return self.adjust_delete(parent)
                else:
                    if parent.childs[0] == node:
                        brother = parent.childs[1]
                    else:
                        brother = parent.childs[index+2]
                    if brother.count-1 >= half:
                        node.childs[node.count + 1] = brother.childs[0]
                        node.childs[node.count + 1].parent = node
                        node.keys[node.count] = brother.childs[0].keys[0]
                        node.count += 1
                        if parent.childs[0] == node:
                            parent.keys[0] = brother.keys[0]
                        else:
                            parent.keys[index+1] = brother.keys[0]
                        brother.childs[0] = brother.childs[1]
                        brother.delete(0)

                        return True

                    else:
                        node.keys[node.count] = parent.keys[index]

                        if parent.childs[0] == node:
                            parent.delete(0)
                        else:
                            parent.delete(index+1)

                        node.count += 1

                        for i in range(0, brother.count):
                            node.childs[node.count + i] = brother.childs[i]
                            node.childs[node.count + i].parent = node
                            node.keys[node.count + i] = brother.keys[i]
                        node.childs[brother.count + node.count] = brother.childs[node.count]
                        node.childs[brother.count + node.count].parent = node

                        node.count += brother.count

                        self.node_num -= 1

                        return self.adjust_delete(parent)

        return False

    def drop_tree(self, node):
        if not node:
            return
        if not node.isleaf:
            for i in range(0, node.count):
                self.drop_tree(node.childs[i])
                node.childs[i] = None
        self.node_num -= 1
        return

    def print_tree(self):
        print("The BPTree:")
        self.print_tree_node(self.root)

    def print_tree_node(self, node):
        node.print_node()
        if not node.isleaf:
            for i in range(0, node.count+1):
                self.print_tree_node(node.childs[i])

if __name__ == '__main__':
    Bp = BPTree("dby", 4)
    Bp.insert("dby", [12, "dby"])
    Bp.insert("ll", [12, "ll"])
    Bp.insert("a", [12, "a"])
    Bp.insert("a", [12, "a"])
    Bp.insert("zx", [12, "zx"])
    Bp.insert("zv", [12, "zv"])

    Bp.print_tree()
    print(Bp.key_num)
    print(Bp.left_leaf.values)






