class Common:

    def __init__(self, sock, kelvin, razer_enabled, ds4_enabled, ds4_paths, nodemcus):
        self.sock = sock
        self.kelvin = kelvin
        self.razer_enabled = razer_enabled
        self.ds4_enabled = ds4_enabled
        self.ds4_paths = ds4_paths
        self.nodemcus = nodemcus

        if razer_enabled:
            from razer import chroma_init, chroma_draw
            self.device, self.rows, self.cols = chroma_init()
            self.chroma_draw = chroma_draw

    def set_ds4_color(self, lightbar_color):
        red, green, blue = lightbar_color

        for controller in self.ds4_paths:
            red_path = f'{controller[:-6]}red/brightness'
            green_path = f'{controller[:-6]}green/brightness'
            blue_path = f'{controller[:-6]}blue/brightness'

            r = open(red_path, 'w')
            r.write(str(red))
            r.close()

            g = open(green_path, 'w')
            g.write(str(green))
            g.close()

            b = open(blue_path, 'w')
            b.write(str(blue))
            b.close()
