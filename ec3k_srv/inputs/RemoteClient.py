#!/usr/bin/python
#import signal
import time
import threading
import socket
import select
import json
import traceback
import logging


class RemoteClient:
    def __init__(self, name, sendStringCB, config, errorCallback):
        self.wantStop = True
        self.callback = sendStringCB
        self.errorCallback = errorCallback
        self.address = config["remote-address"]
        self.port = config.getint("remote-port")
        self.sock = None
        self.Threads = []
        # self.socket_list = []
        self.chunks = []
        self.logger = logging.getLogger(name)


    def _remoteConnect(self):
        # setup incoming socket
        try:
            self.sock = socket.create_connection((self.address, self.port),
                                                 timeout=3)
            self.logger.info("Connected to remote: {}:{}".format(
                self.address, self.port))
            # Set keepalive
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 5)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)
        except socket.error as e:
            self.logger.error("Failed to connect: {}".format(e))
            time.sleep(5)
        except Exception:
            self.logger.error("Failed to setup remote listener: {}".format(
                traceback.format_exc()))
            self.sock = None
            time.sleep(5)


    def start(self):
        # ""Start the remote client""
        assert self.wantStop
        self.wantStop = False

        self.threads = []
        try:
            remoteClientThread = threading.Thread(target=self._process_data)
            self.threads.append(remoteClientThread)
            remoteClientThread.start()
        except:
            self.logger.error("Remote Connection Start failed: " + sys)
            return
        self.logger.info("Started remote client thread")


    def stop(self):
        # ""Stop the remote client thread""
        assert not self.wantStop == True
        self.wantStop = True

        # stop threads
        for thread in self.threads:
            thread.join()

        # close socket, but we are not interested in exceptions
        try:
            self.sock.close()
        except:
            pass


    def _appendData(self, newChunk):
        # Add received data to the list
        self.logger.debug("Received data")
        self.logger.log(5, newChunk)
        self.chunks.extend(newChunk.splitlines())

        while len(self.chunks) > 0:
            # sync to start of a json object
            if self.chunks[0] != "{":
                self.logger.debug("not a start of a new message: ".join(
                    self.chunks[0]))
                del self.chunks[0]
                continue
            else:
                self.logger.debug(
                    "Found start of message, have {} lines".format(
                        len(self.chunks)))
                self.nrReceived = self.nrReceived + 1
                self._processMessage()


    def _processMessage(self):
        for i, line in enumerate(self.chunks):
            if line == "}":
                json_message = "\n".join(self.chunks[0:i + 1]) + "\n"
                # Verify that the message is valid json
                try:
                    message = json.loads(json_message)
                except:  # json.JSONDecodeError:
                    self.logger.warning(
                        "Not a valid json object, skipping {}".format(
                            json_message))
                    del self.chunks[0:i + 1]
                    break
                self.callback(json_message)
                self.nrSent = self.nrSent + 1
                self.logger.debug("message sent")
                del self.chunks[0:i + 1]
                break
            else:
                if i > 1 and self.chunks[i] == "{":
                    # start of a new message, delete and resync
                    self.logger.info(
                        "Received incomplete message, delete it and continue ({} lines: {})"
                        .format(i + 1, self.chunks[0:i + 1]))
                    del self.chunks[0:i]
                    break


    def _process_data(self):
        self.nrReceived = 0
        self.nrSent = 0
        startTime = time.time()

        while not self.wantStop:
            if time.time() - startTime > 60:
                self.logger.info(
                    "Total messages received: {}, sent: {}".format(
                        self.nrReceived, self.nrSent))
                startTime = time.time()
            if self.sock is None:
                self._remoteConnect()
            else:
                readable, writable, errored = select.select([self.sock], [],
                                                            [self.sock], 1)
                for s in readable:
                    chunk = s.recv(4096)
                    if len(chunk) == 0:
                        # Socket is closed!
                        self.logger.info(
                            "Socket to remote is closed, will reconnect")
                        try:
                            s.close()
                            self.sock = None
                        except:
                            continue
                    self.logger.debug("Received message from remote")
                    self.logger.detailed("{}".format(chunk))
                    self._appendData(chunk)
                    del chunk

                for e in errored:
                    try:
                        self.sock = None
                        e.sock.close()
                    except:
                        pass
