# Klerc 
-------

## Introduction

Klerc is an app designed to assist developers in creating apps that allow people to take notes and schedule tasks. The app allows users to create, view, update, and delete notes and tasks that are scheduled to be completed at and within the specified timeframe.


## Getting Started

### Pre-requisites and Local Development
- Developers who wish to contribute to this project should have Python3, pip and node installed on their local machines. Here is a link to download Python3 `www.python.org/downloads`.

- Install *pipenv* by running ```pip install --user pipenv``` on your terminal or command line
- When installed run ```pipenv install``` in the klerc folder to install dependencies.

- To run the application run the following commands:
    ```
    export FLASK_APP=app.py
    export FLASK_DEBUG=True
    flask run
    ```
The application is run on `http://127.0.0.1:5000/`


## API Reference
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`. 
- Authentication: This application does require authentication and uses JSON Web Token (JWT).

### Error Handling

Klerc app uses conventional HTTP response code to indicate success and failure of an API request, errors are returned as JSON objects in the format

{
    "success": False, 
    "error": 400,
    "message": "bad request"
}

Here are some status codes;
- 200 - Ok - Everything works as expected.
- 400 - Bad Request - The request was not accepted which may be due to wrong or unaccepted request.
- 401 - Unauthorized - The client request has not been completed because it lacks valid authentication credentials for the requested resource
- 404 - Not Found - The requested resource does not exist.
- 405 - Method not Allowed - This can occure when the wrong method is used on a resource.
- 422 - Unprocessable - This can occur when the request cannot be processed.

### Endpoint Library

#### GET/registration
- General:
    - Returns a list of categories objects, success value, and total number of categories of questions in the Klerc app.
- Sample: `curl http://127.0.0.1:5000`


### Authors
Celestine Okonkwo


### Acknowledgment

