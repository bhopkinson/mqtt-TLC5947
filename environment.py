import os

client_id = os.getenv("CLIENT_ID")
broker = os.getenv("BROKER")
topic = os.getenv("TOPIC")
discoveryTopic = os.getenv("DISCOVERY_TOPIC")
driverCount = int(os.getenv("DRIVER_COUNT"))
latchPin = os.getenv("LATCH_PIN")
logLevel = os.getenv("LOG_LEVEL")

if (not client_id): client_id = "1234567890"
if (not broker): broker = "192.168.0.23"
if (not topic): topic = "test/topic"
if (not discoveryTopic): discoveryTopic = "homeassistant"
if (not driverCount): driverCount = 1

DEBUG = "DEBUG"