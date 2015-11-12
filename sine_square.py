#
# Basic pyaudio program playing a real time mono sine wave 
#
# (ME) 2015 Marc Groenewegen
#

import pyaudio
import time
import numpy as np
import array
from Tkinter import *


WIDTH = 2 # sample size in bytes
CHANNELS = 1 # number of samples in a frame
RATE = 44100
FRAMESPERBUFFER = 256

global choosedco
global square
global sine
global Frequency

choosedco=1
square=0
sine=0


sineFrequency=2000.0
squareFrequency=440.0
LFOfrequency=0.1

Frequency=440.0


#
# Function showDevices() lists available input- and output devices
#
def showDevices(p):
  info = p.get_host_api_info_by_index(0)
  numdevices = info.get('deviceCount')
  for i in range (0,numdevices):
    if p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
      print "Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0,i).get('name')
    if p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
      print "Output Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0,i).get('name')


#
# Create array of signed ints to hold one sample buffer
# Make it global so it doesn't get re-allocated for every frame
#
outbuf = array.array('h',xrange(FRAMESPERBUFFER)) # array of signed ints

phase1=0 # sine phase
phase2=0 # square phase
phaseLFO=0 
sweep=0
sweepaan=0
pulsewidth=0


#
# Create the callback function which is called by pyaudio
#   whenever it needs output-data or has input-data
#
def callback(in_data,frame_count,time_info,status):
  global phase1
  global phaseLFO
  global sSquare
  global outbuf
  global LFO
  global sweep
  global sweepaan
  global Frequency
  global pulsewidth
  #frame_count * CHANNELS
  
  for n in range(frame_count):
	
	sweep = sweep + sweepaan
	
	if sweep > 1000:
	   sweep=1
	   sweepaan=0
	   
	#print sweep

	if sweep > 100:
	   Frequency=sweep
	if sweep < 101:
	   Frequency=Frequency


	phase1 += 2*np.pi*Frequency/RATE
	phaseLFO += 2*np.pi*LFOfrequency/RATE
	sSquare = np.sin(phase1)
	
	#maak van een sinus een square
	if sSquare > pulsewidth:
	   sSquare = 1
	else:
	   sSquare = -1
	
	if choosedco > 1:
	   sine=0.5
	   square=0.0
	else:
	   sine=0.0
	   square=0.05
	
	LFO = abs(np.sin(phaseLFO))
	
	if LFOfrequency == 0:
	   LFO=1

	#pos = callback.pos
        #callback.pos += frame_count

	outbuf[n] = int(32767 * square * LFO * sSquare) + int(32767*sine*LFO* np.sin(phase1))#[pos:pos+frame_count]

  return (outbuf,pyaudio.paContinue)

	  #########################
	  # Start of main program #
	  #########################


#
# get a handle to the pyaudio interface
#
paHandle = pyaudio.PyAudio()

# select a device
showDevices(paHandle)
outputDevice=1
devinfo = paHandle.get_device_info_by_index(outputDevice)
print "Selected device is ",devinfo.get('name')



#
# open a stream with some given properties
#
stream = paHandle.open(format=paHandle.get_format_from_width(WIDTH),
		channels=CHANNELS,
		rate=RATE,
		frames_per_buffer=FRAMESPERBUFFER,
		input=False, # no input
		output=True, # only output
		output_device_index=outputDevice, # choose output device
		stream_callback=callback)

stream.start_stream()

def makeSomething1(value):
    global choosedco
    choosedco= value

sweepspeed=10000


def sweepa(value):
    global sweep 
    global sweepaan
    global sweepspeed
    sweep=value
    sweepaan=float(value)/sweepspeed    

   # print the slider's current value
def slider1value(value):
      global Frequency
      Frequency=float(value)
      print value

def slider2value(value):
      global LFOfrequency
      LFOfrequency=float(value)/100
      print value

def slider3value(value):
      global sweepspeed
      sweepspeed=int(value)*100
      print sweepspeed

def slider4value(value):
      global pulsewidth
      pulsewidth=float(value)/100
      print pulsewidth

class Application(Frame):
  """ A GUI app """

  def __init__(self,master):
    """ Constructor: init the frame """
    Frame.__init__(self,master)
    self.grid()
    self.button_clicks=0
    self.create_widgets()
       

  def create_widgets(self):
    self.button1 =  Button(self, text="Square",command=lambda *args: makeSomething1(1))
    self.button1.grid()

    self.button2 =  Button(self, text="Sine  ",command=lambda *args: makeSomething1(2))
    self.button2.grid()

    self.button3 =  Button(self, text="Sweep ",command=lambda *args: sweepa(101))
    self.button3.grid()


    self.slider1 = Scale(self, command=slider1value)
    self.slider1.config(orient=HORIZONTAL)
    self.slider1.config(label="Frequency oscillator")
    self.slider1.config(length=300)
    self.slider1.config(width=10)
    self.slider1.config(sliderlength=20)
    self.slider1.config(from_=100)
    self.slider1.config(to_=1000)
    self.slider1.config(tickinterval=200)
    self.slider1.set(440)
    self.slider1.grid(row=0,column=1,sticky=W)
    
    self.slider2 = Scale(self, command=slider2value)
    self.slider2.config(orient=HORIZONTAL)
    self.slider2.config(label="LFO Rate")
    self.slider2.config(length=300)
    self.slider2.config(width=10)
    self.slider2.config(sliderlength=20)
    self.slider2.config(from_=0)
    self.slider2.config(to_=1000)
    self.slider2.config(tickinterval=200)
    self.slider2.set(0)
    self.slider2.grid(row=1,column=1,sticky=W)
    
    self.slider3 = Scale(self, command=slider3value)
    self.slider3.config(orient=HORIZONTAL)
    self.slider3.config(label="sweepspeed")
    self.slider3.config(length=300)
    self.slider3.config(width=10)
    self.slider3.config(sliderlength=20)
    self.slider3.config(from_=10)
    self.slider3.config(to_=100)
    self.slider3.config(tickinterval=200)
    self.slider3.set(100)
    self.slider3.grid(row=2,column=1,sticky=W)

    self.slider4 = Scale(self, command=slider4value)
    self.slider4.config(orient=HORIZONTAL)
    self.slider4.config(label="pulsewidth")
    self.slider4.config(length=300)
    self.slider4.config(width=10)
    self.slider4.config(sliderlength=20)
    self.slider4.config(from_=0)
    self.slider4.config(to_=99)
    self.slider4.config(tickinterval=200)
    self.slider4.set(0)
    self.slider4.grid(row=3,column=1,sticky=W)

         

  def exitEvent(self):
    root.destroy() # not just self.destroy()

  
    
# create a window
root = Tk()

# set window props
root.title("ME Gui")
root.geometry("400x300")

app = Application(root)

root.mainloop()



# Make sure that the main program doesn't finish until all
#  audio processing is done
while stream.is_active():
  time.sleep(0.1)


# in this example you'll never get here
stream.stop_stream()
stream.close()

paHandle.terminate()


