import json


class Common:

    def __init__(self, sock, ds4_paths, devices):
        self.sock = sock
        self.ds4_paths = ds4_paths
        self.devices = devices

    def set_esp_colors(self, ip, port, brightness, kelvin, data):
        self.sock.sendto(
            bytes(json.dumps({
                'brightness': brightness,
                'kelvin': kelvin,
                **data,
            }), 'utf-8'), (ip, port)
        )

    @staticmethod
    def set_ds4_color(lightbar_color, path):
        red, green, blue = lightbar_color

        red_path = f'{path[:-6]}red/brightness'
        green_path = f'{path[:-6]}green/brightness'
        blue_path = f'{path[:-6]}blue/brightness'

        r = open(red_path, 'w')
        r.write(str(red))
        r.close()

        g = open(green_path, 'w')
        g.write(str(green))
        g.close()

        b = open(blue_path, 'w')
        b.write(str(blue))
        b.close()
