import socket
import configparser
import json

config = configparser.ConfigParser()
config.read('../properties.ini')

host = config['REMOTE_CONNECTION']['host']
port = config['REMOTE_CONNECTION']['port']


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
