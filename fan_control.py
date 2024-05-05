#!/usr/bin/env python3

import time
import logging
from pynvml import (
    NVML_TEMPERATURE_GPU,
    nvmlDeviceGetFanSpeed_v2,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetName,
    nvmlDeviceGetNumFans,
    nvmlDeviceGetTemperature,
    nvmlDeviceSetDefaultFanSpeed_v2,
    nvmlDeviceSetFanSpeed_v2,
    nvmlShutdown,
    nvmlInit,
)

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def get_target_fan_speed(temp: int) -> int:
    map = [(40,0), (65,35), (70, 60), (82, 90)]
    for temp_boundary, fan_speed in map:
        if temp < temp_boundary:
            return fan_speed
    return 100

log = logging.getLogger(__name__)

nvmlInit()
device_idx = 0
handle = nvmlDeviceGetHandleByIndex(device_idx)
log.info("Using device %s", nvmlDeviceGetName(handle))
fan_count = nvmlDeviceGetNumFans(handle)
POLLING_INTERVAL = 3
DRY_RUN = False

try:
    while True:
        for i in range(fan_count):
            temp = nvmlDeviceGetFanSpeed_v2(handle, i)
            log.debug("Fan %s : running at speed %s", i, temp)
        temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
        log.info("Device is at %s degrees", temperature)

        new_target = get_target_fan_speed(temperature)
        log.info("Setting target speed to %s", new_target)
        for i in range(fan_count):
            if not DRY_RUN:
                nvmlDeviceSetFanSpeed_v2(handle, i, new_target)
        time.sleep(POLLING_INTERVAL)
finally:
    log.info("Shutting down")
    for i in range(fan_count):
        nvmlDeviceSetDefaultFanSpeed_v2(handle, i)
    nvmlShutdown()





