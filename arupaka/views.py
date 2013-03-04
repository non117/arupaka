# -*- coding: utf-8 -*-
import atexit
import os, glob
import re
import subprocess, shlex
import telnetlib
import time
import urllib

from django.core.cache import cache
from django.http import HttpResponse
from django.views.generic.simple import direct_to_template

from arupaka.settings import VLC_PATH, MOVIE_DIR

encoding = "utf-8"
if os.name == "nt":
    encoding = "cp932"
ip = urllib.urlopen("http://ipcheck.ieserver.net/").read()

def index(request):
    movies = cache.get("movies")
    if movies is None:
        movies = Movies()
        cache.set("movies", movies, 3600)
    files = movies.get_filenames()
    
    return direct_to_template(request, "index.html", {"files":files, "ip":ip})

def select(request):
    if request.method == "POST":
        moviepath = os.path.join(MOVIE_DIR, request.POST["filename"]).encode(encoding)
        cwd, vlc = os.path.split(VLC_PATH)
        os.chdir(cwd)
        if cache.get("pid"):
            Controller().shutdown()
        
        command = vlc + ' -vvv "%s"' %  moviepath + ' --intf telnet --sout "# standard{access=http, mux=ts, dst=:8080, width=1280, height=720}"'
        if os.name == "nt": command = shlex.split(command) # windows
        p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        cache.set("pid", p.pid, 86400) # 24h
        atexit.register(kill)
        time.sleep(0.3)
        Controller().stop()
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
    length = c.get_length()
    time = c.get_time()
    return HttpResponse(100*time/length)

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
        movie_paths = map(lambda s:s.decode(encoding).encode("utf-8"), filter(f, files))
        self.movies = map(Movie, movie_paths)
    
    def get_filenames(self):
        return map(str, self.movies)
    
    def search(self, keyword):
        r = re.compile(keyword)
        return filter(lambda m:r.search(str(m)), self.movies)

class Controller():
    def __init__(self):
        self.client = telnetlib.Telnet("localhost","4212")
        self.write("admin")
        self.read()
    def read(self):
        return self.client.read_until("> ", timeout=1)
    def write(self, command):
        self.client.write(command + "\n")
    def logout(self):
        self.write("logout")
        self.read()
    def shutdown(self):
        self.write("shutdown")
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
