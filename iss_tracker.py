from flask import Flask,request
import requests
import xmltodict
import math
import time
import yaml 
from geopy.geocoders import Nominatim

app = Flask(__name__)

def get_nasa_data() -> dict:
    """
    Function grabs the XML data from the Nasa data-base, and converts it into a usable python dictionary.
    Route Used: None.

    Args:
        None.

    Returns:
        data (dict) : a dictionary of the information within the stateVectors key that was pulled from the XML file. 
                      This route was found using the .keys function, with the XML data.
    """
    url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'
    r = requests.get(url)
    data = xmltodict.parse(r.content)

    return data['ndm']['oem']['body']['segment']['data']['stateVector']

def get_all_data() -> dict:
    """
    Function grabs the XML data from the Nasa data-base, and converts it into a usable python dictionary.
    Route Used: None.

    Args:
        None.

    Returns:
        all_data (dict) : a dictionary of the information within the stateVectors key that was pulled from the XML file.
                      This route was found using the .keys function, with the XML data.
    """
    url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'
    r = requests.get(url)
    all_data = xmltodict.parse(r.content)
    return all_data

data = get_nasa_data()

all_data = get_all_data()

@app.route('/help', methods = ['GET'])
def help_function() -> str:
    """
    Function returns a help message with all routes, what they do, & how to properly use them.
    
    Route Used: '/help'

    Args:
        None

    Returns:
        help_statements (str) : short explanation of all of the functions & routes.
    """
    function_list = ['help_function','get_nasa_data','get_All_Data','epochs_Only','get_Epoch_Entry','get_Epoch_Position','get_Epoch_Speed','delete_nasa_data','post_nasa_data','get_comments','get_header','get_metadata','get_epoch_location']

    help_statements = '\nRoute & Function definitions for the flask app:\n'

    for functions in function_list:
        help_statements = help_statements + f'{functions}:\n' + eval(functions).__doc__+'\n\n'

    return help_statements 

@app.route('/', methods = ['GET'])
def get_All_Data() -> dict:
    """
    This function takes the python dictionary from get_Nasa_Data & returns it.
    
    Route Used: '/'
    
    Args:
        None

    Returns:
        data (dict): python dictionary of all Epochs & the associated data.
    """
    try:    
        global data
        return data
    except NameError:
        return 'Data is missing. Please re-post the data with the post-data route.\n'
    return data

@app.route('/epochs', methods = ['GET'])
def epochs_Only() -> list:
    """
    Function takes the python dictonary created with get_Nasa_Data & creates a list of all current Epochs.
    
    Route Used: '/epochs'
    
    Args:
        None.

    Returns:
        query_epoch (list) : A list that holds all the epochs within the chosen query parameters. Otherwise, all
                             entries are returned.
    """
    epochs = []
    for d in data:
        epochs.append(d['EPOCH'])

    try:
        offset = int(request.args.get('offset',0))
    except ValueError:
        return "Error: offset query parameter needs to be an integer value.\n", 404

    try:
        limit = int(request.args.get('limit',len(epochs) - offset))
    except ValueError:
        return "Error: limit query parameter needs to be an integer value.\n", 404

    if (limit + offset) > len(epochs) or limit > len(epochs) or offset > len(epochs):
        return "Error: query parameters greater than size of data set.", 404

    query_epoch = {}
    for i in range(limit):
        query_epoch[offset+i+1] = epochs[offset + i]
    return query_epoch

@app.route('/epochs/<epoch>', methods = ['GET'])
def get_Epoch_Entry(epoch) -> dict:
    """
    Function takes in a specific epoch, from the list created in epochs_Only. This epoch is specified
    by an integer value.
    
    Route Used: '/epochs/<epoch>'

    Args:
        epoch (int): an integer value that identifies the specific epoch from the epochs list
                     that we want the data from.

    Returns:
        data (dict): returns a dictionary that holds the data from the specific epoch identified earlier.
    """

    try:
        epoch = int(epoch)
    except ValueError:
        return "Error: epoch entry mush be an integer value.\n", 404
    
    if epoch > len(data) or epoch < 0:
        return "Error: Input value was larger, or smaller than bounds of data set. The input value must be 0 or larger, & smaller than the list size of the data set.\n"
    
    return data[int(epoch)]

@app.route('/epochs/<epoch>/position', methods = ['GET'])
def get_Epoch_Position(epoch) -> dict:
    """
    Function takes in a specific epoch, from the list created in epochs_Only. This epoch is specified
    by an integer value. It then returns the X, Y, & Z position coordinates contained within that epoch.
    
    Route Used: '/epochs/<epoch>/position

    Args:
        epoch (int): an integer value that identifies the specific epoch from the epochs list
                     that we want the data from.

    Returns:
        dictionary: returns a dictionary containing the X Y Z coordinates & a key that is associated with 
                    the specific coordinate plane.
    """
    epoch_Data = get_Epoch_Entry(epoch)
    try:
        epoch = int(epoch)
    except ValueError:
        return "Error: epoch entry mush be an integer value.\n", 404

    if epoch > len(data) or epoch < 0:
        return "Error: Input value was larger, or smaller than bounds of data set. The input value must be 0 or larger, & smaller than the list size of the data set.\n"

    position = {'EPOCH': epoch_Data['EPOCH'],'X': epoch_Data['X']['#text'], 'Y': epoch_Data['Y']['#text'], 'Z': epoch_Data['Z']['#text']}

    return position

@app.route('/epochs/<epoch>/speed', methods = ['GET'])
def get_Epoch_Speed(epoch) -> dict:
    """
    Function takes in a specific epoch, from the list created in epochs_Only. This epoch is specified by
    an integer value. It then returns a dictionary holding the final speed value of the epoch.
    
    Route Used: '/epochs/<epoch>/speed'

    Args:
        epoch (int): an integer value that identifies the specific epoch from the epochs list
                     that we want the data from.

    Returns:
        Speed (dict): The speed of the ISS within the specified epoch. 
    """
    epoch_Data = get_Epoch_Entry(epoch)

    try:
        epoch = int(epoch)
    except ValueError:
        return "Error: epoch entry mush be an integer value.\n", 404

    if epoch > len(data) or epoch < 0:
        return "Error: Input value was larger, or smaller than bounds of data set. The input value must be 0 or larger, & smaller than the list size of the data set.\n"

    x_Speed = float(epoch_Data['X_DOT']['#text'])
    y_Speed = float(epoch_Data['Y_DOT']['#text'])
    z_Speed = float(epoch_Data['Z_DOT']['#text'])
   
    speed = math.sqrt(x_Speed**2 + y_Speed**2 + z_Speed**2)
    epoch_speed_data = {'EPOCH': epoch_Data['EPOCH'],'Speed' : speed}
    return epoch_speed_data

@app.route('/post-data', methods = ['POST'])
def post_nasa_data() -> str:
    """
    Restores data to the dictionary
    
    Route Used: '/post-data'

    Args:
        None.

    Returns:
        data_update (str) : Returns status of the data.
    """

    global data
    global all_data

    all_data = get_all_data()
    data = get_nasa_data()

    data_update = 'Data has been updated.\n'

    return data_update

@app.route('/delete-data', methods = ['DELETE'])
def delete_nasa_data() -> str:
    """
    Deletes data obtained from the url in get_nasa_data.

    Route Used: /delete-data

    Args:
        None.

    Returns:
        data_update (str): Returns status of the data
    """
    global data
    global all_data
    
    try:
        del data
        del all_data
    except NameError:
        data_update = 'Data has already been deleted. Please re-post it before attempting to delete again.\n'
        return data_update

    data_update = 'Data has been deleted.\n'
    return data_update

@app.route('/comment', methods = ['GET'])
def get_comments() -> list:
    """
    Function gets the comments that are stored within the XML file we're pulling data from.

    Route Used: /comment

    Args:
        None.

    Returns:
        List of all the comments within the XMl file.
        Or a string that indicates an error accessing the data. Likely a result from not re-posting the data after deletion.
    """

    try:
        global all_data
        return all_data['ndm']['oem']['body']['segment']['data']['COMMENT']
    except NameError:
        return "Data is empty. Please re-post data using the post-data route.\n"

@app.route('/header', methods = ['GET'])
def get_header() -> dict:
    """
    Function gets the headers that are stored within the XML file we're pulling data from.

    Route Used: /header

    Args:
        None.

    Returns:
        dictionary of the headers within the XMl file.
        Or a string that indicates an error accessing the data. Likely a result from not re-posting the data after deletion.
    """
    try:
        global all_data
        return all_data['ndm']['oem']['header']
    except NameError:
        return "Data is empty. Please re-post data using the post-data route.\n"

@app.route('/metadata', methods = ['GET'])
def get_metadata() -> dict:
    """
    Function gets the metadata thats stored within the XML file we're pulling data from.

    Route Used: /metadata

    Args:
        None.

    Returns:
        dictionary of the metadata within the XMl file.
        Or a string that indicates an error accessing the data. Likely a result from not re-posting the data after deletion.
    """
    try:
        global all_data 
        return all_data['ndm']['oem']['body']['segment']['metadata']
    except NameError:
        return "Data is empty. Please re-post data using the post-data route.\n"

@app.route('/epochs/<epoch>/location', methods = ['GET'])
def get_epoch_location(epoch) -> dict:
    """
    Function gets the geographic location of the ISS at a certain epoch.

    Route Used: /epochs/<epoch>/location

    Args:
        epoch(int): determines which epoch is returned from the list generated by the data

    Returns:
        dictionary of geograhpic data including altitude, longitude, latitude & country that its over. Or if its over an ocean.
            Additionally returns which the specific epoch used.
    """
    
    epochs = get_Epoch_Position(epoch) 
    epoch_speed = get_Epoch_Speed(epoch)

    X = float(epochs['X'])
    Y = float(epochs['Y'])
    Z = float(epochs['Z'])
    MEAN_EARTH_RADIUS = 6371 #kilometers
    
    EPOCH = epochs['EPOCH'] # time data is held in EPOCH key

    hours = float(EPOCH[9:11])
    minutes = float(EPOCH[12:14])

    latitude = math.degrees(math.atan2(Z, math.sqrt(X**2 + Y**2)))
    longitude = math.degrees(math.atan2(Y,X)) - ((hours-12) + (minutes/60))*(360/24) + 32

    altitude = math.sqrt(X**2 + Y**2 + Z**2) - MEAN_EARTH_RADIUS

    geocoder = Nominatim(user_agent = 'iss_tracker')
    geoloc = geocoder.reverse((latitude,longitude), zoom = 10, language = 'en')

    try:
        return {'EPOCH':epochs['EPOCH'],'Latitude': latitude, 'Longitude': longitude, 'Altitude': altitude,'Geographic Location': geoloc.address}
    except AttributeError:
        return {'EPOCH':epochs['EPOCH'],'Latitude': latitude, 'Longitude': longitude, 'Altitude': altitude,'Geographic Location':"ISS was/is over the ocean."}

@app.route('/now', methods = ['GET'])
def ISS_location_now() -> dict:
    """
    """
    
    global data
    smallest_time_difference = 1e10 # Ensures smallest difference is always larger initially

    for epochs in data:
        current_time = time.time() # gives presnt time in since unix epoch
        epoch_time = time.mktime(time.strptime(epochs['EPOCH'][:-5],'%Y-%jT%H:%M:%S')) # gives epoch time in seconds since unix
        time_difference = current_time - epoch_time
        if time_difference < smallest_time_difference:
            smallest_time_difference = time_difference
            closest_current_epoch = epochs

    X = float(closest_current_epoch['X']['#text'])
    Y = float(closest_current_epoch['Y']['#text'])
    Z = float(closest_current_epoch['Z']['#text'])

    X_DOT = float(closest_current_epoch['X_DOT']['#text'])
    Y_DOT = float(closest_current_epoch['Z_DOT']['#text'])
    Z_DOT = float(closest_current_epoch['Z_DOT']['#text'])
    epoch_Speed = math.sqrt(X_DOT**2 + Y_DOT**2 + Z_DOT**2)

    MEAN_EARTH_RADIUS = 6371 #kilometers

    EPOCH = epochs['EPOCH'] # time data is held in EPOCH key

    hours = float(EPOCH[9:11])
    minutes = float(EPOCH[12:14])

    latitude = math.degrees(math.atan2(Z, math.sqrt(X**2 + Y**2)))
    longitude = math.degrees(math.atan2(Y,X)) - ((hours-12) + (minutes/60))*(360/24) + 32

    if (longitude <= 180 and longitude >= -180):
        longitude = longitude
    else:
        longitude = -180+(longitude-180)

    altitude = math.sqrt(X**2 + Y**2 + Z**2) - MEAN_EARTH_RADIUS

    geocoder = Nominatim(user_agent = 'iss_tracker')
    geoloc = geocoder.reverse((latitude,longitude), zoom = 5, language = 'en')
    
    try:
        return {"Closest Epoch":closest_current_epoch['EPOCH'],"Time from now": smallest_time_difference,"Location":{'Latitude':latitude, 'Longitude': longitude, 'Altitude':{"Value": altitude,"Units":"km"}}, "Geographic Location": geoloc.address, "Speed":{"Value":epoch_Speed,"Units":"m/s"} }    
    except AttributeError:
        return {"Closest Epoch":closest_current_epoch['EPOCH'],"Time from now": smallest_time_difference,"Location":{'Latitude':latitude, 'Longitude': longitude, 'Altitude':{"Value": altitude, "Units": "km"}, "Geographic Location": "ISS was/is over the ocean."}, "Speed": {"Value":epoch_Speed,"Units": "m/s"}}

if __name__ == '__main__':
    app.run(debug =True, host = '0.0.0.0')
