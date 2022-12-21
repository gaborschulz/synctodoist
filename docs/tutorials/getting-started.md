# Getting Started

???+ Important
    Before you get started, please, make sure that you've completed all the steps covered in [Prerequisites](prereqs.md).

## Getting a TodoistAPI  
The `TodoistAPI` class is the tool you use to send requests to the Todoist API.

???+ Example
    ```python linenums="1"
    from synctodoist import TodoistAPI

    api = TodoistAPI(api_key=<YOUR_API_KEY>)
    ```

    **Line 1**  
    You start by importing `TodoistAPI` from the `synctodoist` package.    
    **Line 3**  
    Then, you instantiate the `TodoistAPI`. You provide the API key you copied in [Prerequisites](prereqs.md) as the `api_key` argument.   

???+ Note
    There are other ways to provide the API key that are more secure. To find out more, visit [Settings & Configuration](how-tos/settings.md).

## Getting a project by id

You may want to get all the details of a project based on its id. 

???+ Example
    ```python linenums="1" hl_lines="4"
    from synctodoist import TodoistAPI

    api = TodoistAPI(api_key=<YOUR_API_KEY>)
    project = api.projects.get(item_id='2303492509')
    ```

    **Line 4**  
    We use `api.projects.get` to get a `Project` instance.

??? question "How do I figure out the id of a project?"
    You have several options to figure out the id of a project. You could visit [todoist.com](https://todoist.com), click on the name of the project and look
    at the URL shown by your browser:  

    `https://todoist.com/app/project/2303492509`

    The numbers after the last slash (`2303492509`) are the id of the project you've selected.  

    Alternatively, you could use the `api.projects.find()` method to look for a project by name, and then check the `id` property of the `project` object.

## Finding a project by name

You may want to find a project based on its name. 

???+ Example
    ```python linenums="1" hl_lines="4"
    from synctodoist import TodoistAPI

    api = TodoistAPI(api_key=<YOUR_API_KEY>)
    project = api.projects.find(pattern='Inbox')
    ```

    **Line 4**  
    We use `api.projects.find()` to find a project based on it's name. `pattern` can be any valid regex pattern. By default, this method will give you the
    first match. If you would like to get all matching projects, change Line 4 to this:

    ```python 
    project = api.projects.find(pattern='Inbox', return_all=True)
    ```

## Getting a task

Getting the details of a task is quite similar to the way you work with projects.

???+ Example
    ```python linenums="1" hl_lines="4"
    from synctodoist import TodoistAPI

    api = TodoistAPI(api_key=<YOUR_API_KEY>)
    project = api.tasks.get(item_id='2303492509')
    ```

    **Line 4**  
    We use `api.projects.get` to get a `Project` instance.
    
??? question "How do I figure out the id of a task?"
    You have several options to figure out the id of a task. You could visit [todoist.com](https://todoist.com), click on the task and look at the URL shown 
    by your browser:  

    `https://todoist.com/app/today/task/6407125024`

    The numbers after the last slash (`6407125024`) are the id of the task you've selected.  

    Alternatively, you could use the `api.tasks.find()` method to look for a task by its content, and then check the `id` property of the `task` object.

## Creating a task

Coming soon...

## Closing a task

Coming soon...