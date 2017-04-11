import os
import ssl
import subprocess
import urllib2

class WPTServer(object):
    base_url = 'https://web-platform.test:8443'

    def __init__(self, wpt_root):
        self.wpt_root = wpt_root

    def start(self):
        self.devnull = open(os.devnull, 'w')
        self.proc = subprocess.Popen(
            [os.path.join(self.wpt_root, 'serve')],
            stdout=self.devnull,
            stderr=self.devnull,
            cwd=self.wpt_root)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        context.check_hostname = False

        while True:
            try:
                urllib2.urlopen(self.base_url, timeout=1, context=context)
                break
            except urllib2.URLError as e:
                pass

    def stop(self):
        self.proc.kill()
        self.proc.wait()
        self.devnull.close()

    def url(self, abs_path):
        return self.base_url + '/' + os.path.relpath(abs_path, self.wpt_root)
