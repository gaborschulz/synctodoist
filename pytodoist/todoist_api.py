import inspect

import httpx


class TodoistAPI:  # pylint: disable=too-few-public-methods
    """Todoist API class for the new Sync v9 API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.todoist.com/sync/v9'
        self.apis = {
            'get_stats': 'completed/get_stats'
        }
        self.headers = {
            'Authorization': f'Bearer {self.api_key}'
        }

    def get_stats(self) -> dict:
        """Get Todoist usage statistics"""
        method_name = inspect.stack()[0][3]
        url = f'{self.base_url}/{self.apis[method_name]}'
        with httpx.Client(headers=self.headers) as client:
            response = client.get(url=url)
            response.raise_for_status()
            return response.json()  # type: ignore


if __name__ == '__main__':
    import os

    key: str = os.environ.get('TODOIST_API')  # type: ignore
    todoist = TodoistAPI(api_key=key)
    stats = todoist.get_stats()
    print(stats)
