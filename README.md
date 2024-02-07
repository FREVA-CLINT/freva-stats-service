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
token, clients can use the `/api/token` endpoint by providing valid username and
password credentials. The access token should then be included in the
Authorization header for secured endpoints.

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
via the ``/api/docs`` end point. For example:
[http://0.0.0.0:8080/api/docs](http://0.0.0.0:8080/api/docs)

Please also refer to the example notebooks, to get an overview over some usage
examples.

## Docker production container

The API is meant to be deployed in production within a dedicated docker
container. You can pull the container from the GitHub container registry:

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
pip install -e .[test]
    ```

3. Start the development environment using Docker:

    ```console
docker-compose -f dev-env/docker-compose.yaml up -d --remove-orphans
    ```

4. Run the CLI command:

    ```console
stats-service --debug --dev
     ```
     You can inspect the available options using the ``--help`` flag.

### Running Tests

Run the unit tests using:

```console
make test
```

Liting is done via

```console
make lint
```
