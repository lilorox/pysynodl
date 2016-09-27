import logging
import requests
from .exceptions import SynologyAuthenticationException

class API:
    def __init__(self, host, user, password, session_name, port=5000, use_https=False):
        self.host = host
        self.user = user
        self.password = password
        self.port = port

        self.scheme = "http://"
        if use_https:
            self.scheme = "https://"

        self.base_url = "%s%s:%s/webapi" % (self.scheme, self.host, str(self.port))

        self.auth_api_version = 2
        self.dl_api_version = 1
        self.session_id = ''
        self.session_name = session_name

        self.login()

    def __del__(self):
        self.logout()

    def login(self):
        res = self.req(
            "%s/auth.cgi?api=SYNO.API.Auth&version=%d&method=login&account=%s&passwd=%s&session=%s&format=sid"
            % (
                self.base_url,
                self.auth_api_version,
                self.user,
                self.password,
                self.session_name
            )
        )
        if not "success" in res or not res["success"]:
            msg = "Cannot login"
            if "error" in res and "code" in res["error"]:
                msg += " (error code: %d)" % res["error"]["code"]
            raise SynologyAuthenticationException(msg)
        self.session_id = res['data']['sid']

    def logout(self):
        res = self.req(
            "%s/auth.cgi?api=SYNO.API.Auth&version=%d&method=logout&session=%s&_sid=%s"
            % (
                self.base_url,
                self.auth_api_version,
                self.session_name,
                self.session_id
            )
        )
        if not "success" in res or not res["success"]:
            msg = "Cannot login"
            if "error" in res and "code" in res["error"]:
                msg += " (error code: %d)" % res["error"]["code"]
            raise SynologyAuthenticationException(msg)

    def req(self, url, params=None):
        logging.debug('GET: ' + url)
        r = requests.get(url, params=params)
        return r.json()

    def req_post(self, url, data=None):
        logging.debug('POST: ' + url)
        r = requests.post(url, data=data)
        return r.json()
