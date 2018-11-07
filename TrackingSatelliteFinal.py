
# coding: utf-8

# In[1]:


from pyorbital import tlefile
from pyorbital.orbital import Orbital
import datetime
import gpxpy
import gpxpy.gpx
import time
import calendar
import urllib
import webbrowser
import sys
import os
from math import *
import ephem
import requests
import threading as th
#import serial
#from interface import *
import webbrowser as wb
import struct
import re
#import defaults
import numpy as np 
import math


# In[2]:


#Declare global variables -> will ideally go into a config file

#Define a list of TLE's
tleList = ["amateur", "argos", "cubesat", "education", "engineering", "geo","gps-ops", "intelsat", 
           "resource", "science", "stations", "tdrss","tle-new", "visual", "weather"]

#defined the URL to fetch the TLE's
url = "http://www.celestrak.com/NORAD/elements/"
base_N2YO_URL =  'http://www.n2yo.com/satellite/?s='
base_CELESTRAK_URL = 'http://www.celestrak.com/NORAD/elements/'
CELESTRAK_paths = ('stations.txt', 'weather.txt', 'noaa.txt', 'goes.txt', 'resource.txt', 'sarsat.txt.', 'dmc.txt', 'tdrss.txt', 'argos.txt',
                                'geo.txt', 'intelsat.txt', 'gorizont.txt', 'raduga.txt', 'molniya.txt', 'iridium.txt', 'orbcomm.txt', 'globalstar.txt',
                                'amateur.txt', 'x-comm.txt', 'other-comm.txt', 'gps-ops.txt', 'glo-ops.txt', 'galileo.txt', 'beidou.txt',
                                'sbas.txt', 'nnss.txt', 'musson.txt', 'science.txt', 'geodetic.txt', 'engineering.txt', 'education.txt', 'military.txt',
                                'radat.txt', 'cubesat.txt', 'other.txt', 'tle-new.txt')
AMSAT_URL = 'http://www.amsat.org/amsat/ftp/keps/current/nasa.all'
#destination = "C:/Users/hp/Documents/Groundcloud/py-sat-track/ephemstuff"

#define the observer location
home = ephem.Observer()
home.lat = '19.01441'
home.lon = '72.84794'
#underscore because ele is not a method of ephem
home.elevation = 14
home.pressure = 0
home.horizon = '-0.34'
current_time = datetime.datetime.utcnow()
home.date = current_time


# In[3]:


#this function takes a decimanl lat lon and returns a degree
def degreeMinutes(lat, lon):
    
    stringList = []
    d1 = int(lat)
    m1 = int((abs(lat) - abs(d1)) * 60)
    s1 = (abs(lat) - abs(d1) - m1/60) * 3600
    
    if d1 >= 0:
        dir1 = 'N'
    else:
        dir1 = 'S'
    
    stringTemp1 = [str(abs(d1)), '°', str(m1), "'", str(round(s1, 1)), '"', dir1]
    stringTemp1 = ''.join(stringTemp1)

    d2 = int(lon)
    m2 = int((abs(lon) - abs(d2)) * 60)
    s2 = (abs(lon) - abs(d2) - m2/60) * 3600
    
    if d2 >= 0:
        dir2 = 'E'
    else:
        dir2 = 'W'
    
    stringTemp2 = [str(abs(d2)), '°', str(m2), "'", str(round(s2, 1)), '"', dir2]
    stringTemp2 = ''.join(stringTemp2)
    
    stringList.append(stringTemp1)
    stringList.append(stringTemp2)
    
    return stringList


# In[4]:


#This subroutine is meant for getting all TLE files 
#the tle files are stored in a subfolder 
def getAllTLEFiles():
               
    tleFiles = []
    for tle in tleList:
        nameTemp = []
        nameTemp.append(os.getcwd())
        nameTemp.append("/tle/")
        nameTemp.append(tle)
        nameTemp.append(".txt")
        nameTemp = ''.join(nameTemp)
        nameTemp = nameTemp.replace('\\', '/')
        tleFiles.append(nameTemp)
    
    return tleFiles


# In[5]:


#this function helps us form the tle links for individual tle files 
def getAllTLELinks():
    
    tleLinks = []
    
    for tle in tleList:
        fullUrl = []
        fullUrl.append(url)
        fullUrl.append(tle)
        fullUrl.append(".txt")
        fullUrl = ''.join(fullUrl)
        tleLinks.append(fullUrl)
        
    return tleLinks


# In[6]:


#this subroutine helps us in getting the TLE file from the list in the subfolder depending on the user input 
def getTLEFile():
    
    nameTemp = []
    nameTemp.append(os.getcwd())
    nameTemp.append("/tle/")   
    while(True):
        tleName = input("Enter TLE File Name: ")        
        if tleName == 'f':
            for tleFile in tleList:
                print(tleFile)
            print()
        elif tleName in tleList:
            nameTemp.append(tleName)
            nameTemp.append(".txt")
            nameTemp = ''.join(nameTemp)
            nameTemp = nameTemp.replace('\\', '/')
            break       
        else:
            break
    
    return nameTemp


# In[7]:


#this function parses a tleinformation based on the satellite name and the platform name
#and prints information about the satellite 
def printTLEInfo(satellite, platformName):
    
    rightAscDM, LonDM = degreeMinutes(satellite.right_ascension, 0)
    
    print("Platform:", platformName,
          "\nSatellite Number:", satellite.satnumber,
          "\nClassification:", satellite.classification,
          "\nID Launch Year:", satellite.id_launch_year,
          "\nID Launch Number:", satellite.id_launch_number,
          "\nID Launch Piece:", satellite.id_launch_piece,
          "\nEpoch Year:", satellite.epoch_year,
          "\nEpoch Day:", satellite.epoch_day,
          "\nEpoch:", satellite.epoch,
          "\nMean Motion Derivative:", satellite.mean_motion_derivative,
          "\nMean Motion Sec Derivative:", satellite.mean_motion_sec_derivative,
          "\nB-Star:", satellite.bstar,
          "\nEphemeris Type:", satellite.ephemeris_type,
          "\nElement Number:", satellite.element_number,
          "\nInclination:", satellite.inclination,
          "\nRight Ascension:", satellite.right_ascension, '(', rightAscDM, ')',
          "\nExcentricity:", satellite.excentricity,
          "\nArg Perigee:", satellite.arg_perigee,
          "\nMean Anomaly:", satellite.mean_anomaly,
          "\nMean Motion:", satellite.mean_motion,
          "\nOrbit:", satellite.orbit)
    
    
    return satellite.satnumber


# In[9]:


#this function returns a list of stations depending on the tlefile    
def getStationList(tleFile):
    
    stationList = []
    file = open(tleFile)
    
    for line in file:
        nameTemp = line.replace("\n", '') 
        stationList.append(nameTemp)
        file.readline()
        file.readline()
        
    file.close()
    
    # visual sorted by brightness
    if "visual" not in tleFile:
        stationList = sorted(stationList)
    
    #print("number of stations", len(stationList))
    #for i in range(len(stationList)):
    #    print("Station Number",i, "Station Name", stationList[i])
    return stationList


# In[8]:


#this function returns a particular station name    
def getStationName(stationList, stationNumber):
    
    while(True):
        
        try:
            stationNumber = input("Enter Station Number: ")
            print()
            
            if stationNumber == 'n':
                for name in enumerate(stationList):
                    print(name[0], ':', name[1].replace('\n', ''))
                print()
        except:
            pass


# In[10]:


def printFreqData(freqLines):

    for line in freqLines:
        satName, number, uplink, downlink, beacon, mode, callsign, status = line.split(";", maxsplit=7)
        
        print("Radio Info:", "\nName: ", satName, "\nNumber: ", number, "\nUplink Frequency(MHz): ", uplink, "\nDownlink Frequency(MHz): ", downlink,
              "\nBeacon: ", beacon, "\nMode: ", mode, "\nCall Sign: ", callsign, "\nStatus: ", status, sep='')


# In[11]:


#getting obeservers lat long
#import geocoder
#g = geocoder.ip('me')
#lat, long = g.latlng
#print(lat,long,ele)


# In[12]:


def setLocation(lat, lon, ele):
        observer_lat = str(lat)
        observer_lon = str(lon)
        observer_elev = int(ele)
        observer_epoch = ephem.Date(str(current_time))
        observer_date = ephem.Date(str(current_time))
        print('Location ' + str(lat) + 'N; ' + str(lon) + 'E; ' + str(ele) + 'm elevation.')
        return observer_lat, observer_lon, observer_elev, observer_epoch, observer_date


# In[13]:


def UpdateKeplers():
    
    tleLinks = getAllTLELinks()
    tleFiles = getAllTLEFiles()
    
    tleList = list(zip(tleLinks, tleFiles))
    
    print("Keplers:")
    
    for tle in tleList:
        
        urllib.request.urlretrieve(tle[0], tle[1])
        
        print("Downloaded", tle[0])


# In[14]:


def UpdateFrequencies():
    
    url = "http://www.ne.jp/asahi/hamradio/je9pel/satslist.csv"
    
    print("Frequencies:")
    
    fileName = []
    fileName.append(os.getcwd())
    fileName.append("/frequencies/")
    fileName.append("satslist.csv")
    fileName = ''.join(fileName)
    
    urllib.request.urlretrieve(url, fileName)
    
    print("Downloaded", url)
        


# In[15]:


def getGPSPosition(platformName, tleFile, dateTime):
    
    orb = Orbital(platformName, tleFile)
    lon, lat, alt = orb.get_lonlatalt(dateTime)
    
    #reading the TLE file
    file = open(tleFile)
    data = file.read().replace("\n","::")    
    arr = data.split("::")

    for i in range(len(arr)):
        if platformName.rstrip() == arr[i].rstrip():
            tleOne= arr[i+1]
            tleTwo = arr[i+2]
    file.close()
    
    sat = ephem.readtle(platformName, tleOne, tleTwo)
    #compute satellite position
    sat.compute(dateTime)
    
    satlat =  math.degrees(sat.sublat)
    satlon = math.degrees(sat.sublong)
    satele = sat.elevation
    satsize = sat.size
    satrad = sat.radius
    satecl = sat.eclipsed
    satasc = sat.a_ra
    satdecl = sat.a_dec
    
    return [satlon, satlat, satele, satsize, satrad, satecl, satasc, satdecl]


# In[17]:


def getFreqData(sateliteNumber, freqFileName):
    
    freqFile = open(freqFileName)
    freqData = freqFile.readlines()   
    freqFile.close()
    
    freqLines = []

    for line in freqData:
        satName, satNum = line.split(';', maxsplit=1)
        satName = satName.upper()
        satNum = satNum.upper()
        
        if sateliteNumber.rstrip() in satNum.rstrip():
            freqLines.append(line)
        
    return freqLines


# In[16]:


def frequencyLookUp(freqFile):
    
    print()
    satName = input("Enter Satellite Name: ")
    satName = satName.upper()
    printFreqData(GetFreqData(satName, freqFile))


# In[18]:


def azimuthDirection(azimuthAngle):

    """   
    North	0°	South	180°
    North-Northeast	22.5°	South-Southwest	202.5°
    Northeast	45°	Southwest	225°
    East-Northeast	67.5°	West-Southwest	247.5°
    East	90°	West	270°
    East-Southeast	112.5°	West-Northwest	292.5°
    Southeast	135°	Northwest	315°
    South-Southeast	157.5°	North-Northwest	337.5°
    """
    
    direction = "Unknown Direction"
    
    north = (0.0, 360.0, "North")
    northNorthEast = (22.5, "N-NE")
    northEast = (45.0, "NE")
    eastNorthEast = (67.5, "E-NE")
    east = (90.0, "E")
    eastSouthEast = (112.5, "E-SE")
    southEast = (135.0, "SE")
    southSouthEast = (157.5, "S-SE")
    south = (180.0, "S")
    southSouthWest = (202.5, "S-SW")
    southWest = (225.0, "SW")
    westSouthWest = (247.5, "W-SW")
    west = (270.0, "W")
    westNorthWest = (292.5, "W-NW")
    northWest = (315.0, "NW")
    northNorthWest = (337.5, "N-NW")
      
    if azimuthAngle == north[0]:
        direction = north[2]     
        
    elif azimuthAngle > north[0] and azimuthAngle <= northNorthEast[0]:
        direction = northNorthEast[1]     
    elif azimuthAngle > northNorthEast[0] and azimuthAngle < eastNorthEast[0]:
        direction = northEast[1]
    elif azimuthAngle >= eastNorthEast[0] and azimuthAngle < east[0]:
        direction = eastNorthEast[1]
        
    elif azimuthAngle == east[0]:
        direction = east[1]
        
    elif azimuthAngle > east[0] and azimuthAngle <= eastSouthEast[0]:
        direction = eastSouthEast[1]     
    elif azimuthAngle > eastSouthEast[0] and azimuthAngle < southSouthEast[0]:
        direction = southEast[1]
    elif azimuthAngle >= southSouthEast[0] and azimuthAngle < south[0]:
        direction = southSouthEast[1]
        
    elif azimuthAngle == south[0]:
        direction = south[1]
        
    elif azimuthAngle > south[0] and azimuthAngle <= southSouthWest[0]:
        direction = southSouthWest[1]     
    elif azimuthAngle > southSouthWest[0] and azimuthAngle < westSouthWest[0]:
        direction = southWest[1]
    elif azimuthAngle >= westSouthWest[0] and azimuthAngle < west[0]:
        direction = westSouthWest[1]
        
    elif azimuthAngle == west[0]:
        direction = west[1]
        
    elif azimuthAngle > west[0] and azimuthAngle <= westNorthWest[0]:
        direction = westNorthWest[1]     
    elif azimuthAngle > westNorthWest[0] and azimuthAngle < northNorthWest[0]:
        direction = northWest[1]
    elif azimuthAngle >= northNorthWest[0] and azimuthAngle < north[1]:
        direction = northNorthWest[1]
        
    return direction


# In[19]:


def serialPortRead(passNumber):
    #passes = satOrb.get_next_passes(datetime.utcnow(),120, -30.8047389406, 72.9167, 180.85)
    
    #next get number of passes the user wants  
    satOrb = Orbital(satName, tleFile)
    passes = satOrb.get_next_passes(current_time,int(passNumber), home.lat, home.lon, home.elevation)
    for eachPass in passes:
                rise = eachPass[0]
                fall = eachPass[1]
                apex = eachPass[2]
                
                # Lon, Lat
                obsRiseAngle, obsRiseElv = satOrb.get_observer_look(rise, home.lat, home.lon, home.elevation)
                obsFallAngle, obsFallElv = satOrb.get_observer_look(fall, home.lat, home.lon, home.elevation)
                obsApexAngle, obsApexElv = satOrb.get_observer_look(apex, home.lat, home.lon, home.elevation)
                print("observer apex", obsApexElv)
                print("Rise Time:", rise, "Azimuth:", round(obsRiseAngle, 2), 
                          '(', azimuthDirection(obsRiseAngle), ')', "Elevation:", abs(round(obsRiseElv, 2)))
                    
                print("Apex Time:", apex, "Azimuth:", round(obsApexAngle, 2),
                          '(', azimuthDirection(obsApexAngle), ')', "Elevation:", abs(round(obsApexElv, 2)))
                          
                print("Fall Time:", fall, "Azimuth:", round(obsFallAngle, 2), 
                          '(', azimuthDirection(obsFallAngle), ')', "Elevation:", abs(round(obsFallElv, 2)))
                print()
                return


# In[21]:


def predictNextPasses(satName, tleFile, nextPasses):
    
    #reading the TLE file
    file = open(tleFile)
    data = file.read().replace("\n","::")    
    arr = data.split("::")

    for i in range(len(arr)):
        if satName.rstrip() == arr[i].rstrip():
            tleOne= arr[i+1]
            tleTwo = arr[i+2]
    file.close()
    
    #initialise the ephem object
    satephem = ephem.readtle(satName,tleOne,tleTwo)
    home.elevation = 60
    
    #next pass returns
    #0  Rise time
    #1  Rise azimuth
    #2  Maximum altitude time
    #3  Maximum altitude
    #4  Set time
    #5  Set azimuth

    for p in range(int(nextPasses)):
        tr, azr, tt, altt, ts, azs = home.next_pass(satephem)
        home.date = tr #set the observer date as rise time
        satephem.compute(home) #for every rise time compute the position
        print("Pass -->", p,"\n")
        print(
        "time rise -->",tr, "\n",
        "altitude -->",math.degrees(satephem.alt),"\n",
        "azimuth -->",math.degrees(satephem.az), "\n",
        "latitude-->",math.degrees(satephem.sublat), "\n",
        "longitude -->",math.degrees(satephem.sublong), "\n",
        "elevation -->",satephem.elevation/1000.)
        tr = ephem.Date(tr + 20.0 * ephem.second)
        print()
        home.date = tr + ephem.minute
    return


# In[20]:


def seconds_between(d1, d2):
    return abs((d2 - d1).seconds)


# In[22]:


def datetime_from_time(tr):
    year, month, day, hour, minute, second = tr.tuple()
    dt = datetime.datetime(year, month, day, hour, minute, int(second))
    return dt


# In[23]:


def get_next_pass(satName,lon, lat, alt, tleFile, nextPasses):
    
    #reading the TLE file
    file = open(tleFile)
    data = file.read().replace("\n","::")    
    arr = data.split("::")

    for i in range(len(arr)):
        if satName.rstrip() == arr[i].rstrip():
            tleOne= arr[i+1]
            tleTwo = arr[i+2]
    file.close()
    sat = ephem.readtle(satName, tleOne, tleTwo)
    
    for p in range(int(nextPasses)):
        #getting the observer details
        tr, azr, tt, altt, ts, azs = home.next_pass(sat)
        while tr < ts :
            home.date = tr
            duration = int((ts - tr) *60*60*24)
            rise_time = datetime_from_time(tr)
            max_time = datetime_from_time(tt)
            set_time = datetime_from_time(ts)
            #observer.date = max_time
            sun = ephem.Sun()
            sun.compute(home)
            sat.compute(home)
            sun_alt = degrees(sun.alt)
            
            #for checking if a pass is visible  
            visible = False
            if sat.eclipsed is False and -18 < degrees(sun_alt) < -6 :
                visible = True
            
            print("observer datetime --->",tr,"\n",
                  "rise time --->",rise_time,"\n",
                  "duration in seconds --->",duration,"\n",
                  "rise azimuth --->",degrees(azr),"\n",
                  #"maximum time --->",calendar.timegm(max_time.timetuple()),"\n",
                  #"maximum elevation --->",sat.elevation/1000,"\n",
                  "maximum alt --->",degrees(altt),"\n",
                  "set azimuth --->",degrees(azs),"\n",
                  "set time --->",set_time,"\n",
                  #"satellite latitude --->", math.degrees(sat.sublat),"\n",
                  #"satellite longitude --->", math.degrees(sat.sublong),"\n",
                  #"satellite altitude --->", sat.alt,"\n",
                  #"satellite azimath --->", sat.az,"\n",
                  "is it visible? --->", visible)
            tr = ephem.Date(tr + 600.0 * ephem.second)
            print("------------------------------------------------------------") 
            home.date = tr + ephem.minute
    return


# In[24]:


# degrees_per_radian = 180.0 / math.pi
#home = ephem.Observer()

print("Observer location latitude and elevation are")
observer_lat, observer_lon, observer_elev, observer_epoch, observer_date = setLocation(home.lat, home.lon, home.elevation)
print("\n------------------------------------------------------------------------------------------------------------\n")

updateFiles = input("Do you want to update the files (Y/N) ?")  
if updateFiles in ("Y","y"):
    #update all TLE files
    print("updating all TLE's")
    UpdateKeplers()
    print()
    #update all frequencies
    print("Updating all frquencies")
    UpdateFrequencies()
    print()

print("\n------------------------------------------------------------------------------------------------------------\n")
#next take user input on the tle name 
print("The list of tle names are : ", tleList)
print()
print("\n------------------------------------------------------------------------------------------------------------\n")
#get the tle file for the input 
tleFile = getTLEFile()

#take the user input on the satellite id from the list of satellite name in the tle
print("\n Tle file found for this name is: ", tleFile)
print()
#print("\n List of satelites for this TLE are :  ")
#print()

#after that for the satellite id, return all the tle parameters
#stationName = input("Enter Station Name: ")  
satNameUser = input("Enter Station Name: ")  
stationList=getStationList(tleFile)

for satelitename in stationList:
    if satelitename.rstrip() == satNameUser:
        satName = satNameUser
        
#satNumber = int(stationNumber)
#satName = stationList[satNumber]

try:
    stationObject = tlefile.read(satName, tleFile)
except:
    print("No satelite name matched, look at the following list and select the satelite number")
    print("\n List of satelites for this TLE are :  \n")
    stationList=getStationList(tleFile)
    for i in range(len(stationList)):
        print("Station Number",i, "Station Name", stationList[i])
    stationNumber = input("\n Enter Station Name: ")  
    satNumber = int(stationNumber)
    satName = stationList[satNumber]

# Print Platform Info
print("\n For the station number entered the TLE information are : \n")
stationObject = tlefile.read(satName, tleFile)
satTLENumber = printTLEInfo(stationObject, satName)
print()
print("\n------------------------------------------------------------------------------------------------------------\n")

print("The satelite name is : ", satName)
print("The satelite number is : ", satTLENumber)


#compute rise and set of satellite compared to groundstation 

#next get the current position of the satellite 
print("\n Current Position of the satellite is : ")
print()
satlon, satlat, satele, satsize, satrad, satecl, satasc, satdecl = getGPSPosition(satName, tleFile, current_time)                    
dmLon, dmLat = degreeMinutes(satlon, satlat)

print("\nLatitude --->", satlat, 
      "\nLongitude --->",satlon, 
      "\nelevation --->", satele/1000, 
      "\nsize --->", satsize,
      "\nradius --->", satrad,
      "\neclipsed --->", satecl,
      "\nright ascension --->", satasc,
      "\ndeclination --->", satdecl,
      "\nLatitude in degrees --->", dmLat, 
      "\nLongitude in degrees --->",dmLon)
print()


print("Frequency details for this satellite are : ")
satTLENumber = str(satTLENumber)
printFreqData(getFreqData(satTLENumber, "C:/Users/hp/Documents/Groundcloud/py-sat-track/frequencies/satfreqlist.csv"))

print()

#take the number of passes (number) and predict the passes for the satellite 
nextPasses = input("Enter the number of passes you want to predict ?")  
print("\n Next",nextPasses,"passes for every 10 minutes are predicted as follows:\n")
get_next_pass(satName,home.long, home.lat, home.elevation, tleFile,nextPasses)


#next prints the current altitude (in degrees above the horizon)
#and azimuth (heading in degrees "clockwise" from North).
#Now all I have to do is pump these numbers out a serial port to an Arduino controlling a 
#couple of servos, and I should be good to go!
#serialPortRead(nextPasses)


