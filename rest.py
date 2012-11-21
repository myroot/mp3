#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, json
from twisted.internet import reactor
from twisted.web import server, resource
from twisted.web.static import File
from twisted.python import log
from twisted.web.server import Session
import time
import mydownload
import threading

def downloadThread(fd,lock,queue):
    print 'start thread'
    while 1 :
        lock.acquire()
        while len(queue) == 0 :
            lock.wait()
        key = queue.pop()
        lock.release()
        fd.download_by_id(key[0], key[1])

class DownloadSession(Session):
    def __init__(self,site,uid):
        Session.__init__(self,site,uid)
        print 'create session'
        self.fd = mydownload.myDownload()
        self.notifyOnExpire(lambda: self.userExpired())
        self.lock = threading.Condition()
        self.queue = []
        reactor.callInThread(downloadThread,self.fd,self.lock,self.queue)   
    def userExpired(self):
        self.fd.clear_all()
        pass
class Root(resource.Resource):
    def render_GET(self, request):
        return 'Hello world user session'

    def getChild(self, name, request):
        if name == '':
            return self
    
        return resource.Resource.getChild(self, name, request)

class Down(resource.Resource):
    def render_GET(self, request):
        print 'request download'
        request.setHeader('content-type','application/x-javascript')
        lock = request.getSession().lock
        fd = request.getSession().fd
        queue = request.getSession().queue
        print request.args
        callback = request.args['callback'][0]
        key = request.args['key'][0]
        upload = request.args['upload'][0]
        if upload == '1' :
            upload = True
        else:
            upload = False
        lock.acquire()
        queue.insert(0,(key,upload))
        lock.notifyAll()
        lock.release()
        return callback+'('+json.dumps({'key':key,'status':'ok'})+')'
    def render_POST(self, request):
        return self.render_GET(request)
    

class Update(resource.Resource):
    def render_GET(self, request):
        request.setHeader('content-type','application/x-javascript')
        fd = request.getSession().fd
        callback = request.args['callback'][0]
        try:
            key = request.args['key'][0]
            progress = fd.logstack[key]['process']
            status = fd.logstack[key]['state']
            path = fd.logstack[key]['path']
            return callback+'('+json.dumps({'key':key,'status':status,'progress':progress, 'path':path,'time':time.time()})+')'
        except:
            return callback+'('+json.dumps({'key':key,'status':'waiting','progress':'-', 'path':'None'})+')'
    
    def render_POST(self, request):
        return self.render_GET(request)


class Request(resource.Resource):
    def render_GET(self, request):
        request.setHeader('content-type','application/x-javascript')
        
        return 'test'
    def render_POST(self, request):
        return self.render_GET(request)

class Test(resource.Resource):
    def render_GET(self, request):
        request.setHeader('content-type','application/x-javascript')
        callback = request.args['callback'][0]
        return callback+'('+json.dumps({'time':'casdfafd'})+')'
    def render_POST(self, request):
        return self.render_GET(request)


if __name__ == '__main__':
    root = Root()
    root.putChild('test', Test())
    root.putChild('down', Down())
    root.putChild('update', Update())
    server = server.Site(root)
    server.sessionFactory = DownloadSession
    reactor.listenTCP(2323, server)
    reactor.run()

    
