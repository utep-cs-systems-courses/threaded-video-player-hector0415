#! /usr/bin/env python3

from threading import Thread, Semaphore
import cv2,os,time,sys

sem = Semaphore()
rawFrames = []
grayFrames = []
queueLimit = 10

def main():
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
            

class extract(Thread):
    def __init__(self,video):
        Thread.__init__(self)
        
    def run(self):
        vid = self.video
        successful, frame = vid.read()
        while successful:
            if len(rawFrames) <= queueLimit:
                sem.acquire()
                rawFrames.append(frame)
                sem.release()
                successful, frame = vid.read()
        sem.acquire()
        rawFrames.append(None)
        sem.release()
        return

class convert(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
           if len(rawFrames) > 0 and len(grayFrames) <= queueLimit:
                sem.acquire()
                frame = rawFrames.pop(0)
                sem.release()

                if frame is None:
                    sem.acquire()
                    grayFrames.append(None)
                    sem.release()
                    return
                
                grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sem.acquire()
                grayFrames.append(grayFrame)
                sem.release()
        return

class display(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.delay = 42

    def run(self):
        while True:
            if len(grayFrames) > 0:
                sem.acquire()
                frame = grayFrames.pop(0)
                sem.release()

                if frame is None:
                    break
                
                cv2.imshow('Video',frame)

                if cv2.waitKey(self.delay) and 0xFF == ord("q"):
                    break
                
        cv2.destroyAllWindows()
        return

main()