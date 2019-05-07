def is_nan(num):
    return num != num


def valid_number(phone_number):
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


def check_address(syn):
    if syn["address"] is None:
        return False, "syn no address"

    if syn["address"] == "":
        return False, "syn empty address"

    return True, ""


def check_name(syn):
    if syn["name"] is None:
        return False, "syn no name"

    if syn["name"] == "":
        return False, "syn empty name"

    return True, ""


def check_nosach(syn):
    if syn["nosach"] is None or is_nan(syn["nosach"]):
        syn["nosach"] = ""
        return True

    if isinstance(syn["nosach"], str):
        if syn["nosach"] in ("",
                             "ספרדי - מרוקאי",
                             "ספרדי - החידא",
                             "ספרדי - עדות המזרח",
                             "תימני - בלדי",
                             "תימני - שאמי",
                             "אשכנז",
                             "ספרד",
                             "ארי",
                             "חסידי",
                             "ארץ ישראל",
                             "לפי החזן"):
            return True

    return False, "syn wrong nosach"


def check_phone(syn):
    if syn["phone_number"] is None or is_nan(syn["phone_number"]):
        syn["phone_number"] = []
        return True, ""

    if isinstance(syn["phone_number"], list) is False:
        if isinstance(syn["phone_number"], int):
            syn["phone_number"] = [str(syn["phone_number"])]
        elif isinstance(syn["phone_number"], str):
            syn["phone_number"] = [syn["phone_number"]]
        else:
            return False, "syn wrong phone"

    for index, phone in enumerate(syn["phone_number"]):
        if phone[0] is not "0":
            phone = "0" + phone
        components = phone.split("-")
        if len(components) > 2:
            phone = components[0] + "-" + "".join(components[1:])
        if len(components) == 1:
            phone = phone[0:-7] + "-" + phone[-7:]
        if valid_number(phone):
            syn["phone_number"][index] = phone
            return True, ""
        else:
            return False, "syn wrong phone"

    return True, ""


def check_externals(syn):
    if syn["externals"] is None:
        syn["externals"] = {"mikve": False, "parking": False, "disabled_access": False, "shtiblach": False}
        return True, ""

    for extern in syn["externals"]:
        if extern not in ("mikve", "parking", "disabled_access", "shtiblach"):
            return False, "syn wrong external"
        if syn["externals"][extern] is None:
            syn["externals"][extern] = False
        elif syn["externals"][extern] is not False and syn["externals"][extern] is not True:
            return False, "syn wrong external"

    return True, ""


def check_location(syn):
    if syn["location"] is None:
        return False, "no location"

    if isinstance(syn["location"], list):
        if len(syn["location"]) == 1:
            syn["location"] = syn["location"][0]

    if len(syn["location"]) != 2:
        return False, "wrong location"

    for item in syn["location"]:
        if item not in ("type", "coordinates"):
            return False, "wrong location items"

    if syn["location"]["type"] != "Point":
        syn["location"]["type"] = "Point"

    if isinstance(syn["location"]["coordinates"], list) is False:
        return False, "wrong location coordinates instance"

    if len(syn["location"]["coordinates"]) != 2:
        return False, "wrong location coordinates"

    for cor in syn["location"]["coordinates"]:
        if isinstance(cor, (float, int)) is False:
            return False, "wrong location coordinates types"

    lat = syn["location"]["coordinates"][0]
    lon = syn["location"]["coordinates"][1]

    if lat < 34 or lat > 36:
        return False, "wrong lat"
    if lon < 29 or lon > 33.5:
        return False, "wrong lon"

    return True, ""


def check_synagogue(syn):
    if len(syn) != 10:
        return False, "wrong synagogue model"

    for item in syn:
        if item not in ("name", "address", "location", "nosach", "phone_number", "externals", "minyans", "lessons", "image", "comments"):
            return False, "api does not support key: " + item

    return True, ""


def check_comments(syn):
    if syn["comments"] is None:
        syn["comments"] = ""

    if isinstance(syn["comments"], str) is False:
        return False, "wrong comments type"

    return True, ""


def check_lessons(syn):
    if syn["lessons"] is None:
        syn["lessons"] = []

    if isinstance(syn["lessons"], list) is False:
        return False, "wrong lessons"

    if len(syn["lessons"]) > 0:
        return False, "got lesson!"

    return True, ""


def check_image(syn):
    if syn["image"] is None:
        return True, ""

    return False, "wrong image"


def check_minyans(syn):
    if syn["minyans"] is None:
        syn["minyans"] = []
        return True, ""

    if isinstance(syn["minyans"], list) is False:
        return False, "wrong minyans"

    for minyan in syn["minyans"]:
        if "hour_float" in minyan:
            minyan["startTime"] = minyan["hour_float"]
            del minyan["hour_float"]
        if "last_verified_at" in minyan:
            minyan["lastVerified"] = minyan["last_verified_at"]
            del minyan["last_verified_at"]
        if "hour" in minyan:
            del minyan["hour"]
        if "endTime" in minyan:
            minyan["endTime"] = None

        for prop in minyan:
            if prop not in ("minyan", "startTime", "endTime", "days", "lastVerified"):
                return False, "wrong minyans props"

        if minyan["minyan"] not in ("ערבית", "מנחה", "שחרית"):
            return False, "wrong minyans minyan"

        if minyan["days"]is None:
            return False, "wrong minyans days"

        if isinstance(minyan["days"], list) is False:
            return False, "wrong minyans days"

        if len(minyan["days"]) == 0:
            return False, "wrong minyans days"

        checked_days = []
        for day in minyan["days"]:
            if day not in (1, 2, 3, 4, 5, 6, 7):
                return False, "wrong minyans days"
            if day in checked_days:
                return False, "wrong minyans multiple days"
            checked_days.append(day)
    return True, ""


def validate_synagogue(syn):
    validators = [check_synagogue,
                  check_address,
                  check_name,
                  check_nosach,
                  check_location,
                  check_externals,
                  check_phone,
                  check_comments,
                  check_lessons,
                  check_image,
                  check_minyans]

    for validator in validators:
        check_result = validator(syn)
        if check_result[0] is False:
            return check_result[1]

    return True

