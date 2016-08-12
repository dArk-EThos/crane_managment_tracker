from ServiceManager import *
from DatabaseManager import *
import enum

class MyEnum(enum.Enum):
    upper = "upper"
    lower = "lower"

def readfile():

    import os
    retStr = ""

    file = open('/Users/bednarchris1/Documents/scott_app/data.csv', 'r')

    for line in file.readlines():

        tempLines = line.split(",")

        tempLines[0] = tempLines[0].replace("~", ",")
        tempLines[1] = tempLines[1].replace("~", ",")
        tempLines[2] = tempLines[2].replace("~", ",")
        tempLines[3] = tempLines[3].replace("~", ",")
        tempLines[4] = tempLines[4].replace("~", ",")
        tempLines[5] = tempLines[5].replace("~", ",")

        name = tempLines[0] if tempLines[0] != "null" else None
        operation = tempLines[3] if tempLines[3] != "null" else None
        interval = tempLines[2] if tempLines[2] != "null" else None
        crane_id = 1
        engine_type = tempLines[1].lower()
        capacity_gallons = tempLines[4] if tempLines[4] != "null" else None
        capacity_liters = tempLines[5] if tempLines[5] != "null" else None

        newService = Service(name, operation, interval, crane_id, engine_type, capacity_gallons, capacity_liters)

        db.session.add(newService)
        db.session.commit()

    file.close()

    return "done."