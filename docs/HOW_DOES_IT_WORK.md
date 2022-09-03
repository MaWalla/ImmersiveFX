# How does ImmersiveFX work?

## Storytime

Started as a small one-evening script to test the live displaying data from my pc to then self programmed ESP microcontrollers with attached LED strips, 
ImmersiveFX has evolved to a modular bridge to process any data source into rgb data for various devices with LED strips, most notably [WLED](https://github.com/Aircoookie/WLED)

It focuses on ease to use/interface high configurability while maintaining the lowest possible latency.

## So, how does it work then?!

Prior to launching the fun part, ImmersiveFX scans for available FXModes and then checks if the installed ones match the requirements of ImmersiveFX and its FXModes.

FXMode is the name for an application plugged into ImmersiveFX. Each of them are required to be in a Python Module (whose name doesn't matter) which 
has a modes array defined in its `__init__.py` that contains at least one uninstantiated class which should inherit from `immersivefx.Core` at some point.
The Python Module must be located inside the `fxmodes` folder in the root directory of this repository.

The ImmersiveFX Core sets the base and takes care of common initialisation (like loading the config), executing independent loops in threads to provide quick processing. 
You just have to set your idea on top!

To get started on your own, read the `CODING_EXAMPLE.md`
