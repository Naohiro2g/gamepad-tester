# sample code from pygame.joystick at https://www.pygame.org/docs/ref/joystick.html
# Added the event printings of button pressed/released or axis changed with timestamps.
# connect a gamepad to Scratch

import pygame
import datetime

from array import array
import socket
import time
import sys
import struct
import unicodedata

PORT = 42001         # Scratch Remote Sensors Protocol port
HOST = 'localhost'   # his-raspi.local or 192.168.1.22
                     # to connect to another computer on the same network

print("\n", "Connecting...")
scratchSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
scratchSock.connect((HOST, PORT))
print("Connected to Scratch!")
print('\n', 'Gamepad tester started...\n')


def sendScratchCommand(cmd):
    scratchSock.send(struct.pack(">I",lenCount(cmd)))
    print(struct.pack(">I",lenCount(cmd)))
    scratchSock.send(bytes(cmd, 'UTF-8'))
    print(bytes(cmd, 'UTF-8'))

def lenCount(text):
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 3
        else:
            count += 1
    return count

def send_broadcast(msg):
    sendScratchCommand('broadcast "' + msg + '"')

def send_sensor_update(sensor_name, sensor_value):
    sendScratchCommand('sensor-update "' + sensor_name + '" ' + sensor_value + ' ')


# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def printS(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

pygame.init()

# Set the width and height of the screen [width,height]
size = [500, 800]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Gamepad Tester")
#Loop until the user clicks the close button.
done = False
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
# Initialize the joysticks
pygame.joystick.init()
# Get ready to print
textPrint = TextPrint()

# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
JOYSTICK_ACTIONS = (
    pygame.JOYAXISMOTION,
    pygame.JOYBUTTONDOWN,
    pygame.JOYBUTTONUP,
    pygame.JOYHATMOTION
)


def send_joystick(event):
    if event.type == pygame.JOYBUTTONDOWN:
        msg = str(event.joy) + "_" + "Button_" + str(event.button) + "_on"
        send_broadcast(msg)
    if event.type == pygame.JOYBUTTONUP:
        msg = str(event.joy) + "_" + "Button_" + str(event.button) + "_off"
        send_broadcast(msg)
    if event.type == pygame.JOYAXISMOTION:
        sensor_name = str(event.joy) + "_" + "Axis_" + str(event.axis)
        sensor_value = axis_value(event.value)
#        send_broadcast(sensor_name)
        send_sensor_update(sensor_name, sensor_value)
    if event.type == pygame.JOYHATMOTION:
#        msg = str(event.joy) + "_" + "Hat_" + str(event.value)
#        msg = str(event.joy) + "_" + "Hat"
#        send_broadcast(msg)
        value = str(event.value)
        if value[1] == "-":
            hat_x = "-1"
        else:
            hat_x = value[1]
        hat_y = str(event.value)[-3:-1]
        sensor_name = str(event.joy) + "_" + "Hat_X"
        sensor_value = hat_x
        send_sensor_update(sensor_name, sensor_value)
        sensor_name = str(event.joy) + "_" + "Hat_Y"
        sensor_value = hat_y
        send_sensor_update(sensor_name, sensor_value)


from decimal import Decimal, ROUND_HALF_UP

def axis_value(value):
    if value > 0.9:
        value = 1.0
    elif 0.1 > value > -0.1:
        value = 0.0
    elif value < -0.9:
        value = -1.0
    value = Decimal(str(value)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    return(str(value))



# -------- Main Program Loop -----------
while done==False:

    # EVENT PROCESSING STEP
    for event in pygame.event.get(): # User did something
        now = datetime.datetime.now()
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        if event.type in JOYSTICK_ACTIONS:
            send_joystick(event)

    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
    textPrint.reset()

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()
    textPrint.printS(screen, "Number of joysticks: {}".format(joystick_count) )
    textPrint.indent()

    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        textPrint.printS(screen, "Joystick {}".format(i) )
        textPrint.indent()

        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()
        textPrint.printS(screen, "Joystick name: {}".format(name) )

        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        textPrint.printS(screen, "Number of axes: {}".format(axes) )
        textPrint.indent()

        for i in range( axes ):
            axis = joystick.get_axis( i )
            textPrint.printS(screen, "Axis {} value: {:>6.7f}".format(i, axis) )
        textPrint.unindent()

        buttons = joystick.get_numbuttons()
        textPrint.printS(screen, "Number of buttons: {}".format(buttons) )
        textPrint.indent()

        for i in range( buttons ):
            button = joystick.get_button( i )
            textPrint.printS(screen, "Button {:>2} value: {}".format(i,button) )
        textPrint.unindent()

        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        hats = joystick.get_numhats()
        textPrint.printS(screen, "Number of hats: {}".format(hats) )
        textPrint.indent()

        for i in range( hats ):
            hat = joystick.get_hat( i )
            textPrint.printS(screen, "Hat {} value: {}".format(i, str(hat)) )
        textPrint.unindent()

    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
    # Limit to 20 frames per second
    clock.tick(50)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()

print("closing socket...")
scratchSock.close()
print("\n", "bye...")
sys.exit()
