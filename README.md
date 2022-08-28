
# ImmersiveFX
ImmersiveFX is a framework which interfaces WLED over UDP, Serial devices, and the Lightbar of DualShock 4 controllers.

It allows you to build Applications that process data to display them onto above devices. It includes 2 reference fxmodes as submodules:

[**ScreenFX**](https://github.com/MaWalla/ScreenFX), which can display the content of screen borders (similar to Phillips Ambilight) 

[**PulseViz**](https://github.com/MaWalla/PulseViz), which analyzes a pulseaudio stream and allows to display it in various ways.
The backend is based off [this Project](https://github.com/pckbls/pulseviz.py).

Besides that, you're hopefully only limited by your creativity. If you're limited by the framework however, consider making a pull request or issue!

## Compatibility

|Device        |Linux|Windows    |Mac OS     |
|--------------|-----|-----------|-----------|
|WLED:         |yes  |untested*  |yes        |
|Serial:       |yes  |untested*  |untested*  |
|DualShock**:  |yes  |no         |no         |

untested* : While I haven't used ImmersiveFX with those configurations on those platforms yet, there is a good chance
that it will work regardless, due to the libraries used being cross-compatible.

DualShock**: This currently only refers to DS4 controllers. While I do own a DS5 controller, I haven't yet found a way to interface the LED.

## Requirements

- Python 3.10, something older/newer may work, but I recommend this version.
- pip and venv to manage the requirements.txt

## Installation

- clone the repo somewhere.
- open a terminal in the cloned folder.

Start off by doing `git submodule update --init` to pull in the reference fxmodes ScreenFX and PulseViz

I boldly assume that `python` links to `python3` and `python-pip` and `python-venv` are installed.
Distributions such as Ubuntu or Debian might still link `python` to `python2` and offer `python3` as packages etc. so in that case use those.

- run `python -m venv env` to create a virtual environment named `env`.
- run `source env/bin/activate` (if you use fish for whatever reason its `env/bin/activate.fish`) to enter the venv.

You're almost ready now, but you need to configure it first though, see below!

Once done, ImmersiveFX can now be run with `python main.py`

On the first launch/whenever there are changes, ImmersiveFX will ask you if you want to install the requirements.

There are launch arguments to change the behaviour:
  - `-d` skips checking the dependencies, so requirements won't be installed. I recommend that you only use it when there are repeated issues with the installation
  - `-p` skips the platform check for fxmodes, generally not recommended, but who am I to order you around?
  - `-s` skips the version check for fxmodes, generally also not recommended, but yet again, who am I to order you around?
  - `-w` surpresses warnings when a frame cycle takes longer than the intended frametime. Recommended if you're annoyed by occasional warnings when things are fine otherwise

## Configuration

Create a file named `config.json`, or copy/rename the provided `config.json.example` for the sake of simplicity and edit it with your favourite text editor!

In there, a variety of settings can be made, in fact fxmodes can even add their own! We'll only cover the settings affecting ImmersiveFx directly here.

| setting | data type | optional | default |
|---------|-----------|----------|---------|
| fxmode  | string    | yes      | null    |
| fps     | integer   | yes      | 30      |
| devices | object    | no       | null    |

- `fxmode` sets the fxmode used on start. The value should match the name of the folder within fxmodes/

If the fxmode isn't available or the key is not set, you'll get a menu with available modes on start.

- `fps` sets the maximum amount of cycles done per second. 30 is a sane default in terms of latency, smoothness and required performance

- `devices` is an object whose keys are named the way you want to name your devices. 
Their values are objects where the following keys can be used. Keep in mind that different devices may use different keys as noted below.

| key               | used by type | data type | optional | default |
|-------------------|--------------|-----------|----------|---------|
| type              | all          | string    | no       | null    |
| enabled           | all          | boolean   | yes      | true    |
| flip              | all          | boolean   | yes      | false   |
| brightness        | all          | float     | yes      | 1.0     |
| leds              | all          | integer   | yes      | 1       |
| color_temperature | all          | integer   | yes      | null    |
| ip                | wled         | string    | no       | null    |
| port              | wled         | integer   | yes      | 21324   |
| path              | serial       | string    | no       | null    |
| baud              | serial       | integer   | yes      | 115200  |
| device_num        | dualshock    | integer   | no       | null    |

- `type`: its can be either wled, serial, or dualshock
- `enable` enable or disable the device
- `flip` reverses the LED order, only makes sense if there are more than 2 LEDs
- `brightness` multiplier between 0.0 and 1.0 to set the brightness. Reduced values may yield more color accurate results on cheap LED strips
- `leds` amount of LEDs the device has
- `color_temperature` a value between 1000 and 12000 in steps of 100, representing the color temperature in Kelvin.

- `ip` IP address of the WLED device
- `port` Port of the WLED device for UDP communication

- `path` Path to the serial device. For example '/dev/ttyACM0' on Linux and mac OS, or 'COM3' on Windows
- `baud` baudrate for communication, must match with the client

- `device_num` counting up, starting at 1. used to differentiate multiple controllers.

## Usage
While ImmersiveFX is running, there are commands available to alter its behaviour. Those can be typed in while it its running.
Available commands are:

- `reload` stops all threads and reloads the config and application core
- `start` starts the threads
- `stop` stops all the threads but keeps them active
- `exit` kills all threads and exits the program

## Notes
For dualshock (4) support, you need to first copy the `ds4perm` file from this repo to /opt, then run `sudo chmod +x /opt/ds4perm` to make it executable.
After this, you'll need to copy the `10-local.rules`, also from this repo, to `/etc/udev/rules.d/`

Just to be safe, run `sudo udevadm control --reload` to reload udev rules. You also need to add you user to the `users` group if not done already and re-login,
or change it with something else in `/opt/ds4perm`.

If the controller was connected during this, it needs to be reconnected. Also it currently only works via bluetooth.

For the receiving end of serial devices, ImmersiveFX sends the amount of LEDs * 3 as bytes, alternating between red green and blue values, very similar to how wled receives data.
