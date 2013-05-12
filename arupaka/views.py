# -*- coding: utf-8 -*-
import atexit
import json
import os, glob
import re
import subprocess, shlex
import urllib

from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render

from arupaka.vlclib import Controller, get_vlc_status, VLC_STATUS_STOPPED, VLC_STATUS_PAUSED
from arupaka.settings import VLC_PATH, MOVIE_DIR, ENCODING, OPTION

ip = urllib.urlopen("http://ipcheck.ieserver.net/").read()

def index(request): #POSTの時にアレする
    movies = cache.get("movies")
    if movies is None:
        movies = Movies()
        cache.set("movies", movies, 3600)
    if request.method == "GET":
        files = movies.get_filenames()
        extra_context = {"files":files, "ip":ip}
        extra_context.update(get_vlc_status())
        return render(request, "index.html", extra_context)
    elif request.method == "POST":
        keyword = request.POST["keyword"].encode("utf-8")
        files = movies.search(keyword)
        return render(request, "search.html", {"files":files})

def select(request):
    if request.method == "POST":
        controller = Controller()
        filename = request.POST["filename"]
        if not controller.alive:
            moviepath = os.path.join(MOVIE_DIR, filename).encode(ENCODING)
            cwd, vlc = os.path.split(VLC_PATH)
            os.chdir(cwd)
            command = vlc + ' -vvv "%s"' %  moviepath + OPTION
            if os.name == "nt": command = shlex.split(command) # windows
            p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            cache.set("pid", p.pid, 86400) # 24h
            atexit.register(kill)
            
            import time
            time.sleep(0.5)
            controller = Controller()
            controller.clear()
        
        moviepath = os.path.join(MOVIE_DIR, filename).encode("utf-8")
        controller.enqueue(moviepath)
        if filename == controller.get_filename():
            controller.pause()
    return HttpResponse()

def control(request):
    if request.method =="POST":
        c = Controller()
        command = request.POST["command"].encode("utf-8")
        if not "seek" in command:
            getattr(c, command)()
        else:
            _, percent = command.split(" ")
            c.seek(int(percent))
        c.logout()
        if command == "shutdown":
            cache.delete("pid")
    return HttpResponse()

def get_time(request):
    c = Controller()
    if c.status == VLC_STATUS_STOPPED or c.status == VLC_STATUS_PAUSED:
        return HttpResponse(0)
    length = c.get_length()
    if length == 0:
        return HttpResponse(0)
    time = c.get_time()
    return HttpResponse(100*time/length)

def get_status(request):
    res = json.dumps(get_vlc_status())
    return HttpResponse(res)

def kill():
    pid = cache.get("pid")
    if pid:
        if os.name == "nt":
            subprocess.Popen("taskkill /F /T /PID %i"%pid , shell=True)
        else:
            import signal
            os.kill(pid, signal.SIGKILL)

class Movie():
    def __init__(self, path):
        self.path = path
    
    def __repr__(self):
        return os.path.basename(self.path)

class Movies():
    def __init__(self):
        extensions = (".mp4",".ts",".avi",".mov",".flv",".wmv")
        files = glob.glob(os.path.join(MOVIE_DIR, "*.*"))
        f = lambda filename:any([filename.endswith(extension) for extension in extensions])
        movie_paths = reversed(map(lambda s:s.decode(ENCODING).encode("utf-8"), filter(f, files)))
        self.movies = map(Movie, movie_paths)
    
    def get_filenames(self):
        return map(str, self.movies)
    
    def search(self, keyword):
        r = re.compile(keyword)
        return filter(lambda m:r.search(str(m)), self.movies)
