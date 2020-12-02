import command
import instruction
import led
import os
import mqtt
import tlc5947
import queuehandler

mqtt = mqtt.Mqtt()
mqtt.connect()
led.mqtt = mqtt

tlc5947 = tlc5947.tlc5947()

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

mqtt.set_on_message_callback(on_message)