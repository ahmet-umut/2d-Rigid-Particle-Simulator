from arcade import *
from random import randrange
savedcolors=[87,114,114]*3,[142]*3,[214]*3,[239,120,120],[206,206,2],[245,142,204]
color0,color1,color2,color3,color4,color5=savedcolors	#0:background color, 1:Object, (2,3):triangles, 4:wheels, 5:the heavy ball
screenwidth,screenheight=999,222
worldzoom=8 	#each pixel corresponds 1/worldzoom meters
class Object:
	def __init__(entity, color=color1,x=0,y=0,vx=0,vy=0,ax=0,ay=0,m=1,r=1,detail=-1):	#x,y: position|vx,vy: velocity|ax,ay: acceleration|m: mass|r: radius
		entity.shape = "filledcircle"
		entity.radius=r
		entity.color=color
		entity.x,entity.y=x,y
		entity.vx,entity.vy=vx,vy
		entity.ax,entity.ay=ax,ay
		entity.objectSetList=[]	#list of sets which has this object as a member
		entity.detail=detail
		entity.mass=m
		entity.fx=entity.fy=0 	#forces in that direction. They are added to the 
	def draw(entity):
		if entity.shape=="filledcircle": draw_circle_filled(entity.x,entity.y,entity.radius,entity.color,0,entity.detail)
	def update(entity,dt):
		entity.x+=dt*(entity.vx+dt*entity.ax/2)*worldzoom
		entity.y+=dt*(entity.vy+dt*entity.ay/2)*worldzoom
		entity.vx+=dt*entity.ax
		entity.vy+=dt*entity.ay
	def delete(entity):
		for a in entity.objectSetList: a.objectdel(entity)
	def distance(entity,entity2): return ((entity.x-entity2.x)**2+(entity.y-entity2.y)**2)**.5
class ObjectSet:
	def __init__(objectSet):objectSet.set=set()
	def draw(objectSet):
		for a in objectSet.set: a.draw()
	def add(objectSet,object):	#add object
		objectSet.set.add(object)
		object.objectSetList.append(objectSet)
	def update(objectSet,dt):
		for a in objectSet.set: a.update(dt)
	def objectdel(objectSet,entity): objectSet.set.remove(entity)	#since it does not remove the object from any other collection, this function should be re-defined for children of ObjectSet class... 
class BallSet(ObjectSet):	#objectdel fn. must be redefined...
	gravacce=0	#gravitational acceleration
	def __init__(ballset):
		super().__init__()
		ballset.connections=set()	#connected balls and connection lengths
		ballset.ballcount=0
		ballset.balls=[]	#used in connections between balls. Makes connections easier to form in the program. If this uses excessive memory or slows the program down, other options can be chosen too.
	def add(ballset,ball):
		super().add(ball)
		ballset.balls.append(ball)
		ballset.ballcount+=1
	def connect(ballset,*indices):	#connects 2 balls rigidly.	|indices in ballset
		a=len(indices)
		b=0
		while a-b:
			c=b+1
			d=ballset.balls[indices[b]]
			while a-c:
				e=ballset.balls[indices[c]]
				ballset.connections.add((d,e,d.distance(e)))
				c+=1
			b+=1
	def update(ballset,dt):	# dt: delta t(ime)
		super().update(dt)
		for a,b,u in ballset.connections:
			du=(uz:=b.distance(a))-u
			dx=(b.x-a.x)
			dy=(b.y-a.y)
			ma,mb=a.mass,b.mass
			if uz==0:	#unexpected situation when the connected balls have the same position
				c=du/2**1.5
				a.x+=c
				b.x-=c
				a.y+=c
				b.y-=c
			else:	#expected: connection length is nonzero and balls are apart from each other
				if u:	#expected: connection length is nonzero and balls are apart from each other
					dvx,dvy=b.vx-a.vx,b.vy-a.vy
					vau=(a.vx*dx+a.vy*dy)/uz
					vbu=(b.vx*dx+b.vy*dy)/uz
					vu=(ma*vau+mb*vbu)/(ma+mb)
					dvau,dvbu=vu-vau,vu-vbu
					a.vx+=dx*dvau/uz
					a.vy+=dy*dvau/uz
					b.vx+=dx*dvbu/uz
					b.vy+=dy*dvbu/uz
				else:	#unexpected: if the connection has no length
					a.vx=b.vx=(a.vx+b.vx)/2
					a.vy=b.vy=(a.vy+b.vy)/2
				#	The 6 lines below is for the correction of the balls' positıons. I chose the divisor 1,2 after experimenting. Since dt is usually at most 1/50 and divisor is greater than, The bobbling effect this makes tends to be reduced to 0 very fast; and also this can represent the elasticity that exist in nature (however, the velocities must be differently arranged then...). Note that in nature, the connections are at atomic level and forces are applied in the speed of light... 
				xx=du*dx/uz/1.2	#the divisor is ideally 2. However, this ideal case results in balls not being able to resist the gravity and gradually disform the polygons they ideally should be part of...
				yy=du*dy/uz/1.2	#the divisor is ideally 2. However, this ideal case results in balls not being able to resist the gravity and gradually disform the polygons they ideally should be part of...
				a.x+=xx
				b.x-=xx
				a.y+=yy
				b.y-=yy
	def addtriangle(ballset,colors=color2,center=None,*vertices):	
		if vertices:a,b,c,ç,d,e=vertices
		if center:
			x,y=center
			if vertices:
				a+=x
				c+=x
				d+=x
				b+=y
				ç+=y
				e+=y
			else:a,b,c,ç,d,e=x-9,y-9,x+9,y-9,x,y+9
		elif not vertices:a,b,c,ç,d,e=(99,99,33,33,99,33)
		ball1=ball(colors,a,b,r=5)
		ball2=ball(colors,c,ç,r=5)
		ball3=ball(colors,d,e,r=5)
		a=len(ballset.set)	#the indice of the first ball in ballset.balls
		ballset.add(ball1)
		ballset.add(ball2)
		ballset.add(ball3)
		ballset.connect(a,a+1,a+2)
	def draw(ballset):
		super().draw()
		for a,b,u in ballset.connections: draw_line(a.x,a.y,b.x,b.y, color3)
class ball(Object):
	def update(to,dt):
		to.ay=BallSet.gravacce+to.fy/to.mass
		to.ax=to.fx/to.mass
		super().update(dt)
		#screendan çıkma durumları
		if to.y<0: 
			to.vy*=-1
			to.y=0
		elif to.y>screenheight:
			to.vy*=-1
			to.y=screenheight
		if to.x<0: 
			to.vx*=-1
			to.x=0
		elif to.x>screenwidth:
			to.vx*=-1
			to.x=screenwidth
		for a in to.objectSetList[0].balls:
			if a.distance(to)<a.radius+to.radius and a!=to:	#if they are close enough to hit
				m1,m2=to.mass,a.mass
				if (to.vx-a.vx)*(to.x-a.x)+(to.vy-a.vy)*(to.y-a.y)<0 and a!=to:	#if they have a suitable velocity-position relation	ball1:to ball2:a
					if a.x==to.x:	#rare case: they are in the same vertical line	
						q,w=(m1-m2)/(m1+m2),2*m2/(m1+m2)	#the multipliers
						to.vy,a.vy=q*to.vy+w*a.vy,w*to.vy-q*a.vy
					else:	#expected case...
						xb=2*(a.x<to.x)-1	#x1>x2
						yb=2*(a.y<to.y)-1	#y1>y2
						c=abs((a.y-to.y)/(a.x-to.x))	#position vector
						A=xb*(to.vx-a.vx)+yb*c*(to.vy-a.vy)
						B=(c**2+1)*(1/m1+1/m2)
						dpx=-2*A/B	#delta P_x	dpy=dpx*c
						to.vx+=xb*dpx/m1
						to.vy+=c*yb*dpx/m1
						a.vx-=xb*dpx/m2
						a.vy-=c*yb*dpx/m2
class Simulation(Window):
	def __init__(simulation,width,height,title):
		super().__init__(width,height,title)
		simulation.ballset=BallSet()
		simulation.framecount=0	#number of frames since the last computation of fps
	def setup(simulation):
		BallSet.gravacce=-10
		set_background_color(color0)
		schedule(simulation.test, 3)
		
		ballcount=60
		while ballcount:
			simulation.ballset.add(ball(color1, randrange(888),randrange(99),randrange(99)-55,randrange(88)-44,r=5,detail=-1))
			ballcount-=1

		simulation.add(ball(color5, randrange(888),randrange(99),randrange(99)-55,randrange(88)-44,r=5,detail=-1,m=111))

		trianumb=1
		while trianumb:
			simulation.ballset.addtriangle()
			trianumb-=1
	def test(simulation,t):	simulation.fps(t)
	def fps(simulation,dt):	#frames per second
		print(f"Averagely, {round(simulation.framecount/dt)} frames are shown per second.")
		simulation.framecount=0
	def add(simulation,to): simulation.ballset.add(to)	#add a ball to ballset.set
	def on_update(simulation,dt):
		simulation.ballset.update(dt)
		simulation.framecount+=1
	def on_draw(simulation):
		start_render()
		simulation.ballset.draw()

def main():
	screen=Simulation(screenwidth,screenheight,"2d Circular Particle Simulation")
	screen.setup()
	run()
if __name__ == "__main__": main()
