from .pulseviz import Intensity, RainbowRoad
from .screenfx import ScreenFX

available_fxmodes = {
    ScreenFX.name: ScreenFX,
    Intensity.name: Intensity,
    RainbowRoad.name: RainbowRoad
}
