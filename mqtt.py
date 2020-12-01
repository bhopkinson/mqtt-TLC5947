import paho.mqtt.client as mqtt

class Mqtt:
    def __init__(self, broker, topic):
        self.client = mqtt.Client()
        self.broker = broker
        self.topic = topic

    def __on_message(self, client, userdata, message):
        print("Message received: " + message.payload.decode())

    def __on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("Connected to MQTT broker")
        else:
            print("Failed to connect to MQTT, reason code %d\n", rc)

    def __on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT, reason code %d\n", rc)

    def connect_forever(self):
        client = self.client
        status_topic = f"{self.topic}/status"

        if (not client.on_connect) : client.on_connect = self.__on_connect
        if (not client.on_message) : client.on_message = self.__on_message

        client.will_set(status_topic, payload="Offline", retain=True)
        client.connect(self.broker)
        client.publish(status_topic, payload="Online", retain=True)

        client.subscribe(f"{self.topic}/+/+/set", qos=1)

        client.loop_forever()

    def set_on_message_callback(self, callback):
        def on_message(client, userdata, message):
            self.__on_message(client, userdata, message)
            callback(message)

        self.client.on_message = on_message