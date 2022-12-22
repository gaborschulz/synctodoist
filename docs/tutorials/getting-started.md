# Getting Started

???+ Important
    Before you get started, please, make sure that you've completed all the steps covered in [Prerequisites](prereqs.md).

## Getting a TodoistAPI  
The `TodoistAPI` class is the tool you use to send requests to the Todoist API.

???+ Example
    ```python linenums="1"
    from synctodoist import TodoistAPI

    api = TodoistAPI(api_key=<YOUR_API_KEY>)
    api.sync()
    ```

    **Line 1**  
    You start by importing `TodoistAPI` from the `synctodoist` package.    
    **Line 3**  
    Then, you instantiate the `TodoistAPI`. You provide the API key you copied in [Prerequisites](prereqs.md) as the `api_key` argument.   
    **Line 4**  
    The API object needs to be synchronized with the Todoist API. To do so, you simply have to call `api.sync() .

???+ Note
    There are other ways to provide the API key that are more secure. To find out more, visit [Settings & Configuration](how-tos/settings.md).

## Getting a project by id

You may want to get all the details of a project based on its id. 

???+ Example
    ```python linenums="1" hl_lines="5"
    from synctodoist import TodoistAPI

    api = TodoistAPI(api_key=<YOUR_API_KEY>)
    api.sync()
    project = api.projects.get(item_id='2303492509')
    ```

    **Line 5**  
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
    ```python linenums="1" hl_lines="5"
    from synctodoist import TodoistAPI

    api = TodoistAPI(api_key=<YOUR_API_KEY>)
    api.sync()
    project = api.projects.find(pattern='Inbox')
    ```

    **Line 5**  
    We use `api.projects.find()` to find a project based on it's name. `pattern` can be any valid regex pattern. By default, this method will give you the
    first match. If you would like to get all matching projects, change Line 4 to this:

    ```python 
    project = api.projects.find(pattern='Inbox', return_all=True)
    ```

## Creating a task

To add a new task you create a new `Task` object and add it to the TaskManager:

???+ Example
    ```python linenums="1" hl_lines="6-8"
    from synctodoist import TodoistAPI

    api = TodoistAPI(api_key=<YOUR_API_KEY>)
    api.sync()

    task = Task(content='Test task')
    api.tasks.add(task)
    api.commit()
    ```

    **Line 6**  
    First, we create a new instance of the `Task` class.  
    **Line 7**  
    Next, add the task to the TaskManager.  
    **Line 8**  
    Every time you want to execute the actions (e.g. adding, deletion, closing, reopening, etc.), you have to commit them to Todoist by calling the `.commit()` 
    method.

???+ Note
    The `task` object will be updated with the id returned by Todoist. You can use this id in the `.get()` method to access the task at a later point in time.

## Getting a task

Getting the details of a task is quite similar to the way you work with projects.

???+ Example
    ```python linenums="1" hl_lines="5"
    from synctodoist import TodoistAPI

    api = TodoistAPI(api_key=<YOUR_API_KEY>)
    api.sync()
    task = api.tasks.get(item_id='2303492509')
    ```

    **Line 5**  
    We use `api.tasks.get` to get a `Task` instance.
    
??? question "How do I figure out the id of a task?"
    You have several options to figure out the id of a task. You could visit [todoist.com](https://todoist.com), click on the task and look at the URL shown 
    by your browser:  

    `https://todoist.com/app/today/task/6407125024`

    The numbers after the last slash (`6407125024`) are the id of the task you've selected.  

    Alternatively, you could use the `api.tasks.find()` method to look for a task by its content, and then check the `id` property of the `task` object.

## Closing a task

Once you have a task instance, you can simply close it by calling the `.close()` method and commiting it back to Todoist.

???+ Example
    ```python linenums="1" hl_lines="6-7"
    from synctodoist import TodoistAPI

    api = TodoistAPI(api_key=<YOUR_API_KEY>)
    api.sync()
    task = api.tasks.get(item_id='2303492509')
    api.tasks.close(task)
    api.commit()
    ```

    **Line 6**  
    We use the `api.tasks.close()` method to close the task.  
    **Line 7**  
    We commit the change back to Todoist.
