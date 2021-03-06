#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gcp_texttospeech.srv import TTS
#音声認識
import stt

import nltk
import pickle
import rospy
import Levenshtein as lev
from std_msgs.msg import String
from ggi.srv import GgiLearning
from ggi.srv import GgiLearningResponse

file='/home/athome/catkin_ws/src/ggi/' #作成場所の指定


class GgiinStruction:
    def __init__(self):

        #初期化
        with open(file+'object/object_file.pkl',"wb") as f:
            dictionary={'object_name':[],'object_feature':[],
                        'place_name':[],'place_feature':[]}
            pickle.dump(dictionary, f)

        with open(file+'set_word/place_name','r') as f:
            self.object_template=[line.strip() for line in f.readlines()]
        with open(file+'set_word/place_name','r') as c:
            self.place_template=[line.strip() for line in c.readlines()]
        self.name=[]
        self.feature=[]
        print("server is ready")
        rospy.wait_for_service('/tts')
        self.server=rospy.Service('/ggi_learning',GgiLearning,self.register_object)
        self.tts=rospy.ServiceProxy('/tts', TTS)

    #オブジェクト登録
    def register_object(self,req):
        recognition=''
        self.tts("please say the object.")
        while 1:
            if not recognition:
                string=stt.google_speech_api(phrases=self.object_template.append('finish　training'),boost=13.0)


                if  lev.distance(string, 'finish　training')/(max(len(string), len('finish　training')) *1.00)<0.3:
                    self.save_name('' , True)
                    self.name=[]
                    self.feature=[]
                    break

                self.tts(string + ' is this OK?')

            recognition = stt.google_speech_api()
            if 'yes' in recognition:
                self.save_name(string , True,add=False)
                recognition=''
                self.tts('next')

            elif 'no' in recognition:
                self.tts('please one more time')
                recognition=''

            elif 'again' in recognition:
                self.tts(string +' is this OK?')

        self.tts('Please tell me the place.')
        while 1:
            if not recognition:

                string=stt.google_speech_api(phrases=self.place_template)
                self.tts(string +' Is this OK?')

            recognition = stt.google_speech_api()

            if 'yes' in recognition:
                res=self.save_name(string , False)
                break

            elif 'no' in recognition:
                self.tts('please one more time')
                recognition=''

            elif 'again' in recognition:
                self.tts(string +' Is this OK?')

        self.feature=[]
        self.name=[]


        return GgiLearningResponse(location_name=res)



    #保存          s=string ob=name or place (True or False)
    def save_name(self,s,ob,add=True):

        split=nltk.word_tokenize(s)
        for h in range(len(split)):
            if split[h]=='the':
                split[h]='a'
        pos = nltk.pos_tag(split)

        for i in range(len(pos)):
            if pos[i][1]=='JJ':
                self.feature.append(pos[i][0])

            elif 'NN' in pos[i][1]:
                self.name.append(pos[i][0])
            #オブジェクト
        if add:
            with open(file+'object/object_file.pkl','rb') as web:
                dict=pickle.load(web)
            if ob:
                dict['object_name'].append(self.name)
                dict['object_feature'].append(self.feature)
                with open(file+'object/object_file.pkl','wb') as f:
                    pickle.dump(dict, f)
            #場所
            else:
                dict['place_name'].append(self.name)
                dict['place_feature'].append(self.feature)
                with open(file+'object/object_file.pkl','wb') as f:
                    pickle.dump(dict, f)
                if dict['place_feature'][len(dict['place_feature'])-1]:
                    str=' '.join(dict['place_feature'][len(dict['place_feature'])-1])+' '+' '.join(dict['place_name'][len(dict['place_name'])-1])
                else:
                    str=' '.join(dict['place_name'][len(dict['place_name'])-1])
                print(dict)
                return str


if __name__=='__main__':
    rospy.init_node('ggi_learning')
    GgiinStruction()
    rospy.spin()
