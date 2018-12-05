"""
访问的文件必须存在！请先在相应文件夹创建文件！
每次改完file要用bufferSave函数！
"""
"""
调用读取文件函数
读取文件，存入对象，读取上限为4K；
调用存入文件函数
把改变的对象存入buffer
"""
import os
from sys import getsizeof 
#储存不同文件，key为文件名
blocks={}
#储存文件访问次数用来LRU，每1000次读取更新1次
fresh=0
times={}
maxsize=4096#一个块最大为4096byte
#参数分别为：数据库名，表|索引名，第几块（从0开始）
def buffer(databaseName,target,num):
    try:
        url=databaseName+'/'+target+'/'+str(num)
        if url in blocks.keys():#如果已经存在，直接返回
            times[url]+=1
            return blocks[url]
        elif getsizeof(blocks)<maxsize*64:#一共有64个block
            path='database/'+databaseName+'/'+target
            f=open(path,'r')
            f.seek(maxsize*num)#偏移到第几块
            blocks[url]=f.read(maxsize)#读入4096
            f.close()
            times[url]=1
            return blocks[url]
        else:
            key=min(times.items(), key=lambda x: x[1])[0]
            #关闭最少使用项
            p=key.split('/')
            f=open('database/'+p[0]+'/'+p[1],'r+')
            f.seek(maxsize*int(p[2]))#偏移到第几块
            f.write(blocks[key])#写入
            f.close()
            times.pop(key)
            blocks.pop(key)           
            #打开新项目
            path='database/'+databaseName+'/'+target
            f=open(path,'r')
            f.seek(maxsize*num)#偏移到第几块
            blocks[url]=f.read(maxsize)#读入4096
            f.close()
            times[url]=1
            return blocks[url]
        #每次更新fresh++
        global fresh
        fresh+=1
        if fresh == 1000:
            fresh = 0
            for i in times:
                times[i]=0
    except:
        print("there is a error in opening file!")
        return None
    
#每修改一次block调用
def bufferSave(databaseName,target,num,block):
	try:
		url=databaseName+'/'+target+'/'+str(num)
		blocks[url]=block
	except:
		print("can not find the block!")

#获取最大块的编号
def getBlockNum(databaseName,target):
    path='database/'+databaseName+'/'+target
    return os.path.getsize(path)//4096

#结束整个minisql时调用，把缓存写入所有文件
def bufferClose():
    for key in blocks:
        p=key.split('/')
        f=open('database/'+p[0]+'/'+p[1],'r+')
        f.seek(maxsize*int(p[2]))#偏移到第几块
        f.write(' '*4096)#写入
        f.close()
        f=open('database/'+p[0]+'/'+p[1],'r+')
        f.seek(maxsize*int(p[2]))#偏移到第几块
        f.write(blocks[key])#写入
        f.close()
    blocks.clear()
    bufferClear()
    return


def bufferClear():
    path = "database/db"
    files= os.listdir(path)
    for file in files:
        if file[0] != '.' and file[0:5] != 'index':
            f = open(path+"/"+file,'r')
            string=f.read()
            #print(string)
            string=string.replace(' ','')
            string=string.split('\n')
            f.close()
            while '' in string:
                string.remove('')
            a="\n"
            string=a.join(string)
            #string=a
            f = open(path+"/"+file,'w')
            f.write(string)
            f.close()

    return
    
if __name__=='__main__':
    file=buffer('db','table.csv',0)
 #   bufferSave('db','table.csv',0,file)

