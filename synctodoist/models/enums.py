# pylint: disable=invalid-name
from enum import Enum


class ColorEnum(str, Enum):
    """
    Colors enum

    The list of available colors can be found here: [https://developer.todoist.com/guides/#colors](https://developer.todoist.com/guides/#colors)
    """

    berry_red = 'berry_red'
    """berry red"""
    blue = 'blue'
    """blue"""
    charcoal = 'charcoal'
    """charcoal"""
    grape = 'grape'
    """grape"""
    green = 'green'
    """green"""
    grey = 'grey'
    """grey"""
    lavender = 'lavender'
    """lavender"""
    light_blue = 'light_blue'
    """light blue"""
    lime_green = 'lime_green'
    """lime green"""
    magenta = 'magenta'
    """magenta"""
    mint_green = 'mint_green'
    """mint green"""
    olive_green = 'olive_green'
    """olive green"""
    orange = 'orange'
    """orange"""
    red = 'red'
    """red"""
    salmon = 'salmon'
    """salmon"""
    sky_blue = 'sky_blue'
    """sky blue"""
    taupe = 'taupe'
    """taupe"""
    teal = 'teal'
    """teal"""
    violet = 'violet'
    """violet"""
    yellow = 'yellow'
    """yellow"""


class ReminderTypeEnum(str, Enum):
    """Reminder type enum"""
    relative = 'relative'
    """relative"""
    absolute = 'absolute'
    """absolute"""
    location = 'location'
    """location"""


class LocTriggerEnum(str, Enum):
    """Location trigger enum"""
    on_enter = 'on_enter'
    """on enter"""
    on_leave = 'on_leave'
    """on leave"""
