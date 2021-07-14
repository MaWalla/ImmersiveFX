
# ImmersiveFX
ImmersiveFX is a framework which interfaces WLED over UDP, Razer Keyboards (specifically the BlackWidow Chroma 2014) and the Lightbar of DualShock 4 controllers.

It allows you to build Applications that process data to display them onto above devices. It includes 2 sample fxmodes:

**ScreenFX**, which can display the content of screen borders (similar to Phillips Ambilight) 

**PulseViz**, which analyzes a pulseaudio stream and either displays the average color based on the music, strongly inspired by [this Video](https://www.youtube.com/watch?v=Sk3v-92r7R0), or makes it a flowing rainbow, reacting to the bass.
The backend is based off [this Project](https://github.com/pckbls/pulseviz.py).

Besides that, you're hopefully only limited by your creativity. If you're limited by the framework however, consider making a pull request or issue!

## Compatibility
#### shipped fxmodes
|Mode     |Linux|Windows    |Mac OS     |
|---------|-----|-----------|-----------|
|ScreenFX:|yes  |untested*  |untested*  |
|PulseViz:|yes  |no         |no         |

#### device compatibility
|Device        |Linux|Windows    |Mac OS     |
|--------------|-----|-----------|-----------|
|WLED:         |yes  |untested*  |untested*  |
|Arduino:      |yes  |untested*  |untested*  |
|Razer:        |yes  |no         |no         |
|DualShock 4:  |yes  |no         |no         |

*I only use Linux, so Windows and Mac OS are entirely untested. The things should work though, according to their used library documententation for example.

Both pulseaudio and the way I speak to Dualshock 4 controllers are limited to Linux so support for other platforms is unlikely, unless there are different implementations for those.

## Requirements

- Python 3.9, something older/newer may work, but I recommend this version.
- pip and optionally venv to manage the requirements.txt

## Installation

- clone the repo somewhere.
- open a terminal in the cloned folder.

I boldly assume that `python` links to `python3` and `python-pip` and `python-venv` are installed.
Distributions such as Ubuntu or Debian might still link `python` to `python2` and offer `python3` as packages etc. so in that case use those.

- run `python -m venv env` to create a virtual environment named `env`.
- run `source env/bin/activate` (if you use fish for whatever reason its `env/bin/activate.fish`) to enter the venv.
- run `pip install -r requirements.txt` to install dependencies.

After this is done, create a file named `config.json`, or copy/rename the provided `config.json.example` for the sake of simplicity and edit it with your favourite text editor!

in there, you'll need at least the following key `devices` which is an object whose keys are named the way you want to name your devices. Their required value differ, based on the device type.

For WLED devices, the following keys are needed:
- `type`: set to "wled" of course.
- `ip`: IP address of the WLED device
- `leds`: The amount of LEDs attached to the device, if you're not sure, use the value specified within WLEDs Config > LED Preferences

Arduino devices need these keys:
- `type`: its "arduino"
- `path`: path to the device, like '/dev/ttyACM0' on Linux and mac OS, or 'COM3' on Windows
- `baud`: baudrate for communication, defaults to 115200, must match with the client
- `leds`: The amount of LEDs attached to the device, must match with the client

If you wanna use ScreenFX, you'll additionally need to set the key `cutout` with the value being either: `top`, `bottom`, `left`, `right`, `center`, or a custom value as specified in `custom_cutouts.py`. This will reflect the screen area projected onto the LEDs.

Optionally you can also set these keys:
- `enabled`: either true or false, to enable/disable the device, defaults to true.
- `flip`: either true or false, reverses the LED order to display the data the other way around, defaults to false.
- `brightness`: float value between 0 and 1, sets the brightness of the LEDs where 0 is off and 1 is full brightness. Defaults to 1, but lower values like 0.75 may offer a more accurate color representation on LEDs like the ws2812 strips.
- `port`: number, sets a custom port for the IP. defaults to `21324`, which is the default for wled.

Razer keyboards take the keys `enabled`, `flip`, `brightness` and `cutout`, with exactly the same specification as for WLED above. the type has to be `razer` however.

The same applies to DualShock 4 controllers minus `flip` (since there's only 1 LED anyway).
The `type` needs to be `ds4` here. Additionally you'll also have to set the key `device_num` counting up, starting at 1.
With that, you can assign different (custom) cutouts for example to different controllers.
The first parsed usually is the first connected controller, the second parsed the second and so on.

## Notes

The razer support relies on openrazer (e.g. using the Arch Linux AUR package `python-openrazer`). My implementation currently is very hacky and slow though.

For ds4 support, you need to first copy the `ds4perm` file from this repo to /opt, then run `sudo chmod +x /opt/ds4perm` to make it executable. Then you'll need to copy the `10-local.rules`, also from this repo, to `/etc/udev/rules.d/`

Just to be safe, run `sudo udevadm control --reload` to reload udev rules.
You may need to reconnect the controller. Also it currently may only work via bluetooth.
