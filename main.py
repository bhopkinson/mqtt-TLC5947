import os
import mqtt
import time

broker = os.getenv("BROKER")
topic = os.getenv("TOPIC")

mqtt = mqtt.Mqtt(broker, topic)
mqtt.connect()



#help("modules")

# print("Hello world")

# broker = '192.168.0.10'
# port = 1883
# mqtt_topic = "python/mqtt"

# socket = SocketPool.socket()

# MQTT.set_socket(socket)

# client = MQTT.MQTT(
#     broker=broker, port=port
# )

# client.on_connect = connect
# client.on_disconnect = disconnect
# client.on_subscribe = subscribe
# client.on_unsubscribe = unsubscribe
# client.on_publish = publish

# print("Attempting to connect to %s" % client.broker)
# client.connect()
 
# print("Subscribing to %s" % mqtt_topic)
# client.subscribe(mqtt_topic)
 
# print("Publishing to %s" % mqtt_topic)
# client.publish(mqtt_topic, "Hello Broker!")
 
# print("Unsubscribing from %s" % mqtt_topic)
# client.unsubscribe(mqtt_topic)
 
# print("Disconnecting from %s" % client.broker)
# client.disconnect()







# def connect_mqtt():
#     def on_connect(client, userdata, flags, rc):
#         if rc == 0:
#             print("Connected to MQTT Broker!")
#         else:
#             print("Failed to connect, return code %d\n", rc)
#     # Set Connecting Client ID
#     client = mqtt_client.Client(client_id)
#     client.on_connect = on_connect
#     client.connect(broker, port)
#     return client

# def publish(client):
#      msg_count = 0
#      while True:
#          time.sleep(1)
#          msg = f"messages: {msg_count}"
#          result = client.publish(topic, msg)
#          # result: [0, 1]
#          status = result[0]
#          if status == 0:
#              print(f"Send `{msg}` to topic `{topic}`")
#          else:
#              print(f"Failed to send message to topic {topic}")
#          msg_count += 1

# def subscribe(client: mqtt_client):
#     def on_message(client, userdata, msg):
#         print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

#     client.subscribe(topic)
#     client.on_message = on_message

# client = connect_mqtt()
# client.loop_start()
# publish(client)