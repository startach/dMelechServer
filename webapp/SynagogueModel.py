from pymodm import fields, EmbeddedMongoModel, MongoModel
from pymodm import connect
from bson import ObjectId
import requests
import datetime
import json

# connect("mongodb://localhost:27017/JewishWorld", alias="derech-hamelech-app")
connect("mongodb://startach:gG123456@ds235022.mlab.com:35022/jewish_world", alias="derech-hamelech-app")


def time_to_float(hour):
    t = datetime.datetime.strptime(hour, "%H:%M").time()
    return t.hour + t.minute / 60


class Externals(EmbeddedMongoModel):
    """
    mikve = fields.BooleanField() \n
    parking = fields.BooleanField() \n
    disabled_access = fields.BooleanField() \n
    shtiblach = fields.BooleanField() \n
    """
    mikve = fields.BooleanField(blank=True)
    parking = fields.BooleanField(blank=True)
    disabled_access = fields.BooleanField(blank=True)
    shtiblach = fields.BooleanField(blank=True)

    def json(self):
        return {
            "mikve": self.mikve,
            "parking": self.parking,
            "disabled_access": self.disabled_access,
            "shtiblach": self.shtiblach
        }

    class Meta:
        final = True


class Minyan(EmbeddedMongoModel):
    """
    minyan = fields.CharField()\n
    hour = fields.CharField()\n
    day = fields.CharField()\n
    """
    minyan = fields.CharField()
    hour = fields.CharField(blank=True)
    hour_float = fields.FloatField(blank=True, required=False)
    days = fields.ListField(field=fields.IntegerField())
    last_verified_at = fields.CharField(default=str(datetime.datetime.now().strftime('%d/%m/%Y')))

    def json(self):
        return {
            "minyan": self.minyan,
            "hour": self.hour,
            "days": self.days,
            "last_verified_at": self.last_verified_at
        }

    class Meta:
        final = True


class Lesson(EmbeddedMongoModel):
    """
    minyan = fields.CharField()\n
    hour = fields.CharField()\n
    day = fields.CharField()\n
    """
    name = fields.CharField()
    hour = fields.CharField(blank=True)
    hour_float = fields.FloatField(blank=True, required=False)
    days = fields.ListField(field=fields.IntegerField())
    last_verified_at = fields.CharField(default=str(datetime.datetime.now().strftime('%d/%m/%Y')))

    def json(self):
        return {
            "name": self.minyan,
            "hour": self.hour,
            "days": self.days,
            "last_verified_at": self.last_verified_at
        }

    class Meta:
        final = True


class Synagogue(MongoModel):
    """
    name = fields.CharField() \n
    address = fields.CharField() \n
    location = fields.PointField() \n
    nosach = fields.CharField() \n
    phone_number = fields.CharField() \n
    externals = fields.EmbeddedDocumentField(Externals) \n
    minyans = fields.EmbeddedDocumentListField(Minyan) \n
    image = fields.ImageField()
    """
    name = fields.CharField(blank=True)
    address = fields.CharField(blank=True)
    location = fields.PointField(blank=True)
    nosach = fields.CharField(blank=True)
    phone_number = fields.CharField(blank=True)
    externals = fields.EmbeddedDocumentField(Externals, blank=True)
    minyans = fields.EmbeddedDocumentListField(Minyan, blank=True)
    lessons = fields.EmbeddedDocumentListField(Lesson, blank=True)
    image = fields.ImageField(blank=True)
    comments = fields.CharField(blank=True)

    def json(self):
        return {
            "syn_id": self._id,
            "name": self.name,
            "address": self.address,
            "location": self.location,
            "nosach": self.nosach,
            "phone_number": self.phone_number,
            "externals": self.externals.json(),
            "minyans": [s.json() for s in self.minyans],
            "lessons": [s.json() for s in self.lessons],
            "comments": self.comments,
            "image": None
        }

    class Meta:
        connection_alias = 'derech-hamelech-app'
        collection_name = "synagogues"
        final = True


def create_synagogue(synagogue_object):
    # location = synagogue_object['location'] if synagogue_object['location'] else None
    #
    # if not location:
    #     url = "https://nominatim.openstreetmap.org/search"
    #     params = {
    #         'q': synagogue_object['address'],
    #         'format': 'json',
    #         'limit': 1,
    #         'accept-language': 'iw'
    #     }
    #     r = requests.get(url, params=params)
    #     if r.status_code == 200:
    #         j = r.json()[0]
    #         lat = float(j['lat'])
    #         lon = float(j['lon'])
    #         location = [lon, lat]
    #     else:
    #         location = None
    #
    for minyan in synagogue_object['minyans']:
        minyan["hour_float"] = time_to_float(minyan["hour"]) if minyan["hour"] is not None else None

    for lesson in synagogue_object['lessons']:
        lesson["hour_float"] = time_to_float(lesson["hour"]) if lesson["hour"] is not None else None

    syn = Synagogue(
        address=synagogue_object['address'],
        externals=synagogue_object['externals'],
        location=synagogue_object['location'],
        name=synagogue_object['name'],
        nosach=synagogue_object['nosach'],
        phone_number=synagogue_object['phone_number'],
        image=None,
        comments=synagogue_object['comments'],
        lessons=synagogue_object['lessons'],
        minyans=synagogue_object['minyans'])

    try:
        result = syn.save()
        if result:
            return True
        else:
            return False
    except Exception:
        return False


def get_synagogue(syn_id):
    try:
        return Synagogue.objects.raw({'_id': ObjectId(syn_id)}).first()
    except Exception:
        return None


def update_synagogue(syn_id, update_object):
    update_query = {}
    for key, value in update_object.items():
        if key != '_id':
            update_query[key] = value

    update = Synagogue.objects.raw({'_id': ObjectId(syn_id)}).update(
        {"$set": update_query}
    )
    try:
        return update
    except Exception:
        return False


#final
def search_synagogue(json_parameters):
    inner_query = {}

    j = json_parameters

    keys = []
    values = []

    for key, value in j.items():
        v = value
        k = key
        
        if key == 'name':
            v = {"$regex": '.*' + value + '.*'}
        elif key == 'address':
            v = {"$regex": '.*'  + value + '.*'}
        elif key == 'days':
            k = "minyans.days"
            v = {"$all": value}
        elif key == 'hours':
            v = {"$gt": time_to_float(hour=value[0]), "$lt": time_to_float(hour=value[1])}
            k = "minyans.hour_float"
        elif key in ["mikve", "parking", "disabled_access", "shtiblach" ]:
            k = "externals." + key

        if value == 'true':
            v = True
        elif value == 'false':
            v = False
        elif value in ('none', 'null'):
            v = None

        if key in ['lat', 'lon', 'min_radius', 'max_radius']:
            keys.append(key)
        else:
            inner_query[k] = v

    if set(['lat', 'lon', 'min_radius', 'max_radius']).issubset(keys):
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

    try:
        res = list(Synagogue.objects.raw(inner_query).limit(15))
        return res
    except Exception:
        return False
