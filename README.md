# HEgeo
HEgeo is a package for demonstrating a prototype for privacy-preserving proof of location.


## Dependency

[SEAL-Python](https://github.com/Huelse/SEAL-Python) provides a Python wrapper for the Microsoft [SEAL](https://github.com/microsoft/SEAL) package. 
Following the installation instruction to install seal for Python


## Installation
Clone the repository to your local file system.
```shell
$ git clone https://github.com/CarmenLee111/HEgeo.git
```

It is recommended to install it under a python virtual environment
```shell
$ python3 -m venv ~/venv/env_name
$ source ~/venv/env_name/bin/activate
(env_name) $ cd HEgeo
(env_name) $ python3 setup.py install
```

## Use the restful API demo
Run the server in one terminal window
```shell
$ cd restful-app/server
$ python server-setup.py
```

Send request to the server with two test coordinates
```shell
$ cd restful-app/client
$ python client-request.py 59.404811 17.948589 127.0.0.1 5000
Location verified
$ python client-request.py 59.404300 17.950540 127.0.0.1 5000   
Location not verified. Service denied.
```