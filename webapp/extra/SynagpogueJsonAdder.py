import json
from pymongo import MongoClient
from extra.SynagogueValidator import validate_synagogue
from extra.SynagogueDuplicateFinder import find_duplicates

client = MongoClient('mongodb://startach:gG123456@ds235022.mlab.com:35022/jewish_world')

db = client['jewish_world']

synagogues_db = db['synagogues']

good_synagogues = []
bad_synagogues = []


def prepare_json(text):
    split_text = text.split("\n")
    split_text = [row for row in split_text
                  if row != '' and row.find("\"_id\"") == -1]
    split_text = [row if (index == (len(split_text) - 1) or row != '}') else '},'
                  for index, row in enumerate(split_text)]
    split_text = [row if row.find("NumberInt(") == -1
                  else row.replace('NumberInt(', '').replace(')', '')
                  for index, row in enumerate(split_text)]
    split_text = [row if row.find("BinData(") == -1
                  else "    \"image\" : null,"
                  for index, row in enumerate(split_text)]

    return "[" + "\n".join(split_text) + "]"


def fix_model(synagogues):
    for syn in synagogues:
        if "nosahc" in syn:
            syn["nosach"] = syn["nosahc"]
            del syn["nosahc"]


def fix_to_db():
    with open('allSynagogues.json') as file:
        text = file.read()
    synagogues_json = prepare_json(text)
    all_synagogues = json.loads(synagogues_json)

    for syn in all_synagogues:
        valid = validate_synagogue(syn)
        if valid is True:
            good_synagogues.append(syn)
        else:
            bad_synagogues.append((valid, syn))


fix_to_db()

uniq, dup = find_duplicates(good_synagogues)

some_variable = 1  # for debug brake point
