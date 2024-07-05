from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

logging.basicConfig(level=logging.INFO)

# Mengubah class ProcessTheClient menjadi function
def ProcessTheClient(connection, address):
    rcv = ""
    while True:
        try:
            data = connection.recv(32)
            if data:
                d = data.decode()
                rcv = rcv + d
                if rcv[-2:] == '\r\n':
                    logging.info("data dari client: {}".format(rcv))
                    hasil = httpserver.proses(rcv)
                    hasil = hasil + "\r\n\r\n".encode()
                    logging.info("balas ke client: {}".format(hasil))
                    connection.sendall(hasil)
                    rcv = ""
                    connection.close()
                    return
            else:
                break
        except OSError as e:
            logging.error("OSError: {}".format(e))
            break
        except Exception as e:
            logging.error("Exception: {}".format(e))
            break
    connection.close()
    return

def Server(portnumber=8889):
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', portnumber))
    my_socket.listen(1)

    with ProcessPoolExecutor(max_workers=20) as executor:
        while True:
            try:
                connection, client_address = my_socket.accept()
                logging.info("connection from {}".format(client_address))
                p = executor.submit(ProcessTheClient, connection, client_address)
                the_clients.append(p)
                # Menampilkan jumlah process yang sedang aktif
                jumlah = ['x' for i in the_clients if i.running()]
                logging.info("Jumlah proses aktif: {}".format(len(jumlah)))
            except KeyboardInterrupt:
                logging.info("Server dihentikan oleh pengguna")
                break
            except Exception as e:
                logging.error("Exception: {}".format(e))
                break

    my_socket.close()

def main():
    portnumber = 8000
    try:
        portnumber = int(sys.argv[1])
    except Exception as e:
        logging.warning("Menggunakan port default: {}. Error: {}".format(portnumber, e))
    Server(portnumber)

if __name__ == "__main__":
    main()
