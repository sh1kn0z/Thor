from CONST import COMMANDS
import signal
import socket
from queue import Queue
import logging


queue = Queue()

class Server():

    def __init__(self):
        self.host = ''
        self.port = 9999
        self.socket = None
        self.all_connections = []
        self.all_ip_addresses = []

    def help(self):
        for cmd, description in COMMANDS.items():
            print(f'{cmd}:\t{description}')

    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)


    def handle_command(self):
        while True:
            cmd = input('> ')
            if cmd == 'clients':
                self.show_clients()
            elif 'client' in cmd:
                try:
                    client_id = int(cmd.split(' ')[-1])
                except ValueError:
                    print('Enter a valid index (integer)')
                client_id, connection = self.get_target(client_id)

    def show_clients(self):
        print('ID\t-\tClient Addresses')
        for i, client in enumerate(self.all_ip_addresses):
            print(f'{i}\t-\t{client}')

    def connect_to_target(self, id):
        try:
            connection = self.all_connections[id]
        except IndexError:
            print('Not a valid selection')
            return None, None
        print(f'Connected to {self.all_ip_addresses[id]}')
        logging.info(f'Connected to {self.all_ip_addresses[id]}')
        return id, connection

def main():
    logging.basicConfig(filename='Thor_logs.log',
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        level=logging.INFO)