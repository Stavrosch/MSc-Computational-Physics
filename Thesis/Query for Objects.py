import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle
from astropy.time import Time
from astropy.table import Table
from astroquery.mpc import MPC
from pytz import timezone
from datetime import datetime, timedelta, date
from suntime import Sun
import requests
import numpy as np
from dateutil import tz
import os 
from astroquery.jplsbdb import SBDB
import numpy as np


def is_it_visible(time,observation_location,ra,dec):
    #Define alt-az frame of reference based on the time intervals and geocentric location
    alt_az_conversion = AltAz(location = observation_location,obstime = time)
    coord=SkyCoord(ra,dec,unit='deg')#define coordinate
    
    
    #transform coordinate
    alt_az=coord.transform_to(alt_az_conversion)
    
    #Check whether altitude is above 30.
    if alt_az.alt>Angle('30d'):
        print('Ra:',ra,'Dec:',dec)
        print('Ιs visible at altitude:',alt_az.alt)
        return True
    else:
        return False

#def write_file(txt,type,ast):
    #fl = open(r'C:\Users\stavr\OneDrive\Desktop'+'\\'+ast+'.'+type,'w')
    #fl.write(txt)
    #fl.close()
    
# Define the location of the telescope and Sun position
the = EarthLocation(lat='40.5624', lon='22.9956', height=68*u.m)
hol = EarthLocation(lat='40.43291', lon='23.5055', height=800*u.m)
cyp = EarthLocation(lat='34.932056', lon='32.840167', height=1411*u.m)
sun_noess = Sun(40.5624,22.9956)
sun_cyp = Sun(34.932056,32.840167)
sun_hol = Sun(40.43291,23.5055)

#Let the observer choose their Observatory.
print('Choose the location of your telescope.')
ans=input('Type THE, CYP or HOL.')
if ans=='THE' or ans=='the':
    loc=the
    sun = sun_noess
elif ans=='cyp' or ans=='cyp':
    loc = cyp
    sun = sun_cyp
else:
    loc = hol
    sun = sun_hol

def fetch_mpc_objects():
    objects = MPC.query_objects('asteroid',absolute_magnitude_min=14,neo=1,
                                return_fields="number, absolute_magnitude,name", limit=100)
                                #,location=loc)
                                #, coordinates=SkyCoord(ra=location.lon, dec=location.lat, unit=(u.deg, u.deg)))
    return objects

def fetch_mpc_ephemeris(objects, obs_time, loc, n):
    eph = MPC.get_ephemeris(objects,location = loc,start=obs_time ,number = n)
    return eph


mpc_objects = fetch_mpc_objects()
# by using pop you reduce the number of elements in list, however the range(len(mpc_objects)) has the initial length of
# the list, so you need a counter to determine the new place of the element you want to parse
internal_counter = 0
for i in range(len(mpc_objects)):
    i -= internal_counter
    #print(mpc_objects[i])
    
    if mpc_objects[i]['number'] is None:
        mpc_objects.pop(i)
        
        internal_counter += 1

l=len(mpc_objects)
DT=[]
CH=np.zeros((l,2))
SR=np.zeros((l,2))
OBJ=[]

# Define the time range for the observations different for each object. Added 1 min for the code to run. 
# Added 40sec delay bewteen observations.
# The observations should start after night time. And so the ephemeris is printed for night time.
date_tmw=date.today()+timedelta(1)

datetime_tmw = datetime.combine(date_tmw, datetime.min.time()) #Convert from date object to datetime object.
today_ss = sun.get_sunset_time(datetime_tmw)

night_tmw = datetime.combine(date_tmw, datetime.min.time())

#median_night=night_tmw+timedelta(seconds=1)
test_day=night_tmw-timedelta(1)
median_night=night_tmw
print(median_night)


for j in range(l):

    #One step ephemeris to check wheter or not objext above 0 altitude.
    eph = MPC.get_ephemeris(mpc_objects[j]['number'],start=median_night ,number = 1) 

    # now=eph['Date'][0]
    # tm = now.strftime("%m/%d/%Y, %H:%M:%S")
    # DT.append(tm)
    CH[j][0]=eph['RA'][0]
    CH[j][1]=eph['Dec'][0]
    
    #Check whether object is above 0 altitude whith function.
    if is_it_visible(median_night,loc,CH[j][0],CH[j][1])==True:
        OBJ.append(mpc_objects[j]['number'])
        print(mpc_objects[j]['number'],mpc_objects[j]['absolute_magnitude'],'\n')#OBJ-> Objects that are above 0 altitude and therefore visible.

#Time when observations start.
dnow=datetime.now()
#Can't compare offset-naive and offset-aware datetimes so need to set timezone.
dnow=dnow.astimezone(timezone('UTC'))

if dnow<today_ss:
    print("It is still datetime.")
    print("Scheduled for midnight minutes.")
    obs_time=median_night
else:
    obs_time=median_night
    #obs_time = dnow +timedelta(minutes=3) #Time added after data aqcuisition is 3 minutes. 

N=5 #Number of data points for each asteroid
MPC.clear_cache()
#The file is cleared of its previous contents.
if os.path.exists("Schedule.dat"):
    f = open(r'C:\Users\stavr\OneDrive\Desktop\\Schedule.dat', "r+")  
    f.seek(0)
    f.truncate()
for k in range(len(OBJ)):
    #N points of observations.    
    eph1 = MPC.get_ephemeris(OBJ[k],start=obs_time ,step='10s',number = N ) #step depending on exposure time.

    # Writing the Schedule.dat file with the values for time Ra Dec
    for m in range(N):
        now=eph1['Date'][m]
        tm = now.strftime("%m/%d/%Y, %H:%M:%S")
        r2=round(eph1['RA'][m],3)
        r3=round(eph1['Dec'][m],3)
        l2=str(r2)
        l3=str(r3)

        
        file = open(r'C:\Users\stavr\OneDrive\Desktop\\Schedule.dat','a')
        file.writelines([tm,"\t",l2,"\t",l3,"\n"])
        file.close()
        #DT.append(tm)
        #SR[k][0]=eph1['RA'][m]
        #SR[k][1]=eph1['Dec'][m]
    obs_time=obs_time+timedelta(seconds=80) #40 seconds per observation + 40 sec delay.
    
    #print(DT[k],'\t',SR[k][0],'\t',SR[k][1])