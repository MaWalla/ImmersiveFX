import json
import sys


class Common:
    # those need to be set by their respective fxmodes, as a list containing all applying values
    target_versions = None  # TODO find a good way for versioning
    target_platforms = None  # check https://docs.python.org/3/library/sys.html#sys.platform or use 'all' if it applies

    def __init__(self, sock, ds4_paths, devices, *args, core_version='dev', flags=[], **kwargs):
        """
        fancy little base class, make your fxmode inherit from it to spare yourself unnecessary work
        or don't, I'm a comment not a cop.
        """
        self.sock = sock
        self.ds4_paths = ds4_paths
        self.devices = devices

        self.flags = flags
        self.check_target(core_version)

    def check_target(self, core_version):
        """
        checks if the user's ImmersiveFX Core version and platform match the fxmode requirements
        can be overridden with --no-version-check and --no-platform-check, expect errors in this case though
        """
        if '--no-version-check' not in self.flags:
            if core_version not in self.target_versions:
                print('your ImmersiveFX Core is on version %(core)s but it needs to be %(targets)s.' % {
                    'core': core_version,
                    'targets': ', '.join(self.target_versions),
                })
                exit()

        if '--no-platform-check' not in self.flags:
            if 'all' not in self.target_platforms:
                if sys.platform not in self.target_platforms:
                    print('your platform is %(platform)s but it needs to be %(targets)s.' % {
                        'platform': sys.platform,
                        'targets': ', '.join(self.target_platforms),
                    })
                    exit()

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
