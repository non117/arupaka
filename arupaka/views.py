# -*- coding: utf-8 -*-
import atexit
import os, glob
import re
import subprocess

from django.core.cache import cache
from django.http import HttpResponse
from django.views.generic.simple import direct_to_template

from arupaka.settings import VLC_PATH, MOVIE_DIR

def index(request):
    movies = cache.get("movies")
    if movies is None:
        movies = Movies()
        cache.set("movies", movies, 3600)
    files = movies.get_filenames()
    return direct_to_template(request, "index.html", {"files":files})

def play(request):
    if request.method != "POST":
        return HttpResponse()
    moviepath = os.path.join(MOVIE_DIR, request.POST["filename"]).encode("utf-8")
    _, ext = os.path.splitext(moviepath)
    stop()
    command = [VLC_PATH + " -vvv %s" %  moviepath + ' --sout "# standard{access=http, mux=%s, dst=:8080, width=1280, height=720}"' % ext[1:]]
    print command
    p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    cache.set("child process", p, 946080000) # 1year
    atexit.register(stop)
    return HttpResponse()

def stop(request=None):
    if request != None and request.method != "POST":
        return HttpResponse()
    p = cache.get("child process")
    if p is None:
        return HttpResponse()
    if p.poll() is None:
        p.kill()
    return HttpResponse()

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
        movie_paths = filter(f, files)
        self.movies = map(Movie, movie_paths)
    
    def get_filenames(self):
        return map(str, self.movies)
    
    def search(self, keyword):
        r = re.compile(keyword)
        return filter(lambda m:r.search(str(m)), self.movies)
