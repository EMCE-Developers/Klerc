# Klerc 
-------

## Introduction

Klerc is a app intended to help individuals keep notes and schedule tasks. The app lets you create, view, update and delete notes and tasks scheduled to be done at and withing desired timeframe.


## Getting Started

### Pre-requisites and Local Development
- Developers who wish to use this project should have Python3, pip and node installed on their local machines. Here is a link to download Python3 `www.python.org/downloads`.

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
- Authentication: This version of the application does not require authentication or API keys yet but is intended to use flask-login for authentication.

### Error Handling

Klerc app uses conventional HTTP response code to indicate success and failure of an API request, errors are returned as JSON objects in the format

{
    "success": False, 
    "error": 400,
    "message": "bad request"
}

Here are some status codes;
- 200 - Ok Everything works as expected.
- 400 - Bad Request The request was not accepted which may be due to wrong or unaccepted request.
- 404 -Not Found The requested resource does not exist.
- 405 - Method not Allowed This can occure when the wrong method is used on a resource.
- 422 - Unprocessable This can occur when the request cannot be processed.

### Endpoint Library

### `GET '/'`

  -Returns a success key of true
  
  -Request arguments: None
  
  
Example: `curl http://127.0.0.1:5000/`
```
{
    "success": True
}
```

### `POST '/register'`


  -Endpoint is used to create new users in the database.
  
  -Body should contain a first_name(string), last_name(string), email(string), username(string) and password(string).
  
  -Returns a success key of true and message
  
  -Request arguments: None
  
  
Example: `curl http://127.0.0.1:5000/register -X POST -H "Content-Type: application/json" -d '{"first_name": "Eiyzy","last_name": "Eusy","email": "test005@test.com","username": "Bee5","password": "test5"}'`

```
{
    "message": "okyouna created",
    "success": true
}
```

### `POST '/login'`

  -Body should contain a username(string) and password(string)

  -Returns a success key of true and message of login successful
  
  -Request arguments: None
  
  
Example: `curl http://127.0.0.1:5000/login -X POST -H "Content-Type: application/json" -d '{"username": "Bee5","password": "test5" }'`

```
{
    "message": "Login successful",
    "success": true
}
```
### `POST '/logout'`

  -Returns a success key of true
  
  -Request arguments: None
  
  
Example: `curl http://127.0.0.1:5000/logout`
```
{
    "message": "User logged out",
    "success": true
}
```

### `POST '/notes'`

  -Body contains content(string), title(string) and category_id(integer)

  -Returns a success key of true and message
  
  -Request arguments: None
  
  
Example: `curl http://127.0.0.1:5000/notes -X POST -H "Content-Type: application/json" -d '{"content": "Here goes your notes","title":"Note 4", "category_id":"5" }'`

```
{
    "message": "Note 4 created!",
    "success": true
}
```

### `POST '/categories'`

  -Body contains name(string)

  -Returns a success key of true and message
  
  -Request arguments: None
  
Example: `curl http://127.0.0.1:5000/categories -X POST -H "Content-Type: application/json" -d '{"name":"category 1"}'`
  
```
{
    "message": "Category category 1 added successfully!",
    "success": true
}
```
### Skip for now its giving an error

### `POST '/notes/<notes_id>'`

  -Returns a success key of true and message
  
  -Request arguments: Notes id
  
  
Example: `curl http://127.0.0.1:5000/notes/4

```
{
    "message": "Note 4 created!",
    "success": true
}
```

### `GET '/notes'`

  -Used to get all the notes in the database

  -Returns a success key of true and a list of notes data
  
  -Request arguments: None
  
  
Example: `curl http://127.0.0.1:5000/notes

```
{
    "notes": {
        "notes_data": [
            {
                "category_id": 1,
                "content": "Here goes your notes",
                "date_created": "14/12/2022 12:57:12",
                "id": 17,
                "title": "Note 1"
            },
            {
                "category_id": 1,
                "content": "Here goes your notes",
                "date_created": "14/12/2022 12:57:12",
                "id": 18,
                "title": "Note 2"
            },
            {
                "category_id": 3,
                "content": "Here goes your notes",
                "date_created": "15/12/2022 21:51:40",
                "id": 19,
                "title": "Note 4"
            }
        ]
    },
    "success": true
}
```

### `POST '/notes/category/<category>/`

  -Returns a success key of true and a list of notes data
  
  -Request arguments: category id
  
  
Example: `curl http://127.0.0.1:5000/notes/category/Category 1

```
{
    "notes": {
        "notes_data": []
    },
    "success": true
}
```


### `PUT/PATCH '/notes/<note id>/`

  -Returns a success key of true and a list of notes data
  
  -Request arguments: category id
  
  
Example: `curl http://127.0.0.1:5000/notes/category/Category 1

```
{
    "notes": {
        "notes_data": []
    },
    "success": true
}
```


### Authors
- Celestine Okonkwo
- Monsur Oyedeji
- Ekemini Udongwo


### Acknowledgment
