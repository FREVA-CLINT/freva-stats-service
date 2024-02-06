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

- Python 3.10+
- Docker (for running the development environment)

## Installation

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

## Usage

After running the API service you can access the documentation via the
`/api/docs` end point. For example:
[http://0.0.0.0:8080/api/docs](http://0.0.0.0:8080/api/docs)

## Running Tests

Run the unit tests using:

```console
make test
```
