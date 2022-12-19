"""
This module provides access to various data managers for interacting with Todoist.

There is a respective manager class for every Todoist data model of the package.

These classes are never instantiated directly, instead, they are accessed through their accessors on the TodoistAPI class.
"""

from .label_manager import LabelManager
from .project_manager import ProjectManager
from .reminder_manager import ReminderManager
from .section_manager import SectionManager
from .task_manager import TaskManager
