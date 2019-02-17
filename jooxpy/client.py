# -*- coding: utf-8 -*-
from .utils import encryptPassword

import requests
import base64
import json
import os

""" A simple and thin Python library for the Joox Web API
"""


class Joox(object):

    DEFAULT_PARAMS = dict(country="id", lang="en")

    def __init__(self, auth=None):
        self.prefix = "https://api-jooxtt.sanook.com/web-fcgi-bin"
        self.headers = {
            "Origin": "https://www.joox.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }
        self._auth = auth

    """ HTTP REQUEST """

    def _auth_session(self):
        if self._auth:
            return self._auth.getUserInfo()
        return None

    def _get(self, url, params={}, withAuth=False, headers=None):
        if withAuth:
            auth = self._auth_session()
            params.update(dict(wmid=auth["wmid"],
                               s=auth["session_key"], u=auth["user_type"], c=auth["reg_country"]
                               ))
        params.update(self.DEFAULT_PARAMS)

        if headers is None:
            headers = self.headers
        return requests.get(url, params=params, headers=headers)

    def _post(self, url, params={}, payload={}, files=None, headers=None):
        auth = self._auth_session()
        params = dict(wmid=auth["wmid"],
                      s=auth["session_key"], u=auth["user_type"], c=auth["reg_country"]
                      )
        payload.update({"wmid": auth["wmid"], **self.DEFAULT_PARAMS})
        if headers is None:
            headers = self.headers
        return requests.post(url, params=params, data=json.dumps(payload), headers=headers)

    """ USER JOOX FITURE"""

    def getAllMyPlaylist(self):
        params = dict(reqtype=4, inner=1)

        r = self._get(self.prefix + "/web_getfav",
                      params=params, withAuth=True)
        if r.status_code != 200:
            raise("Failed to get all my playlist request.")
        return json.loads(r.text)

    def getMyPlaylist(self, myPlaylistId):
        params = dict(reqtype=3, inner=1, listid=myPlaylistId)

        r = self._get(self.prefix + "/web_getfav",
                      params=params, withAuth=True)
        if r.status_code != 200:
            raise("Failed to get my playlist request.")
        return json.loads(r.text)

    def createPlaylist(self, playlistName):
        playlistName = base64.b64encode(
            bytes(playlistName, "utf-8")).decode("utf-8")
        
        payload = dict(channel_id=1, from_type=3, items=[
                       dict(gt=0, gl="", mv=0, dv=0, fn=playlistName)])
        
        r = self._post(self.prefix + "/web_fav_add_dir", payload=payload)
        if r.status_code != 200:
            raise("Failed to create playlist request.")
        return json.loads(r.text)

    def removeMyPlaylist(self, myPlaylistId):
        getMyplaylist = self.getMyPlaylist(myPlaylistId)
        dv = getMyplaylist["detail_ver"]
        
        payload = dict(
            items=[dict(gt=myPlaylistId, gl="", mv=dv, dv=dv, fn="")])
        
        r = self._post(self.prefix + "/web_fav_del_dir", payload=payload)
        if r.status_code != 200:
            raise("Failed to remove my playlist request.")
        return json.loads(r.text)

    def addTracksToMyPlaylist(self, songId, myPlaylistId):
        getMyplaylist = self.getMyPlaylist(myPlaylistId)
        dv = getMyplaylist["detail_ver"]

        payload = dict(
            items=[dict(gt=myPlaylistId, gl=songId, mv=dv, dv=dv, fn="")])
        
        r = self._post(self.prefix + "/web_fav_add_song", payload=payload)
        if r.status_code != 200:
            raise("Failed to add track to my playlist request.")
        return json.loads(r.text)

    def removeTracksFromMyPlaylist(self, songId, myPlaylistId):
        getMyplaylist = self.getMyPlaylist(myPlaylistId)
        dv = getMyplaylist["detail_ver"]
        
        payload = dict(
            items=[dict(gt=myPlaylistId, gl=songId, mv=dv, dv=dv, fn="")])
        
        r = self._post(self.prefix + "/web_fav_del_song", payload=payload)
        if r.status_code != 200:
            raise("Failed to remove track to my playlist request.")
        return json.loads(r.text)

    """ PUBLIC JOOX FITURE"""

    def search(self, q, type, limit, offset):
        params = dict(search_input=q, sin=offset, ein=limit, type=type)

        r = self._get(self.prefix + "/web_search",
                      params=params)
        if r.status_code != 200:
            raise("Failed to get search request.")
        return json.loads(r.text)

    def searchTracks(self, q, limit=30, offset=0):
        return self.search(q, None, limit, offset)

    def searchArtists(self, q, limit=30, offset=0):
        return self.search(q, 2, limit, offset)

    def searchAlbums(self, q, limit=30, offset=0):
        return self.search(q, 1, limit, offset)

    def searchPlaylist(self, q, limit=30, offset=0):
        return self.search(q, 3, limit, offset)

    def getPlaylistTaglist(self):
        r = self._get(self.prefix + "/web_tag_list")
        if r.status_code != 200:
            raise("Failed to get playlist taglist request.")
        return json.loads(r.text)

    def getAllPlaylist(self, tagId=None, limit=50, offset=0):
        params = dict(sin=offset, ein=limit, req_type=5, tag_id=tagId)

        r = self._get(self.prefix + "/web_recommend_more", params=params)
        if r.status_code != 200:
            raise("Failed to get all playlist request.")
        return json.loads(r.text)

    def getCategoryPlaylist(self, tagId, limit=50, offset=0):
        return self.getAllPlaylist(tagId, limit, offset)

    def getPlaylist(self, playlistId):
        params = dict(qryDissID=playlistId)

        r = self._get(self.prefix + "/web_get_diss", params=params)
        if r.status_code != 200:
            raise("Failed to get playlist request.")
        return json.loads(r.text)

    def getAllAlbum(self, limit=50, offset=0):
        params = dict(sin=offset, ein=limit, req_type=4)

        r = self._get(self.prefix + "/web_recommend_more", params=params)
        if r.status_code != 200:
            raise("Failed to get all album request.")
        return json.loads(r.text)

    def getAlbumInfo(self, albumId):
        params = dict(all=1, albumid=albumId)

        r = self._get(self.prefix + "/web_get_albuminfo", params=params)
        if r.status_code != 200:
            raise("Failed to get album info request")
        return json.loads(r.text)

    def getHotTracksAndArtists(self):
        r = self._get(self.prefix + "/web_hot_query")
        if r.status_code != 200:
            raise("Failed to get hot tracks request.")
        return json.loads(r.text)

    def getTopChartList(self):
        params = dict(song_num=1)

        r = self._get(self.prefix + "/web_get_toplist", params=params)
        if r.status_code != 200:
            raise("Failed to get top list request.")
        return json.loads(r.text)

    def getTopChart(self, topId=33, limit=100, offset=0):
        params = dict(sin=offset, ein=limit, topid=topId)

        r = self._get(self.prefix + "/web_toplist_detail", params=params)
        if r.status_code != 200:
            raise("Failed to get top charts request.")
        return json.loads(r.text)

    def getAllArtist(self, limit=49, offset=0):
        params = dict(sin=offset, ein=limit, is_all=1)

        r = self._get(self.prefix + "/web_all_singer_list", params=params)
        if r.status_code != 200:
            raise("Failed to get all artist request.")
        return json.loads(r.text)

    def getArtistCategory(self):
        r = self._get(self.prefix + "/web_singer_category", params=params)
        if r.status_code != 200:
            raise("Failed to get artist category request.")
        return json.loads(r.text)

    def getCategoryArtists(self, categoryId, limit=49, offset=0):
        params = dict(sin=offset, ein=limit, category_id=categoryId)

        r = self._get(self.prefix + "/web_all_singer_list", params=params)
        if r.status_code != 200:
            raise("Failed to get category artists request.")
        return json.loads(r.text)

    def getArtistTracks(self, singerId, limit=29, offset=0):
        params = dict(sin=offset, ein=limit, cmd=2, singerid=singerId)

        r = self._get(self.prefix + "/web_album_singer", params=params)
        if r.status_code != 200:
            raise("Failed to get artist tracks request.")
        return json.loads(r.text)

    def getArtistAlbums(self, singerId, limit=29, offset=0):
        params = dict(sin=offset, ein=limit, cmd=1, singerid=singerId)

        r = self._get(self.prefix + "/web_album_singer", params=params)
        if r.status_code != 200:
            raise("Failed to get artist albums request.")
        return json.loads(r.text)

    def getTrackLyric(self, musicId):
        params = dict(musicid=musicId)

        r = self._get(self.prefix + "/web_lyric", params=params)
        if r.status_code != 200:
            raise("Failed to get track lyric request")
        return json.loads(r.text)

    def getTrackInfo(self, songId):
        params = dict(songid=songId)

        r = self._get(self.prefix + "/web_get_songinfo", params=params)
        if r.status_code != 200:
            raise("Failed to get track info request.")
        return json.loads(r.text)
