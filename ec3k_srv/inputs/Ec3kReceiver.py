#!/usr/bin/python
import time
import threading
import json
import logging
import configparser
import ec3k


class Ec3kWrapper(ec3k.EnergyCount3K):
    def _log(self, msg):
        assert (hasattr(self, "logger"))
        self.logger.detailed(msg)

    def setLogger(self, name):
        self.logger = logging.getLogger(name)


class Ec3kReceiver:
    def __init__(self, name, sendString, config, errorCallback):
        self.logger = logging.getLogger(name)
        self.loggerPath = name
        self.wantStop = True
        self.sendString = sendString
        self.errorCallback = errorCallback
        self.thread = None

        # Parse configuration
        self.device = config.getint("device")
        self.frequency = config.getfloat("frequency")
        self.rescan = config.getboolean("rescan")
        self.interval = config.getint("interval")


    def start(self):
        # ""Start the ec3k receiver""
        assert self.wantStop
        self.wantStop = False

        self.thread = None
        self.thread = threading.Thread(target=self._processData)
        self.thread.start()
        self.nrReceived = 0
        self.nrSent = 0


    def stop(self):
        # ""Stop the ec3k receiver thread""
        assert not self.wantStop == True
        self.wantStop = True

        # stop thread
        self.thread.join()
        self.logger.info("Total messags received: {}, Total sent: {}".format(
            self.nrReceived, self.nrSent))


    def _processStatus(self, status):
        try:
            self.nrReceived = self.nrReceived + 1
            outputString = json.dumps(
                {
                    "id": hex(status.id)[2:],
                    "data": {
                        "time_total": status.time_total,
                        "time_on": status.time_on,
                        "energy": status.energy,
                        "power_current": status.power_current,
                        "power_max": status.power_max,
                        "reset_counter": status.reset_counter
                    }
                },
                indent=2) + "\n"
        except Exception as e:
            self.logger.error(
                "Error converting status object to string: {}".format(e))
            return

        try:
            self.logger.debug("Sending status string")
            self.logger.detailed("{}".format(outputString))
            self.sendString(outputString)
            self.nrSent = self.nrSent + 1
        except Exception as e:
            self.logger.error("Failed to send status {}".format(e))


    def _processData(self):
        try:
            ec3kReceiver = Ec3kWrapper(callback=self._processStatus,
                                       freq=self.frequency,
                                       device=self.device)
            ec3kReceiver.setLogger(self.loggerPath + ".ec3k")
            ec3kReceiver.start()
        except Exception as e:
            self.logger.error("Cannot start ec3kReceiver {}".format(e))
            self.errorCallback(self.name, "".format(e))

        startTime = time.time()
        while not self.wantStop:
            if time.time() - startTime > self.interval:
                self.logger.info("Noise level: %.1f dB" %
                                 (ec3kReceiver.noise_level, ))
                self.logger.info("Messages received: {}, sent: {}".format(
                    self.nrReceived, self.nrSent))
                if self.rescan:
                    self.logger.info('Start a (re)scan....')
                    ec3kReceiver.stop()
                    ec3kReceiver.start()
                startTime = time.time()
            time.sleep(1)
        ec3kReceiver.stop()
