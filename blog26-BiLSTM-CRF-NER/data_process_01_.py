#encoding:utf-8
import os
import re

#----------------------------功能:获取实体类别及个数---------------------------------
def get_entities(dirPath):
    entities = {}                 #存储实体类别
    files = os.listdir(dirPath)   #遍历路径

    #获取所有文件的名字并去重 0.ann => 0
    filenames = set([file.split('.')[0] for file in files])
    filenames = list(filenames)
    #print(filenames)

    #重新构造ANN文件名并遍历文件
    for filename in filenames:
        path = os.path.join(dirPath, filename+".ann")
        #print(path)
        #读文件
        with open(path, 'r', encoding='utf8') as f:
            for line in f.readlines():
                #TAB键分割获取实体类型
                name = line.split('\t')[1]
                #print(name)
                value = name.split(' ')[0]
                #print(value)
                #实体加入字典并统计个数
                if value in entities:
                    entities[value] += 1   #在实体集合中数量加1
                else:
                    entities[value] = 1    #创建键值且值为1
    #返回实体集
    return entities

#----------------------------功能:命名实体BIO标注--------------------------------
def get_labelencoder(entities):
    #排序
    entities = sorted(entities.items(), key=lambda x: x[1], reverse=True)
    print(entities)
    #获取实体类别名称
    entities = [x[0] for x in entities]
    print(entities)
    #标记实体
    id2label = []
    id2label.append('O')
    #生成实体标记
    for entity in entities:
        id2label.append('B-'+entity)
        id2label.append('I-'+entity)

    #字典键值生成
    label2id = {id2label[i]:i for i in range(len(id2label))}

    return id2label, label2id

#-------------------------功能:自定义分隔符文本分割------------------------------
def split_text(text):
    #分割后的下标
    split_index = []

    #--------------------------------------------------------------------
    #                             文本分割
    #--------------------------------------------------------------------
    #第一部分 按照符号分割
    pattern = '。|，|,|;|；|？|\?|\.'
    
    #获取字符的下标位置
    for m in re.finditer(pattern, text):
        """
        print(m)
        start = m.span()[0]   #标点符号位置
        print(text[start])
        start = m.span()[0] - 5
        end = m.span()[1] + 5
        print('****', text[start:end], '****')
        """
        #特殊符号下标
        idx = m.span()[0]
        #判断是否断句 contniue表示不能直接分割句子
        if text[idx-1]=='\n':         #当前符号前是换行符
            continue
        if text[idx-1].isdigit() and text[idx+1].isdigit():  #前后都是数字或数字+空格
            continue
        if text[idx-1].isdigit() and text[idx+1].isspace() and text[idx+2].isdigit():
            continue
        if text[idx-1].islower() and text[idx+1].islower():  #前后都是小写字母
            continue
        if text[idx-1].isupper() and text[idx+1].isupper():  #前后都是大写字母
            continue
        if text[idx-1].islower() and text[idx+1].isdigit():  #前面是小写字母 后面是数字
            continue
        if text[idx-1].isupper() and text[idx+1].isdigit():  #前面是大写字母 后面是数字
            continue
        if text[idx-1].isdigit() and text[idx+1].islower():  #前面是数字 后面是小写字母
            continue
        if text[idx-1].isdigit() and text[idx+1].isupper():  #前面是数字 后面是大写字母
            continue
        if text[idx+1] in set('.。;；,，'):                  #前后都是标点符号
            continue
        if text[idx-1].isspace() and text[idx-2].isspace() and text[idx-3].isupper():
            continue                                         #HBA1C  。两个空格+字母
        if text[idx-1].isspace() and text[idx-3].isupper():
            continue
            #print(path)
            #print('****', text[idx-20:idx+20], '****')
        
        #将分句的下标存储至列表中 -> 标点符号后面的字符
        split_index.append(idx+1)

    #--------------------------------------------------------------------
    #第二部分 按照自定义符号分割
    #下列形式进行句子分割
    pattern2 = '\([一二三四五六七八九十零]\)|[一二三四五六七八九十零]、|'
    pattern2 += '注:|附录 |表 \d|Tab \d+|\[摘要\]|\[提要\]|表\d[^。，,;；]+?\n|'
    pattern2 += '图 \d|Fig \d|\[Abdtract\]|\[Summary\]|前  言|【摘要】|【关键词】|'
    pattern2 += '结    果|讨    论|and |or |with |by |because of |as well as '
    #print(pattern2)            
    for m in re.finditer(pattern2, text):
        idx = m.span()[0]
        #print('****', text[idx-20:idx+20], '****')
        #连接词位于单词中间不能分割 如 goodbye
        if (text[idx:idx+2] in ['or','by'] or text[idx:idx+3]=='and' or text[idx:idx+4]=='with')\
            and (text[idx-1].islower() or text[idx-1].isupper()):
            continue
        split_index.append(idx)  #注意这里不加1 找到即分割

    #--------------------------------------------------------------------
    #第三部分 中文字符+数字分割
    #判断序列且包含汉字的分割(13.接下来...) 同时小数不进行切割
    pattern3 = '\n\d\.'  #数字+点
    for m in  re.finditer(pattern3, text):
        idx = m.span()[0]
        if ischinese(text[idx+3]): #第四个字符为中文汉字 含换行
            #print('****', text[idx-20:idx+20], '****')
            split_index.append(idx+1)

    #换行+数字+括号  (1)总体治疗原则:淤在选择降糖药物时
    for m in re.finditer('\n\(\d\)', text):
        idx = m.span()[0]
        split_index.append(idx+1)

    #--------------------------------------------------------------------
    #获取句子分割下标后进行排序操作 增加第一行和最后一行
    split_index = sorted(set([0, len(text)] + split_index))
    split_index = list(split_index)
    #print(split_index)

    #计算机最大值和最小值
    lens = [split_index[i+1]-split_index[i] for i in range(len(split_index)-1)]
    print(max(lens), min(lens))
        
    #输出切割的句子
    #for i in range(len(split_index)-1):
    #    print(i, '******', text[split_index[i]:split_index[i+1]])


#---------------------------功能:判断字符是不是汉字-------------------------------
def ischinese(char):
    if '\u4e00' <=char <= '\u9fff':
        return True
    return False

#-------------------------------功能:主函数--------------------------------------
if __name__ == '__main__':
    dirPath = "data/train_data"

    #获取实体类别及个数
    entities = get_entities(dirPath)
    print(entities)
    print(len(entities))

    #完成实体标记 列表 字典
    #得到标签和下标的映射
    label, label_dic = get_labelencoder(entities)
    print(label)
    print(len(label))
    print(label_dic, '\n\n')

    #遍历路径
    files = os.listdir(dirPath)   
    filenames = set([file.split('.')[0] for file in files])
    filenames = list(filenames)
    for filename in filenames:
        path = os.path.join(dirPath, filename+".txt")  #TXT文件
        #print(path)
        with open(path, 'r', encoding='utf8') as f:
            text = f.read()
            #分割文本
            split_text(text)
    print("\n")
