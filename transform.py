import numpy as np
import math
import pycurl
import StringIO
import xml.etree.ElementTree as ET
import json


pi_value = math.pi * 3000 / 180.0;

def BD09_To_GCJ02(lng, lat):
	x_lat = lng - 0.0065
	y_lng = lat - 0.006
	z = math.sqrt(x_lat * x_lat + y_lng * y_lng) - 0.00002 * math.sin(y_lng * pi_value)
	theta = math.atan2(y_lng, x_lat) - 0.000003 * math.cos(x_lat * pi_value)
	gcj02_lat = z * math.cos(theta)
	gcj02_lng = z * math.sin(theta)
	return [float(gcj02_lat), float(gcj02_lng)]

# For GPS point a, first get its coordination a' in Baidu, then use a' & function BD09_To_GCJ02 to get the calculated coodination in Gaode
def GPS_To_GCJ02(lnglats):
	baiduCoordinations = multiTransferBaidu(lnglats)
	result = map(transformFunction, baiduCoordinations)
	# print ";".join([str(latlng[0]) + "," + str(latlng[1]) for latlng in result])
	return result

def webTransfer(lat, lng):
	url = "http://restapi.amap.com/v3/assistant/coordinate/convert?locations=%f,%f&coordsys=baidu&output=xml&key=cd1d281de48e9a96e2d688ff6288e7a8" % (lng, lat)
	buf = StringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	e = ET.fromstring(buf.getvalue())
	result = []
	for latlng in e.findall('locations'):
		result = latlng.text.split(',')
		break
	buf.close()
	return result[0:2]

# others {"baidu", "gps"} to Gaode
def multiTransfer(latlngs, coordinate_type):
	# print ";".join([str(latlng[0]) + "," + str(latlng[1]) for latlng in latlngs])
	url = "http://restapi.amap.com/v3/assistant/coordinate/convert?locations=%s&coordsys=%s&output=xml&key=cd1d281de48e9a96e2d688ff6288e7a8" % (";".join([str(latlng[0]) + "," + str(latlng[1]) for latlng in latlngs]), coordinate_type)
	
	buf = StringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()
	
	e = ET.fromstring(buf.getvalue())

	locations = e.find("locations").text
	lnglats = locations.split(";")
	result = [ lnglat.split(',') for lnglat in lnglats]

	buf.close()
	return result

# GPS to Baidu
def multiTransferBaidu(latlngs):
	# print ";".join([str(latlng[0]) + "," + str(latlng[1]) for latlng in latlngs])
	url = "http://api.map.baidu.com/geoconv/v1/?coords=%s&from=1&to=5&ak=BqgNOpFhsxe6GdQZSwZWKoGU" % (";".join([str(latlng[0]) + "," + str(latlng[1]) for latlng in latlngs]))
	# print url
	buf = StringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	# print str(buf.getvalue())
	
	json_result = json.loads(buf.getvalue())['result']
	result = [[float(latlng['x']), float(latlng['y'])] for latlng in json_result]

	print ";".join([str(latlng[0]) + "," + str(latlng[1]) for latlng in result])

	buf.close()
	return result

transformFunction = lambda f : BD09_To_GCJ02(f[0], f[1])
transformFunction_gps2gaode = lambda f : GPS_To_GCJ02(f[0], f[1])


# calculate functions
def oneLine():
	stepCount = 700 # Length limit in HTTP Get with AMap request
	start = 90

	transformedCoordinates = []
	expectedCoordinates = []

	# lng range in lng -- (lng + 21)
	for index in range(30):
		originalCds = [[start + index * 0.7 + i / 1000.0, 30] for i in range(stepCount)]
		transformedCds = map(transformFunction, originalCds)
		expectedCds = multiTransfer(originalCds, "baidu")

		transformedCoordinates += transformedCds
		expectedCoordinates += expectedCds

	epCoordinates = [[float(exLng[0]), float(exLng[1])] for exLng in expectedCoordinates]
	tfCoordinates = [[float(transLng[0]), float(transLng[1])] for transLng in transformedCoordinates]
	errors = np.array(epCoordinates) - np.array(tfCoordinates)

	print "max: " + str(errors.max()) + ", min: " + str(errors.min())

# one line across [90, 30] to [111, 30]
#oneLine()


# net Hangzhou, from [120.002632, 30.131888] lng + 0.38, lat + 0.27
def hangzhouNet():
	stepCount = 300
	start = [120.002632, 30.131888]
	transformedCoordinates = []
	expectedCoordinates = []

	for index in range(70):
		originalCds = [start + [index * (0.38/ 300/ 70) + i / stepCount, index * (0.27/ 300/70) + i / stepCount] for i in range(stepCount)]
		transformedCds = map(transformFunction, originalCds)
		expectedCds = multiTransfer(originalCds, "baidu")

		transformedCoordinates += transformedCds
		expectedCoordinates += expectedCds

	epCoordinates = [[float(exLng[0]), float(exLng[1])] for exLng in expectedCoordinates]
	tfCoordinates = [[float(transLng[0]), float(transLng[1])] for transLng in transformedCoordinates]
	errors = np.array(epCoordinates) - np.array(tfCoordinates)

	print "max: " + str(errors.max()) + ", min: " + str(errors.min())

# hangzhouNet()

def GPSBaseHangzhou():
	stepCount = 100 # Length limit in HTTP Get with AMap request
	lng_df = 0.38
	lat_df = 0.27
	number = 200
	start = [120.002632000, 30.131888000]

	transformedCoordinates = []
	expectedCoordinates = []
	originals = []

	for j in range(stepCount * number):
		originals += [(np.array(start) + np.array([float((i+1)/stepCount)/number * lng_df, float((j+1)/stepCount)/number*lat_df])).tolist() for i in range(stepCount * number)]

	# print ";".join(str(original[0]) + "," + str(original[1]) for original in originals)

	for index in range(number * stepCount * number):

		originalCds = originals[index * stepCount: (index+1) * stepCount]
		print ";".join(str(originalCd[0]) + "," + str(originalCd[1]) for originalCd in originalCds)
		transformedCds = GPS_To_GCJ02(originalCds)
		expectedCds = multiTransfer(originalCds, "gps")

		transformedCoordinates += transformedCds
		expectedCoordinates += expectedCds

	epCoordinates = [[float(exLng[0]), float(exLng[1])] for exLng in expectedCoordinates]
	tfCoordinates = [[float(transLng[0]), float(transLng[1])] for transLng in transformedCoordinates]
	errors = np.array(epCoordinates) - np.array(tfCoordinates)

	print "max: " + str(errors.max()) + ", min: " + str(errors.min())

GPSBaseHangzhou()

# step = ([float(expectedCoordinates[-1][0]), float(expectedCoordinates[-1][1])] - [float(expectedCoordinates[0][0]), float(expectedCoordinates[0][1]]) )/ (stepCount - 1)

# expectedCoordinates = np.array([transformedCoordinates + step * i for i in range(stepCount)])
# epCoordinates = [[float(exLng[0]), float(exLng[1])] for exLng in expectedCoordinates]

# errors = np.array(epCoordinates) - np.array(tfCoordinates)

# print ";".join([str(latlng[0]) + ',' + str(latlng[1]) for latlng in errors])

# print "Step: " + step 
# print ";".join([str(errorLatLng) for errorLatLng in errors])
# expectedCoordinates = np.array([transformedCoordinates[0] + step * i for i in range(stepCount)])


# errors = expectedCoordinates - transformedCoordinates



#p = [x * 10.0 for x in range(10)]

# for i in errors:
# 	print i


# i = 0
# p = 0
# acsending = True
# pi = 0
# for v in errors:
# 	if (v < p) == acsending:
# 		print "Inflection Point: %d %d %f" % (i - pi, i, v)
# 		pi = i
# 	acsending = v > p
# 	p = v
# 	i+=1