import json
import threading
import random
import time


class TempSensor:
    def __init__(self, did, pid, mqtt_client, discovery_prefix, base_topic, logger, initial_value=250, simulate_cfg=None):
        self.did = did
        self.pid = pid
        self.mqtt = mqtt_client
        self.logger = logger
        self.discovery_prefix = discovery_prefix
        self.base_topic = f"{base_topic}/{did}"
        self.availability_topic = f"{self.base_topic}/availability"
        self.state_topic = f"{self.base_topic}/status"
        self.value = initial_value  # stored as integer representing 0.1 \u00b0C
        self.sim_cfg = simulate_cfg or {}

        if self.sim_cfg.get("enabled"):
            threading.Thread(target=self.simulate_loop, daemon=True).start()

    def announce_discovery(self):
        topic = f"{self.discovery_prefix}/sensor/{self.pid}/{self.did}/config"
        payload = {
            "unique_id": self.did,
            "name": self.did,
            "availability_topic": self.availability_topic,
            "device_type": "sensor",
            "device_class": "temperature",
            "state_topic": self.state_topic,
            "value_template": "{{ (value_json.envtemp * 0.1) | round(1) }}",
            "unit_of_measurement": "\u00b0C",
            "device": {
                "identifiers": [f"did_{self.did}"],
                "name": "Test Temperature",
                "model": "Link&Link Temperature",
                "manufacturer": "Link&Link",
            },
        }
        self.mqtt.publish(topic, json.dumps(payload), retain=True)
        self.logger.info(f"[{self.did}] Sensor discovery sent to {topic}")

    def publish_state(self):
        payload = json.dumps({"envtemp": int(self.value)})
        self.mqtt.publish(self.state_topic, payload, retain=True)
        self.mqtt.publish(self.availability_topic, "online", retain=True)
        self.logger.info(f"[{self.did}] Published temperature: {payload}")

    def simulate_loop(self):
        min_v, max_v = self.sim_cfg.get("range", [250, 300])
        interval = self.sim_cfg.get("interval", 10)
        random_mode = self.sim_cfg.get("random", True)
        step = self.sim_cfg.get("step", 1)
        current = self.value
        increasing = True
        while True:
            time.sleep(interval)
            if random_mode:
                current = random.randint(min_v, max_v)
            else:
                if increasing:
                    current += step
                    if current >= max_v:
                        current = max_v
                        increasing = False
                else:
                    current -= step
                    if current <= min_v:
                        current = min_v
                        increasing = True
            self.value = current
            self.publish_state()
