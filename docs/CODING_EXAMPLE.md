# FXMode Coding Example

## Your very own FXMode!

If not already done, follow the steps in the `README.md`. This guide assumes that you have a working setup.

Start off by creating a new directory in the `fxmodes` folder in the root of this repository and giving it any name. For this tutorial I'll choose `HelloWorld`.
In there must be at least one file `__init__.py` which makes it a Python module (more on that later). I'll also create a main.py where the actual logic is implemented though.

The `main.py` contains all the logic, which will later on look like this:

```
from immersivefx import Core


class HelloWorld(Core):
    name = 'Hello World'
    
    target_versions = ['1.2']
    target_platforms = ['all']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_threads()
    
    def splash(self):
        print('--------------')
        print(' Hello World! ')
        print('--------------')
        
    def data_processing(self, *args, **kwargs):
        self.raw_data = [255, 0, 0]
        
    def device_processing(self, device, device_instance):
        return [self.raw_data for _ in range(device_instance.leds)]

```

Hold on, what's all that?!

This is a minimal implementation of a working FXMode that should turn all device LEDs red. The setup to achieve it is actually quite simple.

First we define a class, Its name doesn't matter, but it should inherit from `ìmmersivefx.Core` like shown or this whole thing would be really useless here.
The class needs to have 3 attributes set:

- `name` This one actually matters! Its supposed to be a string that is displayed on ImmersiveFX startup.
- `target_versions` is an array of supported ImmersiveFX versions. Versions are stored in strings with `major.minor`. While there is no specific rule to increment the major version, minor versions are incremented on breaking changes. ImmersiveFX also features a patch version number which is ignored in the check though, since those aren't supposed to break functionality behavior.
- `target_platform` is an array of operating systems the FXMode can run on. `all` is fine, unless you do something very specific. Use `linux` if it runs on that, `win32` for Windows and `darwin` for Mac OS.

Next, we need to override the classes `__init__()` method. Even if you don't plan on putting any extra logic in it, like in the example above, 
you need to at least call `super().__init__(*args, **kwargs)` followed by `self.start_threads()`.

The `super()` call starts the ImmersiveFX initialization (loading the config and creating device instances, showing the splash, etc.)
`start_threads()` launches the data loop and device loops each in an individual thread, therefore actually launching the FXMode.

In `splash()` you can print whatever you want, so time for some ASCII-Art!

Next up is processing. The general idea here is, that `data_processing()` takes data from any source, preprocesses it for the device threads and then writes to an instance variable `self.raw_data`. 
Accordingly, for each device `device_processing()` reads from `self.raw_data` and shapes that to fit onto the amount of LEDs attached to the device. 
Both data_processing and each instance of device_processing run up to `n` times per second, where `n` is the fps setting defined in the config (default 30). 

In our example, `data_processing()` repeatedly sets `self.raw_data` to `[255, 0, 0]` which is full red as rgb value.

Then, `device_processing()` just takes that value and fills it into a list for each LED the device has, which is then returned.
In general, the method is expected to return a 2D-array with red, green and blue values for each LED.

Note: Speaking of expected shapes. `self.raw_data` can have any shape or type you need, but defaults to a 1D array with 3 values: red, green and blue.
If you intend to change this shape (which will most likely be the case), you'll have to provide a suitable default in `__init__()`, between `super()` call and `start_threads()`.

Technically this example is quite a waste of resources, since the same value is set over and over again `fps` times a second, but its fine enough for demonstration purposes.

Finally, the FXMode must be defined in `__init__.py`, so it can be discovered by ImmersiveFX at launch. 
For that, the class (not an instance, so no brackets) must be defined in a modules list in the file. It could look like this:

```
from .main import HelloWorld

modes = [
    HelloWorld,
]
```

This list can contain as many FXModes as you like, for example if you wanna provide different variations for the same codebase, like in [PulseViz](https://github.com/MaWalla/PulseViz)

And that's it! When launching ImmersiveFX, `Hello World` should now show up as an option and when selecting it, all your defined devices should become red.
Apart from the expected return format of `device_processing()`, you're completely free to design the FXMode in your desired way. Have fun!

## Further reading

If you're done here and want some inspiration from real-world examples, read into the code of the pre-provided [ScreenFX](https://github.com/MaWalla/ScreenFX) and [PulseViz](https://github.com/MaWalla/PulseViz) FXModes.
If you've followed the ImmersiveFX installation instructions carefully, those should already exist and be populated in the `fxmodes` folder in the root of this repository.
