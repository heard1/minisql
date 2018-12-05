#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2018/6/9 15:16
# @Author : Drametov# @Site :
# @File : catalog_manager.py
# @Software: PyCharm

import csv
import interpreter
import copy
import re
from indexManager import index_manager

#######以下为可用接口#######


def deal(input):# if success, case == 1; if failed, case == 0
    if interpreter.interpreter(input):
        situation, detail = interpreter.interpreter(input)
    else:
        return
    # Read dictionary files
    dic = read_csv()
    case = 0
    if situation == 2:  # create table
        table_name = detail['table']
        unique = [x for x in detail['unique']]
        key = dict.keys(detail)
        attr = [x for x in key if (x != 'unique' and x != 'table' and x != 'primary')]
        attr_type = {}
        for attr_name in attr:
            attr_type[attr_name] = detail[attr_name]
        primary = detail['primary']
        dic, case = create_table(dic, table_name, unique, attr, attr_type, primary)
    elif situation == 3:  #  create index
        index_name = detail['index']
        table_name = detail['table']
        attr = detail['column']
        dic, case = create_index(dic, index_name, table_name, attr)
    elif situation == 5:  #  drop table
        table_name = detail['table']
        dic, case = drop_table(dic, table_name)
    elif situation == 6:  #  drop index
        index_name = detail['index']
        dic, case = drop_index(dic,index_name)
    elif situation == 7:  #  select
        table_name = detail['table']
        condition = detail['condition']
        case = select(dic, table_name, condition)
    elif situation == 8:  #  insert
        table_name = detail['table']
        line = detail['condition']
        values = line.split(',')
        case = insert(dic, table_name, values)
    elif situation == 9:  #  delete
        table_name = detail['table']
        condition = detail['condition']
        case = delete(dic, table_name, condition)
    #  Output dictionary file
    write_csv(dic)
    return case


def tables_data():
    data = {}
    dic = read_csv()
    table_num = int(dic[0][0])
    for x in range(table_num):
        data[x] = dic[x + 1][0]
    return data


def attr_data(table_name):
    data = {}
    dic = read_csv()
    # Find the table
    table_num = int(dic[0][0])
    table_place = find_table(table_name, table_num, dic)
    if table_place == -1:
        print("Table", table_name, "don't exist!")
        return data
    # Find attributions
    attr_name = []
    attr_type = {}
    attr_type_length = {}
    attr_unique = {}
    attr_to_index = {}
    attr_count = 0
    attr_num = int(dic[table_place][1])
    data["attr_num"] = attr_num
    for x in range(table_place - 1):
        attr_count += int(dic[x + 1][1])
    attr_place = attr_count + table_num + 1
    for x in range(attr_num):
        attr_type[dic[attr_place + x][0]] = dic[attr_place + x][1]
        attr_type_length[dic[attr_place + x][0]] = dic[attr_place + x][2]
        attr_unique[dic[attr_place + x][0]] = dic[attr_place + x][3]
        attr_name.insert(x, dic[attr_place + x][0])
        if dic[attr_place + x][4] == "NULL":
            attr_to_index[dic[attr_place + x][0]] = None
        else:
            attr_to_index[dic[attr_place + x][0]] = dic[attr_place + x][4]
    data["attr_name"] = attr_name
    data["attr_type"] = attr_type
    data["attr_type_length"] = attr_type_length
    data["attr_unique"] = attr_unique
    data["attr_to_index"] = attr_to_index
    return data


def index_data(table_name):
    data = {}
    dic = read_csv()
    # Find the table
    table_num = int(dic[0][0])
    table_place = find_table(table_name, table_num, dic)
    if table_place == -1:
        print("Table", table_name, "don't exist!")
        return data
    # Find index
    attr_count = 0
    attr_num = int(dic[table_place][1])
    for x in range(table_place - 1):
        attr_count += int(dic[x + 1][1])
    attr_place = attr_count + table_num + 1
    index_num = 0
    index_name = []
    index_to_attr = {}
    for x in range(attr_num):
        if dic[attr_place + x][4] != 'NULL':
            index_name.append(dic[attr_place + x][4])
            index_to_attr[dic[attr_place + x][4]] = dic[attr_place + x][0]
            index_num += 1
    data["index_num"] = index_num
    data["index_name"] = index_name
    data["index_to_attr"] = index_to_attr
    return data

#######以下为内部函数#######


def create_table(dic, table_name, unique, attr, attr_type, primary):
    tmp_dic = copy.deepcopy(dic)
    # Determine if the table name exists
    table_num = int(dic[0][0])
    table_place = find_table(table_name, table_num, dic)
    if table_place != -1:
        print("Table", table_name, "already exists!")
        return tmp_dic, 0
    # Update the number of tables, insert table data
    table_num += 1
    dic[0][0] = str(table_num)
    dic.insert(table_num, [table_name, len(attr), 0])
    attr_count = 0
    for x in range(table_num - 1):
            attr_count += int(dic[x + 1][1])
    # Insert attribute data
    insert_place = attr_count + table_num + 1
    for x in range(len(attr)):
        tmp_type, tmp_length = find_type(attr_type[attr[x]])
        unique_type = 'normal'
        index = 'NULL'
        for y in unique:
            if tmp_type == 'wrong':
                return tmp_dic, 0
            if y == attr[x]:
                unique_type = 'unique'
            else:
                unique_type = 'normal'
        if primary == attr[x]:
            index = table_name + attr[x]
            unique_type = 'unique'
        dic.insert(insert_place, [attr[x], tmp_type, tmp_length, unique_type, index])
        insert_place += 1
    print("Create table", table_name, "!")
    return dic, 1


def create_index(dic, index_name, table_name, attr):
    tmp_dic = copy.deepcopy(dic)
    # Determine if the table name exists
    table_num = int(dic[0][0])
    table_place = find_table(table_name, table_num, dic)
    if table_place == -1:
        print("Table", table_name, "don't exist!")
        return tmp_dic, 0
    attr_count = 0
    attr_num = int(dic[table_place][1])
    for x in range(table_place - 1):
        attr_count += int(dic[x + 1][1])
    attr_place = attr_count + table_num + 1
    for x in range(attr_num):
        if attr == dic[attr_place + x][0]:
            if dic[attr_place + x][3] != 'unique':
                print("Attr", attr, "is not unique !")
                return tmp_dic, 0
            elif dic[attr_place + x][4] != 'NULL':
                print("Attr", attr, "already has an index!")
                return tmp_dic, 0
            else:
                dic[attr_place + x][4] = index_name
                break
        elif x + 1 == attr_num and attr != dic[attr_place + x][0]:
            print("Attr", attr, "not exists !")
            return tmp_dic, 0
    print("Create index", index_name, "!")
    return dic, 1


def drop_table(dic, table_name):
    # Determine if the table name exists
    table_num = int(dic[0][0])
    table_place = find_table(table_name, table_num, dic)
    if table_place == -1:
        print("Table", table_name, "don't exist!")
        return dic, 0
    # Delete attribute data
    attr_count = 0
    for x in range(table_place - 1):
        attr_count += int(dic[x + 1][1])
    delete_place = attr_count + table_num + 1
    for x in range(int(dic[table_place][1])):
        if dic[delete_place][4] != 'NULL':
            index = index_manager()
            index.drop_index(dic[delete_place][4])
            index.write_disk()
        dic.pop(delete_place)
    # Delete table data and change the number of tables
    dic.pop(table_place)
    dic[0][0] = str(table_num - 1)
    print("Drop table", table_name, "!")
    return dic, 1


def drop_index(dic, index_name):
    tmp_dic = copy.deepcopy(dic)
    table_num = int(dic[0][0])
    length = len(dic)
    exist = 1
    for x in range(length):
        if x > table_num:
            if dic[x][4] == index_name:
                index = index_manager()
                index.drop_index(index_name)
                index.write_disk()
                dic[x][4] = 'NULL'
                exist = 0
            elif x + 1 == length and dic[x][4] != index_name and exist:
                print("Index", index_name, "not exists !")
                return tmp_dic, 0
    print("Index", index_name, "is dropped !")
    return dic, 1


def select(dic, table_name, condition):
    # Determine if the table name exists
    table_num = int(dic[0][0])
    table_place = find_table(table_name, table_num, dic)
    if table_place == -1:
        print("Table", table_name, "don't exist!")
        return 0
    # Determine whether the conditions are legal
    if condition[0] == '':
        return 1
    for x in condition:
        if get_condition(table_name, x) == 0:
            return 0
    return 1


def insert(dic, table_name, values):
    # Determine if the table name exists
    table_num = int(dic[0][0])
    table_place = find_table(table_name, table_num, dic)
    if table_place == -1:
        print("Table", table_name, "don't exist!")
        return 0
    # Confirm the number of values
    attr = attr_data(table_name)
    length = len(values)
    if length != attr["attr_num"]:
        print("Incorrect number of inserted values !")
        return 0
    # Confirm value type
    for x in range(length):
        name = attr["attr_name"][x]
        t = judge_type(values[x])
        stn = attr["attr_type"][name]
        if stn == 'char':
            st = 0
        elif stn == 'int':
            st = 1
        else:
            st = 2
        if t != st:
            if t == 1 and st == 2:
                continue
            else:
                print(values[x], "is not a", stn, "value")
                return 0
        elif t == st and st == 0:
            if int(attr["attr_type_length"][name]) + 2 < len(values[x].lstrip()):
                print(values[x], "is not a", stn, "(", attr["attr_type_length"][name], ")", "type value !")
                return 0
    print("Insert format correct !")
    return 1


def delete(dic, table_name, condition):
    # Determine if the table name exists
    table_num = int(dic[0][0])
    table_place = find_table(table_name, table_num, dic)
    if table_place == -1:
        print("Table", table_name, "don't exist!")
        return 0
    # Delete all records if there are no conditions
    if condition[0] == '':
        return 1
    # Determine whether the conditions are legal
    for x in condition:
        if get_condition(table_name, x) != 1:
            return 0
    return 1

#######以下是辅助性函数#######


def read_csv():
    with open('database/db/dictionary.csv') as r:
        reader = csv.reader(r)
        dic = []
        for row in reader:
            dic.append(row)
    return dic


def write_csv(dic):
    with open('database/db/dictionary.csv', 'w', newline='') as w:
        writer = csv.writer(w)
        writer.writerows(dic)


def find_table(table_name, table_num, dic):
    table_place = 0
    if table_num == 0:
        return -1
    for x in range(table_num):
        if dic[x + 1][0] == table_name:
            table_place = x + 1
            break
        elif x + 1 == table_num and dic[x + 1][0] != table_name:
            return -1
    return table_place


def find_type(type):
    if type == 'int':
        return 'int', 0
    elif type == 'float':
        return 'float', 0
    elif re.compile(r'char\((.*)\)').findall(type) != []:
        t = re.compile(r'char\((.*)\)').findall(type)
        attr_length = t[0]
        attr_length = int(attr_length)
        return 'char', attr_length
    else:
        print("type", type, "is illegal !")
        return 'wrong', 0


def judge_type(str):
    str = str.lstrip()
    length = len(str)
    if (str[0] == '\'' and str[length - 1] == '\'') or (str[0] == '\"' and str[length - 1] == '\"'):
        type = 0
    elif str.isdigit():
        type = 1
    else:
        count = 1
        t = str.split('.')
        for x in t:
            count *= x.isdigit()
        if count and len(t) == 2:
            type = 2
        else:
            type = 3
    return type


def get_condition(table_name, condition):
    con = condition.split(' ')
    while '' in con:
        con.remove('')
    attr = attr_data(table_name)
    if len(con) < 3:
        print("sucess!")
        return 0
    attr_name = con[0]
    const = con[2]
    attr_name = attr_name.lstrip()
    const = const.lstrip()
    count = 0
    # Determine if the attribute exists
    for x in range(len(attr["attr_name"])):
        if attr_name == attr["attr_name"][x]:
            count = 1
    if count == 0:
        print("Attribute", attr_name, "don't exist !")
        return 0
    # Determine whether the conditions are legal
    judge = judge_type(const)
    if attr["attr_type"][attr_name] == 'char':
        if judge == 0 and len(const) <= int(attr["attr_type_length"][attr_name]) + 2:
            return 1
        else:
            print(attr_name, "and", const, "do not match !")
            return 0
    elif attr["attr_type"][attr_name] == 'int':
        if judge == 1:
            return 1
        else:
            print(attr_name, "and", const, "do not match !")
            return 0
    elif attr["attr_type"][attr_name] == 'float':
        if judge == 1 or judge == 2:
            return 1
        else:
            print(attr_name, "and", const, "do not match !")
            return 0


if __name__ == '__main__':
    #  此处是获取输入语句（待插入）
    #  a = 'Create table book (bno int unique, name char(4) unique, price float, primary key (bno));'
    #  deal(a)
    #  b = 'Drop table book;'
    #  deal(b)
    #  c = 'Create index key on book(name);'
    #  deal(c)
    #  d = 'Drop index key;'
    #  deal(d)
    #  e = 'Select * from book where bno = 12'
    #  deal(e)
    #  f = "Insert into book values(11, 'gate', 15.53);"
    #  deal(f)
    #  g = "Select * from book where bno < 15;"
    #  deal(g)
      h = "Delete from book where bno < 15 and name = 'good';"
      deal(h)
    #  test1 = tables_data()
    #  test2 = attr_data('book')
    #  test3 = index_data('book')
    #  i = judge_type('2.5')
    #  print(i)
    # h = get_condition('book',"price <= 12.5")
    # b = 1
