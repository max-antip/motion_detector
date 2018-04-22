import configparser
import socket
import configparser
import json

import cv2

config = configparser.ConfigParser()
config.read('../properties.ini')

read_from_fie = config['OPENCV']['capture_from_file']
checkpoint_frame = int(config['OPENCV']['send_message_per_frames'])
detection = config['OPENCV']['detection']
host = config['REMOTE_CONNECTION']['host']
port = config['REMOTE_CONNECTION']['port']


if detection == 'full_body':
    cascade = cv2.CascadeClassifier('../data/haarcascade_fullbody.xml')
elif detection == 'face':
    cascade = cv2.CascadeClassifier('../../data/haarcascade_frontalface_default.xml')
else:
    cascade = cv2.CascadeClassifier('../data/haarcascade_fullbody.xml')

if read_from_fie == 'yes':
    cap = cv2.VideoCapture('../data/vtest.avi')
else:
    cap = cv2.VideoCapture(0)

frame_cnt = 0
ID = 0
screen_width = 0
screen_height = 0

if cap.isOpened():
    screen_width = cap.get(3)
    screen_height = cap.get(4)


def sendMessageMotion(id, zone):
    mess = {'id': id, 'action': 'application',
            'params': {'module': 'escada_json', 'function': 'trigger_event', 'function_params': {
                'tag': zone, 'field': 'motion'
            }}}
    send_mess(mess)


def send_mess(message):
    global host
    global port
    sock = socket.socket()
    sock.connect((str(host), int(port)))
    message = json.dumps(message)
    size = len(message)
    arr = size.to_bytes(4, 'big')
    arr2 = bytes(message, 'utf-8')
    sock.send(arr + arr2)

    data = sock.recv(4)
    sock.close()

    print(data.decode())


def repatinZones():
    global zone1W, zone1H, zone2W, zone2H, zone3W, zone3H, zone4W, zone4H
    # ZONE1
    zone1W = int(screen_width / 2)
    zone1H = int(screen_height / 2)
    cv2.rectangle(img, (0, 0), (zone1W, zone1H), (0, 255, 0), 2)
    zone1TextW = int(0)
    zone1TextH = int(30)
    cv2.putText(img, "ZONE 1", (zone1TextW, zone1TextH), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 100), 2)
    # ZONE2
    zone2W = int(screen_width)
    zone2H = int(screen_height / 2)
    cv2.rectangle(img, (zone1W, 0), (zone2W, zone2H), (0, 255, 0), 2)
    zone2TextW = int(zone1W)
    zone2TextH = int(30)
    cv2.putText(img, "ZONE 2", (zone2TextW, zone2TextH), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 100), 2)
    # ZONE3
    zone3W = int(screen_width / 2)
    zone3H = int(screen_height)
    cv2.rectangle(img, (0, zone1H), (zone3W, zone3H), (0, 255, 0), 2)
    zone3TextW = int(0)
    zone3TextH = int(zone1H + 30)
    cv2.putText(img, "ZONE 3", (zone3TextW, zone3TextH), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 100), 2)
    # ZONE4
    zone4W = int(screen_width)
    zone4H = int(screen_height)
    cv2.rectangle(img, (zone3W, zone2H), (zone4W, zone4H), (0, 255, 0), 2)
    zone4TextW = int(zone3W)
    zone4TextH = int(zone2H + 30)
    cv2.putText(img, "ZONE 4", (zone4TextW, zone4TextH), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 100), 2)


while 1:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    body = cascade.detectMultiScale(gray, 1.6, 2)
    repatinZones()
    for (x, y, w, h) in body:
        repatinZones()

        detectedWidth = x + w
        detectedHeight = y + h
        if detectedWidth <= zone1W and detectedHeight <= zone1H:
            cv2.rectangle(img, (0, 0), (zone1W, zone1H), (0, 0, 250), 2)

        if detectedWidth <= zone2W and detectedHeight <= zone2H:
            cv2.rectangle(img, (zone1W, 0), (zone2W, zone2H), (0, 0, 250), 2)

        if detectedWidth <= zone3W and detectedHeight <= zone3H:
            cv2.rectangle(img, (0, zone1H), (zone3W, zone3H), (0, 0, 250), 2)

        if detectedWidth <= zone4W and detectedHeight <= zone4H:
            cv2.rectangle(img, (zone3W, zone2H), (zone4W, zone4H), (0, 0, 250), 2)

        cv2.rectangle(img, (x, y), (detectedWidth, detectedHeight), (255, 0, 0), 2)
        # roi_gray = gray[y:y + h, x:x + w]
        # roi_color = img[y:y + h, x:x + w]
    frame_cnt = frame_cnt + 1
    if frame_cnt >= checkpoint_frame:
        print('Checkpoint')
        for (x, y, w, h) in body:
            repatinZones()

            detectedWidth = x + w
            detectedHeight = y + h
            if detectedWidth <= zone1W and detectedHeight <= zone1H:
                ID=ID+1
                sendMessageMotion(ID,"/ZONE1")

            if detectedWidth <= zone2W and detectedHeight <= zone2H:
                ID=ID+1
                sendMessageMotion(ID,"/ZONE2")

            if detectedWidth <= zone3W and detectedHeight <= zone3H:
                ID=ID+1
                sendMessageMotion(ID,"/ZONE3")

            if detectedWidth <= zone4W and detectedHeight <= zone4H:
                ID=ID+1
                sendMessageMotion(ID,"/ZONE4")

        frame_cnt = 0

    cv2.imshow('img', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
