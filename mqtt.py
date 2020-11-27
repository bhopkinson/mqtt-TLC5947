import paho.mqtt.client as mqtt

class Mqtt:
    def __init__(self, broker, topic):
        self.client = mqtt.Client()
        self.broker = broker
        self.topic = topic

    def connect(self):
        def on_connect(client, userdata, flags, rc):
            if rc==0:
                print("Connected to MQTT broker")
            else:
                print("Failed to connect to MQTT, reason code %d\n", rc)

        def on_disconnect(client, userdata, rc):
            print("Disconnected from MQTT, reason code %d\n", rc)
        
        def on_message(client, userdata, message):
            print("Message received: " + message.payload.decode())

        client = self.client
        status_topic = self.topic + "/status"

        client.on_connect = on_connect
        client.on_message = on_message

        client.will_set(status_topic, payload="Offline", retain=True)
        client.connect(self.broker)

        client.subscribe(self.topic, qos=1)

        client.publish(status_topic, payload="Online", retain=True)
        
        client.loop_forever()