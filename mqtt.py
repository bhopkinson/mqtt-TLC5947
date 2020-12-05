import discovery
import environment as env
import json
import paho.mqtt.client as mqtt

class Mqtt:
    def __init__(self):
        self.client = mqtt.Client(env.client_id)

    def __on_message(self, client, userdata, message):
        print(f"Message received: {message.topic}")
        print(message.payload.decode())

    def __on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("Connected to MQTT broker")
        else:
            print("Failed to connect to MQTT, reason code %d\n", rc)

    def __on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT, reason code %d\n", rc)

    def connect(self):
        client = self.client
        status_topic = f"{env.topic}/status"

        if (not client.on_connect) : client.on_connect = self.__on_connect
        if (not client.on_message) : client.on_message = self.__on_message

        client.will_set(status_topic, payload="offline", retain=True)
        client.connect(env.broker)
        client.publish(status_topic, payload="online", retain=True)

        client.subscribe(f"{env.topic}/+/+/set", qos=1)

        client.loop_start()

    def set_on_message_callback(self, callback):
        def on_message(client, userdata, message):
            self.__on_message(client, userdata, message)
            callback(message)

        self.client.on_message = on_message

    def send_discovery_message(self, message, uniqueId, type):
        if (env.discoveryTopic):
            unique_id = f"{env.client_id}_{uniqueId}"
            message[discovery.unique_id] = unique_id
            message[discovery.availability_topic] = "~/status"
            message[discovery.tilde] = env.topic
            payload = json.dumps(message)
            topic = f"{env.discoveryTopic}/{type}/{unique_id}/config"
            self.client.publish(topic, payload, qos=0, retain=True)

    def publish(self, subTopic, message):
        topic = f"{env.topic}/{subTopic}"
        payload = json.dumps(message)
        self.client.publish(topic, payload)