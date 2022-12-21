# Welcome to SyncTodoist

SyncTodoist helps you interact with the Todoist Sync API v9 in Python. To find out more about the Todoist API, please, visit
[developer.todoist.com](https://developer.todoist.com).

## Design Principles

This package was designed with the following principles in mind:

1. **Modern Python**: It follows modern Python design concepts, e.g. careful type annotation wherever it makes sense.
2. **Pydantic everywhere**: Data is moved around as a Pydantic data model. The package relies heavily on Pydantic for validation, serialization and 
deserialization of objects.
3. **Match the Todoist REST API**:The API follows the Todoist REST API as closely as possible, only deviating where it is necessary due to the different nature 
of the Sync API.
4. **Properly documented**: this documentation follows the [Diátaxis](https://diataxis.fr) model.
5. **Thoroughly tested**: every part of the code is tested thoroughly with unit tests and integration tests. Tests are created with `pytest`.

## Bugs & Feature Requests

If you find a bug, or you're missing a feature, please, open an issue on [GitHub](https://github.com/gaborschulz/synctodoist/issues). Please, use the 
templates to describe the bug or feature request. This project is still work-in-progress, so new features will be added soon.

## Contributing

If you'd like to contribute, please, check the [Contributing Guide](https://github.com/gaborschulz/synctodoist/blob/main/CONTRIBUTING.md) in the GitHub repo.

## Disclaimer

This package is not created by, affiliated with, or supported by Doist.

## Privacy Policy

This site does not collect any personal data about you. It does not use cookies, tracking or anything similar. The sole purpose of this site is to provide a
documentation for the `synctodoist` package.