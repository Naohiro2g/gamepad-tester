# sample code from pygame.joystick at https://www.pygame.org/docs/ref/joystick.html
# Added the event printings of button pressed/released or axis changed with timestamps.
# connect a gamepad to Scratch

import pygame
import datetime

from array import array
import socket
import time
import sys
from Tkinter import Tk
from tkSimpleDialog import askstring

root = Tk()
root.withdraw()

PORT = 42001
HOST = askstring('Scratch Connector', 'IP:')
if not HOST: HOST = 'localhost'

print("connecting...")
scratchSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
scratchSock.connect((HOST, PORT))
print("connected")

def sendScratchCommand(cmd):
    n = len(cmd)
    a = array('c')
    a.append(chr((n >> 24) & 0xFF))
    a.append(chr((n >> 16) & 0xFF))
    a.append(chr((n >>  8) & 0xFF))
    a.append(chr(n & 0xFF))
    scratchSock.send(a.tostring() + cmd)


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
size = [500, 700]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("My Game")

#Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()
    
# Get ready to print
textPrint = TextPrint()

# -------- Main Program Loop -----------
while done==False:
    # EVENT PROCESSING STEP
    for event in pygame.event.get(): # User did something
        now = datetime.datetime.now()
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        if event.type == pygame.JOYBUTTONDOWN:
            msg = "Button_" + str(event.button) + "_on" 
            sendScratchCommand('broadcast "' + msg + '"')
#            printS("Button:" + str(event.button) + " pressed.   "  + now.strftime("  %H:%M:%S.") + "%03d" % (now.microsecond // 1000))
        if event.type == pygame.JOYBUTTONUP:
            msg = "Button_" + str(event.button) + "_off" 
            sendScratchCommand('broadcast "' + msg + '"')
#            printS("Button:" + str(event.button) + " released.  "  + now.strftime("  %H:%M:%S.") + "%03d" % (now.microsecond // 1000))
        if event.type == pygame.JOYAXISMOTION:
            msg = "Axis_" + str(event.axis)
            sendScratchCommand('broadcast "' + msg + '"')
#            printS("Axis:{} {:>6.3f} ".format(event.axis, event.value) + now.strftime("  %H:%M:%S.") + "%03d" % (now.microsecond // 1000) )
 
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
print("done")
sys.exit()