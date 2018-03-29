import itchat
import pickle
import time
import datetime
import difflib
import random
import pymysql.cursors

Learning_mod_user={}
key_words={}
key_in={}

class robot(object):

    def __init__(self):
        #self.learning_model=learning_model #a flag which shows whether learning moder open or close
        self.other_dit={}
        self.msg_text=''
        #self.learning_step_key = None
        #self.learning_step_value = None
        self.more_words = {}
        self.learning_call_back = ''
        self.similar=0
        self.similar_data=[]
        self.random=-1
        self.length=0
        self.key_all_key=[]
        self.i=0
        self.connection=None


    def contact_model(self,text):
        if text not in key_words:
            return '我还没有学习这个'
        else:
            return key_words[text][0][random.randint(0,len(key_words[text][0]))]

    def check(self,text,user_name):#check if learning moder or chat ,check only enable when chatting
        if user_name in Learning_mod_user :
            if text=='退出学习模式':

                del Learning_mod_user[user_name]
                #self.msg_text=key_words[text][0][random.randint(0,len(key_words[text][0]))]
                self.msg_text = key_words[text][random.randint(0, len(list(key_words[text]))-1)]
                self.save_myself()
            else:
                self.msg_text=self.learning_step(text,user_name) #调用机器人
                #self.msg_text='我该回答什么呢'
        else:
            #print(key_words)
            if text in key_words:  # find
                if text == '进入学习模式':
                    Learning_mod_user[user_name] = 1

                    self.save_tempfile()
                else:  # normal chat
                    pass
                self.msg_text = key_words[text][random.randint(0,len(list(key_words[text]))-1)]
            elif self.find_similar(text):
                self.msg_text=key_words[self.similar_data[self.random]][random.randint(0,len(key_words[self.similar_data[self.random]])-1)]
            else:
                self.msg_text = '我还没有学习这个，回复 帮助 就可查看教我学习的方法'

        return self.msg_text

    def learning_step(self, text,user_name):

        if Learning_mod_user[user_name]% 2 == 1:

            self.other_dit[user_name]=text #key

            self.learning_call_back='我要回答什么呢'

        else:
            self.more_words[self.other_dit[user_name]]=text #value
            #self.learning_step_value=text
            self.learning_call_back='get,结束学习 请回复 退出学习模式 或者输入题目继续开始学习 Plufo祝福你哦'
            key_words.setdefault(self.other_dit[user_name],[]).append(self.more_words[self.other_dit[user_name]])
        Learning_mod_user[user_name]+=1
        return self.learning_call_back
    def connect_mysql(self):
        self.connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='cailuqi',
                                     db='robot',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

    def load_myself(self):
        self.connect_mysql()
        try:

            with self.connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT `Question`, `Answer` FROM `information` "
                cursor.execute(sql)
                result = cursor.fetchall()

                i = 0
                print('I have '+str(len(result))+' words')
                for i in range(0, len(result)):

                    temp_dict = result[i]
                    dict_key = temp_dict['Question']
                    dict_value = temp_dict['Answer']

                    key_words.setdefault(dict_key,[]).append(dict_value)


        finally:
            self.connection.close()

    def save_myself(self):
        self.connect_mysql()
        try:
            with self.connection.cursor() as cursor:
                for key in self.more_words:
                    # Create a new record
                    sql = "INSERT INTO `information` (`Question`, `Answer`) VALUES (%s, %s)"
                    val = self.more_words[key]
                    cursor.execute(sql, (str(key), val))
                    self.connection.commit()
        finally:
            self.connection.close()


    def save_tempfile(self): #每次进入学习模式时候保存
        t=time.time()
        time_s = int((round(t * 1000))) #毫秒级
        f = open('temp_data\myself ' + str(time_s) + '.txt', 'wb')
        pickle.dump(key_words, f)
        f.close()

    def find_similar(self,text):
        self.similar=0
        self.key_all_key=list(key_words.keys())
        self.length=0
        self.similar_data=[]
        #print(self.key_all_key)
        for self.i in range(0,len(self.key_all_key)) :

            self.similar=difflib.SequenceMatcher(None,text,str(self.key_all_key[self.i])).quick_ratio()
            if self.similar >= 0.75 :
                self.similar_data.append(self.key_all_key[self.i])
        self.length=len(self.similar_data)
        if self.length >0 :
            self.random = random.randint(0, self.length - 1)
            return True
        else:
            return False



y = robot()
y.load_myself()
@itchat.msg_register(itchat.content.TEXT)

def text_reply(msg):
    user_name=msg.fromUserName
    print(msg.fromUserName+" : "+msg.text)
    call_b=y.check(msg.text,user_name)
    itchat.send_msg(call_b,user_name)
def add_friend(msg):
    msg.user.verify()
    msg.user.send('Nice to meet you')


itchat.auto_login(enableCmdQR=2,hotReload=True)
itchat.run()






