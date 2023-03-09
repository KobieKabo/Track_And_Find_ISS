# Homework 5: "Undone: The Sweater Container"

### Project Description:
This project was to develop a Flask-web based application that provides the user with current information about the International Space Station(ISS). This information
contains its position, and speed at different points and time. In addition, we were required to create a working docker container that can be used to ensure our application works in any enviroment by having the correct versions of modules & packages in use. 

#### Project Objective:
The purpose of this project was to become more familiar with Flask application development & the use of the DELETE method. In addition we also became more familiar with the creation of docker images, and pulling and pushing docker images.

### Data:
The data used was sourced from: https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml
Which was easily converted into a python dictionary with the use of the xmltodict module.

### Scripts:
`iss_tracker.py`: Flask application that is used to query for information about the ISS. Application loads in data from the URL referenced above in the data section. 
Depending on the route used different information is returned. 

### Flask Application & Routes:

| Route         | Return        | 
| ------------- |:-------------:| 
| `/`     | the full data set | 
| `/epochs`       | all epochs in the data set      |
| `/epochs/<epoch>`  | the data (state vectors) associated with the specified epoch      |
| `/epochs/<epoch>/position`  | the positional coordinates of the specified epoch     |
| `/epochs/<epoch>/speed`  | the speed of the specified epoch      |
| `/delete-data` | deletes the data & renders the other routes useless |
| `/post-data` | re-inserts the data from the URL above & allows the other routes to be used again |

Where `<epoch>` is any integer value. If a non-integer is used, you'll receive an error message.

### Usage & Installation:
To properly use this program you'll need to have docker, so that you the user can use the image already created, or make your own.

# Method 1: Using the image already generated
To use the image that I've already created you simply need to pull the docker file from dockerhub, and then run it.
As such you'll need to do the following:

```
docker pull kobiekabo/iss_tracker:1.0
...
...
...
docker run -it --rm -p 5000:5000 kobiekabo/iss_tracker:1.0
```
Doing it this way constructs the image & allows the docker image to be run, which will immediately start the flask application.

# Method 2: Creating your own image
To use this method, the Dockerfile needs to be in the current working directory for the commands to work properly.
As such you'll need to use the docker build command as follows:
```
docker build -t <yourdockerusername>/<fileName>:<version> .
```
This will then create an image based on the Dockerfile in the current directory.

The image built can then be checked with:
```
docker images
...
REPOSITORY              TAG       IMAGE ID       CREATED         SIZE
kobiekabo/iss_tracker   1.0       1932e3be3921   2 hours ago     897MB
...
```
Now, regardless of the method used it's time to run the image!
This is done with the following command:
```
docker run -it --rm -p 5000:5000 <yourdockerusername>/<fileName>:<version>
```
if you're using the image I've created then the command looks like:
```
docker run -it --rm -p 5000:5000 kobiekabo/iss_tracker:1.0
```
This starts the flask application, and queries are now accessible using the API.

# NOTE:
Ensure that the --rm option is not forgotten! Otherwise you'll have to stop the docker container manually.
If you do the --rm option you'll receive an error similar to the following:
```
Error response from daemon: driver failed programming external connectivity on endpoint magical_kare 
(e109f1045da2d2d1d937e2d7079cd2b0e3b1951a56e27fa9f24eec6b7fcb5fbd): Bind for 0.0.0.0:5000 failed: port is already allocated
```
This can be easily fixed by using:
```
docker ps
```
This allows you to check the container's unique id which is necessary to close the container.
You then use:
```
docker stop <container ID>
```
To close the container.
# END NOTE

Now from a new terminal window that's within the same machine you're able to make queries via the command line. Using curl requests & the routes from above we can begin to get results like the following:

Route One: `/`
```
curl 127.0.0.1:5000/
...
{
    "EPOCH": "2023-063T12:00:00.000Z",
    "X": {
      "#text": "2820.04422055639",
      "@units": "km"
    },
    "X_DOT": {
      "#text": "5.0375825820999403",
      "@units": "km/s"
    },
    "Y": {
      "#text": "-5957.89709645725",
      "@units": "km"
    },
    "Y_DOT": {
      "#text": "0.78494316057540003",
      "@units": "km/s"
    },
    "Z": {
      "#text": "1652.0698653803699",
      "@units": "km"
    },
    "Z_DOT": {
      "#text": "-5.7191913150960803",
      "@units": "km/s"
    }
  }
```
It should also be noted that on your other terminal you should be receiving messages like the following after each route call.
```
127.0.0.1 - - [21/Feb/2023 05:31:34] "GET / HTTP/1.1" 200 -
```
Now, for Route Two: `/epochs`
```
curl 127.0.0.1:5000/epochs
...
{
  "1": "2023-055T12:00:00.000Z",
  "2": "2023-055T12:04:00.000Z",
  "3": "2023-055T12:08:00.000Z",
  "4": "2023-055T12:12:00.000Z",
  "5": "2023-055T12:16:00.000Z",
  "6": "2023-055T12:20:00.000Z",
  "7": "2023-055T12:24:00.000Z",
  "8": "2023-055T12:28:00.000Z",
  "9": "2023-055T12:32:00.000Z",
  "10": "2023-055T12:36:00.000Z",
  ...
}
```
Route three: `/epochs/<epoch>`
```
curl 127.0.0.1:5000/epochs/1
...
{
  "EPOCH": "2023-048T12:04:00.000Z",
  "X": {
    "#text": "-5998.4652356788401",
    "@units": "km"
  },
  "X_DOT": {
    "#text": "-2.8799691318087701",
    "@units": "km/s"
  },
  "Y": {
    "#text": "391.26194859011099",
    "@units": "km"
  },
  "Y_DOT": {
    "#text": "-5.2020406581448801",
    "@units": "km/s"
  },
  "Z": {
    "#text": "-3164.26047476555",
    "@units": "km"
  },
  "Z_DOT": {
    "#text": "4.8323394499086101",
    "@units": "km/s"
  }
}
```
Route Four: `/epochs/<epoch>/position`
```
curl 127.0.0.1:5000/epochs/1/position
...
{
  "EPOCH": "2023-055T12:04:00.000Z",
  "X": "5818.7531209531799",
  "Y": "-2960.76752193736",
  "Z": "1892.95882490642"
}
```
Route Five: `/epochs/<epoch>/speed`
```
curl 127.0.0.1:5000/epoch/1/speed
...
{
  "EPOCH": "2023-055T12:04:00.000Z",
  "Speed": 7.660018331736536
}
```
Route Six: `/help`
```
curl 127.0.0.1:5000/help
...
Route & Function definitions for the flask app:
help_function:

    Function returns a help message with all routes, what they do, & how to properly use them.

    Route Used: '/help'

    Args:
        None

    Returns:
        help_statements (str) : short explanation of all of the functions & routes.
...
```
Route Seven: `/delete-data`
```
curl -X DELETE 127.0.0.1:5000/delete-data
...
Data has been deleted.
```
Route Eight: `/post-data`
```
curl -X POST 127.0.0.1:5000/post-data
...
Data has been updated.
```
