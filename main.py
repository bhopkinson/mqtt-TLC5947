import command
import instruction
import led
import os
import mqtt
import tlc5947
import queuehandler

broker = os.getenv("BROKER")
topic = os.getenv("TOPIC")
driverCount = os.getenv("DRIVER_COUNT")

broker = "192.168.0.23"
topic = "test/topic"
driverCount = 1

tlc5947 = tlc5947.tlc5947(driverCount)

def on_instruction(instruction):
    tlc5947.handle(instruction)
    
instructionHandler = queuehandler.handler()
instructionHandler.set_callback(on_instruction)
instructionHandler.loop_start()

ledController = led.controller(tlc5947.numberOfLeds, instructionHandler)

def on_command(command):
    ledController.handle(command)

commandHandler = queuehandler.handler()
commandHandler.set_callback(on_command)
commandHandler.loop_start()

def on_message(message):
    if message.topic.endswith("set"):
        commandHandler.handle(command.command(message))

mqtt = mqtt.Mqtt(broker, topic)
mqtt.set_on_message_callback(on_message)
mqtt.connect_forever()