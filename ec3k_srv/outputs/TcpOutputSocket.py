#!/usr/bin/python
import time
import threading
import Queue
import socket
import select
import json
import logging
import configparser


class TcpOutputSocket:
    def __init__(self, name, my_queue, config, errorCallback):
        self.wantStop = True
        self.errorCallback = errorCallback
        self.queue = my_queue
        self.address = config["listen-address"]
        self.port = config.getint("listen-port")
        self.socket_list = []
        self.logger = logging.getLogger(name)


    def start(self):
        assert self.wantStop
        self.wantStop = False
        self.nrReceived = 0
        self.nrSent = 0

        # ""Start the TCP server""
        self.logger.info("Starting TCP listener: {}:{}".format(self.address, self.port))
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.address, self.port))
            self.sock.listen(5)
        except Exception as e:
            raise IOError("Failed to setup TCP server: {}".format(e))

        self.threads = []
        tcpServer_thread = threading.Thread(target=self._process_data)
        self.threads.append(tcpServer_thread)
        tcpServer_thread.start()


    def stop(self):
        # ""Stop the tcp-server thread""
        assert not self.wantStop == True
        self.wantStop = True

        # stop threads
        for thread in self.threads:
            thread.join()
        self.logger.info("Received messages: {}, sent {}".format(
            self.nrReceived, self.nrSent))

        # close outgoing sockets, but we are not interested in exceptions
        try:
            for s in self.socket_list:
                s.close()
                self.socket_list.remove(s)
                # close listener socket
                self.sock.close()
        except:
            pass
        self.logger.info("Received messages: {}, sent {}".format(
            self.nrReceived, self.nrSent))


    def _process_data(self):
        startTime = time.time()
        self.logger.debug("Starting data processing thread")
        self.read_list = [self.sock]
        while self.wantStop == False:
            # we do not want select to block
            # TODO: read and discard received input on socket
            readable, writable, errored = select.select(
                self.read_list, self.socket_list, self.socket_list, 1)

            for s in readable:
                client_socket, address = self.sock.accept()
                self.logger.info("New connection from {}".format(address))
                self.socket_list.append(client_socket)

            for e in errored:
                try:
                    self.socket_list.remove(e)
                    e.close()

                except:
                    pass

            # Send json out: get item from queue
            # we use the wait on the queue to avoid busy looping
            try:
                output_string = self.queue.get(True, 1)
                self.nrReceived = self.nrReceived + 1

                self.logger.debug("sending message")
                self.logger.detailed("{}".format(output_string))
                for w in writable:
                    try:
                        w.send(output_string)
                        self.nrSent = self.nrSent + 1
                    except Exception as e:
                        self.logger.info(
                            "Cannot write to socket, closing this connection: "
                            .format(e))
                        self.socket_list.remove(w)
                        try:
                            w.close()
                        except Exception as e:
                            self.logger.error(
                                "Exception on socket cleanup! :{}".format(e))
                self.queue.task_done()
            except Queue.Empty:
                pass
            if time.time() - startTime > 60:
                self.logger.info("Received messages: {}, sent {}".format(
                    self.nrReceived, self.nrSent))
                startTime = time.time()
