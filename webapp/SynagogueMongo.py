from bson import ObjectId
import datetime
from pymongo import MongoClient

client = MongoClient('mongodb://startach:gG123456@ds235022.mlab.com:35022/jewish_world')

db = client['jewish_world']

synagogues_db = db['synagogues']


def time_to_float(hour):
    t = datetime.datetime.strptime(hour, "%H:%M").time()
    return t.hour + t.minute / 60


def float_to_time(time):
    if time is None:
        return None
    hour = str(int(time))
    if len(hour) == 1:
        hour = "0" + hour

    minute = str((time - int(time)) * 60)
    if len(minute) == 1:
        minute = "0" + minute

    time_str = hour + ":" + minute

    return time_str


def convert_model_to_synagogue(model):
    for minyan in model["minyans"]:
        minyan["startTime"] = float_to_time(minyan["startTime"])
        minyan["endTime"] = float_to_time(minyan["endTime"])
    return model


def convert_synagogue_to_model(synagogue):
    for minyan in synagogue["minyans"]:
        minyan["startTime"] = time_to_float(minyan["startTime"])
        minyan["endTime"] = time_to_float(minyan["endTime"])
    return synagogue


def create_synagogue(synagogue_object):
    try:
        if synagogues_db.find_one({
                'address': synagogue_object['address'],
                'name': synagogue_object['name']}) is not None:
            return False, "Synagogue already exists"
        model = convert_synagogue_to_model(synagogue_object)
        synagogue_id = synagogues_db.insert_one(model).inserted_id
        if synagogue_id:
            return True, synagogue_id
        else:
            return False, "Error in creating synagogue"
    except Exception as e:
        print("Unexpected error: " + e)
        return False, "Unexpected error!"


def get_synagogue_by_id(syn_id):
    try:
        model = synagogues_db.find_one({'_id': ObjectId(syn_id)})
        return convert_model_to_synagogue(model)
    except Exception as e:
        return e


def update_synagogue(syn_id, update_object):
    model = convert_synagogue_to_model(update_object)
    update_query = {}
    for key, value in model.items():
        if key != '_id':
            update_query[key] = value

    try:
        return synagogues_db.update_one({'_id': ObjectId(syn_id)}, {"$set": update_query})
    except Exception as e:
        return e


def search_synagogue(json_parameters):
    inner_query = {}

    range_keys = []

    for key, value in json_parameters.items():
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
        elif value in ('none', 'null'):
            value = None

        if key in {'name', 'address'}:
            if not isinstance(value, str):
                return False, "Wrong Type: " + str(key) + " type of value is: " + str(type(value))
            inner_query[key] = {"$regex": '.*' + value + '.*'}
        elif key == 'days':
            if not isinstance(value, list):
                return False, "Wrong Type: " + str(key)
            inner_query["minyans.days"] = {"$all": value}
        elif key == 'hours':
            if not isinstance(value[0], str) or not isinstance(value[1], str):
                return False, "Wrong Type: " + str(key)
            inner_query["minyans.startTime"] = {"$gte": time_to_float(hour=value[0])}
            inner_query["minyans.endTime"] = {"$lte": time_to_float(hour=value[1])}
        elif key in ["mikve", "parking", "disabled_access", "shtiblach"]:
            if not isinstance(value, bool):
                return False, "Wrong Type: " + str(key)
            inner_query["externals." + key] = value
        elif key in ['lat', 'lon', 'min_radius', 'max_radius']:
            if not isinstance(value, (int, float)):
                return False, "Wrong Type: " + str(key)
            range_keys.append(key)

    if {'lat', 'lon', 'min_radius', 'max_radius'}.issubset(range_keys):
        inner_query['location'] = {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [float(json_parameters['lon']),
                                    float(json_parameters['lat'])]
                },
                "$maxDistance": int(int(json_parameters['max_radius']) * 1000),
                "$minDistance": int(int(json_parameters['min_radius']) * 1000),
            }
        }
    elif 'lat' in range_keys or 'lon' in range_keys or 'min_radius' in range_keys or 'max_radius' in range_keys:
        return False, "Missing keys"

    try:
        models = list(synagogues_db.find(inner_query).limit(15))
        result = []
        for model in models:
            synagogue = convert_model_to_synagogue(model)
            result.append(synagogue)
        return True, result
    except Exception as e:
        return False, e
