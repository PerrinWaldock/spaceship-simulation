"""
This defines a class "Thing" that characterizes the movement of a 3D object. It also throws in a child class "Craft" that behaves like a space ship
Currently, it does not take rotational momentum into account (although it does allow the objects to be manually rotated), but it would be fun to add it into account in future.
"""

from __future__ import division #does fun stuff
from visual import * #for the 3D graphics stuff

import constants as c #gives useful physics constants
import collisions #calculates the result of a collision

#exception for when craft is out of ammo
class OutOfAmmoException(Exception):
	pass

#generic object with position, etc
class Thing:
	#defines the allowed types of collisions
	collisionTypes = ("elastic", "inelastic")

	#constructor
	"""
	shapesArg is a list of shapes that makes up the object
	r is the "radius" of the object; it is used to calculate if two objects are touching
	position is the starting position of the object
	forward is the "forward" direction of the object
	velocity is the initial velocity of the object
	mass is the mass of the object
	collisionType is either "elastic" or "inelastic"; elastic objects bounce when they collide, and inelastic objects do not
	name identifies the objects
	trail specifies whether or not the object leaves a visible trail
	"""
	def __init__(self, shapesArg, r=0, position=vector(0,0,0), forward=vector(0,0,1), velocity=vector(0,0,0), mass=1, collisionType="elastic", name="normal", trail=False):
		self.shapes = shapesArg
		self.trail = curve(color=self.shapes[0].color)
		self.trail.visible = trail
		if(position==vector(0,0,0)):
			position=shapesArg[0].pos
		self.position = position
		self.forward = forward
		self.left = vector(-1, 0, 0)
		if(norm(proj(self.forward, vector(0,1,0))) != vector(0,1,0)): #checks to make sure that left will actually give a left direction
			self.left = cross(vector(0,1,0), self.forward)
		self.velocity = velocity
		self.mass = mass
		if(r==0):
			try:
				r = self.shapes[0].radius
			except Exception:
				r = c.radiusEarth
		self.r = r
		self.name = name
		self.collisionType = collisionType

	#accessors
	def getPos(self):
		return self.position

	def getForward(self):
		return norm(self.forward)

	def getLeft(self):
		return norm(self.left)

	def getUp(self):
		return norm(cross(self.getForward(), self.getLeft()))

	def getVelocity(self):
		return self.velocity

	def getMass(self):
		return self.mass

	def getCollisionType(self):
		return self.collisionType

	def getTrailActive(self):
		return self.trail.visible

	def getName(self):
		return self.name

	#msets the position of new shapes
	def setPos(self, position):
		for shape in self.shapes:
			relPos = shape.pos - self.getPos()
			shape.pos = position + relPos

		self.position = position

	#sets the velocity of the thing
	def setVelocity(self, velocity):
		self.velocity = velocity

	#sets the mass of the thing
	def setMass(self, mass):
		self.mass = mass

	#sets the collision type of the thing
	def setCollisionType(self, t):
		if t in Thing.collisionTypes:
			self.collisionType = t
		else:
			print t, "is not a valid collision type"

	#if true, makes a trail, if false, does not
	def setTrail(self, makeTrail):
		self.trail.visible = makeTrail

	#set the colour of the thing
	def setColour(self, colour):
		for shape in self.shapes:
			shape.color = colour

	#rotates the thing by amount angle about the axis axis
	def rotate(self, angle, axis):
		self.forward = self.forward.rotate(angle, axis)
		self.left = self.left.rotate(angle, axis)
		for shape in self.shapes:
			shape.rotate(angle=angle, axis=axis, origin=self.position)

	#get the separation between two things
	def getSep(self, thing):
		sep = thing.getPos() - self.getPos()
		#prevent divide by zero
		if sep == vector(0,0,0):
			sep = norm(vector(random.random(), random.random(), random.random()))
		return sep

	#automatically moves the object, given a net force and the amount of time it is acting over
	def autoMove(self, netForce, changeTime):
		acceleration = netForce/float(self.getMass())
		velocity = acceleration*changeTime + self.getVelocity()
		self.setVelocity(velocity)
		position = velocity*changeTime + self.getPos()
		self.setPos(position)
		#update the trail
		self.trail.append(pos=self.getPos(), color=self.shapes[0].color)

	#true if the two objects are touching
	def isTouching(self, thing):
		if mag(thing.getPos() - self.getPos()) < (thing.r + self.r):
			return True
		else:
			return False

	#changes position of objects until they are no longer touching
	def separate(self, thing):
		if self.isTouching(thing):
			sep = self.getSep(thing)
			desSep = (self.r + thing.r)*norm(sep)
			changePos = (desSep - sep)
			self.setPos(self.getPos() - (changePos*thing.getMass())/(self.getMass() + thing.getMass()))
			thing.setPos(thing.getPos() + (changePos*self.getMass())/(self.getMass() + thing.getMass()))

	#joins two objects, including the momentum
	def join(self, thing):
		#adds the shape to the new one
		for shape in thing.shapes:
			self.shapes.append(shape)
		thing.shapes = list()
		#sets the new velocity
		self.setVelocity(collisions.inelasticCollision(self, thing))
		#sets the new mass
		self.setMass(self.getMass() + thing.getMass())

	#returns the gravitational force another object nearby can exert on it
	def gravForce(self, thing):
		sep = thing.getPos() - self.getPos()
		#prevent divide by zero
		if sep == vector(0,0,0):
			randChange = norm(vector(random.random(), random.random(), random.random()))
			thing.setPos(thing.getPos() + randChange)
			return self.gravForce(thing)

		force = norm(sep)*c.gravitationalConstant*thing.getMass()*self.getMass()/mag(sep)**2
		return force

	#kind of a makeshift deconstructor
	def clear(self):
		for shape in self.shapes:
			shape.visible = False
			del shape
		self.trail.visible = false
		del self.trail


#a type of thing that looks like a spaceship ...kinda
class Craft(Thing):
	#constructor
	"""
	r is the radius of collision
	position is the initial position of the craft
	forward is the forward direction of the craft
	velocity is the initial velocity of the craft
	mass is the mass of the object
	length is the length of the craft
	fuel is the initial mass of the fuel
	ammo is the initial number of projectiles
	exhaustSpeed is the exhaust speed of the craft
	"""
	def __init__(self, r=0, position=vector(0,0,0), forward=vector(0,0,1), velocity=vector(0,0,0), mass=1, length=.5*c.radiusEarth, fuel=10000, ammo=10, exhaustSpeed=60000, name="craft"):
		if(r==0):
			r = length
		shapes = list()
		shapes.append(arrow(pos=position, axis=length*norm(forward), shaftwidth=.1*length, material=materials.marble, color=color.green))
		shapes.append(cone(pos=position, axis=-.5*shapes[0].axis, radius=.75*shapes[0].shaftwidth, color=color.red, opacity=0))
		Thing.__init__(self, shapes, r=r, position=position, forward=forward, velocity=velocity, mass=mass, collisionType="elastic", name=name)
		self.fuel = fuel
		self.ammo = ammo
		self.exhaustSpeed = exhaustSpeed

	#accessors
	def getFuel(self):
		return self.fuel

	def getAmmo(self):
		return self.ammo

	def getExhaustSpeed(self):
		return self.exhaustSpeed

	def getMass(self):
		return self.mass + self.fuel #has fuel and normal mass

	def getLength(self):
		return mag(shapes[0].axis)

	#basic mutators
	def setFuel(self, newFuel):
		if(newFuel >= 0):
			self.fuel = newFuel

	def setAmmo(self, newAmmo):
		if newAmmo >= 0:
			self.ammo = newAmmo

	def setExhaustSpeed(self, newSpeed):
		self.exhaustSpeed = newSpeed

	#overriding this to stop the tail from changing colour
	def setColour(self, colour):
		self.shapes[0].color = colour

	#turns the craft left by an angle
	def turnLeft(self, angle):
		self.rotate(angle, self.getUp())

	#turns the craft up by an angle
	def turnUp(self, angle):
		self.rotate(-angle, self.getLeft())

	#creates a new object that will be fired away from the rocket
	def fireAmmo(self, colour, radius, mass, speed, collisionType, trail):
		if self.getAmmo() == 0:
			raise OutOfAmmoException('Out Of Ammunition')
		else:
			self.ammo -= 1

		#create the projectile
		temp = list()							#start position is further away
		temp.append(sphere(pos=self.getPos() + ((2*radius + 2*self.r)*self.getForward()), radius=radius, material=materials.emissive, color=colour, trail=trail))
		absoluteVelocity = (speed*self.getForward()) + self.getVelocity()
		projectile = Thing(temp, r=radius, forward=self.getForward(), velocity=absoluteVelocity, mass=mass, name="projectile")
		projectile.setCollisionType(collisionType)

		#calculates the effect of the projectile
		momentum = self.getVelocity()*self.getMass()
		momentum -= projectile.getVelocity()*projectile.getMass()
		self.setVelocity(momentum/self.getMass())

		#returns the projecile for animation
		return projectile

	#returns the force that the rocket exerts
	def rocketForce(self, burnRate, time):
		#animate tail
		if(burnRate > 0):
			self.shapes[1].opacity = .6
			self.shapes[1].axis = -self.shapes[0].axis*burnRate #changes the length of the tail to reflect the burn rate
		else:
			#makes the tail invisible
			self.shapes[1].opacity = 0

		#calculate amount of fuel used
		burnt = burnRate*time
		if burnt > self.getFuel():
			burnt = self.getFuel()
		#decrement fuel tank
		self.setFuel(self.getFuel() - burnt)

		#calculate and return the force
		return norm(self.getForward())*burnRate*self.exhaustSpeed

	#returns a camera vector that looks at the craft at the specified angle
	def cameraVector(self, hOffset, vOffset):
		#hack to make offset work; not sure why
		vOffset %= 2*math.pi
		if(vOffset < math.pi/2) or (vOffset > 3*math.pi/2):
			vOffset = (2*math.pi - vOffset)

		#sets the vector
		cameraVector = self.getForward()
		cameraVector = cameraVector.rotate(vOffset, self.getLeft()) #rotates camera up-down
		cameraVector = cameraVector.rotate(hOffset, cross(self.getForward(), self.getLeft())) #rotates camera left/right
		return cameraVector 

	#sets the camera angle to look the same direction as the craft
	def setCameraAngle(self, scene, hOffset, vOffset, cameraZoom):
		scene.forward = self.cameraVector(hOffset, vOffset)
		scene.center = self.getPos()
		scene.up = self.getUp()
		scene.range = cameraZoom


