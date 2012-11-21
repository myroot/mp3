#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gmusicapi.api import Api

from youtube_dl import *
import os
import gpass #saved google id and password

class myDownload(FileDownloader):
    current_key = None
    logstack = {}
    def __init__(self):
        FileDownloader.__init__(self,{'outtmpl': u'%(stitle)s.%(ext)s'})
        jar = cookielib.CookieJar()
        cookie_processor = urllib2.HTTPCookieProcessor(jar)
        proxy_handler = urllib2.ProxyHandler()
        opener = urllib2.build_opener(proxy_handler, cookie_processor, YoutubeDLHandler())
        urllib2.install_opener(opener)
        socket.setdefaulttimeout(300)
        extractors = gen_extractors()
        for extractor in extractors:
            self.add_info_extractor(extractor)
        self.add_post_processor(FFmpegExtractAudioPP(preferredcodec='mp3'))

    def report_progress(self, percent_str, data_len_str, speed_str, eta_str):
        process_str = '%s of %s %s'%(percent_str, data_len_str, speed_str)
        if percent_str.find('100.0%') != -1 :
            self.logstack[self.current_key]['state'] = 'converting'
        if self.current_key != None :
            self.logstack[self.current_key]['process'] = process_str
        print process_str

    def report_destination(self, filename):
        if self.current_key != None :
            self.logstack[self.current_key]['path'] = filename
    def to_screen(self, message, skip_eol=False):
        if message.startswith('[ffmpeg] Destination:') :
            if self.current_key != None :
                self.logstack[self.current_key]['path'] = message.split()[-1]
        FileDownloader.to_screen(self,message,skip_eol);

    def download_by_id(self, key, upload=False):
        if self.logstack.has_key(key) and self.logstack[key]['state'] != 'fail' :
            return
        url = 'http://www.youtube.com/watch?v=%s'%(key)
        if upload :
            print 'upload google music!!!'
        self.current_key = key
        self.logstack[key] = {'path':'', 'process':'', 'state': 'downloading'}
        result = None
        try:
            self.download([url])
        except:
            self.logstack[key]['state'] = 'fail'
            return
        if upload :
            self.logstack[key]['state'] = 'uploading'
            print self.logstack[key]['path']
            path = self.logstack[key]['path'].encode('utf-8')
            api = Api()
            api.login(gpass.id, gpass.passwd)
            ids = api.get_all_playlist_ids(auto=False,instant=False)
            playlist_id = ids['user']['youtube']
            try:
                result = api.upload([path])
            except:
                print 'upload error'
                self.logstack[key]['state'] = 'fail'
                return
            if len(result) :
                api.add_songs_to_playlist(playlist_id , result.values()[0])
        self.logstack[key]['state'] = 'complete'
    def clear_id(self,key):
        os.unlink(self.logstack[key]['path'])
        self.logstack.pop(key)

    def clear_all(self):
        for key in self.logstack.keys() :
            self.clear_id(key)

def test():
    fd = myDownload()
    fd.download_by_id('Q3Dfl3ed1bA', True)
    print fd.logstack['Q3Dfl3ed1bA']['path']
    print 'done'
    fd.clear_all()

if __name__ == '__main__':
    test()
