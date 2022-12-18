# pylint: disable=invalid-name
from enum import Enum


class ColorEnum(str, Enum):
    """Colors enum"""
    berry_red = 'berry_red'
    blue = 'blue'
    charcoal = 'charcoal'
    grape = 'grape'
    green = 'green'
    grey = 'grey'
    lavender = 'lavender'
    light_blue = 'light_blue'
    lime_green = 'lime_green'
    magenta = 'magenta'
    mint_green = 'mint_green'
    olive_green = 'olive_green'
    orange = 'orange'
    red = 'red'
    salmon = 'salmon'
    sky_blue = 'sky_blue'
    taupe = 'taupe'
    teal = 'teal'
    violet = 'violet'
    yellow = 'yellow'


class ReminderTypeEnum(str, Enum):
    """Reminder type enum"""
    relative = 'relative'
    absolute = 'absolute'
    location = 'location'


class LocTriggerEnum(str, Enum):
    """Location trigger enum"""
    on_enter = 'on_enter'
    on_leave = 'on_leave'
