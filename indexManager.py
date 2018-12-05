"""
    提供创建、删除索引函数
    提供在索引中插入、删除、搜索记录函数
    结束时记得调用将索引写入文件的函数
"""
import BPTree
import sys
from bufferManager import buffer, bufferSave, bufferClose, getBlockNum
import catalog_manager

blank = 4096 * " "

class index_manager:
    def __init__(self):
        self.index_dic = {}
        self.key_types = {}
        self.read_disk()

    def __del__(self):
        del self.index_dic
        del self.key_types

    #寻找当前索引
    def find_index(self, index_name):
        if index_name in self.index_dic:
            return True
        else:
            return False

    #创建空索引  参数：索引名、M
    def create_blank_index(self, index_name, key_type, degree):
        new_tree = BPTree.BPTree(index_name, degree)
        self.index_dic[index_name] = new_tree
        self.key_types[index_name] = key_type

    #创建索引 参数：索引的表名、索引名、索引的属性名
    def create_index(self, table_name, index_name, key_attr):
        table_file = table_name + '.csv'
        block_num = getBlockNum("db", table_file)  # max block number
        data = catalog_manager.attr_data(table_name)
        index = data["attr_name"].index(key_attr)
        if data["attr_type"][key_attr] == "int":
            key_size = 10
        elif data["attr_type"][key_attr] == "float":
            key_size = 40
        elif data["attr_type"][key_attr] == "char":
            key_size = int(data["attr_type_length"][key_attr])
        degree = int((4096 - (sys.getsizeof(index_name) - 48) + 6 + 11) / (key_size + 23))
        self.create_blank_index(index_name, data["attr_type"][key_attr], degree)

        for num in range(block_num + 1):
            block_list = buffer("db", table_file, num).strip().split('\n')
            offset = 0
            for s in block_list:
                if ',' not in s:
                    break
                row = s.split(',')
                key = row[index]
                self.insert_index(index_name, key, [num, offset])
                offset += 1
            bufferClose()



        #删除索引
    def drop_index(self, index_name):
        if self.find_index(index_name):
            del self.index_dic[index_name]
        else:
            print("Not found the index to be dropped")

    #通过Key寻找记录位置并返回
    def search_index(self, index_name, key):
        if self.find_index(index_name):
            return self.index_dic[index_name].search(key)
        else:
            print("Not found the index in search_index")
            return -1

    def search_index_by_range(self, index_name, left_key=None, right_key=None, left_equal=False, right_equal=False):
        res = []
        index = 0
        if left_key is None and right_key is None:
            return -1
        elif left_key is None:
            current_node = self.index_dic[index_name].left_leaf
            while current_node:
                is_found, index = current_node.search(right_key, index)
                if index < current_node.count or is_found:
                    for j in range(0, index):
                        res.append(current_node.values[j])
                    if right_equal is True and is_found:
                        res.append(current_node.values[index])
                    break
                else:
                    for j in current_node.values:
                        if j is None:
                            break
                        res.append(j)
                current_node = current_node.next_leaf_node
        elif right_key is None:
            current_node = self.index_dic[index_name].left_leaf
            if left_key < current_node.keys[0]:
                pass
            else:
                while current_node:
                    is_found, index = current_node.search(left_key, index)
                    if index < current_node.count or is_found:
                        break
                    current_node = current_node.next_leaf_node
                if not current_node:
                    return res
                if not (left_equal is False and is_found):
                    res.append(current_node.values[index])
                for j in range(index+1, len(current_node.values)):
                    if current_node.values[j] is None:
                        break
                    res.append(current_node.values[j])
                current_node = current_node.next_leaf_node
            while current_node:
                for j in current_node.values:
                    if j is None:
                        break
                    res.append(j)
                current_node = current_node.next_leaf_node
        else:
            current_node = self.index_dic[index_name].left_leaf
            if left_key < current_node.keys[0]:
                pass
            else:
                while current_node:
                    is_found, index = current_node.search(left_key, index)
                    if index < current_node.count or is_found:
                        break
                    current_node = current_node.next_leaf_node
                if not current_node:
                    return res
                if not (left_equal is False and is_found):
                    res.append(current_node.values[index])
                for j in range(index+1, len(current_node.values)):
                    if current_node.values[j] is None:
                        break
                    res.append(current_node.values[j])
                current_node = current_node.next_leaf_node
            while current_node:
                is_found, index = current_node.search(right_key, index)
                if index < current_node.count:
                    for j in range(0, index):
                        res.append(current_node.values[j])
                    if right_equal is True and is_found:
                        res.append(current_node.values[index])
                    break
                else:
                    for j in current_node.values:
                        if j is None:
                            break
                        res.append(j)
                current_node = current_node.next_leaf_node
        return res



    #在索引插入一条记录，需要key和记录所在位置
    def insert_index(self, index_name, key, value):
        if self.find_index(index_name):
            self.index_dic[index_name].insert(key, value)
        else:
            print("Not found the index in insert_index")

    #删除索引中记录
    def delete_index(self, index_name, key):
        if self.find_index(index_name):
            self.index_dic[index_name].delete(key)
        else:
            print("Not found the index in delete_index")

    #从文件中读取一次数据
    def read_one(self, block, offset):
        res = ''
        while block[offset] != ',' and block[offset] != ' ':
            res += block[offset]
            offset += 1
        return res, offset+1

    #从磁盘中读取索引
    def read_disk(self):
        bnum = 0
        block = buffer('db', 'index.txt', bnum)
        bufferSave('db', 'index.txt', bnum, blank)
        bufferClose()
        block = str(block)
        while block and block[0] != ' ':
            offset = 0
            index_name, offset = self.read_one(block, offset)
            degree, offset = self.read_one(block, offset)
            degree = int(degree)
            key_type, offset = self.read_one(block, offset)
            if self.find_index(index_name):
                pass
            else:
                self.create_blank_index(index_name, key_type, degree)
            for i in range(degree-1):
                current_key, offset = self.read_one(block, offset)
                if current_key == "None":
                    current_key = None
                    current_value, offset = self.read_one(block, offset)
                else:
                    if key_type == "int":
                        current_key = int(current_key)
                    elif key_type == "float":
                        current_key = float(current_key)
                    current_values = []
                    for j in range(0, 2):
                        current_value, offset = self.read_one(block, offset)
                        if current_value == "None":
                            current_value = None
                        current_value = int(current_value)
                        current_values.append(current_value)
                    self.insert_index(index_name, current_key, current_values)
            bnum += 1
            block = buffer('db', 'index.txt', bnum)
            bufferSave('db', 'index.txt', bnum, blank)
            bufferClose()
            block = str(block)

    #将索引信息保存在文件中
    def write_disk(self):
        bnum = 0
        for i in self.index_dic:
            cur = self.index_dic[i].left_leaf
            while not cur is None:
                block = i
                block += "," + str(self.index_dic[i].degree)
                if self.key_types[i] == "int":
                    block += ",int"
                elif self.key_types[i] == "float":
                    block += ",float"
                elif self.key_types[i] == "char":
                    block += ",char"
                for j in range(self.index_dic[i].degree-1):
                    block += "," + str(cur.keys[j])
                    if cur.values[j] is None:
                        block += ",None"
                    else:
                        for k in range(len(cur.values[j])):
                            cur.values[j][k] = str(cur.values[j][k])
                        block += "," + ",".join(cur.values[j])
                block += ","
                bufferSave('db', 'index.txt', bnum, blank)
                bufferSave('db', 'index.txt', bnum, block)
                bufferClose()
                bnum += 1
                cur = cur.next_leaf_node


if __name__ == '__main__':
    index = index_manager()
  #  index.create_index("book", "dby", "bno")
  #  index.drop_index("dby")
 #   index.create_blank_index("dby", "int", 123)
    for i in index.index_dic:
        index.index_dic[i].print_tree()
 #   print(index.search_index_by_range("dby", left_key=0, right_key=11, left_equal=True, right_equal=True))
  #  print(index.search_index("dby", 11))
    index.write_disk()
