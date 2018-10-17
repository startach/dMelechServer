# from pymodm import fields, EmbeddedMongoModel, MongoModel
# from pymodm import connect
# from bson import ObjectId
# import requests
# import datetime


# pip install fuzzywuzzy
import json
from fuzzywuzzy import fuzz

FUZZY_THRESHOLD = 50

from SynagogueModel import Synagogue


def get_near_by_synagogues(current_id, lat, lon):
    inner_query = {}
    min_radius = 0
    max_radius = 30  # meters??

    inner_query['location'] = {
        "$near": {
            "$geometry": {
                "type": "Point",
                "coordinates": [float(lon),
                                float(lat)]
            },
            "$maxDistance": min_radius * 1000,
            "$minDistance": max_radius * 1000,
        }
    }

    try:
        res = list(Synagogue.objects.raw(inner_query).limit(50))
        return [x for x in res if x['id'] != current_id]
    except Exception as e:
        print(e)


def get_all_synagogues():
    # this should be fetched from db...

    all_synagogues = [{
        "syn_id": 'aaaaa',
        "name": 'bircat aharon',
        "address": 'some address',
        "location": (16.8584426, -99.8595524),  # lat, lon
        "nosach": 'ashkenaz'
    }, {
        "syn_id": 'bbbbb',
        "name": 'bircat aharon hacohen',
        "address": 'some similar address',
        "location": (16.8588865, -99.8599987),  # lat, lon
        "nosach": 'ashkenaz'
    }]

    return all_synagogues


def duplication_score(syna, other_syna):
    duplication_score = 0
    if syna["nosach"] == other_syna["nosach"]:
        duplication_score += 1
    if fuzz.ratio(syna["name"], other_syna["name"]) >= FUZZY_THRESHOLD:
        duplication_score += 1
    if fuzz.ratio(syna["address"], other_syna["address"]) >= FUZZY_THRESHOLD:
        duplication_score += 1
    return duplication_score


if __name__ == "__main__":

    all_synagogues = get_all_synagogues()
    for synagogue in all_synagogues:
        near_by_synagogues = get_near_by_synagogues(synagogue["id"], synagogue["location"][0], synagogue["location"][1])

        for x in near_by_synagogues:
            score = duplication_score(synagogue, x)
            if score:
                print('=======================================')
                print('duplicated might found: score ' + score)
                print('orig: \n' + json.dumps(synagogue, indent=4, sort_keys=True))
                print('suspected: \n' + json.dumps(x, indent=4, sort_keys=True))

    print('done!')
