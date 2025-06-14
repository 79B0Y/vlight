
import json
import threading
import random
import time
from vlight.state_store import save_state, load_state

class LightDevice:
    def __init__(self, did, pid, mqtt_client, discovery_prefix, base_topic, logger, initial_state=None, simulate=False):
        self.did = did
        self.pid = pid
        self.mqtt = mqtt_client
        self.logger = logger
        self.discovery_prefix = discovery_prefix
        self.base_topic = f"{base_topic}/{did}"
        self.availability_topic = f"{self.base_topic}/availability"
        self.state_topic = f"{self.base_topic}/status"
        self.simulate = simulate

        persisted = load_state(self.did)
        self.state = persisted or initial_state or {
            "state": "OFF",
            "brightness": 128,
            "color_temp": 250,
            "rgb_color": [255, 255, 255]
        }

        if simulate:
            threading.Thread(target=self.random_behavior_loop, daemon=True).start()

    def handle_command(self, key, payload):
        try:
            self.logger.info(f"[{self.did}] {key} <- {payload}")
            if key == "switch":
                self.state["state"] = "ON" if payload == "1" else "OFF"
            elif key == "brightness":
                self.state["brightness"] = int(payload)
            elif key == "colortemp":
                self.state["color_temp"] = int(payload)
            elif key == "rgb":
                rgb = [int(x) for x in payload.split(",")]
                self.state["rgb_color"] = rgb
            self.publish_state()
        except Exception as e:
            self.logger.error(f"[{self.did}] handle_command error: {e}")

    def publish_state(self):
        payload = json.dumps(self.state)
        self.mqtt.publish(self.state_topic, payload, retain=True)
        self.mqtt.publish(self.availability_topic, "online", retain=True)
        save_state(self.did, self.state)
        self.logger.info(f"[{self.did}] Published state: {payload}")

    def announce_discovery(self):
        topic = f"{self.discovery_prefix}/light/{self.pid}/{self.did}/config"
        config = {
            "name": f"{self.did}",
            "unique_id": self.did,
            "availability_topic": self.availability_topic,
            "state_topic": self.state_topic,
            "brightness": True,
            "rgb": True,
            "color_temp": True,
            "command_topic": self.base_topic + "/switch",
            "brightness_command_topic": self.base_topic + "/brightness",
            "rgb_command_topic": self.base_topic + "/rgb",
            "color_temp_command_topic": self.base_topic + "/colortemp",
            "schema": "json",
            "device": {
                "identifiers": [self.did],
                "name": "vLight 虚拟灯控制器",
                "manufacturer": "LinknLink",
                "model": "vlight-sim",
                "sw_version": "0.4.4"
            }
        }
        self.mqtt.publish(topic, json.dumps(config), retain=True)
        self.logger.info(f"[{self.did}] Discovery sent to {topic}")

    def random_behavior_loop(self):
        while True:
            time.sleep(random.randint(10, 20))
            self.state["state"] = random.choice(["ON", "OFF"])
            self.state["brightness"] = random.randint(0, 255)
            self.state["color_temp"] = random.randint(153, 500)
            self.state["rgb_color"] = [random.randint(0, 255) for _ in range(3)]
            self.publish_state()
