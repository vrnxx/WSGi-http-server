# WSGi-http-server
> This is a simple `WSGI http server` project.
> I used Flask as a framework.

It is made for educational purposes so that everyone can get 

acquainted with how the WSGI protocol works in general and how 

it relates to the work of Python frameworks.

Study the source code of the wsgi.py file, 

a small documentation has been written for each method, 

it will help you figure out how it works.

> At the end you will also find useful links on this topic.
# Installation

- Clone this repository
  
  ```
  git clone https://github.com/AlexanderSeryakov/WSGi-http-server.git
  ```
- Move to project dir
  
  ```
  cd WSGi-http-server
  ``` 
- Install dependencies

  ```
  poery install
  ```
- Now you can start WSGI http server

# Let`s start
- Move to direcory with source code
  
  ```
  cd wsgi_http_server
  ```
- Start WSGI http server
  ```
  python wsgi.py flask_app:app
  ```
- If all done, you will see a message in the console
  
  ![start_server](https://github.com/AlexanderSeryakov/WSGi-http-server/assets/110708669/41ef24fe-98c3-43f5-8b4e-e228f27e9c5c)

- Open new tab in your browser and paste this url
  ```
  127.0.0.1:9000
  ```
  ![open_tab](https://github.com/AlexanderSeryakov/WSGi-http-server/assets/110708669/7ba67db4-bc09-4e61-b62c-8adba3a57a9f)

- Well, now you can use this WSGI http server for your application

# Use application

This project uses a Flask application as a web application.

You can add new endpoints and change existing ones.

To do this, go to the flask_app.py file.

> You can also use another framework to connect it to this WSGi server see the framework documentation.

