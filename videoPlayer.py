#! /usr/bin/env python3

from threading import Thread, Semaphore, Lock
import cv2,os,time,sys

class Queue():
    def __init__(self,capacity = 10):
        self.queue = []
        self.lock = Lock()
        self.full = Semaphore(0)
        self.empty = Semaphore(capacity)
    
    def put(self,frame):
        self.empty.acquire()
        self.lock.acquire()
        self.queue.append(frame)
        self.lock.release()
        self.full.release()
    
    def get(self):
        self.full.acquire()
        self.lock.acquire()
        frame = self.queue.pop(0)
        self.lock.release()
        self.empty.release()

class extract(Thread):
    def __init__(self,video):
        Thread.__init__(self)
        self.video = video
        
    def run(self):
        vid = self.video
        successful, frame = vid.read()
        while successful:
            rawFrames.put(frame)
            successful, frame = vid.read()
        rawFrames.put(None)
        return

class convert(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            frame = rawFrames.get()
            if frame is None:
                grayFrames.append(None)
                return
            grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            grayFrames.put(grayFrame)
        return

class display(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.delay = 42

    def run(self):
        while True:
            frame = grayFrames.get()
            if frame is None:
                break
            cv2.imshow('Video',frame)
            if cv2.waitKey(self.delay) and 0xFF == ord("q"):
                break
        cv2.destroyAllWindows()
        return

queueLimit = 10
rawFrames = Queue(queueLimit)
grayFrames = Queue(queueLimit)

if len(sys.argv) != 2:
    print("No video name was given, run program as below")
    print("python3 videoPlayer.py <video file name>")
    sys.exit(0)
else: #correct number of arguments given
    if not os.path.isfile(sys.argv[1]):
        print("Valid video was not found, run program as below")
        print("python3 videoPlayer.py <video file name>")
        sys.exit(0)
    else: #valid file given
        fileName = sys.argv[1]
        try:
            video = cv2.VideoCapture(fileName)
            extract_thread = extract(video)
            extract_thread.start()
            convert_thread = convert()
            convert_thread.start()
            display_thread = display()
            display_thread.start()
        except:
            print("Something went wrong!")