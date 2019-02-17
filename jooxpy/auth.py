# -*- coding: utf-8 -*-

from .utils import *
from datetime import datetime

import requests
import json
import os


class JooxAuthError(Exception):
    pass


class JooxAuth(object):

    AUTH_JOOX_URL = 'https://api-jooxtt.sanook.com/web-fcgi-bin/web_wmauth'
    DEFAULT_PARAMS = dict(country='id', lang='en')

    def __init__(self, email, password, cachePath="data/"):
        self._email = email
        self._password = password
        if cachePath[-1] != '/':
            cachePath += "/"
        if not os.path.isdir(cachePath):
            os.makedirs(cachePath)
        self._cachePath = cachePath

    def isSessionExpired(self, userInfo):
        now = datetime.today()
        expiredTime = "".join(userInfo["expire_time"].split()[
            1:]).replace("GMT", "")
        expireSession = datetime.strptime(expiredTime, "%d%b%Y%H:%M:%S")
        return expireSession <= now

    def getCachedUserInfo(self):
        with open("{}{}.json".format(self._cachePath, self._email.split("@")[0])) as f:
            userInfo = json.loads(f.read())
        if "expire_time" in userInfo:
            if self.isSessionExpired(userInfo):
                log("Session key is expired, will login again")
                os.remove("{}{}.json".format(
                    self._cachePath, self._email.split("@")[0]))
                log("Remove old user info file!")
                return self.getUserInfo()
            return userInfo
        return None

    def _saveUserInfo(self, userInfo):
        try:
            with open("{}{}.json".format(self._cachePath, self._email.split("@")[0]), "w") as f:
                f.write(json.dumps(userInfo, indent=4))
                log("User info file has been saved!")
        except IOError:
            log("couln't write user info cache to " + self._cachePath)

    def getUserInfo(self):
        if os.path.exists("{}{}.json".format(self._cachePath, self._email.split("@")[0])):
            return self.getCachedUserInfo()
        newPassword = encryptPassword(self._password)
        params = dict(callback="callBackEmailAuth", authtype=2,
                      wxopenid=self._email, password=newPassword)
        params.update(self.DEFAULT_PARAMS)

        r = requests.get(self.AUTH_JOOX_URL, params=params)
        if r.status_code != 200:
            raise JooxAuthError(r.reason)
        userInfo = json.loads(parseJSONP(r.text))
        if "nickname" in userInfo:
            self._saveUserInfo(userInfo)
            return userInfo
        return None
