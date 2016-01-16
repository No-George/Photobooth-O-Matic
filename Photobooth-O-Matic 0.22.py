__author__ = 'George Bailey'

import io
import json
import pygame
import Queue
import requests
import struct
import threading
import time
import urllib2


#camera address, may be different for other nex devices
url = 'http://192.168.122.1:8080/sony/camera'
#Place to save framed images, folder must exist
save_directory ='C:\Users\Admin\Desktop\Photobooth'

# <editor-fold desc="Variables">
#object initialization

#variables for communicating between threads
liveview_buffer = Queue.Queue(2)
capture_data = Queue.Queue(4)
capture_request = threading.Event()

# Window Variables
pygame.init()
width_screen, height_screen = pygame.display.Info().current_w, pygame.display.Info().current_h
width_window = int(min(width_screen, 1920*height_screen/1080))
height_window = int(min(1080*width_screen/1920,height_screen))
img_positions = [[int(width_window * 68 / 1920), int(width_window * 985 / 1920)],
                 [int(height_window * 33 / 1080), int(height_window * 553 / 1080)]]
width_img = int(width_window * 872 / 1920)
height_img = int(width_window * 490 / 1920)
width_live = int(width_window-2* img_positions[0][0])
height_live = int(height_window- 2*img_positions[1][0])
window = pygame.display.set_mode((width_screen, height_screen), pygame.FULLSCREEN)# | pygame.HWSURFACE)
pygame.display.set_caption("Photobooth-O-Matic")
pygame.mouse.set_visible(0)

#image variables
live_frame_unscaled = pygame.Surface((640, 360))
live_frame = pygame.Surface((width_live,height_live))
Frame = pygame.image.load('Frame.png')
Frame.set_colorkey(Frame.get_at((100,100)))             #set the background colour to transparent
Frame = pygame.transform.scale(Frame, (width_window, height_window)).convert()
white = (255, 255, 255)
grey = (100, 100, 100)
colour_theme = Frame.get_at((0,0))

#message variables, used in the screensaver
countdown_timer = 0.8
messages = []
message_list = open('messages.txt')
message_lines = message_list.readlines()
for line in message_lines:
    messages.append([line.split(';')[0], (line.split(';')[1].strip()), (line.split(';')[2].strip())])
message_range = len(messages)
message_count = 0
waiting = time.time()
# </editor-fold>

def camera_action(method, par=[]):
#send a command to camera, return response
    payload = {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
    data = json.dumps(payload)
    requests.post(url, data=data)

def camera_init():
#start record mode is a call required by nex6 before liveview will work. May not be necessary for other models
    try:
        camera_action('startRecMode')
    except:
        pygame.quit()
        print 'Connection Error'
        raise SystemExit

class BackgroundTakePicture(threading.Thread):
# thread which captures a picture upon threading event flag and places it in a buffer
    running = True
    def __init(self):
        threading.Thread.__init__(self)
        running = True
    def run(self):
        while self.running:
            if capture_request.is_set():
                method = 'actTakePicture'
                par = []
                payload = {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
                data = json.dumps(payload)
                response = requests.post(url, data=data).json()
                link = str(response.get('result')[0][0])
                #empty liveview buffer of now outdated frames
                capture_data.put(io.BytesIO(urllib2.urlopen(link).read()))
                while not liveview_buffer.empty():
                    liveview_buffer.get()
                capture_request.clear()
    def stop_running(self):
        self.running = False

def countdown(message):
#routine which counts down and takes a picture
    while  capture_request.is_set():        #wait for last picture to finish downloading
        print capture_request.is_set()
        time.sleep(0.1)
    for i in reversed(range(2, 4)):
        start_time = time.time()
        while (time.time() < (start_time + countdown_timer)):
            screen_update(100, message, i,'',1)
    start_time = time.time()
    capture_request.set()                   #raise threading event flag
    while (time.time() < (start_time + countdown_timer)):
        screen_update(100, message, 1,'',1)
    screen_update(150, ' ', 'SMILE','',0 )

def capture_sequence():
#routine for capturing 4 images and blitting them behind a frame
    countdown('SMILE')                  #countdown then capture an image
    countdown('AND ANOTHER ONE')
    countdown('ALMOST DONE')
    countdown('LAST ONE')


    image0 = pygame.transform.scale(pygame.image.load(capture_data.get()), (width_img,height_img))#load images from buffer
    image1 = pygame.transform.scale(pygame.image.load(capture_data.get()), (width_img,height_img))
    image2 = pygame.transform.scale(pygame.image.load(capture_data.get()), (width_img,height_img))
    image3 = pygame.transform.scale(pygame.image.load(capture_data.get()), (width_img,height_img))
    window.blit(image0, (img_positions[0][0],img_positions[1][0]))                                #blit images in grid
    window.blit(image1, (img_positions[0][1],img_positions[1][0]))
    window.blit(image2, (img_positions[0][0],img_positions[1][1]))
    window.blit(image3, (img_positions[0][1],img_positions[1][1]))
    window.blit(Frame, (0,0))                                                                     #overlay frame
    pygame.display.flip()
    path = save_directory   #shell.SHGetFolderPath (0, shellcon.CSIDL_DESKTOP, None, 0)                             #locate desktop and save framed images
    print path
    path += '\\'                                                                       #folder must exist
    path += time.strftime("%H%M%S%d%m%Y")
    path += ".jpg"
    pygame.image.save(window,path)
    time.sleep(5)

def screen_update(character_height, line1='', line2='', line3='', live=1):
#routine for updating the display with overlayed text
    window.fill(colour_theme)                       #plain background for non live_view calls
    border = 2
    myfont = pygame.font.SysFont("Arial", character_height)
    label, shadow, xpos, ypos = [], [], [], []
    label.append(myfont.render((str(line1)), 1, (white)))
    shadow.append(myfont.render((str(line1)), 1, (grey)))
    label.append(myfont.render((str(line2)), 1, (white)))
    shadow.append(myfont.render((str(line2)), 1, (grey)))
    label.append(myfont.render((str(line3)), 1, (white)))
    shadow.append(myfont.render((str(line3)), 1, (grey)))
    xpos.append((width_screen - label[0].get_size()[0]) / 2)
    xpos.append((width_screen - label[1].get_size()[0]) / 2)
    xpos.append((width_screen - label[2].get_size()[0]) / 2)
    ypos.append(height_screen / 2 - character_height * 9 / 4)
    ypos.append(height_screen / 2 - character_height * 1 / 4)
    ypos.append(height_screen / 2 + character_height * 3 / 4)
    if live:
        if liveview_buffer.qsize()>0:               #if a new frame has been downloaded then process it and blit to the live_frame surface
            imgdata = liveview_buffer.get()
            global live_frame
            live_frame_unscaled = pygame.image.load(io.BytesIO(imgdata)).convert()
            live_frame = pygame.transform.scale(live_frame_unscaled, (width_live,height_live)).convert()
            live_frame = pygame.transform.flip(live_frame,1,0)
            pygame.draw.rect(live_frame, white, (0,0,width_live,height_live), 7)    #add a white border
        window.blit(live_frame, (img_positions[0][0], img_positions[1][0]))
    for i in range(0, 3):
        window.blit(shadow[i], (xpos[i] + border, ypos[i] + border))
        window.blit(shadow[i], (xpos[i] + border, ypos[i] - border))
        window.blit(shadow[i], (xpos[i] - border, ypos[i] + border))
        window.blit(shadow[i], (xpos[i] - border, ypos[i] - border))
        window.blit(label[i], (xpos[i], ypos[i]))
    pygame.display.flip()

class BackgroundStreaming(threading.Thread):
#thread for downloading liveview frames in the background
    running = True
    def __init(self):
        threading.Thread.__init__(self)
        self.running = True
    def fetch_streaming_link(self):  #start camera liveview
        method = 'startLiveview'
        par = []
        payload = {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
        data = json.dumps(payload)
        response = requests.post(url, data=data).json()
        link = str(response.get('result')[0])
        return link
    def fetch_frame(self,link):
        stream = urllib2.urlopen(link)
        data = stream.read(136)
        size = struct.unpack('>i', '\x00' + data[12:15])[0]
        imgdata = stream.read(size)
        return imgdata
    def run(self):
        link = self.fetch_streaming_link()
        while self.running:
            stream = urllib2.urlopen(link)
            data = stream.read(136)
            size = struct.unpack('>i', '\x00' + data[12:15])[0]
            imgdata = stream.read(size)
            liveview_buffer.put(imgdata)
    def stop_running(self):
        self.running = False

def Screensaver():
#routine which displays messages on the screen when the system isn't capturing images
    global message_count
    global waiting
    screen_update(70, messages[message_count][0],messages[message_count][1],messages[message_count][2],1)
    if (time.time()> (waiting+15)):
        waiting = time.time()
        message_count +=1
        if (message_count>=(message_range)):
            message_count=0

# <editor-fold desc="Setup">
camera_init()                               #initialize nex6 camera
live_view = BackgroundStreaming()
live_view.start()                           #start a thread to download liveview stream in background
capture = BackgroundTakePicture()
capture.start()                             #start a thread to take pictures in the background
Loop = True
#window.blit(Text_Backdrop, (0, 0))          #set blank screen whilst connecting to camera
window.fill(colour_theme)
pygame.display.flip()
# </editor-fold>

# <editor-fold desc="Main">
while Loop:
    Screensaver()                                       #if no interaction has occured run the screensaver
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            Loop = False
        elif (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_SPACE):
                capture_sequence()
                pygame.event.clear()                      #ignore extra keypresses during routine
            if (event.key == pygame.K_ESCAPE):
                Loop = False
live_view.stop_running()
capture.stop_running()
pygame.quit()
# </editor-fold>