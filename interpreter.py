import re

strnow=""
def interpreter(string):
    #remove ' ' in tail
    while(string[-1]==' '):
        string=string[:-1]
    #if there is a ';'    
    if string[-1]!=';':
        print("syntax error: no ';' in the end!")
        return None
    string=string[:-1]
    #switch type
    global strnow
    strnow=string.lower()
    tem=string.lower().split(' ')#make it be lower charactor and list
    tem = [x for x in tem if x != '']
    #judge the first word to decide which function should be done
    if tem[0]=='create':
        return create(tem)
    elif tem[0]=='drop':
        return drop(tem)
    elif tem[0]=='select':
        return select(tem)
    elif tem[0]=='insert':
        return insert(tem)
    elif tem[0]=='delete':
        return delete(tem)
    elif tem[0]=='use':
        return use(tem)
    elif tem[0]=='execfile':
        return execfile(tem)
    elif tem[0]=='help':
        return help(tem)
    elif tem[0]=='quit':
        return quit(tem)
    else:
        print("syntax error:",tem[0],"is not a valid key word!")
        return 0, None

def create(tem):
    if tem[1] == 'database':
        if len(tem) != 3:#judge the syntax
            print("syntax error: database name error!")
            return 0, None
        return 1,{'database':tem[2]}
    if tem[1] == 'table':
        try:
            result={'table':tem[2]}
            result['unique']=[]#store the unique column by a list
            b=re.findall(r'\((.*)\)',strnow)
            c=""
            res=c.join(b).split(",")#find every type
            for i in res:
                rr=[x for x in i.split(' ') if x!='']#find evey 'unique' in end of a type
                result[rr[0]]=rr[1]
                if len(rr)== 3:
                    if rr[2] == 'unique':
                        result['unique'].append(rr[0])
                    elif rr[0] == 'primary':
                        result['primary']=re.findall(r'\((.*)\)',rr[2])[0]
                    else:
                        print("syntax error!")
                        return 0, None  
            return 2, result
        except:
            print("syntax error!")
            return 0, None
    if tem[1] == 'index':
        try:
            res = {'index':tem[2]}
            res['table']=tem[4]
            b=re.findall(r'\((.*)\)',strnow)#find the (***)
            str=""
            res['column']=str.join(b)
            res["table"]=res["table"].split('(')[0]
            return 3, res
        except:
            print("syntax error!")
            return 0, None
    print("syntax error:",tem[1],"is not a valid key word!")
    return None

def drop(tem):
    if len(tem) != 3:
        print("syntax error: drop sentence is wrong!")
    if tem[1] == 'database':
        return 4,{'database':tem[2]}
    if tem[1] == 'table':
        return 5,{'table':tem[2]}
    if tem[1] == 'index':
        return 6,{'index':tem[2]}
    print("syntax error:",tem[1],"is not a valid key word!")
    return 0,None

def select(tem):
    try:
        dic = {"table":tem[3],"colomn":tem[1]}
        b=re.findall(r'where(.*)',strnow)
        c=""
        c=c.join(b).split("and")
        dic["condition"]=c
        return 7,dic
    except:
        print("syntax error!")
        return 0,None
    
def insert(tem):
    try:
        dic = {"table":tem[2]}
        b=re.findall(r'\((.*)\)',strnow)
        c=""
        c=c.join(b)
        dic["condition"]=c
        return 8, dic
    except:
        print("syntax error!")
        return 0, None
    
def delete(tem):
    try:
        dic = {"table":tem[2]}
        b=re.findall(r'where(.*)',strnow)
        c=""
        c=c.join(b).split('and')
        dic["condition"]=c
        return 9, dic
    except:
        print("syntax error!")
        return 0, None
    
def use(tem):
    try:
        if len(tem)!=2:
           print("syntax error!")
           return 0, None 
        dic = {"database":tem[1]}
        return 10, dic
    except:
        print("syntax error!")
        return 0, None
    
def help(tem):
    print("use the correct syntax like 助教提供的！")   
    return 11,None
    
def quit(tem):
    if tem[0]=="quit" and len(tem)==1 :
        return 12,True
    else:
        return 0,False
    
def execfile(tem):    
    url=tem[1]
    f=open(url,'r')
    a=f.read().split('\n')
    res=[]
    for i in a:
        if i:
            res.append(i)
    return 12,res
    
if __name__=='__main__':
    a="create index qwq on book (bno);"
    a,a1=interpreter(a)
    b="create table hello ( a int unique, b char(30), c float unique, primary key (a)); "
    b,b1=interpreter(b)
    c="select * from book where bno = 12 and cno =12 ;"
    c,c1=interpreter(c)
    d="create index iname on t1 (name);"
    d,d1=interpreter(d)
    e="drop table hello;"
    e,e1=interpreter(e)
    f="insert into hello values(12,hello,qw);"
    f,f1=interpreter(f)
    g="delete from hello where name=dby and fuck = 12;"
    g,g1=interpreter(g)
    h="use hellobase ;"
    h,h1=interpreter(h)
    i="quit;"
    i,i1=interpreter(i)
    j="help;"
    j,j1=interpreter(j)
    k="execfile /Users/admin/Desktop/数据库/a.txt; "
    k,k1=interpreter(k)