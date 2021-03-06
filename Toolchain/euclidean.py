"""
Euclidean is a collection of python utilities for complex numbers, paths, polygons & Vec3s.

To use euclidean, install python 2.x on your machine, which is avaliable from http://www.python.org/download/

Then in the folder which euclidean is in, type 'python' in a shell to run the python interpreter.  Finally type
'import euclidean' to import these utilities and 'from vec3 import Vec3' to import the Vec3 class.


Below are examples of euclidean use.

>>> from euclidean import *
>>> from vec3 import Vec3
>>> origin=Vec3()
>>> right=Vec3(1.0,0.0,0.0)
>>> back=Vec3(0.0,1.0,0.0)
>>> getAngleAroundZAxisDifference(back, right)
1.5707963267948966
>>> getPointMaximum(right,back)
1.0, 1.0, 0.0
>>> polygon=[origin, right, back]
>>> getPolygonLength(polygon)
3.4142135623730949
>>> getPolygonArea(polygon)
0.5
"""

try:
	import psyco
	psyco.full()
except:
	pass
from vec3 import Vec3
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addToThreadsFromLoop( extrusionHalfWidthSquared, gcodeType, loop, oldOrderedLocation, skein ):
	"Add to threads from the last location from loop."
	nearestIndex = int( round( getNearestDistanceSquaredIndex( oldOrderedLocation, loop ).imag ) )
	loop = getAroundLoop( nearestIndex, nearestIndex, loop )
	nearestPoint = getNearestPointOnSegment( loop[ 0 ], loop[ 1 ], oldOrderedLocation )
	if nearestPoint.distance2( loop[ 0 ] ) > extrusionHalfWidthSquared and nearestPoint.distance2( loop[ 1 ] ) > extrusionHalfWidthSquared:
		loop = [ nearestPoint ] + loop[ 1 : ] + [ loop[ 0 ] ]
	oldOrderedLocation.setToVec3( loop[ 0 ] )
	gcode = 'M101\n(<loop>'
	if gcodeType != '':
		gcode += ' ' + gcodeType
	gcode += ' )'
	skein.addGcodeFromGcodeThread( gcode, loop + [ loop[ 0 ] ] ) # Turn extruder on and indicate that a loop is beginning.

def addToThreadsRemoveFromSurroundings( oldOrderedLocation, surroundingLoops, skein ):
	"Add to threads from the last location from surrounding loops."
	while len( surroundingLoops ) > 0:
		getTransferClosestSurroundingLoop( oldOrderedLocation, surroundingLoops, skein )

def addXIntersections( loop, solidIndex, xIntersectionList, y ):
	"Add the x intersections for a loop."
	for pointIndex in range( len( loop ) ):
		pointFirst = loop[ pointIndex ]
		pointSecond = loop[ ( pointIndex + 1 ) % len( loop ) ]
		isYAboveFirst = y > pointFirst.y
		isYAboveSecond = y > pointSecond.y
		if isYAboveFirst != isYAboveSecond:
			xIntersection = getXIntersection( pointFirst, pointSecond, y )
			xIntersectionList.append( complex( xIntersection, float( solidIndex ) ) )

def addXIntersectionsFromLoops( loops, solidIndex, xIntersectionList, y ):
	"Add the x intersections for the loops."
	for loop in loops:
		addXIntersections( loop, solidIndex, xIntersectionList, y )

def compareSolidXByX( solidXFirst, solidXSecond ):
	if solidXFirst.real > solidXSecond.real:
		return 1
	if solidXFirst.real < solidXSecond.real:
		return - 1
	return 0

def getAngleAroundZAxisDifference( subtractFromVec3, subtractVec3 ):
	"""Get the angle around the Z axis difference between a pair of Vec3s.

	Keyword arguments:
	subtractFromVec3 -- Vec3 whose angle will be subtracted from
	subtractVec3 -- Vec3 whose angle will be subtracted"""
	subtractVectorMirror = complex( subtractVec3.x , - subtractVec3.y )
	differenceVector = getRoundZAxisByPlaneAngle( subtractVectorMirror, subtractFromVec3 )
	return math.atan2( differenceVector.y, differenceVector.x )

def getAroundLoop( begin, end, loop ):
	"Get an arc around a loop."
	aroundLoop = []
	if end <= begin:
		end += len( loop )
	for pointIndex in range( begin, end ):
		aroundLoop.append( loop[ pointIndex % len( loop ) ] )
	return aroundLoop

def getAwayPath( path, radius ):
	"Get a loop with only the points that are far enough away from each other."
	away = []
	overlapDistanceSquared = 0.0001 * radius * radius
	for pointIndex in range( len( path ) ):
		if not isClose( overlapDistanceSquared, path, pointIndex ):
			point = path[ pointIndex ]
			away.append( point )
	return away

def getComplexMaximum( firstComplex, secondComplex ):
	"Get a complex with each component the maximum of the respective components of a pair of complexes."
	return complex( max( firstComplex.real, secondComplex.real ), max( firstComplex.imag, secondComplex.imag ) )

def getComplexMaximumFromVec3List( vec3List ):
	"Get a complex with each component the maximum of the respective components of a list of Vec3s."
	maximum = complex( - 999999999.0, - 999999999.0 )
	for point in vec3List:
		maximum = getComplexMaximum( maximum, point.dropAxis( 2 ) )
	return maximum

def getComplexMinimum( firstComplex, secondComplex ):
	"Get a complex with each component the minimum of the respective components of a pair of complexes."
	return complex( min( firstComplex.real, secondComplex.real ), min( firstComplex.imag, secondComplex.imag ) )

def getComplexMinimumFromVec3List( vec3List ):
	"Get a complex with each component the minimum of the respective components of a list of Vec3s."
	minimum = complex( 999999999.0, 999999999.0 )
	for point in vec3List:
		minimum = getComplexMinimum( minimum, point.dropAxis( 2 ) )
	return minimum

def getDistanceSquaredToPlaneSegment( segmentBegin, segmentEnd, point ):
	"Get the distance squared from a point to the x & y components of a segment."
	segmentDifference = segmentEnd.minus( segmentBegin )
	pointMinusSegmentBegin = point.minus( segmentBegin )
	beginPlaneDot = getPlaneDot( pointMinusSegmentBegin, segmentDifference )
	if beginPlaneDot <= 0.0:
		return point.distance2( segmentBegin )
	differencePlaneDot = getPlaneDot( segmentDifference, segmentDifference )
	if differencePlaneDot <= beginPlaneDot:
		return point.distance2( segmentEnd )
	intercept = beginPlaneDot / differencePlaneDot
	segmentDifference.scale( intercept )
	interceptPerpendicular = segmentBegin.plus( segmentDifference )
	return point.distance2( interceptPerpendicular )

def getFillOfSurroundings( surroundingLoops ):
	"Get extra fill loops of surrounding loops."
	fillSurroundings = []
	for surroundingLoop in surroundingLoops:
		fillSurroundings += surroundingLoop.getFillLoops()
	return fillSurroundings

def getHalfSimplifiedLoop( loop, radius, remainder ):
	"Get the loop with half of the points inside the channel removed."
	if len( loop ) < 2:
		return loop
	channelRadius = radius * .01
	simplified = []
	addIndex = 0
	if remainder == 1:
		addIndex = len( loop ) - 1
	for pointIndex in range( len( loop ) ):
		point = loop[ pointIndex ]
		if pointIndex % 2 == remainder or pointIndex == addIndex:
			simplified.append( point )
		elif not isWithinChannel( channelRadius, pointIndex, loop ):
			simplified.append( point )
	return simplified

def getInsidesAddToOutsides( loops, outsides ):
	"Add loops to either the insides or outsides."
	insides = []
	for loopIndex in range( len( loops ) ):
		loop = loops[ loopIndex ]
		if isInsideOtherLoops( loopIndex, loops ):
			insides.append( loop )
		else:
			outsides.append( loop )
	return insides

def getLeftPoint( path ):
	"Get the leftmost point in the path."
	left = 999999999.0
	leftPoint = None
	for point in path:
		if point.x < left:
			left = point.x
			leftPoint = point
	return leftPoint

def getMaximumSpan( loop ):
	"Get the maximum span in the xy plane."
	extent = getComplexMaximumFromVec3List( loop ) - getComplexMinimumFromVec3List( loop )
	return max( extent.real, extent.imag )

def getNearestDistanceSquaredIndex( point, loop ):
	"Get the distance squared to the nearest segment of the loop and index of that segment."
	smallestDistanceSquared = 999999999999999999.0
	nearestDistanceSquaredIndex = None
	for pointIndex in range( len( loop ) ):
		segmentBegin = loop[ pointIndex ]
		segmentEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
		distanceSquared = getDistanceSquaredToPlaneSegment( segmentBegin, segmentEnd, point )
		if distanceSquared < smallestDistanceSquared:
			smallestDistanceSquared = distanceSquared
			nearestDistanceSquaredIndex = complex( distanceSquared, float( pointIndex ) )
	return nearestDistanceSquaredIndex

def getNearestPathDistanceSquaredIndex( point, path ):
	"Get the distance squared to the nearest segment of the path and index of that segment."
	smallestDistanceSquared = 999999999999999999.0
	nearestDistanceSquaredIndex = None
	for pointIndex in range( len( path ) - 1 ):
		segmentBegin = path[ pointIndex ]
		segmentEnd = path[ pointIndex + 1 ]
		distanceSquared = getDistanceSquaredToPlaneSegment( segmentBegin, segmentEnd, point )
		if distanceSquared < smallestDistanceSquared:
			smallestDistanceSquared = distanceSquared
			nearestDistanceSquaredIndex = complex( distanceSquared, float( pointIndex ) )
	return nearestDistanceSquaredIndex

def getNearestPointOnSegment( segmentBegin, segmentEnd, point ):
	segmentDifference = segmentEnd.minus( segmentBegin )
	pointMinusSegmentBegin = point.minus( segmentBegin )
	beginPlaneDot = getPlaneDot( pointMinusSegmentBegin, segmentDifference )
	differencePlaneDot = getPlaneDot( segmentDifference, segmentDifference )
	intercept = beginPlaneDot / differencePlaneDot
	intercept = max( intercept, 0.0 )
	intercept = min( intercept, 1.0 )
	segmentDifference.scale( intercept )
	return segmentBegin.plus( segmentDifference )

def getNumberOfIntersectionsToLeft( leftPoint, loop ):
	"Get the number of intersections through the loop for the line starting from the left point and going left."
	numberOfIntersectionsToLeft = 0
	for pointIndex in range( len( loop ) ):
		firstPoint = loop[ pointIndex ]
		secondPoint = loop[ ( pointIndex + 1 ) % len( loop ) ]
		isLeftAboveFirst = leftPoint.y > firstPoint.y
		isLeftAboveSecond = leftPoint.y > secondPoint.y
		if isLeftAboveFirst != isLeftAboveSecond:
			if getXIntersection( firstPoint, secondPoint, leftPoint.y ) < leftPoint.x:
				numberOfIntersectionsToLeft += 1
	return numberOfIntersectionsToLeft

def getPathLength( path ):
	"Get the length of a path ( an open polyline )."
	pathLength = 0.0
	for pointIndex in range( len( path ) - 1 ):
		firstPoint = path[ pointIndex ]
		secondPoint  = path[ pointIndex + 1 ]
		pathLength += firstPoint.distance( secondPoint )
	return pathLength

def getPathRoundZAxisByPlaneAngle( planeAngle, path ):
	"""Get Vec3 array rotated by a plane angle.

	Keyword arguments:
	planeAngle - plane angle of the rotation
	path - Vec3 array whose rotation will be returned"""
	planeArray = []
	for point in path:
		planeArray.append( getRoundZAxisByPlaneAngle( planeAngle, point ) )
	return planeArray

def getPlaneDot( vec3First, vec3Second ):
	"Get the dot product of the x and y components of a pair of Vec3s."
	return vec3First.x * vec3Second.x + vec3First.y * vec3Second.y

def getPlaneDotPlusOne( vec3First, vec3Second ):
	"Get the dot product plus one of the x and y components of a pair of Vec3s."
	return 1.0 + getPlaneDot( vec3First, vec3Second )

def getPointMaximum( firstPoint, secondPoint ):
	"Get a point with each component the maximum of the respective components of a pair of Vec3s."
	return Vec3( max( firstPoint.x, secondPoint.x ), max( firstPoint.y, secondPoint.y ), max( firstPoint.z, secondPoint.z ) )

def getPointMinimum( firstPoint, secondPoint ):
	"Get a point with each component the minimum of the respective components of a pair of Vec3s."
	return Vec3( min( firstPoint.x, secondPoint.x ), min( firstPoint.y, secondPoint.y ), min( firstPoint.z, secondPoint.z ) )

def getPointPlusSegmentWithLength( length, point, segment ):
	"Get point plus a segment scaled to a given length."
	return segment.times( length / segment.length() ).plus( point )

def getPolar( angle, radius ):
	"""Get polar complex from counterclockwise angle from 1, 0 and radius.

	Keyword arguments:
	angle -- counterclockwise angle from 1, 0
	radius -- radius of complex"""
	return complex( radius * math.cos( angle ), radius * math.sin( angle ) )

def getPolygonArea( polygon ):
	"Get the xy plane area of a polygon."
	polygonArea = 0.0
	for pointIndex in range( len( polygon ) ):
		point = polygon[ pointIndex ]
		secondPoint  = polygon[ ( pointIndex + 1 ) % len( polygon ) ]
		area  = point.x * secondPoint.y - secondPoint.x * point.y
		polygonArea += area
	return 0.5 * polygonArea

def getPolygonLength( polygon ):
	"Get the length of a polygon perimeter."
	polygonLength = 0.0
	for pointIndex in range( len( polygon ) ):
		point = polygon[ pointIndex ]
		secondPoint  = polygon[ ( pointIndex + 1 ) % len( polygon ) ]
		polygonLength += point.distance( secondPoint )
	return polygonLength

def getRotatedClockwiseQuarterAroundZAxis( vector3 ):
	"Get vector3 rotated a quarter clockwise turn around Z axis."
	return Vec3( vector3.y, - vector3.x, vector3.z )

def getRotatedWiddershinsQuarterAroundZAxis( vector3 ):
	"Get Vec3 rotated a quarter widdershins turn around Z axis."
	return Vec3( - vector3.y, vector3.x, vector3.z )

def getRoundedPoint( point ):
	"Get point with each component rounded."
	return Vec3( round( point.x ), round( point.y ), round( point.z ) )

def getRoundedToThreePlaces( number ):
	"Get value rounded to three places as string."
	return str( 0.001 * math.floor( number * 1000.0 + 0.5 ) )

def getRoundXAxis( angle, vector3 ):
	"""Get Vec3 rotated around X axis from widdershins angle and Vec3.

	Keyword arguments:
	angle - widdershins angle from 1, 0
	vector3 - Vec3 whose rotation will be returned"""
	x = math.cos( angle );
	y = math.sin( angle );
	return Vec3( vector3.x, vector3.y * x - vector3.z * y, vector3.y * y + vector3.z * x )

def getRoundYAxis( angle, vector3 ):
	"""Get Vec3 rotated around Y axis from widdershins angle and Vec3.

	Keyword arguments:
	angle - widdershins angle from 1, 0
	vector3 - Vec3 whose rotation will be returned"""
	x = math.cos( angle );
	y = math.sin( angle );
	return Vec3( vector3.x * x - vector3.z * y, vector3.y, vector3.x * y + vector3.z * x )

def getRoundZAxis( angle, vector3 ):
	"""Get Vec3 rotated around Z axis from widdershins angle and Vec3.

	Keyword arguments:
	angle - widdershins angle from 1, 0
	vector3 - Vec3 whose rotation will be returned"""
	x = math.cos( angle );
	y = math.sin( angle );
	return Vec3( vector3.x * x - vector3.y * y, vector3.x * y + vector3.y * x, vector3.z )

def getRoundZAxisByPlaneAngle( planeAngle, vector3 ):
	"""Get Vec3 rotated by a plane angle.

	Keyword arguments:
	planeAngle - plane angle of the rotation
	vector3 - Vec3 whose rotation will be returned"""
	return Vec3( vector3.x * planeAngle.real - vector3.y * planeAngle.imag, vector3.x * planeAngle.imag + vector3.y * planeAngle.real, vector3.z )

def getSegmentsFromIntersections( solidXIntersectionList, y, z ):
	"Get endpoint segments from the intersections."
	segments = []
	xIntersectionList = []
	fill = False
	solid = False
	solidTable = {}
	solidXIntersectionList.sort( compareSolidXByX )
	for solidX in solidXIntersectionList:
		solidXYInteger = int( solidX.imag )
		if solidXYInteger >= 0:
			toggleHashtable( solidTable, solidXYInteger, "" )
		else:
			fill = not fill
		oldSolid = solid
		solid = ( len( solidTable ) == 0 and fill )
		if oldSolid != solid:
			xIntersectionList.append( solidX.real )
	for xIntersectionIndex in range( 0, len( xIntersectionList ), 2 ):
		firstX = xIntersectionList[ xIntersectionIndex ]
		secondX = xIntersectionList[ xIntersectionIndex + 1 ]
		endpointFirst = Endpoint()
		endpointSecond = Endpoint().getFromOtherPoint( endpointFirst, Vec3( secondX, y, z ) )
		endpointFirst.getFromOtherPoint( endpointSecond, Vec3( firstX, y, z ) )
		segment = ( endpointFirst, endpointSecond )
		segments.append( segment )
	return segments

def getSimplifiedLoop( loop, radius ):
	"Get loop with points inside the channel removed."
	if len( loop ) < 2:
		return loop
	simplificationMultiplication = 256
	simplificationRadius = radius / float( simplificationMultiplication )
	maximumIndex = len( loop ) * simplificationMultiplication
	pointIndex = 1
	while pointIndex < maximumIndex:
		loop = getHalfSimplifiedLoop( loop, simplificationRadius, 0 )
		loop = getHalfSimplifiedLoop( loop, simplificationRadius, 1 )
		simplificationRadius += simplificationRadius
		simplificationRadius = min( simplificationRadius, radius )
		pointIndex += pointIndex
	return getAwayPath( loop, radius )

def getSurroundingLoops( extrusionWidth, loops ):
	"Get surrounding loops from loops."
	outsides = []
	insides = getInsidesAddToOutsides( loops, outsides )
	surroundingLoops = []
	for outside in outsides:
		surroundingLoops.append( SurroundingLoop().getFromInsides( extrusionWidth, insides, outside ) )
	return surroundingLoops

def getTransferClosestSurroundingLoop( oldOrderedLocation, remainingSurroundingLoops, skein ):
	"Get and transfer the closest remaining surrounding loop."
	closestDistanceSquared = 999999999999999999.0
	closestSurroundingLoop = None
	for remainingSurroundingLoop in remainingSurroundingLoops:
		distanceSquared = getNearestDistanceSquaredIndex( oldOrderedLocation, remainingSurroundingLoop.loop ).real
		if distanceSquared < closestDistanceSquared:
			closestDistanceSquared = distanceSquared
			closestSurroundingLoop = remainingSurroundingLoop
	remainingSurroundingLoops.remove( closestSurroundingLoop )
	closestLoop = closestSurroundingLoop.loop
	closestSurroundingLoop.addToThreads( oldOrderedLocation, skein )
	return closestSurroundingLoop

def getTransferredPaths( insides, loop ):
	"Get transferred paths from inside paths."
	transferredPaths = []
	for insideIndex in range( len( insides ) - 1, - 1, - 1 ):
		inside = insides[ insideIndex ]
		if isPathInsideLoop( loop, inside ):
			transferredPaths.append( inside )
			del insides[ insideIndex ]
	return transferredPaths

def getXIntersection( firstPoint, secondPoint, y ):
	"Get where the line crosses y."
	secondMinusFirst = secondPoint.minus( firstPoint )
	yMinusFirst = y - firstPoint.y
	return yMinusFirst / secondMinusFirst.y * secondMinusFirst.x + firstPoint.x

def getWiddershinsDot( vec3First, vec3Second ):
	"Get the magintude of the positive dot product plus one of the x and y components of a pair of Vec3s, with the reversed sign of the cross product."
	dot = getPlaneDotPlusOne( vec3First, vec3Second )
	zCross = getZComponentCrossProduct( vec3First, vec3Second )
	if zCross >= 0.0:
		return - dot
	return dot

def getZComponentCrossProduct( vec3First, vec3Second ):
	"Get z component cross product of a pair of Vec3s."
	return vec3First.x * vec3Second.y - vec3First.y * vec3Second.x

def isClose( overlapDistanceSquared, loop, pointIndex ):
	"Determine if the the point close to another point on the loop."
	point = loop[ pointIndex ]
	for overlapPoint in loop[ : pointIndex ]:
		if overlapPoint.distance2( point ) < overlapDistanceSquared:
			return True
	return False

def isInsideOtherLoops( loopIndex, loops ):
	"Determine if a loop in a list is inside another loop in that list."
	return isPathInsideLoops( loops[ : loopIndex ] + loops[ loopIndex + 1 : ], loops[ loopIndex ] )

def isLineIntersectingInsideXSegment( segmentFirstX, segmentSecondX, vector3First, vector3Second, y ):
	"Determine if the line is crossing inside the x segment."
	isYAboveFirst = y > vector3First.y
	isYAboveSecond = y > vector3Second.y
	if isYAboveFirst == isYAboveSecond:
		return False
	xIntersection = getXIntersection( vector3First, vector3Second, y )
	if xIntersection <= min( segmentFirstX, segmentSecondX ):
		return False
	return xIntersection < max( segmentFirstX, segmentSecondX )

def isLoopIntersectingInsideXSegment( loop, segmentFirstX, segmentSecondX, segmentYMirror, y ):
	"Determine if the loop is intersecting inside the x segment."
	rotatedLoop = getPathRoundZAxisByPlaneAngle( segmentYMirror, loop )
	for pointIndex in range( len( rotatedLoop ) ):
		pointFirst = rotatedLoop[ pointIndex ]
		pointSecond = rotatedLoop[ ( pointIndex + 1 ) % len( rotatedLoop ) ]
		if isLineIntersectingInsideXSegment( segmentFirstX, segmentSecondX, pointFirst, pointSecond, y ):
			return True
	return False

def isLoopListIntersectingInsideXSegment( loopList, segmentFirstX, segmentSecondX, segmentYMirror, y ):
	"Determine if the loop list is crossing inside the x segment."
	for alreadyFilledLoop in loopList:
		if isLoopIntersectingInsideXSegment( alreadyFilledLoop, segmentFirstX, segmentSecondX, segmentYMirror, y ):
			return True
	return False

def isPathInsideLoop( loop, path ):
	"Determine if a path is inside another loop."
	leftPoint = getLeftPoint( path )
	return getNumberOfIntersectionsToLeft( leftPoint, loop ) % 2 == 1

def isPathInsideLoops( loops, path ):
	"Determine if a path is inside another loop in a list."
	for loop in loops:
		if isPathInsideLoop( loop, path ):
			return True
	return False

"""
#later see if this version of isPathInsideLoops should be used
def isPathInsideLoops( loops, path ):
	"Determine if a path is inside another loop in a list."
	for loop in loops:
		if not isPathInsideLoop( loop, path ):
			return False
	return True
"""

def isSegmentCompletelyInX( segment, xFirst, xSecond ):
	"Determine if the segment overlaps within x."
	segmentFirstX = segment[ 0 ].point.x
	segmentSecondX = segment[ 1 ].point.x
	if max( segmentFirstX, segmentSecondX ) > max( xFirst, xSecond ):
		return False
	return min( segmentFirstX, segmentSecondX ) >= min( xFirst, xSecond )

def isWiddershins( polygon ):
	"Determines if the polygon goes round in the widdershins direction."
	return getPolygonArea( polygon ) > 0.0

def isWithinChannel( channelRadius, pointIndex, loop ):
	"Determine if the the point is within the channel between two adjacent points."
	point = loop[ pointIndex ]
	behindPosition = loop[ ( pointIndex + len( loop ) - 1 ) % len( loop ) ]
	behindSegment = behindPosition.minus( point )
	behindSegmentLength = behindSegment.length()
	if behindSegmentLength < channelRadius:
		return True
	aheadPosition = loop[ ( pointIndex + 1 ) % len( loop ) ]
	aheadSegment = aheadPosition.minus( point )
	aheadSegmentLength = aheadSegment.length()
	if aheadSegmentLength < channelRadius:
		return True
	behindSegment.scale( 1.0 / behindSegmentLength )
	aheadSegment.scale( 1.0 / aheadSegmentLength )
	absoluteZ = getPlaneDotPlusOne( aheadSegment, behindSegment )
	if behindSegmentLength * absoluteZ < channelRadius:
		return True
	if aheadSegmentLength * absoluteZ < channelRadius:
		return True
	return False

def toggleHashtable( hashtable, key, value ):
	"Toggle a hashtable between having and not having a key."
	if key in hashtable:
		del hashtable[ key ]
	else:
		hashtable[ key ] = value

def transferClosestFillLoop( extrusionHalfWidthSquared, oldOrderedLocation, remainingFillLoops, skein ):
	"Transfer the closest remaining fill loop."
	closestDistanceSquared = 999999999999999999.0
	closestFillLoop = None
	for remainingFillLoop in remainingFillLoops:
		distanceSquared = getNearestDistanceSquaredIndex( oldOrderedLocation, remainingFillLoop ).real
		if distanceSquared < closestDistanceSquared:
			closestDistanceSquared = distanceSquared
			closestFillLoop = remainingFillLoop
	remainingFillLoops.remove( closestFillLoop )
	addToThreadsFromLoop( extrusionHalfWidthSquared, '', closestFillLoop[ : ], oldOrderedLocation, skein )

def transferClosestPath( oldOrderedLocation, remainingPaths, skein ):
	"Transfer the closest remaining path."
	closestDistanceSquared = 999999999999999999.0
	closestPath = None
	for remainingPath in remainingPaths:
		distanceSquared = min( oldOrderedLocation.distance2( remainingPath[ 0 ] ), oldOrderedLocation.distance2( remainingPath[ - 1 ] ) )
		if distanceSquared < closestDistanceSquared:
			closestDistanceSquared = distanceSquared
			closestPath = remainingPath
	remainingPaths.remove( closestPath )
	if oldOrderedLocation.distance2( closestPath[ - 1 ] ) < oldOrderedLocation.distance2( closestPath[ 0 ] ):
		closestPath.reverse()
	skein.addGcodeFromGcodeThread( 'M101', closestPath ) # Turn extruder on.
	oldOrderedLocation.setToVec3( closestPath[ - 1 ] )

def transferPathsToSurroundingLoops( paths, surroundingLoops ):
	"Transfer paths to surrounding loops."
	for surroundingLoop in surroundingLoops:
		surroundingLoop.transferPaths( paths )


class Endpoint:
	"The endpoint of a segment."
	def __repr__( self ):
		"Get the string representation of this Endpoint."
		return 'Endpoint ' + str( self.touched ) + str( self.point ) + ' ' + str( self.otherEndpoint.point )

	def getFromOtherPoint( self, otherEndpoint, point ):
		"Initialize from other endpoint."
		self.otherEndpoint = otherEndpoint
		self.point = point
		self.touched = False
		return self

	def getNearestEndpoint( self, endpoints ):
		"Get nearest endpoint."
		smallestDistanceSquared = 999999999999999999.0
		nearestEndpoint = None
		for endpoint in endpoints:
			distanceSquared = self.point.distance2( endpoint.point )
			if distanceSquared < smallestDistanceSquared:
				smallestDistanceSquared = distanceSquared
				nearestEndpoint = endpoint
		return nearestEndpoint

	def getNearestMiss( self, arounds, endpoints, extrusionWidth, path, stretchedXSegments ):
		"Get the nearest endpoint which the segment to that endpoint misses the other extrusions."
		smallestDistanceSquared = 999999999999999999.0
		nearestMiss = None
		penultimateMinusPoint = complex( 0.0, 0.0 )
		if len( path ) > 1:
			penultimateMinusPoint = path[ - 2 ].dropAxis( 2 ) - self.point.dropAxis( 2 )
			if abs( penultimateMinusPoint ) > 0.0:
				penultimateMinusPoint /= abs( penultimateMinusPoint )
		for endpoint in endpoints:
			segment = endpoint.point.minus( self.point )
			normalizedSegment = segment.dropAxis( 2 )
			normalizedSegmentLength = abs( normalizedSegment )
			if normalizedSegmentLength > 0.0:
				normalizedSegment /= normalizedSegmentLength
				segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
				segmentFirstPoint = getRoundZAxisByPlaneAngle( segmentYMirror, self.point )
				segmentSecondPoint = getRoundZAxisByPlaneAngle( segmentYMirror, endpoint.point )
				distanceSquared = self.point.distance2( endpoint.point )
				if distanceSquared < smallestDistanceSquared:
					if not isLoopListIntersectingInsideXSegment( arounds, segmentFirstPoint.x, segmentSecondPoint.x, segmentYMirror, segmentFirstPoint.y ):
						if not self.isPointIntersectingSegments( extrusionWidth, endpoint.point, stretchedXSegments ):
							if penultimateMinusPoint.real * normalizedSegment.real + penultimateMinusPoint.imag * normalizedSegment.imag < 0.8:
								smallestDistanceSquared = distanceSquared
								nearestMiss = endpoint
			else:
				print >> sys.stderr, ( 'This should never happen, the endpoints are touching' )
				print >> sys.stderr, ( endpoint )
				print >> sys.stderr, ( path )
		return nearestMiss

	def isOtherEndpointExtrudable( self, path ):
		"Determine if the other endpoint is not touched and if it can be extruded without doubling back."
		self.touched = True
		#if not doubling back below & nextEndpoint.otherEndpoint.touched == False, else otherEndpoint = nextEndpoint & nextEndpoint.touched = True
		if self.otherEndpoint.touched:
			return False
		if len( path ) < 2:
			return True
		pointComplex = self.point.dropAxis( 2 )
		penultimateMinusPoint = path[ - 2 ].dropAxis( 2 ) - pointComplex
		if abs( penultimateMinusPoint ) == 0.0:
			return True
		penultimateMinusPoint /= abs( penultimateMinusPoint )
		normalizedSegment = self.otherEndpoint.point.dropAxis( 2 ) - pointComplex
		normalizedSegmentLength = abs( normalizedSegment )
		if normalizedSegmentLength == 0.0:
			return True
		normalizedSegment /= normalizedSegmentLength
		return penultimateMinusPoint.real * normalizedSegment.real + penultimateMinusPoint.imag * normalizedSegment.imag < 0.95

	def isPointIntersectingSegments( self, extrusionWidth, inputPoint, stretchedXSegments ):
		"Determine if the segment to the point is crossing a stretched x segment."
		segment = inputPoint.minus( self.point )
		alongSegmentLength = min( 0.333 * segment.length(), 0.2 * extrusionWidth ) #later find a more reliable way of avoiding an overlap
		segment.scale( alongSegmentLength / segment.length() )
		attractedPoint = self.point.plus( segment )
		attractedInputPoint = inputPoint.minus( segment )
		for stretchedXSegment in stretchedXSegments:
			if isLineIntersectingInsideXSegment( stretchedXSegment.xMinimum, stretchedXSegment.xMaximum, attractedPoint, attractedInputPoint, stretchedXSegment.y ):
				return True
		return False


class SurroundingLoop:
	"A loop that surrounds paths."
	def __repr__( self ):
		"Get the string representation of this surrounding loop."
		return '%s, %s, %s' % ( self.loop, self.innerSurroundings, self.paths )

	def addToThreads( self, oldOrderedLocation, skein ):
		"Add to paths from the last location."
		addToThreadsFromLoop( self.extrusionHalfWidthSquared, 'edge', self.loop[ : ], oldOrderedLocation, skein )
		addToThreadsRemoveFromSurroundings( oldOrderedLocation, self.innerSurroundings, skein )
		if self.lastFillLoops != None:
			remainingFillLoops = self.lastFillLoops[ : ]
			while len( remainingFillLoops ) > 0:
				transferClosestFillLoop( self.extrusionHalfWidthSquared, oldOrderedLocation, remainingFillLoops, skein )
		remainingPaths = self.paths[ : ]
		while len( remainingPaths ) > 0:
			transferClosestPath( oldOrderedLocation, remainingPaths, skein )

	def getFillLoops( self ):
		"Get last fill loops from the outside loop and the loops inside the inside loops."
		fillLoops = self.getLoopsToBeFilled()[ : ]
		for surroundingLoop in self.innerSurroundings:
			fillLoops += getFillOfSurroundings( surroundingLoop.innerSurroundings )
		return fillLoops

	def getFromInsides( self, extrusionWidth, inputInsides, loop ):
		"Initialize from inside loops."
		self.extraLoops = []
		self.extrusionHalfWidthSquared = 0.25 * extrusionWidth * extrusionWidth
		self.extrusionWidth = extrusionWidth
		self.loop = loop
		transferredLoops = getTransferredPaths( inputInsides, loop )
		self.innerSurroundings = getSurroundingLoops( extrusionWidth, transferredLoops )
		self.lastFillLoops = None
		self.paths = []
		return self

	def getLoopsToBeFilled( self ):
		"Get last fill loops from the outside loop and the loops inside the inside loops."
		if self.lastFillLoops != None:
			return self.lastFillLoops
		loopsToBeFilled = [ self.loop ]
		for surroundingLoop in self.innerSurroundings:
			loopsToBeFilled.append( surroundingLoop.loop )
		return loopsToBeFilled

	def transferPaths( self, paths ):
		"Transfer paths."
		for surroundingLoop in self.innerSurroundings:
			transferPathsToSurroundingLoops( paths, surroundingLoop.innerSurroundings )
		self.paths = getTransferredPaths( paths, self.loop )


