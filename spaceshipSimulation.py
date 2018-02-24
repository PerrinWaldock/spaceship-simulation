"""
This program simulates the movement of a spaceship through a multi-body system
"""

#imports
from __future__ import division #does fun stuff
from visual import * #for the 3D graphics stuff
import math
import wx #for buttons/controls

import things #custom class for physics modelling
import constants as c #a few useful constants
import collisions #


###constants
#constants
mCraftI = 30e3				# Mass of the craft, kg
lCraft = .4*c.radiusEarth   #length of the craft, m
mFuelI = 1e4				#amount of fuel in the craft, kg
maxBurnRate = .5			#amount of fuel burnt per second, kg/s
maxExhaustSpeed = 200000	#maximum exhaust speed, m/s

#simulation constants
MAX_SIMULATION_TIME = 28*24*60*60 #max number of seconds to simulate

#window constants
L = 640 		#window base unit
widgetL = 200	#basic widget length
border = 20		#border width
zoomMax = 1.0e8 #biggest zoom in

#misc constants
colourChoices = ['Green', 'Blue', 'Yellow', 'Pink', 'Cyan', 'Orange'] #colour options

#simulation variables
dt = 60         # The time step for the simulation
frameRate = 60 	#number of frames to simulate per second
t = 0 			#time passed
objects = list()#list of all things in the system that need to be animated and modelled

##function definitions
#makes a list of strings that display stats about the craft
def makeStatsStrings(craft, ratio, time):
	strings = list()
	strings.append("Orientation: " + str(craft.getForward()) + "\n")
	strings.append("Position: " + str(craft.getPos()) + "m\n")
	strings.append("Velocity: " + str(craft.getVelocity()) + "m/s\n")
	strings.append("Speed: " + str(mag(craft.getVelocity())) + "m/s\n")
	strings.append("Fuel Remaining: " + str(craft.getFuel()) + "kg\n")
	strings.append("Ammo Remaining: " + str(craft.getAmmo()) + "\n")
	
	seconds = time
	minutes = seconds/60
	seconds %= 60
	hours = minutes/60
	minutes %= 60
	days = hours/24
	hours %= 24
 
	strings.append("Time Passed: %i:%i:%i.%i\n"%(days, hours, minutes, seconds))
	strings.append("Time Scale: %i:1"%ratio)
	strings.append("Mass: " + str(craft.getMass()) + "kg\n")
	strings.append("Distance From Origin: " + str(mag(craft.getPos())) + "m")

	return strings

#makes all of the starting objects in the system
def makeStartObjects():
	obs = list()
	#spaceship
	obs.append(things.Craft(r=50, position=vector(0,0,6e7), forward=vector(0, 0, -1), velocity=vector(0, 0, -0), mass=mCraftI, length=lCraft, fuel=mFuelI, ammo=10, exhaustSpeed=exhaustSlider.GetValue()))
	obs[0].setTrail(True)

	#planet 1
	planet1 = list()
	planet1.append(sphere(pos=vector(0,0,0), material=materials.earth, radius=c.radiusEarth))
	obs.append(things.Thing(planet1, position=planet1[0].pos, forward=vector(1,0,0), velocity=vector(0,0,0), mass=.9*c.massEarth, name="earth1"))

	#planet 2
	planet2 = list() 
	planet2.append(sphere(pos=vector(2e7,5e7,0), material=materials.BlueMarble, radius=c.radiusEarth))
	obs.append(things.Thing(planet2, position=planet2[0].pos, forward=vector(1,0,0), velocity=vector(0, 0, 3e3), mass=c.massEarth, name="earth2"))
	return obs

#translates a number into a colour for use with the projectile colour and craft colour radioboxes
def translateColour(colourNumber):
	if(colourNumber == 0):
		return color.green
	elif(colourNumber == 1):
		return color.blue
	elif(colourNumber == 2):
		return color.yellow
	elif(colourNumber == 3):
		return vector(1,0.5,0.5)
	elif(colourNumber == 4):
		return color.cyan
	elif(colourNumber == 5):
		return color.orange
	else:
		print colourNumber
		return color.red

###make the GUI
#makes the window that shows everything
w1 = window(width=L + (3*widgetL) + (2*window.dwidth), height= L + window.dheight + window.menuheight, menus=True, title='SpaceshipSimulation')
#makes the 3D display window
display1 = display(window=w1, x=border, y=border, width=L-2*border, height=L-2*border, forward=vector(0,0,-1))#, range=zoomMax)

#variable for the panel for all of the buttons
p1 = w1.panel

##gives stats
stats = list()
for i in range(0,8):
	stats.append(wx.StaticText(p1, pos=(1.0*L,border + i*.023*L)))
for i in range(0,2):
	stats.append(wx.StaticText(p1, pos=(1.0*L + 2*widgetL, border + i*.024*L)))

##simulation controls
#stars/stops the simulation
startStop = wx.RadioBox(p1, pos=(L,0.21*L), size=(widgetL/2,65),
                 choices = ['Pause', 'Run'], style=wx.RA_SPECIFY_ROWS)
#toggles trails TODO: fix 
showTrails = wx.RadioBox(p1, pos=(L+widgetL/2,0.21*L), size=(widgetL/2,65), choices=['Hide Trails', 'Show Trails'], style=wx.RA_SPECIFY_ROWS)
trails = not showTrails.GetSelection()

#specifies the frame rate
rateSlider = wx.Slider(p1, pos=(L,.44*L), size = (widgetL, widgetL), style = wx.SL_LABELS | wx.SL_HORIZONTAL, minValue = 1, maxValue = 100, value = frameRate)
rateSlider.text = wx.StaticText(p1, pos=(1.0*L, .41*L), label='Frames Per Second')
#specifies the time slider
timeSlider = wx.Slider(p1, pos=(L,.35*L), size = (widgetL, widgetL), style = wx.SL_LABELS | wx.SL_HORIZONTAL, minValue = 1, maxValue = 300, value = dt)
timeSlider.text = wx.StaticText(p1, pos=(1.0*L, .31*L), label="Time Step Size (s)\n")
#reset the simulation
resetButton = wx.Button(p1, pos=(L, .5*L), label="Reset Simulation")


##camera contols
#sets the zoom of the camera
zoomSlider = wx.Slider(p1, pos=(1.0*L,0.58*L), size=(widgetL/2,widgetL), \
               style = wx.SL_LABELS | wx.SL_VERTICAL, \
               minValue=0.01*zoomMax, maxValue=zoomMax, \
               value=.1*zoomMax)
zoomSlider.text = wx.StaticText(p1, pos=(1.0*L,0.55*L), label='Zoom Level')
#sets the vertical angle of the camera relative to the craft
vSlider = wx.Slider(p1, pos=(1.0*L + widgetL/2,0.58*L), size=(widgetL/2,widgetL), \
               style = wx.SL_LABELS | wx.SL_VERTICAL, \
               minValue=-180, maxValue=180, \
               value=0)
vSlider.text = wx.StaticText(p1, pos=(1.0*L + widgetL/2 + 30,0.5*L), label='Vertical \nCamera \nAngle')
#sets the horizontal angle of the camera relative to the craft
hSlider = wx.Slider(p1, pos=(1.0*L,0.93*L), size=(widgetL,widgetL), \
               style = wx.SL_LABELS | wx.SL_HORIZONTAL, \
               minValue=-180, maxValue=180, \
               value=0)
hSlider.text = wx.StaticText(p1, pos=(1.0*L,0.9*L), label='Horizontal Camera Angle')
#prevents conflicts with mouse
display1.userspin = False
display1.userzoom = False


##ship controls
#turns craft
upButton = wx.Button(p1, label='Turn Up', pos=(L+5*widgetL/4,.1*L))
leftButton = wx.Button(p1, label='Turn Left', pos=(L+widgetL,.14*L))
rightButton = wx.Button(p1, label='Turn Right', pos=(L+3*widgetL/2,.14*L))
downButton = wx.Button(p1, label='Turn Down', pos=(L+5*widgetL/4,.18*L))

#add slider for the thrust
thrustSlider = wx.Slider(p1, pos=(1.0*L+widgetL,0.25*L), size=(widgetL,widgetL), style=wx.SL_LABELS | wx.SL_HORIZONTAL, minValue=0, maxValue=maxBurnRate*1000, value=maxBurnRate*1000)
thrustSlider.text = wx.StaticText(p1, pos=(1.0*L+widgetL,0.22*L), label='Fuel Burn Rate (g/s)')
#add slider for exhaust speed
exhaustSlider = wx.Slider(p1, pos=(1.0*L+2*widgetL,0.25*L), size=(widgetL,widgetL), style=wx.SL_LABELS | wx.SL_HORIZONTAL, minValue=1, maxValue=maxExhaustSpeed, value=.3*maxExhaustSpeed)
exhaustSlider.text = wx.StaticText(p1, pos=(1.0*L+2*widgetL,0.22*L), label='Exhaust Velocity (m/s)')
#add slider for empty mass of ship
massSlider = wx.Slider(p1, pos=(1.0*L+2*widgetL,0.15*L), size=(widgetL,widgetL), style=wx.SL_LABELS | wx.SL_HORIZONTAL, minValue=1, maxValue=10*mCraftI, value=.3*maxExhaustSpeed)
massSlider.text = wx.StaticText(p1, pos=(1.0*L+2*widgetL,0.1*L), label='Mass of Ship When Empty (kg)')
#adds refuel button
refuelButton = wx.Button(p1, label='Refuel', pos=(L+widgetL,.32*L))
#recenters the craft TODO: implement
recentreButton = wx.Button(p1, label='Recentre', pos=(L+3*widgetL/2,.32*L))
#pick the colour of the craft
craftColourBox = wx.RadioBox(p1, pos=(L+widgetL,0.38*L), choices=colourChoices)
craftColourBox.text = wx.StaticText(p1, pos=(L+widgetL,0.36*L), label='Craft Colour')


#reload-type buttons
triggerButton = wx.Button(p1, pos=(1.0*L+widgetL, .45*L), size=(.33*widgetL,.04*L), label = 'Fire')
reloadButton = wx.Button(p1, pos=(L+4*widgetL/3, .45*L), size=(.33*widgetL,.04*L), label='Reload')
clearButton = wx.Button(p1, pos=(L+5*widgetL/3, .45*L), size=(.33*widgetL,.04*L), label='Clear')

#pick the colour of the projectile
projectileColourBox = wx.RadioBox(p1, pos=(L+widgetL,0.52*L), choices=colourChoices)
projectileColourBox.text = wx.StaticText(p1, pos=(L+widgetL,0.5*L), label='Projectile Colour')
projectileColourBox.SetSelection(2)

#add slider for the radius
projectileRadiusSlider = wx.Slider(p1, pos=(1.0*L+widgetL,0.61*L), size=(widgetL,widgetL), style=wx.SL_LABELS | wx.SL_HORIZONTAL, minValue=1, maxValue=.2*c.radiusEarth, value=.05*c.radiusEarth)
projectileRadiusSlider.text = wx.StaticText(p1, pos=(1.0*L+widgetL,0.59*L), label='Projectile Radius, m')

#add slider for the mass
projectileMassSlider = wx.Slider(p1, pos=(1.0*L+widgetL,0.71*L), size=(widgetL,widgetL), style=wx.SL_LABELS | wx.SL_HORIZONTAL, minValue=1, maxValue=mCraftI, value=10)
projectileMassSlider.text = wx.StaticText(p1, pos=(1.0*L+widgetL,0.69*L), label='Projectile Mass, kg')

#add slider for the launch speed
projectileSpeedSlider = wx.Slider(p1, pos=(1.0*L+widgetL,0.81*L), size=(widgetL,widgetL), style=wx.SL_LABELS | wx.SL_HORIZONTAL, minValue=1, maxValue=100000, value=15000)
projectileSpeedSlider.text = wx.StaticText(p1, pos=(1.0*L+widgetL,0.79*L), label='Projectile Launch Speed, m/s')

#add box for collisionType
collisionTypeBox = wx.RadioBox(p1, pos=(L+widgetL,0.91*L), choices=['Inelastic', 'Elastic'])
collisionTypeBox.SetSelection(1)
collisionTypeBox.text = wx.StaticText(p1, pos=(L+widgetL,0.89*L), label='Projectile Collision Type')


#creates all of the starting objects in the system
objects = makeStartObjects()

###event handler functions
#I know they are in an ugly spot, but with how python handles variables and function definitions, I can't really put them anywhere else

#adds more fuel to the ship
def refill(evt):
	objects[0].setFuel(objects[0].getFuel() + mFuelI)

#adds more ammo to the ship
def reload(evt):
	objects[0].setAmmo(objects[0].getAmmo() + 10)

#places the craft back to where it started
def recentre(evt):
	objects[0].setPos(vector(0,0,0))
	objects[0].setVelocity(vector(0,0,0))

#deletes all projectiles
def clear(evt):
	i = 0
	while(i < len(objects)): #need to use while loop because length of list can change
		if(objects[i].getName() == "projectile"):
			objects[i].clear() #deletes shapes; works kind of like a deconstructor
			del objects[i]
		else:
			i += 1

#fires a projectile from the craft
def fire(evt):
	#get colour
	colour = translateColour(projectileColourBox.GetSelection())

	#set parameters
	radius = projectileRadiusSlider.GetValue()
	mass = projectileMassSlider.GetValue()
	dSpeed = projectileSpeedSlider.GetValue()

	#set collision type
	collisionType = "elastic"
	if collisionTypeBox.GetSelection() == 0:
		collisionType = "inelastic"

	#should create a new object that flies through space
	if(objects[0].getAmmo() > 0):
		objects.append(objects[0].fireAmmo(colour, radius, mass, dSpeed, collisionType, trails))
		trailsValue = False
		if showTrails.GetSelection() == 1:
			trailsValue = True
		objects[len(objects) - 1].setTrail(trailsValue)

#turns the craft to the left
def turnLeft(evt):
	objects[0].turnLeft(math.pi/12)

#turns the craft to the right
def turnRight(evt):
	objects[0].turnLeft(-math.pi/12)

#turns the craft up
def turnUp(evt):
	objects[0].turnUp(math.pi/12)

#turns the craft down
def turnDown(evt):
	objects[0].turnUp(-math.pi/12)

#handles a variety of text intputs
def keyPress(evt):
	#gets the number associated with the key pressed
	keycode = evt.GetKeyCode()

	if(keycode == 315): #up arrow, rotates craft upwards
		objects[0].turnUp(math.pi/60)
	elif(keycode == 317): #down arrow, rotates craft down
		objects[0].turnUp(-math.pi/60)
	elif(keycode == 314): #left arrow, rotates craft left
		objects[0].turnLeft(math.pi/60)
	elif(keycode == 316): #right arrow, rotates craft right
		objects[0].turnLeft(-math.pi/60)
	elif(keycode == 87): #w, turns camera up
		currentAngle = vSlider.GetValue()
		if currentAngle <= 180 - 4:
			vSlider.SetValue(currentAngle + 4)
		else:
			vSlider.SetValue(currentAngle - 360 + 4)
	elif(keycode == 83): #s, turns camera down
		currentAngle = vSlider.GetValue()
		if currentAngle >= -180 + 4:
			vSlider.SetValue(currentAngle - 4)
		else:
			vSlider.SetValue(currentAngle + 360 - 4)
	elif(keycode == 65): #a, turns camera left
		currentAngle = hSlider.GetValue()
		if currentAngle <= 180 - 4:
			hSlider.SetValue(currentAngle + 4)
		else:
			hSlider.SetValue(currentAngle - 360 + 4)
	elif(keycode == 68): #d, turns camera right
		currentAngle = hSlider.GetValue()
		if currentAngle >= -180 + 4:
			hSlider.SetValue(currentAngle - 4)
		else:
			hSlider.SetValue(currentAngle + 360 - 4)
	elif(keycode >= 48) and (keycode <= 57): #set thruster power using 0-9 keys
		value = keycode - 48
		thrustSlider.SetValue(value*1000*maxBurnRate/9)
	elif(keycode == 80): #p, pause/play
		if(startStop.GetSelection() == 0):
			startStop.SetSelection(1)
		else:
			startStop.SetSelection(0)
	elif(keycode == 82): #r, refuel
		refill(evt)
	elif(keycode == 70): #f, fire
		fire(evt)
	elif(keycode == 76): #l, reload
		reload(evt)

#resets the simulation to starting conditions
def resetSim(evt):
	global objects
	global t
	#deletes all of the objects
	for o in objects:
		o.clear() #works kinda like a deconstructor
		del o
	objects = makeStartObjects() #resets objects to starting condition
	t = 0


##bind buttons to handler functions
leftButton.Bind(wx.EVT_BUTTON, turnLeft)
rightButton.Bind(wx.EVT_BUTTON, turnRight)
upButton.Bind(wx.EVT_BUTTON, turnUp)
downButton.Bind(wx.EVT_BUTTON, turnDown)
refuelButton.Bind(wx.EVT_BUTTON, refill)
triggerButton.Bind(wx.EVT_BUTTON, fire)
reloadButton.Bind(wx.EVT_BUTTON, reload)
resetButton.Bind(wx.EVT_BUTTON, resetSim)
recentreButton.Bind(wx.EVT_BUTTON, recentre)
clearButton.Bind(wx.EVT_BUTTON, clear)

#binds keys to handler function
p1.Bind(wx.EVT_CHAR_HOOK, keyPress) #ideally, want to replace with two functions (key down and key up) so I don't have to rely on repeating keys, etc

###main loop
while t < MAX_SIMULATION_TIME:
	#updates rates 
	frameRate = rateSlider.GetValue()
	dt = timeSlider.GetValue()

	#specifies the max rate this loop will run at
	rate(frameRate)

	#update Camera Angle
	newZoom = zoomSlider.GetValue()
	newV = vSlider.GetValue()*math.pi/180
	newH = hSlider.GetValue()*math.pi/180
	objects[0].setCameraAngle(display1, newH, newV, newZoom)

	#update stats
	strings = makeStatsStrings(objects[0], frameRate*dt, t)
	for i in range(0,len(stats)):
		stats[i].SetLabel(strings[i])

	#set fuel burn rate
	burnrate = 0
	if(objects[0].getFuel() > 0) and (thrustSlider.GetValue() > 0):
		burnrate = thrustSlider.GetValue()/1000.
	else:
		burnrate = 0
		thrustSlider.SetValue(0)
	#sets exhaust velocity
	objects[0].setExhaustSpeed(exhaustSlider.GetValue())

	#show/hide trails
	if trails != showTrails.GetSelection():
		trails = showTrails.GetSelection()
		trailsValue = False
		if trails == 1:
			trailsValue = True
		for o in objects:
			o.setTrail(trailsValue)

	#set craft colour
	colour = translateColour(craftColourBox.GetSelection())
	objects[0].setColour(colour)

	#if simulation is paused, loop back to start
	checkIfRunning = startStop.GetSelection()
	if checkIfRunning == 0:
		continue

	#update time
	t += dt

	#check for collisions and handles them. This is done before calculating forces to try to stop singularities from happening
	i=0
	#using while loop because length of list could change
	while i < len(objects):
		j=i
		while j < len(objects):
			if(i != j):
				if objects[i].isTouching(objects[j]):
					objects[i].separate(objects[j]) #gets the objects to no longer touch; if objects are touching for too long, they can reach the same point, causing a divide by zero on the gravitation
					if objects[i].collisionType == "elastic" and objects[j].collisionType == "elastic":
						collisions.elasticCollision(objects[i], objects[j])
					elif objects[i].collisionType == "elastic" or objects[j].collisionType == "inelastic":
						objects[i].join(objects[j])
						del objects[j]
					else:
						objects[i].join(objects[j])
						del objects[j]
			j += 1
		i += 1

	#force calculations
	force = list()
	for i in range(0, len(objects)): #initialize to zero
		 force.append(vector(0,0,0))
	for i in range(0, len(objects)):
		for j in range(i, len(objects)):
			if(i != j):
				forceij = objects[i].gravForce(objects[j])
				force[i] += forceij
				force[j] -= forceij
	#add force of rocket
	force[0] += objects[0].rocketForce(burnrate, dt)

	#move the objects
	for i in range(0, len(objects)):
		objects[i].autoMove(force[i], dt)


#pauses output so that you can look around
while True:
	rate(10)
	newZoom = zoomSlider.GetValue()
	newV = vSlider.GetValue()*math.pi/180
	newH = hSlider.GetValue()*math.pi/180
	objects[0].setCameraAngle(display1, newH, newV, newZoom)


