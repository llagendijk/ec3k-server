#!/usr/bin/python
import time
import threading
import Queue
import select
import json
import logging
import configparser
import paho.mqtt.client as mqtt
from enum import Enum


class MqttOutput:
    def __init__(self, name, my_queue, config, errorCallback):
        self.wantStop = True
        self.name = name
        self.errorCallback = errorCallback
        self.queue = my_queue
        self.mqttServer = config["mqtt-server"]
        self.mqttPort = config.getint("mqtt-port")
        self.mqttUsername = config["username"]
        self.mqttPassword = config["password"]
        self.mqttClientId = config["clientid"]
        self.mqttTopic = config["topic"]
        self.socket_list = []
        self.logger = logging.getLogger(name)

    def start(self):
        self.logger.info("Starting MQTT mqttClient thread: " +
                         self.mqttServer + " " + str(self.mqttPort))
        # ""Start the MQTT output""
        assert self.wantStop
        self.wantStop = False
        self.nrSent = 0
        self.nrPublished = 0
        self.connected = False
        self.connectionRecoverable = True

        self.mqttClient = mqtt.Client(self.mqttClientId,
                                      clean_session=True,
                                      userdata=self)
        if self.mqttUsername != "":
            self.mqttClient.username_pw_set(self.mqttUsername,
                                            self.mqttPassword)
            logging.debug("Using mqtt username: %s, password: %s",
                          self.mqttUsername, self.mqttPassword)

        mqttLogger = logging.getLogger(self.name + ".mqtt")
        self.mqttClient.enable_logger(mqttLogger)
        self.mqttClient.on_connect = self._onConnect
        self.mqttClient.on_disconnect = self._onDisconnect
        self.mqttClient.on_publish = self._onPublish
        self.logger.debug("start connect")
        self.mqttClient.connect(self.mqttServer, self.mqttPort)
        self.logger.debug("started connect, start loop")
        self.mqttClient.loop_start()
        self.logger.debug("started loop")

        self.mqttClientThread = threading.Thread(target=self._process_data)
        self.mqttClientThread.start()

    def stop(self):
        # ""Stop the MQTT mqttClient thread""
        assert not self.wantStop == True
        self.wantStop = True

        # stop threads
        self.mqttClientThread.join()

        # close MQTT connection
        try:
            self.mqttClient.disconnect()
            self.mqttClient.loop_stop()
        except Exception as e:
            self.logger.error(
                "Exception at closing MQTT connection: {}".format(e))
        self.logger.info("Status: Sent {} messages, published {}".format(
            self.nrSent, self.nrPublished))

    def _onConnect(self, client, userdata, flags, rc):
        # rc: 0: Connection successful
        #     1: Connection refused - incorrect protocol version
        #     2: Connection refused - invalid mqttClient identifier
        #     3: Connection refused - server unavailable
        #     4: Connection refused - bad username or password
        #     5: Connection refused - not authorised
        #     6-255: Currently unused.
        if rc == 0:
            self.connected = True
            self.ConnectionRecoverable = False
            self.reason = "Connected"

        elif rc == 3:
            self.connected = False
            self.connectionRecoverable = True
            self.reason = "server unavailable"
        else:
            self.connected = False
            self.connectionFailed = True
            if rc == 2:
                self.reason = "invalid mqttClient identifier"
            elif rc == 4:
                self.reason = "bad username or password"
            elif rc == 5:
                self.reason = "not authorised"
            else:
                self.reason = "Unknown error"

    def _onDisconnect(self, client, userdata, rc):
        # rc : MQTT_ERR_SUCCESS (0), he callback was called in response to a disconnect() call.
        #      If any other value the disconnection was unexpected
        self.connected = False
        self.connectionRecoverable = True

    def _onPublish(self, client, userdata, mid):
        self.nrPublished = self.nrPublished + 1

    def _process_data(self):
        self.logger.debug("Starting data processing thread")
        startTime = time.time()
        while not self.wantStop:
            if not self.connected and not self.connectionRecoverable:
                # Do something to stop
                self.errorCallback(self.name, "MQTT failed")
                break
            else:
                # get item from queue
                try:
                    if time.time() - startTime > 60:
                        self.logger.info(
                            "Status: Sent {} messages, published {}".format(
                                self.nrSent, self.nrPublished))
                        startTime = time.time()
                    outputString = self.queue.get(True, 1)
                    if (self.connected):
                        self.logger.debug("Sending message")
                        self.logger.detailed("{}".format(outputString))
                        jsonObject = json.loads(outputString)
                        id = jsonObject["id"]
                        data = jsonObject["data"]
                        toTopic = json.dumps(data)
                        self.mqttClient.publish(self.mqttTopic.format(id),
                                                toTopic)

                        self.nrSent = self.nrSent + 1
                    self.queue.task_done()
                except Queue.Empty:
                    time.sleep(1)
                    continue
                except Exception as e:
                    self.errorCallback(self.name, "{}".format(e))
                    break
        self.logger.debug("Exited _process_data")
