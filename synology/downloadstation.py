from .api import API

class DownloadStation(API):

    def __init__(self, host, user, password, port=5000, use_https=False):
        super(DownloadStation, self).__init__(host, user, password, "DownloadStation", port, use_https)
        self.cgi = "DownloadStation/task.cgi"
        self.dl_api_version = 1

    def list(self):
        res = self.req(
            "%s/%s?api=SYNO.DownloadStation.Task&version=%d&method=list&_sid=%s"
            % (
                self.base_url,
                self.cgi,
                self.dl_api_version,
                self.session_id
            )
        )
        return res['data']['tasks']

    def get_details(self, download_ids):
        res = self.req(
            "%s/%s?api=SYNO.DownloadStation.Task&version=%d&method=getinfo&id=%s&additional=detail,transfer&_sid=%s"
            % (
                self.base_url,
                self.cgi,
                self.dl_api_version,
                download_ids,
                self.session_id
            )
        )
        return res['data']['tasks']

    def add(self, download_url, destination=None, user=None, password=None):
        data = {
            "api": "SYNO.DownloadStation.Task",
            "uri": download_url,
            "version": self.dl_api_version,
            "method": "create",
            "_sid": self.session_id
        }

        if user is not None and password is not None:
            data["username"] = user
            data["password"] = password

        if destination is not None:
            data["destination"] = destination

        res = self.req_post(
            "%s/%s" % (self.base_url, self.cgi),
            data
        )
        return res
