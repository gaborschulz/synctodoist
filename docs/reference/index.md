# Overview

The architecture of the package is built around the design principles described [here](../index.md#design-principles). There are two classes for each Todoist
API data type:

- a model: the model is the exact data structure that is expected by the Todoist API or that you receive when the API responds to your request
- a manager: the manager simplifies interacting with the API.

All models are subclasses of the [`TodoistBaseModel`](models.md#todoistbasemodel) class. All managers are derived from the 
[`BaseManager`](managers.md#basemanager) class which implements the shared functionality available in all managers (e.g. `add`, `delete`, `find`, `get`, 
and `update`).

Certain managers, like [`ProjectManager`](managers.md#projectmanager) and [`TaskManager`](managers.md#taskmanager) offer some special functionality. 

Managers should never be instantiated directly, instead, you can access them through the TodoistAPI class, like this:

???+ example
    ```python
    from synctodoist import TodoistAPI
    
    api = TodoistAPI(api_key=<YOUR_TODOIST_API_KEY>)
    project = api.projects.get(item_id='1234')
    ```

    1. You start by instantiating the `TodoistAPI` as `api`
    2. You access the `ProjectManager` through `api.projects`

