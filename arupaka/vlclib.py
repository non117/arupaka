# -*- coding: utf-8 -*-
import os
import re
import socket
import telnetlib

VLC_STATUS_PLAYING = "playing"
VLC_STATUS_STOPPED = "stopped"
VLC_STATUS_PAUSED = "paused"

def get_vlc_status():
    c = Controller()
    alive = c.alive
    playlist = []
    status = VLC_STATUS_STOPPED
    filename = ""
    if alive:
        playlist = c.playlist()
        status = c.status()
        filename = c.get_filename()
    return {"alive":alive, "playlist":playlist, "status":status, "filename":filename}

class Controller():
    def __init__(self):
        try:
            self.client = telnetlib.Telnet("localhost","4212")
            self.alive = True
            self.write("admin")
            self.read()
        except socket.error:
            self.alive = False
    
    def read(self):
        if self.alive:
            return self.client.read_until("> ", timeout=1)
    
    def write(self, command):
        if self.alive:
            self.client.write(command + "\n")
    
    def logout(self):
        self.write("logout")
        self.read()
    
    def shutdown(self):
        self.write("shutdown")
    
    def status(self):
        self.write("status")
        s = self.read()
        return re.search("state\s[a-z]+", s).group().split()[1]
    
    def playlist(self):
        self.write("playlist")
        s = self.read()
        status = self.status()
        if status == VLC_STATUS_PLAYING or status == VLC_STATUS_PAUSED:
            return map(lambda s:re.search("[0-9]\s-\s.+\s\(",s).group()[4:-2], s.split("\n")[2:-3])
        return ""
    
    def pause(self):
        self.write("pause")
        self.read()
    
    def stop(self):
        self.write("stop")
    
    def play(self):
        self.write("play")
        self.read()
    
    def seek(self, percent):
        self.write("seek %d%%" % percent)
        self.read()
    
    def next(self):
        self.write("next")
        self.read()
    
    def prev(self):
        self.write("prev")
        self.read()
    
    def enqueue(self, filename):
        self.write("enqueue %s" % filename)
        self.read()
    
    def clear(self):
        self.write("clear")
        self.read()
    
    def is_playing(self):
        self.write("is_playing")
        status = self.read().splitlines()[0]
        return int(status) == 1
    
    def get_length(self):
        self.write("get_length")
        return int(self.read().splitlines()[0])
    
    def get_time(self):
        self.write("get_time")
        return int(self.read().splitlines()[0])
    
    def get_filename(self):
        self.write("status")
        s = self.read()
        status = re.search("state\s[a-z]+", s).group().split()[1]
        if status == VLC_STATUS_PLAYING or status == VLC_STATUS_PAUSED:
            filename = os.path.split(re.search("file.*\)",s).group()[:-2])[-1]
            print filename #DEBUG
            return os.path.split(re.search("file.*\)",s).group()[:-2])[-1]
        return ""
