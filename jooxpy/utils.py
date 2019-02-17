# -*- coding: utf-8 -*-
from datetime import datetime

import hashlib
import json


def encryptPassword(password):
    md5 = hashlib.md5()
    old_password = password.encode('utf-8')
    md5.update(old_password)
    new_password = md5.hexdigest()
    return new_password


def parseJSONP(data_jsonp):
    data_json = data_jsonp.split('(')[1].strip(')')
    return data_json


def log(text):
    print("[%s] %s" % (str(datetime.now()), text))
