# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str, smart_unicode

import xml.etree.ElementTree as ET
import urllib,urllib2,time,hashlib
import json

import socket
import sys
import codecs
encoding_type = sys.getfilesystemencoding()

TOKEN = "jasonlv"
flag = 0

@csrf_exempt
def handleRequest(request):
        if request.method == 'GET':
                #response = HttpResponse(request.GET['echostr'],content_type="text/plain")
                response = HttpResponse(checkSignature(request),content_type="text/plain")
                return response
        elif request.method == 'POST':
                #c = RequestContext(request,{'result':responseMsg(request)})
                #t = Template('{{result}}')
                #response = HttpResponse(t.render(c),content_type="application/xml")
                response = HttpResponse(responseMsg(request),content_type="application/xml")
                return response
        else:
                return None

def checkSignature(request):
        global TOKEN
        signature = request.GET.get("signature", None)
        timestamp = request.GET.get("timestamp", None)
        nonce = request.GET.get("nonce", None)
        echoStr = request.GET.get("echostr",None)

        token = TOKEN
        tmpList = [token,timestamp,nonce]
        tmpList.sort()
        tmpstr = "%s%s%s" % tuple(tmpList)
        tmpstr = hashlib.sha1(tmpstr).hexdigest()
        if tmpstr == signature:
                return echoStr
        else:
                return None

def responseMsg(request):
        rawStr = smart_str(request.raw_post_data)
        #rawStr = smart_str(request.POST['XML'])
        msg = paraseMsgXml(ET.fromstring(rawStr))
        
        queryStr = msg.get('Content')
        helpmessage = "输入:" + '\n' + "1:音乐加空格加您想搜索的关键词 " + '\n' + "2:图书加空格加您想搜索的关键词" + '\n' + "3:电影加空格加您想搜索的关键词" + '\n' +'例如：音乐 The Wall'

        start = "谢谢您使用豆瓣评分，我们的应用正在开发中，如有错误，请包容"
        replyContent = smart_str(start) + '\n'
        replyContent = replyContent + '\n'
        
        #return getReplyXml(msg,replyContent)
        #replyContent = ''
        queryStr_list = queryStr.split(' ',1)
        
        
        if queryStr_list[0] != "" and len(queryStr_list) > 1:
                flag = queryStr_list[0]

                if flag == '音乐':
                        #sreturn getReplyXml(msg,queryStr_list[1])
                        for id in search(queryStr_list[1],'music'):
                                #return getReplyXml(msg,queryStr_list[1])
                                replyContent = smart_unicode(replyContent) + get_item_rating('music',id) + '\n'

                        
                elif flag == '图书':
                        for id in search(queryStr_list[1],'book'):
                                replyContent = smart_unicode(replyContent) + get_item_rating('book',id) + '\n'

                        
                elif flag == '电影':
                        replyContent = smart_unicode(replyContent) +get_movie_rating(queryStr_list[1])
                else:
                        replyContent = replyContent + smart_str(helpmessage)
                                        


        else:
                replyContent = replyContent + smart_str(helpmessage)
                
        
        return getReplyXml(msg,replyContent)

def getReplyXml(msg,replyContent):
        extTpl = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>";
        extTpl = extTpl % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'text',replyContent)
        return extTpl
    
def paraseMsgXml(rootElem):
        msg = {}
        if rootElem.tag == 'xml':
                for child in rootElem:
                        msg[child.tag] = smart_str(child.text)
        return msg
    
    
def get_item_id(url, item_type):
        """get the douban item id,which type id "musics" ,"books", and"movies"""
 
        f = urllib.urlopen(url)
        text = json.loads(f.read())

        if item_type == 'movies':
                return [item['id'] for item in text['subjects']]
        else:
                return [item['id'] for item in text[item_type]]

def search(keyword, type_of_item , count = "12"):
        #url:https://api.douban.com/v2/book/search?q=eminem
        base_url = "https://api.douban.com/v2/"
        
        #book_url = urlparse.urljoin(url_base_url,"q+"+keyword)
        item_url = base_url + type_of_item + '/' + 'search?'+ "q="+ keyword + '&'+"count=" + count
        #print item_url
        return get_item_id(item_url, type_of_item + 's')
        

def get_item_rating(type_of_item, id):

        base_url = 'https://api.douban.com/v2/'
        item_url = base_url + type_of_item + '/' + id

        f = urllib.urlopen(item_url)
        content = json.load(f)

        rating = content["rating"]['average']
        name = content['title']
        #print str(name).decode('UTF-8').encode(encoding_type) + ' ' + str(rating).decode('UTF-8').encode(encoding_type)
        return smart_unicode(str(rating) + ' ' + name)

def get_movie_rating(keyword, count = "12"):
        #url:https://api.douban.com/v2/book/search?q=eminem
        base_url = "https://api.douban.com/v2/"
        
        #book_url = urlparse.urljoin(url_base_url,"q+"+keyword)
        item_url = base_url + "movie" + '/' + 'search?'+ "q="+ keyword + '&'+"count=" + count

        f = urllib.urlopen(item_url)
        text = json.loads(f.read())

        rating = ''

        for i in text['subjects']:
                rating = smart_unicode(rating) + str(i['rating']['average']) + ' ' +  i['title'] + '\n' 

        return smart_unicode(rating)

