from pymodm import fields, EmbeddedMongoModel, MongoModel
from pymodm import connect
from bson import ObjectId
import requests

connect("mongodb://localhost:27017/JewishWorld", alias="derech-hamelech-app")


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
    hour = fields.CharField()
    hour_float = fields.FloatField(blank=True, required=False)
    days = fields.ListField(field=fields.IntegerField())

    def json(self):
        return {
            "minyan": self.minyan,
            "hour": self.hour,
            "days": self.days
        }

    class Meta:
        final = True


class Synagogue(MongoModel):
    """
    name = fields.CharField() \n
    address = fields.CharField() \n
    location = fields.PointField() \n
    nosahc = fields.CharField() \n
    phone_number = fields.CharField() \n
    externals = fields.EmbeddedDocumentField(Externals) \n
    minyans = fields.EmbeddedDocumentListField(Minyan) \n
    image = fields.ImageField()
    """
    name = fields.CharField(blank=True)
    address = fields.CharField(blank=True)
    location = fields.PointField(blank=True)
    nosahc = fields.CharField(blank=True)
    phone_number = fields.CharField(blank=True)
    externals = fields.EmbeddedDocumentField(Externals, blank=True)
    minyans = fields.EmbeddedDocumentListField(Minyan, blank=True)
    image = fields.ImageField(blank=True)

    def json(self):
        return {
            "name": self.name,
            "address": self.address,
            "location": self.location,
            "nosahc": self.nosahc,
            "phone_number": self.phone_number,
            "externals": self.externals.json(),
            "minyans": [s.json() for s in self.minyans],
            "image": None
        }

    class Meta:
        connection_alias = 'derech-hamelech-app'
        collection_name = "synagogues"
        final = True


def create_synagogue(synagogue_object):
    location = synagogue_object['location'] if synagogue_object['location'] else None

    if not location:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': synagogue_object['address'],
            'format': 'json',
            'limit': 1,
            'accept-language': 'iw'
        }
        r = requests.get(url, params=params)
        if r.status_code == 200:
            j = r.json()[0]
            lat = float(j['lat'])
            lon = float(j['lon'])
            location = [lon, lat]
        else:
            location = None

    syn = Synagogue(
        name=synagogue_object['name'], address=synagogue_object['address'],
        location=location, nosahc=synagogue_object['nosahc'],
        phone_number=synagogue_object['phone_number'], image=None,
        externals=synagogue_object['externals'], minyans=synagogue_object['minyans'])
    try:
        result = syn.save()
        if result and location:
            return True, ""
        else:
            return False, 'no_location'
    except Exception:
        return False, 'failed'


def get_synagogue(**kwargs):
    if len(kwargs.keys()) is 1 and 'syn_id' in kwargs.keys():
        try:
            return Synagogue.objects.raw({'_id': ObjectId(kwargs['syn_id'])}).first()
        except Exception:
            return None
    else:
        return search_synagogue(**kwargs)


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


def search_synagogue(**kwargs):
    inner_query = {}

    keys = []
    values = {}

    for key, value in kwargs.items():

        keys.append(key)
        values[key] = value

        if value == 'true':
            inner_query[key] = True
        if value == 'false':
            inner_query[key] = False
        if value in ('none', 'null'):
            inner_query[key] = None

        if key in ('id', '_id') or '_id' in key:
            inner_query['_id'] = ObjectId(value)
        elif key == 'name':
            inner_query[key] = {"$regex": '.*' + value + '.*'}
        elif key == 'address':
            inner_query[key]  = {"$regex": '/' + value + '$/'}
        elif key in ('lat', 'lon', 'min_radius', 'max_radius'):
            pass
        else:
            inner_query[key] = value

    if set(['lat', 'lon', 'min_radius', 'max_radius']).issubset(keys):
        inner_query['location'] = {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [float(values['lon']),
                                    float(values['lat'])]
                },
                "$maxDistance": int(int(values['max_radius']) * 1000),
                "$minDistance": int(int(values['min_radius']) * 1000),
            }
        }

    if len(kwargs.keys()) > 1:
        query = {
            "$and": [{k: v} for k, v in inner_query.items()]
        }
        inner_query = query

    try:
        res = list(Synagogue.objects.raw(inner_query))
        return res
    except Exception:
        return False
