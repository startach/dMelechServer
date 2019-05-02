from pymongo import MongoClient
import json
import mpu
import logging, sys
from googletrans import Translator

client = MongoClient('mongodb://startach:gG123456@ds235022.mlab.com:35022/jewish_world')

db = client['jewish_world']

synagogues_db = db['synagogues']

dafuk = []

synagogues = []

phones = []

locations = []


def check_address(syn):
    if syn["address"] is None:
        dafuk.append(("syn no address", syn))
        return False

    if syn["address"] == "":
        dafuk.append(("syn empty address", syn))
        return False

    # translator = Translator()
    #
    # syn["address"] = translator.translate(syn["address"], dest="he").text

    return True


def check_name(syn):
    if syn["name"] is None:
        dafuk.append(("syn no name", syn))
        return False

    if syn["name"] == "":
        dafuk.append(("syn empty name", syn))
        return False

    # translator = Translator()
    #
    # syn["name"] = translator.translate(syn["name"], dest="he").text

    return True


def isNaN(num):
    return num != num


def check_nosach(syn):
    if syn["nosach"] is None or isNaN(syn["nosach"]):
        syn["nosach"] = ""
        return True

    if isinstance(syn["nosach"], str):
        return True

    dafuk.append(("syn wrong nosach", syn))
    return False


def validNumber(phone_number):
    components = phone_number.split("-")
    if len(components) != 2:
        return False

    if len(components[0]) not in (2, 3):
        return False
    if len(components[1]) != 7:
        return False

    for comp in components:
        if comp.isalnum() is False:
            return False

    return True


def check_phone(syn):
    if syn["phone_number"] is None or isNaN(syn["phone_number"]):
        syn["phone_number"] = []
        return True

    if isinstance(syn["phone_number"], list) is False:
        if isinstance(syn["phone_number"], int):
            syn["phone_number"] = str(syn["phone_number"])
        if isinstance(syn["phone_number"], str):
            components = syn["phone_number"].split("-")
            if len(components) > 2:
                syn["phone_number"] = components[0] + "-" + "".join(components[1:])
            if len(components) == 1:
                syn["phone_number"] = syn["phone_number"][0:-7] + "-" + syn["phone_number"][-7:]

            if validNumber(syn["phone_number"]):
                syn["phone_number"] = [syn["phone_number"]]
                return True
            else:
                dafuk.append(("syn wrong phone", syn))
                return False
        else:
            dafuk.append(("syn wrong phone", syn))
            return False

    for phone in syn["phone_number"]:
        components = syn["phone_number"].split("-")
        if len(components) > 2:
            syn["phone_number"] = components[0] + "-" + "".join(components[1:])
        if len(components) == 1:
            syn["phone_number"] = syn["phone_number"][0:-7] + "-" + syn["phone_number"][-7:]

        if validNumber(phone) is False:
            dafuk.append(("syn wrong phone", syn))
            return False

    return True


def check_externals(syn):
    if syn["externals"] is None:
        syn["externals"] = {"mikve": False, "parking": False, "disabled_access": False, "shtiblach": False}
        return True

    for extern in syn["externals"]:
        if extern not in ("mikve", "parking", "disabled_access", "shtiblach"):
            dafuk.append(("syn wrong external", syn))
            return False
        if syn["externals"][extern] is None:
            syn["externals"][extern] = False
        elif syn["externals"][extern] is not False and syn["externals"][extern] is not True:
            dafuk.append(("syn wrong external", syn))
            return False

    return True


def check_location(syn):
    if syn["location"] is None:
        dafuk.append(("wrong location", syn))
        return False

    if isinstance(syn["location"], list):
        if len(syn["location"]) == 1:
            syn["location"] = syn["location"][0]
        else:
            dafuk.append(("wrong location", syn))

    if len(syn["location"]) != 2:
        dafuk.append(("syn wrong location", syn))
        return False

    for item in syn["location"]:
        if item not in ("type", "coordinates"):
            dafuk.append(("syn wrong location items", syn))
            return False

    if syn["location"]["type"] != "Point":
        dafuk.append(("syn wrong location type", syn))
        return False

    if len(syn["location"]["coordinates"]) != 2:
        dafuk.append(("syn wrong location coordinates", syn))
        return False
    if isinstance(syn["location"]["coordinates"], list) is False:
        dafuk.append(("syn wrong location coordinates instance", syn))
        return False

    for cor in syn["location"]["coordinates"]:
        if isinstance(cor, (float, int)) is False:
            dafuk.append(("syn wrong location coordinates types", syn))
            return False

    lat = syn["location"]["coordinates"][0]
    lon = syn["location"]["coordinates"][1]

    if lat < 34 or lat > 36:
        dafuk.append(("wrong lat", syn))
        return False
    if lon < 29 or lon > 33.5:
        dafuk.append(("wrong lon", syn))
        return False

    return True


def check_synagogue(syn):
    if len(syn) != 10:
        dafuk.append(syn)
        return False

    for item in syn:
        if item not in ("name", "address", "location", "nosach", "phone_number", "externals", "minyans", "lessons", "image", "comments"):
            dafuk.append(("wrong item: " + item, syn))
            return False

    return True


def check_comments(syn):
    if syn["comments"] is None:
        syn["comments"] = ""

    if isinstance(syn["comments"], str) is False:
        dafuk.append(("wrong comments", syn))
        return False

    return True


def check_lessons(syn):
    if syn["lessons"] is None:
        syn["lessons"] = []

    if isinstance(syn["lessons"], list) is False:
        dafuk.append(("wrong lessons", syn))
        return False

    if len(syn["lessons"]) > 0:
        dafuk.append(("got lesson!", syn))
        return False

    return True


def check_image(syn):
    if syn["image"] is None:
        return True

    dafuk.append(("wrong image", syn))
    return False


def check_minyans(syn):
    if syn["minyans"] is None:
        syn["minyans"] = []
        return True

    if isinstance(syn["minyans"], list) is False:
        dafuk.append(("wrong minyans", syn))
        return False

    for minyan in syn["minyans"]:
        for prop in minyan:
            if prop not in ("minyan", "hour", "hour_float", "days", "last_verified_at"):
                dafuk.append(("wrong minyans props", syn))
                return False

        if minyan["minyan"] not in ("ערבית", "מנחה", "שחרית"):
            dafuk.append(("wrong minyans minyan", syn))
            return False

        if minyan["days"]is None:
            dafuk.append(("wrong minyans days", syn))
            return False

        if isinstance(minyan["days"], list) is False:
            dafuk.append(("wrong minyans days", syn))
            return False

        if len(minyan["days"]) == 0:
            dafuk.append(("wrong minyans days", syn))
            return False

        for day in minyan["days"]:
            if day not in (1, 2, 3, 4, 5, 6, 7):
                dafuk.append(("wrong minyans days", syn))
                return False

        minyan["startTime"] = minyan["hour_float"]
        minyan["lastVerified"] = minyan["last_verified_at"]
        del minyan["hour_float"]
        del minyan["last_verified_at"]

        minyan["endTime"] = None
        del minyan["hour"]


def fix_to_db():
    with open('allSynagogues.json') as file:
        text = file.read()
        split_text = text.split("\n")

        split_text = [row for index, row in enumerate(split_text) if row != ''
                      and row.find("\"_id\"") == -1]

        split_text = [row if (index == (len(split_text) - 1) or row != '}') else '},'
                      for index, row in enumerate(split_text)]

        split_text = [row if row.find("NumberInt(") == -1
                      else row.replace('NumberInt(', '').replace(')', '')
                      for index, row in enumerate(split_text)]

        split_text = [row if row.find("BinData(") == -1
                      else "    \"image\" : null,"
                      for index, row in enumerate(split_text)]

        all_synagogues = json.loads("[" + "\n".join(split_text) + "]")

        for syn in all_synagogues:
            if "nosahc" in syn:
                syn["nosach"] = syn["nosahc"]
                del syn["nosahc"]

        for syn in all_synagogues:
            if check_synagogue(syn) is False:
                continue

            if check_address(syn) is False:
                continue

            if check_name(syn) is False:
                continue

            if check_nosach(syn) is False:
                continue

            if check_location(syn) is False:
                locations.append(syn["location"]["coordinates"])
                continue

            if check_externals(syn) is False:
                continue

            if check_phone(syn) is False:
                phones.append(syn["phone_number"])
                continue

            if check_comments(syn) is False:
                continue

            if check_lessons(syn) is False:
                continue

            if check_image(syn) is False:
                continue

            if check_minyans(syn) is False:
                continue

            synagogues.append(syn)


def dist(loc1, loc2):
    lat1 = loc1["coordinates"][0]
    lon1 = loc1["coordinates"][1]

    lat2 = loc2["coordinates"][0]
    lon2 = loc2["coordinates"][1]

    return mpu.haversine_distance((lat1, lon1), (lat2, lon2)) * 1000


def is_different(syn1, syn2):
    if syn1["name"] != syn2["name"]:
        return True
    if dist(syn1["location"], syn2["location"]) > 10:
        return True

    return False


def is_uniq(syn, uniq, index):
    a = index
    if index % 100 == 0:
        logging.debug(index)
    return all([is_different(syn, syn2) for syn2 in uniq])


def find_duplicates():
    dup = []
    uniq = []
    [uniq.append(syn) if is_uniq(syn, uniq, index) else dup.append(syn) for index, syn in enumerate(synagogues)]

    x = 1


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

fix_to_db()

find_duplicates()
