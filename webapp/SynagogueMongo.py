from bson import ObjectId
import datetime
from pymongo import MongoClient

client = MongoClient('mongodb://startach:gG123456@ds235022.mlab.com:35022/jewish_world')

db = client['jewish_world']

synagogues_db = db['synagogues']

def time_to_float(hour):
    t = datetime.datetime.strptime(hour, "%H:%M").time()
    return t.hour + t.minute / 60


def create_synagogue(synagogue_object):
    try:
        if synagogues_db.find_one({
                'address': synagogue_object['address'],
                'name': synagogue_object['name']}) is not None:
            return False, "בית הכנסת כבר קיים במערכת"
        synagogue_id = synagogues_db.insert_one(synagogue_object).inserted_id
        if synagogue_id:
            return True, synagogue_id
        else:
            return False, "אירעה שגיאה בהוספת בית הכנסת"
    except Exception as e:
        print("Unexpected error: " + e)
        return False, "Unexpected error!"


def get_synagogue(syn_id):
    try:
        return synagogues_db.find_one({'_id': ObjectId(syn_id)})
    except Exception as e:
        return e


def update_synagogue(syn_id, update_object):
    update_query = {}
    for key, value in update_object.items():
        if key != '_id':
            update_query[key] = value

    try:
        return synagogues_db.update_one({'_id': ObjectId(syn_id)}, {"$set": update_query})
    except Exception as e:
        return e


def search_synagogue_name(name):
    try:
        return list(synagogues_db.find({'name': {"$regex": '.*' + name + '.*'}}))
    except Exception as e:
        return e


# final
def search_synagogue(json_parameters):
    inner_query = {}

    j = json_parameters

    keys = []

    for key, value in j.items():
        v = value
        k = key

        if value == 'true':
            v = True
        elif value == 'false':
            v = False
        elif value in ('none', 'null'):
            v = None

        if key == 'name':
            if not isinstance(value, str):
                return False, "Wrong Type: " + str(key)
            v = {"$regex": '.*' + value + '.*'}
        elif key == 'address':
            if not isinstance(value, str):
                return False, "Wrong Type: " + str(key)
            v = {"$regex": '.*' + value + '.*'}
        elif key == 'days':
            if not isinstance(value, list):
                return False, "Wrong Type: " + str(key)
            k = "minyans.days"
            v = {"$all": value}
        elif key == 'hours':
            if not isinstance(value, float) or not isinstance(value, int):
                return False, "Wrong Type: " + str(key)
            v = {"$gt": time_to_float(hour=value[0]), "$lt": time_to_float(hour=value[1])}
            k = "minyans.hour_float"
        elif key in ["mikve", "parking", "disabled_access", "shtiblach"]:
            if not isinstance(value, bool):
                return False, "Wrong Type: " + str(key)
            k = "externals." + key

        if key in ['lat', 'lon', 'min_radius', 'max_radius']:
            if not isinstance(value, (int, float)):
                return False, "Wrong Type: " + str(key)
            keys.append(key)
        else:
            inner_query[k] = v

    if {'lat', 'lon', 'min_radius', 'max_radius'}.issubset(keys):
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
    elif 'lat' in keys or 'lon' in keys or 'min_radius' in keys or 'max_radius' in keys:
        return False, "Missing keys"

    try:
        res = list(synagogues_db.find(inner_query).limit(15))
        return True, res
    except Exception as e:
        return False, e
