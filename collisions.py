"""
This calculates the new velocities of objects after they collide
"""

#this should calculate new trajectories after objects collide
from __future__ import division #does fun stuff
from visual import * #for the 3D graphics stuff
import random

#modifies the velocities of the two objects 
def elasticCollision(o1, o2):
	#useful things
	v1 = o1.getVelocity()
	m1 = o1.getMass()
	v2 = o2.getVelocity()
	m2 = o2.getMass()
	diffV = v1 - v2
	sepHat = norm(o1.getSep(o2))

	#from https://en.wikipedia.org/wiki/Elastic_collision
	v1new = v1 - ((2*m2)/(m1 + m2))*dot(diffV, sepHat)*sepHat
	v2new = v2 - ((2*m1)/(m1 + m2))*dot(-diffV, -sepHat)*(-sepHat)

	o1.setVelocity(v1new)
	o2.setVelocity(v2new)

#returns the velocity of the new, combined object
def inelasticCollision(o1, o2):
	momentum1 = o1.getVelocity()*o1.getMass()
	momentum2 = o2.getVelocity()*o2.getMass()
	velocity = (momentum1 + momentum2)/(o1.getMass() + o2.getMass())
	return velocity