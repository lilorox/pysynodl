import signal
import time

def human_sizeof(num):
    for x in ['B', 'KB', 'MB', 'GB']:
        if(num < 1024.0):
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

class ProgressWatcher(object):
    def __init__(self, ds):
        self.ds = ds
        signal.signal(signal.SIGINT, self._term_signal_catch)
        signal.signal(signal.SIGTERM, self._term_signal_catch)

        self.running = False

    def __del__(self):
        self.stop()

    def _term_signal_catch(self, signum, frame):
        self.stop()

    def stop(self):
        self.running = False

    def start(self):
        self.running = True
        while self.running:
            self.update()
            time.sleep(1)

    def update(self):
        dl_list = self.ds.list()
        fields_max_length = [0, 0, 0, 0, 0, 0]
        titles = [
            "Id",
            "Download",
            "Destination",
            "Status",
            "Downloaded",
            "Total"
        ]

        for dl in dl_list:
            fields_max_length = [
                max(len(dl['id']), len(titles[0]), fields_max_length[0]),
                max(len(dl['title']), len(titles[1]), fields_max_length[1]),
                max(len(dl['additional']['detail']['destination']), len(titles[2]), fields_max_length[2]),
                max(len(dl['status']), len(titles[3]), fields_max_length[3]),
                max(len(human_sizeof(float(dl['additional']['transfer']['size_downloaded']))), len(titles[4]), fields_max_length[4]),
                max(len(human_sizeof(float(dl['size']))), len(titles[5]), fields_max_length[5])
            ]
        format_string = "%%-%ds %%-%ds  %%-%ds  %%-%ds  %%%ds / %%-%ds" % tuple(fields_max_length)

        print(format_string % tuple(titles))
        for dl in dl_list:
            print(
                format_string
                % (
                    dl['id'],
                    dl['title'],
                    dl['additional']['detail']['destination'],
                    dl['status'],
                    human_sizeof(float(dl['additional']['transfer']['size_downloaded'])),
                    human_sizeof(float(dl['size']))
                )
            )

