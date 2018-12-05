# -*- coding: utf-8 -*-
import csv
import sys
import os
import prettytable as pt
from bufferManager import *
from indexManager import index_manager
from catalog_manager import attr_data, index_data

MAX_SIZE = 4096  # max size of a block is 4096b
# attr_list = ['bno', 'category', 'title', 'press', 'year', 'author', 'price']


# create an empty csv file of the table
def create_table_file(db_name, table_name):
    file_path = 'database/' + db_name + '/' + table_name + '.csv'
    with open(file_path, 'w') as empty_csv:
        print('create csv file!')
        pass
    bufferClear()


def drop_table_file(db_name, table_name):
    table_file = 'database/' + db_name + '/' + table_name + '.csv'
    print("Table cleared!")
    if os.path.exists(table_file):
        os.remove(table_file)
        print('table %s removed!' % table_name)
    else:
        print('no such file:%s' % table_file)


# insert a tuple of value into the table
def insert_record(db_name, table_name, values):
    # after handling exception by catalog manager
    attr_info = attr_data(table_name)  # function by catalog
    index_info = index_data(table_name)  # function by catalog
    table_file = table_name + '.csv'
    block_num = getBlockNum(db_name, table_file)  # max block number
    block = buffer(db_name, table_file, block_num)  # get content in th block

    # if block space not available, get next block
    if getsizeof(block) + getsizeof(values) > MAX_SIZE:
        block_num += 1
        block = buffer(db_name, table_file, block_num)

    print(block_num)
    # check unique value conflict
    if check_unique(db_name, table_name, values):
        print('Unique value conflict!')
        return

    # insert values to end of block
    block_list = block.split('\n')
    new_val = ','.join([str(i) for i in values])  # convert list to str
    block_list.append(new_val)  # append new value
    block_offset = block_list.index(new_val)  # block offset of insert position
    block_str = '\n'.join(block_list)  # convert to str in the block
    bufferSave(db_name, table_file, block_num, block_str)
    bufferClose()

    # update index
    # value: [block_num, offset]
    # function by index: insert_index(self, index_name, key, value)
    for item in index_info["index_name"]:
        attr = index_info["index_to_attr"][item]   # dic: {"index_name": attr_name}
        i = attr_info['attr_name'].index(attr)  # get index下标
        update_key = values[i]
        update_value = [block_num, block_offset]
        manager = index_manager()
        manager.insert_index(item, update_key, update_value)
        manager.write_disk()


    # insert success
    print("1 row inserted!")


def check_unique(db_name, table_name, values):
    table_file = table_name + '.csv'
    block_num = getBlockNum(db_name, table_file)  # max block number
    res_record = []  # result records
    attr_info = attr_data(table_name)
    attr_uni = attr_info['attr_unique']  # dict {'attr': 'unique'}
    attr_list = attr_info['attr_name']
    attr_type = attr_info["attr_type"]

    for i in range(block_num + 1):
        block_list = buffer(db_name, table_file, i).strip().strip('\0').split('\n')
        for row in block_list:
            row = row.split(',')
            if len(row) == attr_info['attr_num'] and row[0] != '':
                for j in range(len(row)):
                    if attr_type[attr_list[j]] == "int":
                        row[j] = int(row[j])
                    elif attr_type[attr_list[j]] == "float":
                        row[j] = float(row[j])
                res_record.append(row)

    # get unique attr from catalog
    for attr in attr_list:
        if attr_uni[attr] == 'unique':
            mark = attr_list.index(attr)  # index下标
            for row in res_record:
                if len(row) == attr_info['attr_num']:
                    if row[mark] == values[mark]:
                        return 1
    return 0


def select_record(db_name, table_name, condition):
    # after handling exception by catalog manager
    res_record = []  # result records, list of records
    attr_type = attr_data(table_name)["attr_type"]
    attr_list = attr_data(table_name)["attr_name"]  # function by catalog
    index_list = index_data(table_name)["index_to_attr"].values()  # function by catalog
    # index_list = []
    
    if condition is None:  # no condition, return the whole table
        res_record = select_all_table(db_name, table_name)
    
    elif len(condition) == 1:  # one condition
        col, op, val = condition[0].strip().split(' ')
        if attr_type[col] == "int":
            val = int(val)
        elif attr_type[col] == "float":
            val = float(val)
        elif attr_type[col] == "char":
            val = val.strip('\'')
            val = val.strip('\"')
        if col in index_list:
            res_record = search_with_index(db_name, table_name, col, op, val)
        else:
            res_record = search_by_record(db_name, table_name, col, op, val)
    
    elif len(condition) == 2:  # two conditions
        # handle the first condition
        col, op, val = condition[0].strip().split(' ')
        if attr_type[col] == "int":
            val = int(val)
        elif attr_type[col] == "float":
            val = float(val)
        elif attr_type[col] == "char":
            val = val.strip('\'')
            val = val.strip('\"')
        if col in index_list:
            res1 = search_with_index(db_name, table_name, col, op, val)
        else:
            res1 = search_by_record(db_name, table_name, col, op, val)

        # handle the second condition
        col, op, val = condition[1].strip().split(' ')
        if attr_type[col] == "int":
            val = int(val)
        elif attr_type[col] == "float":
            val = float(val)
        elif attr_type[col] == "char":
            val = val.strip('\'')
            val = val.strip('\"')
        if col in index_list:
            res2 = search_with_index(db_name, table_name, col, op, val)
        else:
            res2 = search_by_record(db_name, table_name, col, op, val)

        # get the intersection records of res1 and res2
        res_record = [i for i in res1 if i in res2]
    
    else:
        print("At most 2 'AND' conditions!")


    # print(res_record)
    clear_list = []
    for item in res_record:
        if len(item) == len(attr_list):
            item = [s.strip().strip('\0') for s in item]
            clear_list.append(item)
    # print(res_record)
    count = len(clear_list)
    # print(count)
    print_record(table_name, clear_list, count)
    return count, clear_list


def select_all_table(db_name, table_name):
    table_file = table_name + '.csv'
    block_num = getBlockNum(db_name, table_file)  # max block number
    attr_list = attr_data(table_name)["attr_name"]  # function by catalog
    res_record = []  # result records

    for i in range(block_num + 1):
        block_list = buffer(db_name, table_file, i).strip().strip('\0').split('\n')
        for row in block_list:
       #     if len(row) == len(attr_list):
            res_record.append(row.split(','))
    # print("select all")
    return res_record


def search_with_index(db_name, table_name, col, op, val):
    # search_index_by_range(col, left_key=None, right_key=None, left_equal=False, right_equal=False)
    # return list of block_num and offset
    # search_index(self, index_name, key)
    # return record
    table_file = table_name + '.csv'
    index_key = attr_data(table_name)["attr_to_index"]
    index_name = index_key[col]
    if index_name is None:
        return
    manager = index_manager()  # new object
    if op == "=":
        pos = manager.search_index(index_name, val)
    elif op == ">":
        pos = manager.search_index_by_range(index_name, val, None, False, False)
    elif op == ">=":
        pos = manager.search_index_by_range(index_name, val, None, True, False)
    elif op == "<":
        pos = manager.search_index_by_range(index_name, None, val, False, False)
    elif op == "<=":
        pos = manager.search_index_by_range(index_name, None, val, False, True)
    else:
        print("Unknown operator!")
    manager.write_disk()
    res = []
    if pos == -1:
        return res
    if op == "=":
        block = buffer(db_name, table_file, int(pos[0])).split('\n')
        res.append(block[int(pos[1])].split(','))  # 'a,b,c,d' => ['a','b','c','d']
    else:
        for i in pos:  # i: [block_num, offset]
            block = buffer(db_name, table_file, int(i[0])).split('\n')
            res.append(block[int(i[1])].split(','))  # 'a,b,c,d' => ['a','b','c','d']
    return res


def search_by_record(db_name, table_name, col, op, val):
    table_file = table_name + '.csv'
    block_num = getBlockNum(db_name, table_file)  # max block number
    res = []  # result list of records
    # attr_list = catalogManager.getAttr(table_name) #attributes of table
    attr_info = attr_data(table_name)  # function by catalog
    attr_list = attr_info['attr_name']
    attr_type = attr_data(table_name)["attr_type"]
    index = attr_list.index(col)
    # print(block_num)
    # print(index)

    for num in range(block_num+1):
        block_list = buffer(db_name, table_file, num).strip().split('\n')
        for s in block_list:
            row = s.split(',')
            for j in range(len(row)):
                if attr_type[attr_list[j]] == "int":
                    row[j] = int(row[j])
                elif attr_type[attr_list[j]] == "float":
                    row[j] = float(row[j])
            if check_operator(op, row[index], val):
                res.append([str(i) for i in row])

    return res
            

def print_record(table_name, records, count):
    res_table = pt.PrettyTable()
    # attr_list = catalogManager.getAttr(table_name) #attributes of table
    attr_info = attr_data(table_name)  # function by catalog
    attr_list = attr_info['attr_name']
    res_table.field_names = attr_list
    for row in records:
        if len(row) == len(attr_list):
            res_table.add_row(row)
    print(res_table)
    print(str(count) + " rows in set.")


def delete_record(db_name, table_name, condition):
    # after handling exception by catalog manager
    table_file = table_name + '.csv'
    block_num = getBlockNum(db_name, table_file) # max block number
    # index_list = catalogManager.getIndex(table_name)
    index_list = []
    res_record = []

    for i in range(block_num+1):
        block_list = buffer(db_name, table_file, i).strip().split('\n')
        for row in block_list:
            res_record.append(row.split(','))

    if condition is None:  # clear the whole table
        count = len(res_record)
        for i in range(block_num+1):
            bufferSave(db_name, table_file, i, '\0')  # 好像不管用？？
            bufferClose()
        print("Table cleared!")
        return count
    
    elif len(condition) == 1:
        col, op, val = condition[0].strip().split(' ')
        if col in index_list:
            res_record, count = del_with_index(db_name, table_name, col, op, val)
        else:
            res_record, count = del_by_record(db_name, table_name, col, op, val)
    else:
        print("Too many conditions!")
        return

    # print(res_record)
    # print(str(count) + ' records deleted!')
    return count


def del_with_index(db_name, table_name, col, op, val):
    table_file = table_name + '.csv'
    attr_info = attr_data(table_name)  # function by catalog
    index_info = index_data(table_name)  # function by catalog
    res = []  # deleted records
    pos = []

    index_name = attr_info(table_name)["attr_to_index"][col]

    if index_name is None:
        return
    manager = index_manager()
    if op == "=":
        pos = manager.search_index(index_name, val)
    elif op == ">":
        pos = manager.search_index_by_range(index_name, val, None, False, False)
    elif op == ">=":
        pos = manager.search_index_by_range(index_name, val, None, True, False)
    elif op == "<":
        pos = manager.search_index_by_range(index_name, None, val, False, False)
    elif op == "<=":
        pos = manager.search_index_by_range(index_name, None, val, False, True)
    else:
        print("Unknown operator!")
    manager.write_disk()
    for i in pos:  # i: [block_num, offset]
        block_num = i[0]
        offset = i[1]
        block_list = buffer(db_name, table_file, block_num).split('\n')
        record = block_list[offset]  # 'a,b,c,d'
        res.append(record.split(','))  # => ['a','b','c','d']
        block_list.remove(record)  # append new value
        block_str = '\n'.join(block_list)  # convert to str in the block
        bufferSave(db_name, table_file, block_num, block_str)

    # delete index
    # delete_index(self, index_name, key)
    for name in index_info['index_name']:
        if index_info['index_to_attr'][name] == col:  # attr_name
            manager_1 = index_manager()
            manager_1.delete_index(name, val)
            manager_1.write_disk()

    return res, len(res)


def del_by_record(db_name, table_name, col, op, val):
    table_file = table_name + '.csv'
    attr_info = attr_data(table_name)  # function by catalog
    attr_list = attr_info['attr_name']
    block_num = getBlockNum(db_name, table_file)  # max block number
    res = []  # result list of records
    # attr_list = catalogManager.getAttr(table_name) #attributes of table
    col_index = attr_list.index(col)
    new_list = []
      
    for num in range(block_num+1):
        block_list = buffer(db_name, table_file, num).strip().split('\n')

        new_list = block_list[:]  # deep copy
        
        for s in block_list:
            row = s.split(',')
            if check_operator(op, row[col_index], val):  # if condition is satisfied
                res.append(row)
                new_list.remove(s)  # delete record

        block_str = '\n'.join(new_list)  # convert to str in the block
        # print(block_str)
        bufferSave(db_name, table_file, num, block_str)
        bufferClose()

    # print("test del", len(res))
    # print(block_list)
    # print(res)
    return res, len(res)


def check_operator(op, v, val):
    def f1(v):
        return v > val

    def f2(v):
        return v < val

    def f3(v):
        return v == val

    def f4(v):
        return v >= val

    def f5(v):
        return v <= val

    def f6(v):
        return v != val
    
    funcs = {'>': f1, '<': f2, '=': f3, '>=': f4, '<=': f5, '<>': f6}
    if op in funcs:
        check = funcs[op]
    else:
        print('Illegal operator!')
    
    flag = check(v)
    return flag


if __name__ == '__main__':
    # record values
    # record1 = ['A1', '文学', '了不起的盖茨比', '上海译文出版社', 2008, 'Jack', 25.3]
    # record2 = ['B2', '哲学', '理想国', '商务出版社', 2005, '大佬', 30.5]
    # record3 = ['C344', '英语', '托福阅读', '新东方出版社', 2011, '俞敏洪', 18.6]
    
    # # conditions
    # condition1 = ["category = 英语"]
    # condition2 = ["year > 2008"]
    # condition3 = ["category = 文学", "price > 27"]

    # table = 'book'
    create_table_file('db', 'zzz')
    # # print("block_num:", getBlockNum('db', table+'.csv'))
    # select_record('db', table, condition1)
    # select_record('db', table, condition3)
    # # select_record('db', table, condition3)

    # # delete_record('db', table, None)
    # delete_record('db', table, condition2)
    # insert_record('db', table, record1)
    # insert_record('db', table, record2)
    # select_record('db', table, None)

    # bufferClose()

    # drop_table_file('db', '1')