import interpreter
import catalog_manager
import recordManager
import re
import prettytable as pt
from indexManager import index_manager


def input_instruction(string):
    situation, detail=interpreter.interpreter(string)
    if situation == 12:
        for i in detail:
            print(i)
            if i[0] == "q":
                break
            else:
                input_instruction(i)
    if situation == 0 or situation == 11:
        return
    elif catalog_manager.deal(string) == 0:
        return
    elif situation == 1 or situation == 2 or situation == 3:
        return create(situation,detail)
    elif situation == 4 or situation == 5 or situation == 6:
        return drop(situation,detail)
    elif situation == 7:
        return select(detail)
    elif situation == 8:
        return insert(detail)
    elif situation == 9:
        return delete(detail)
    # use database
    elif situation == 10:
        return


def create(situation,detail):
    # create database
    if situation == 1:
        return
    # create table
    elif situation == 2:
        table_name = detail['table']

        recordManager.create_table_file("db", table_name)
        if 'primary' in detail:
            index_name = table_name + detail['primary']
            index = index_manager()
            index.create_index(table_name, index_name, detail['primary'])
            index.write_disk()
        return
    # create index
    elif situation == 3:
        table_name = detail['table']
        index_name = detail['index']
        key_arr = detail['column']
        index = index_manager()
        index.create_index(table_name, index_name, key_arr)
        index.write_disk()
        return


def drop(situation,detail):
    # drop database
    if situation == 4:
        return
    # drop table
    elif situation == 5:
        table_name = detail['table']
        recordManager.drop_table_file("db", table_name)
        return
    # drop index
    elif situation == 6:
        index_name = detail['index']
        return


def select(detail):
    table_name = detail['table']
    con = detail['condition']
    condition = con
    if con[0] == '':
        condition = None
    recordManager.select_record("db", table_name, condition)


def insert(detail):
    table_name = detail['table']
    con = detail['condition']
    condition = con.split(',')
    attr = catalog_manager.attr_data(table_name)
    for x in range(attr["attr_num"]):
        if attr["attr_type"][attr["attr_name"][x]] == "int":
            condition[x] = int(condition[x])
        elif attr["attr_type"][attr["attr_name"][x]] == "float":
            condition[x] = float(condition[x])
        elif attr["attr_type"][attr["attr_name"][x]] == "char":
            if condition[x][0] == '\'':
                condition[x] = re.findall(r'\'(.*)\'', condition[x])[0]
            elif condition[x][0] == '\"':
                condition[x] = re.findall(r'\"(.*)\"', condition[x])[0]
    recordManager.insert_record("db", table_name, condition)


def delete(detail):
    table_name = detail['table']
    condition = detail['condition']
    if condition[0] == '':
        condition = None
    recordManager.delete_record("db", table_name, condition)


if __name__ == '__main__':
    print("------------------Welcome to use our MiniSQL-------------------")
    while True:
        read_input = input("MiniSQL>>>")
        print(read_input)
        if read_input[0] == "q":
            break
        input_instruction(read_input)
