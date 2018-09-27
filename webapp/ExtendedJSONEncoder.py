import json
from bson import ObjectId
from SynagogueModel import Synagogue


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, Synagogue):
            return o.json()
        return json.JSONEncoder.default(self, o)


