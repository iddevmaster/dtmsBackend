import math
import os
import random
import string
import uuid
from pytz import timezone as tz
from datetime import date, datetime, timedelta, timezone

from dateutil.relativedelta import relativedelta

from data_common import course_group, vehicle_type

now = datetime.now()  # current date and time
year = now.strftime("%Y")
month = now.strftime("%m")
directory = str(year) + '/' + str(month) + '/'


def rows_limit(value: int):
    if value > 150:
        limit = 150
    else:
        limit = value
    return limit


def isodatetime(datetimeValue):
    date, time = str(datetimeValue).split(" ")
    year, month, day = str(date).split("-")
    timef = str(time).split("+")[0]
    h, m, s = str(timef).split(":")
    tz = timezone(timedelta(hours=7))
    date1 = datetime(int(year), int(month), int(
        day), int(h), int(m), int(s), tzinfo=tz)
#    print(date1.isoformat())
    return date1.isoformat()


def datetimeSplit(datetimeValue, request):
    r = int(request)
    date, time = str(datetimeValue).split(" ")
    year, month, day = str(date).split("-")
    timef = str(time).split(".")[0]
    hour, minute, second = str(timef).split(":")
    if r == 1:
        return (date, timef)
    elif r == 2:
        return (year, month, day)
    elif r == 3:
        return (hour, minute, second)
    return (date, timef)


def minusSecond(time, value):
    fmt = '%H:%M:%S'
    # tf = datetime.strptime('13:30:00', fmt)
    tf = datetime.strptime(time, fmt)
    next = tf + relativedelta(seconds=-int(value))
    r = str(next).split(" ")[1]
    # print(r)
    return r


def plusSecond(time, value):
    fmt = '%H:%M:%S'
    # tf = datetime.strptime('13:30:00', fmt)
    tf = datetime.strptime(time, fmt)
    next = tf + relativedelta(seconds=+int(value))
    r = str(next).split(" ")[1]
    # print(r)
    return r


def today():
    time_format = '%Y-%m-%d'
    date = datetime.now(tz('Asia/Bangkok')).strftime(time_format)
    return date


def ymdtodmy(date):
    # 2022-10-05 to 05/10/2022
    f = str(date)
    year, month, day = f.split("-")
    return day + "/"+month+"/"+year


def histohi(time):
    # 02:30:00 to 02:30
    f = str(time)
    return f[0:5]


def time_difference(starttime, endtime):

    # start time and end time
    start_time = datetime.strptime(str(starttime), "%H:%M:%S")
    end_time = datetime.strptime(str(endtime), "%H:%M:%S")

    # get difference
    delta = end_time - start_time

    sec = delta.total_seconds()
    # print('difference in seconds:', sec)

    # min = sec / 60
    # print('difference in minutes:', min)

    # get difference in hours
    hours = sec / (60 * 60)
    # print('difference in hours:', hours)
    # //ถ้าจำนวนติดลบ ให้คำนวนข้ามคืนเช่น 23.00 - 01.00 เท่ากับ 3 ชั่วโมง
    if hours < 0:
        eph = hours + 24
    else:
        eph = hours
    return eph


def todaytime():
    # time_format = '%Y-%m-%d %H:%M:%S %Z%z'
    time_format = '%Y-%m-%d %H:%M:%S'
    dateTime = datetime.now(tz('Asia/Bangkok')).strftime(time_format)
    return dateTime


def generateId():
    generateId = uuid.uuid4().hex[:24]
    return generateId


def generateShortId():
    # choose from all lowercase letter
    length = 3
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    ranNumber = random.randint(0, 999)
    return str(result_str) + str("{:03d}".format(ranNumber))


def datetimetoint():
    timestamp = int(round(now.timestamp()))
    ranNumber = random.randint(0, 999)
    return str(timestamp) + str(ranNumber)

# print(generateShortId())


def ternaryZero(value):
    if (int(value) <= 0):
        r = 0
    else:
        r = value
    return r


def noneToZero(value):
    if value == None:
        r = 0
    else:
        r = value
    return float(r)


def treeDigit(value):
    number = int(value)
    if number >= 100:
        r = value
    elif number <= 99 and number >= 10:
        r = "0" + str(value)
    elif number <= 9:
        r = "00" + str(value)
    else:
        r = "000"
    return str(r)


def CourseGroupConvert(id):
    id = str(id)
    for k in course_group:
        if id == k["course_group_id"]:
            # course_group_id = k["course_group_id"]
            course_group_name = k["course_group_name"].encode("utf-8")
            return course_group_name

    return False


def vehicle_typeConvert(id):
    id = str(id)
    for k in vehicle_type:
        if id == k["vehicle_type_id"]:
            vehicle_type_name = k["vehicle_type_name"].encode("utf-8")
            return vehicle_type_name

    return False


def subject_typeConvert(val):
    if val == 1:
        subject_type_format = "วิชาบังคับ"
    elif val == 2:
        subject_type_format = "วิชาเพิ่มเติม"
    else:
        subject_type_format = "-"

    return subject_type_format


def subject_learn_typeConvert(val):
    if val == 1:
        subject_learn_type_format = "ทฤษฏี"
    elif val == 2:
        subject_learn_type_format = "ปฏิบัติ"
    else:
        subject_learn_type_format = "-"

    return subject_learn_type_format


def pay_statusConvert(val):
    if val == "RS":
        type_name = "ลูกค้าจองตารางเรียน แต่ยังไม่ชำระเงิน"
    elif val == "PP":
        type_name = "ชำระเงินบางส่วนแต่ยังไม่ครบ"
    elif val == "PA":
        type_name = "ชำระเงินครบทั้งหมดแล้ว"
    else:
        type_name = "-"

    return type_name


def register_statusConvert(val):
    if val == "NR":
        type_name = "สมัครเรียนเสร็จแล้ว"
    elif val == "LC":
        type_name = "การเรียนครบชั่วโมงแล้ว"
    elif val == "RT":
        type_name = "ลงทะเบียนสอบแล้ว"
    else:
        type_name = "-"

    return type_name


def unit_type(val):
    if val == 1:
        type_name = "รายชั่วโมง"
    elif val == 2:
        type_name = "รายวัน"
    elif val == 3:
        type_name = "รายเดือน"
    elif val == 4:
        type_name = "รายคน"
    else:
        type_name = "-"

    return type_name


def amount_type(val):
    if val == 1:
        type_name = "สอน"
    elif val == 2:
        type_name = "คุมสอบ"
    elif val == 3:
        type_name = "กรรมการ"
    elif val == 4:
        type_name = "ประธาน"
    elif val == 5:
        type_name = "เงินเดือน"
    else:
        type_name = "-"

    return type_name


def staff_exam_typeConvert(val):
    if val == 1:
        type_name = "ประธาน"
    elif val == 2:
        type_name = "กรรมการ"
    else:
        type_name = "-"

    return type_name


def ceil(value):
    return math.ceil(value)


def floattoint(value):
    # 10.0 to 10
    # 10.5 to 10.5
    integer, decimal = str(value).split(".")
    if int(decimal) <= 0:
        f = integer
    else:
        f = value
    return f


def create_directory(parent_dir):
    path = os.path.join(parent_dir, directory)
    if not os.path.exists(path):
        os.makedirs(path)
        return str(path)
    return str(path)


# print(create_directory("static/"))
