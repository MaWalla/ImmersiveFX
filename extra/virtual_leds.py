import argparse
import socket
import sys
import threading
from tkinter import Tk, Canvas

parser = argparse.ArgumentParser()

parser.add_argument('-x', '--width', help='canvas width in pixels', default=320)
parser.add_argument('-y', '--height', help='canvas height in pixels', default=40)
parser.add_argument('-p', '--port', help='port, this script is listening on', default=21324)


args = parser.parse_args()

try:
    width = int(args.width)
    height = int(args.height)
    port = int(args.port)
except ValueError:
    print('ERROR: Arguments need to be passed as numbers', file=sys.stderr)
    exit(1)


class Data:

    def __init__(self, port):
        self.port = port

        self.pixels = 1
        self.processed = [[0, 0, 0]]

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', port))

        threading.Thread(target=self.update_data).start()

    def update_data(self):
        while True:
            message, *_ = self.sock.recvfrom(1024)
            data = list(message)[2:]
            self.pixels = int(len(data) / 3)
            self.processed = [
                [data[pixel * 3 + subpixel] for subpixel in range(3)]
                for pixel in range(self.pixels)
            ]


data = Data(port)


window = Tk()
window.title('Virtual LED Strip')
canvas = Canvas(window, width=width, height=height, bg="#000000")
canvas.pack()


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(rgb)


while True:
    canvas.delete('all')
    processed = data.processed
    pixels = data.pixels

    for pixel in range(pixels):
        hex_color = rgb_to_hex(processed[pixel])
        canvas.create_rectangle(
            pixel * width / pixels,
            0,
            (pixel + 1) * width / pixels,
            height,
            outline=hex_color,
            fill=hex_color,
        )
    canvas.update()
