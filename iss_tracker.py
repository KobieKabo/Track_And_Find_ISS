from flask import Flask,request
import requests
import xmltodict
import math

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

data = get_nasa_data()

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
    function_list = ['help_function','get_nasa_data','get_All_Data','epochs_Only','get_Epoch_Entry','get_Epoch_Position','get_Epoch_Speed','delete_nasa_data','post_nasa_data']

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

    if epoch > len(epoch_Data) or epoch < 0:
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

    if epoch > len(epoch_Data) or epoch < 0:
        return "Error: Input value was larger, or smaller than bounds of data set. The input value must be 0 or larger, & smaller than the list size of the data set.\n"

    x_Speed = float(epoch_Data['X_DOT']['#text'])
    y_Speed = float(epoch_Data['Y_DOT']['#text'])
    z_Speed = float(epoch_Data['Z_DOT']['#text'])
   
    speed = math.sqrt(x_Speed**2 + y_Speed**2 + z_Speed**2)
    return {'EPOCH': epoch_Data['EPOCH'],'Speed' : speed}

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
    data = get_nasa_data()

    data_update = 'Data has been updated.\n'

    return data_update

@app.route('/delete-data', methods = ['DELETE'])
def delete_nasa_data() -> str:
    """
    Deletes data obtained from the url in get_nasa_data.

    Args:
        None.

    Returns:
        data_update (str): Returns status of the data
    """
    global data
    data = {}
    
    data_update = 'Data has been deleted.\n'
    return data_update


if __name__ == '__main__':
    app.run(debug =True, host = '0.0.0.0')
