# The freva storage restAPI 🚀

The freva storage restAPI is a powerful interface designed to interact with a
database storage systems, providing functionalities to store, query, and
manage statistical data related to user searches in the freva application.
It is designed with security, flexibility, and ease of use in mind.

Currently the following functionality is implemented:

- add, retrieve, delete databrowser user search queries.
- add, retrieve, delete freva plugin statistics.


### Authentication
The API supports token-based authentication using OAuth2. To obtain an access
token, clients can use the ``/api/storage/v2/token`` endpoint by providing
valid username and password credentials. The access token should then be
included in the Authorization header for secured endpoints.

### Data Validation
Data payloads are validated using JSON Schema to ensure the correct
structure and types. The validation prevent unauthorized access
or invalid inputs.


## Prerequisites

- Python 3.11+
- Docker (for running the development environment)

## Usage

A detailed documentation is available via the auto generated docs.
You can access the documentation after the API is running (deployed or in dev mode)
via the ``/api/storage/docs`` end point. For example:
[http://0.0.0.0:8080/api/storage/docs](http://0.0.0.0:8080/api/storage/docs)

Please also refer to the example notebooks, to get an overview over some usage
examples in the [examples](examples) folder.

## Production deployment
The API is set up using a command line interface called ``storage-service``.
There are several options to configure the API:

```console
storage-service --help

 Usage: storage-service [OPTIONS]

 Command line interface for the freva storage API.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --port                                             INTEGER                          The port the api is running on [default: 8080]                                       │
│ --reload                --no-reload                                                 Reload on code changes (development mode). [default: no-reload]                      │
│ --debug                 --no-debug                                                  Turn on debug mode. [default: no-debug]                                              │
│ --workers                                          INTEGER                          Set the number of parallel processes serving the API. [default: 8]                   │
│ --mongo-username                                   TEXT                             Set the mongoDB username as fallback for the MONGO_USERNAME env variable.            │
│                                                                                     [default: mongo]                                                                     │
│ --mongo-host                                       TEXT                             Set the mongoDB host sever as fallback for the MONGO_HOST env variable.              │
│                                                                                     [default: localhost:27017]                                                           │
│ --ask-mongo-password    --no-ask-mongo-password                                     Set the mongoDB user password as fallback for the MONGO_PASSWORD env variable.       │
│                                                                                     [default: no-ask-mongo-password]                                                     │
│ --api-username                                     TEXT                             Set the API admin username as fallback for the API_USERNAME env variable.            │
│                                                                                     [default: stats]                                                                     │
│ --ask-api-password      --no-ask-api-password                                       Set the API admin user password as fallback for the API_PASSWORD env variable.       │
│                                                                                     [default: no-ask-api-password]                                                       │
│ --install-completion                               [bash|zsh|fish|powershell|pwsh]  Install completion for the specified shell. [default: None]                          │
│ --show-completion                                  [bash|zsh|fish|powershell|pwsh]  Show completion for the specified shell, to copy it or customize the installation.   │
│                                                                                     [default: None]                                                                      │
│ --help                                                                              Show this message and exit.                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```


### Docker production container

Instead of running the command line interface the API can be deployed
in production within a dedicated docker container. You can pull the container
from the GitHub container registry:

```console
docker pull ghcr.io/freva-clint/freva-storage-service:latest
```

In the production container the API is configured via the following environment
variables:

- ``DEBUG``: Start server in debug mode (1), (default: 0 -> no debug).
- ``API_PORT``: the port the rest service should be running on (default 8080).
- ``API_USERNAME``: the user name of the privileged user (admin)
- ``API_PASSWORD``: the password of the privileged user (admin)
- ``MONGO_HOST``: host name of the mongodb server, where query statistics are
                 stored. Host name and port should separated by a ``:``, for
                 example ``localhost:27017``
- ``MONGO_USERNAME``: user name for the mongodb.
- ``MONGO_PASSWORD``: password to log on to the mongodb.

> ``📝`` You can override these environment settings by using the command line
         arguments of the ``storage-service`` command. For more information run
         ``storage-service --help``


## Development and local deployment

To locally install the API for development purposes follow these steps:

1. Clone the repository:

```console
git clone git@github.com:FREVA-CLINT/freva-stats-service.git
cd freva-stats-service
```

2. Install the project in editable mode with test dependencies:

```console
pip install -e .[dev]
```

3. Start the development environment using Docker:

```console
docker-compose -f dev-env/docker-compose.yaml up -d --remove-orphans
```

4. Run the CLI command:

 ```console
stats-service --debug --reload
```
You can inspect the available options using the ``--help`` flag.

### Running Tests

Unit tests, Example notebook tests, type annotations and code style tests
are done with [tox](https://tox.wiki/en/latest/). To run all tests, linting
simply execute the following command:

```console
tox
```

Tox runs in a separate python environment to run the tests in the current
environment use:

```console
pytest
```

## Contributing

If you would like to contribute to the project, please follow these guidelines.

1.    Fork the repository.
2.    Create a new branch: git checkout -b your-feature.
3.    Make your changes and commit them: git commit -am 'Add some feature'.
4.    Push to the branch: git push origin your-feature.
5.    Submit a pull request.

## License

This project is licensed under the BSD 2-Clause License -
see the LICENSE file for details.
