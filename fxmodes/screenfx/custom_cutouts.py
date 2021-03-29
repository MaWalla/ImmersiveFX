def custom_cutouts(w, h):
    """
    Custom cutouts for ScreenFX to use.
    :param w: screen width, passed in by ScreenFX
    :param h: screen height, passed in by ScreenFX
    :return: a dict with each key being a cutout. The value is a tuple with:
             (top_left_x, top_left_y, bottom_right_x, bottom_right_y) in that order.
    """
    return {
        'tetris1080': (w/2 - 125, h/2 - 250, w/2 + 125, h/2 + 125),
    }
