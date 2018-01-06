import sys
import socket
import time
import datetime
import telnetlib

class RRDcached:

  def __init__(self,server='localhost',port=42217):
    self.SERVER=server
    self.PORT=port

    try:
      self.RRD = telnetlib.Telnet(self.SERVER, self.PORT)
    except socket.error, msg:
      print >>sys.stderr, msg
      sys.exit(1)

  def add(self,DB,value,time=int(time.time())):
    command = 'update ' + DB + '.rrd ' + str(time) + ':' + str(value)
    self.RRD.write(command+"\n")
    reply = self.RRD.read_until("\n",1)
    reply = reply.rstrip()
    print >>sys.stderr, command + ': ' + reply


class RTKsite:

  SATS = 0; READS = 0
  LAT = 0; LON = 0; HGHT = 0
  VELX = 0; VELY = 0; VELZ = 0
  FLTX = 0; FLTY = 0; FLTZ = 0
  FLTSX = 0; FLTSY = 0; FLTSZ = 0
  TIME=datetime.datetime(1,1,1)

  def setLocation(self,llh):
    self.LAT,self.LON,self.HGHT=llh.split(',')

  def setVelocity(self,xyz):
    self.VELX,self.VELY,self.VELZ=xyz.split(',')

  def setFloat(self,xyz):
    self.FLTX,self.FLTY,self.FLTZ=xyz.split(',')

  def setFloatS(self,xyz):
    self.FLTSX,self.FLTSY,self.FLTSZ=xyz.split(',')



class RTKRCVtelnet:

  ROVER = RTKsite()
  BASE = RTKsite()

  RUNTIME=datetime.timedelta()


  def __init__(self,password='admin',server='pylon.navdata.net',port=3130):
    self.PASSWORD=password
    self.SERVER=server
    self.PORT=port
    self.RTKRCV = telnetlib.Telnet(self.SERVER, self.PORT)
    self.RTKRCV.read_until("password: ")
    self.RTKRCV.write(self.PASSWORD + "\r\n")
    self.RTKRCV.read_until("rtkrcv> ",2)

  def send(self,command):
    self.RTKRCV.write(command+"\r\n")

  def setRuntime(self,time):
    hrs,mins,secs=time.split(':',3)
    secs=secs.split('.',1)[0]
    self.RUNTIME=datetime.timedelta(hours=int(hrs), minutes=int(mins), seconds=int(secs))

  def readStatus(self,timeout,callback=None):
    while True:
      LINE = self.RTKRCV.read_until("\r\n",timeout)
      if LINE == '': return

      if ':' in LINE:
        FIELD,VALUE=LINE.split(":",1)
        FIELD=FIELD.lstrip()
        FIELD=FIELD.rstrip()
        VALUE=VALUE.rstrip()
        VALUE=VALUE.lstrip()

        #print("<"+FIELD+"> = <"+VALUE+">")

        if FIELD == "rtklib version": self.VERSION=VALUE; self.TIMESTAMP=int(time.time()); print "timestamped"
        if FIELD == "rtk server state": self.ACTIVE=VALUE
        if FIELD == "processing cycle (ms)": self.PROCTIME=VALUE
        if FIELD == "positioning mode": self.MODE=VALUE
        if FIELD == "frequencies": self.FREQ=VALUE
        if FIELD == "accumulated time to run": self.setRuntime(VALUE)
        if FIELD == "cpu time for a cycle (ms)": self.CPUTIME=VALUE
        if FIELD == "missing obs data count": self.OBSMISSING=VALUE
        if FIELD == "# of input data rover": self.ROVER.READS=VALUE
        if FIELD == "# of input data base": self.BASE.READS=VALUE
        if FIELD == "# of input data corr": self.CORRECTIONS=VALUE
        if FIELD == "solution status": self.STATUS=VALUE
        if FIELD == "time of receiver clock rover": self.ROVER.TIME=VALUE
        if FIELD == "time sys offset (ns)": self.TIMEOFFSET=VALUE
        if FIELD == "solution interval (s)": self.SOLINTERVAL=VALUE
        if FIELD == "age of differential (s)": self.DIFFAGE=VALUE
        if FIELD == "ratio for ar validation": self.ARRATIO=VALUE
        if FIELD == "# of satellites rover": self.ROVER.SATS=VALUE
        if FIELD == "# of satellites base": self.BASE.SATS=VALUE
        if FIELD == "# of valid satellites": self.VALIDSATS=VALUE
        if FIELD == "GDOP/PDOP/HDOP/VDOP": self.DOP=VALUE
        if FIELD == "pos llh single (deg,m) rover": self.ROVER.setLocation(VALUE)
        if FIELD == "vel enu (m/s) rover": self.ROVER.setVelocity(VALUE)
        if FIELD == "pos xyz float (m) rover": self.ROVER.setFloat(VALUE)
        if FIELD == "pos xyz float std (m) rover": self.ROVER.setFloatS(VALUE)
        if FIELD == "pos llh (deg,m) base": self.BASE.setLocation(VALUE)
        if FIELD == "# of average single pos base": self.AVGBASEPOS=VALUE
        if FIELD == "vel enu (m/s) base": self.BASE.setVelocity(VALUE)
        if FIELD == "baseline length float (m)": self.BASELINEFLT=VALUE
        if FIELD == "baseline length fixed (m)": self.BASELINEFIX=VALUE
        if FIELD == "monitor port" and callback: callback(self)

  def close(self):
    self.RTKRCV.close()

if __name__ == "__main__":

  def updateRRD(rcv):
    rrd.add('rtkrcv_lat',rcv.ROVER.LAT,rcv.TIMESTAMP)
    rrd.add('rtkrcv_lon',rcv.ROVER.LON,rcv.TIMESTAMP)
    rrd.add('rtkrcv_hght',rcv.ROVER.HGHT,rcv.TIMESTAMP)
    rrd.add('rtkrcv_fltsx',rcv.ROVER.FLTSX,rcv.TIMESTAMP)
    rrd.add('rtkrcv_fltsy',rcv.ROVER.FLTSY,rcv.TIMESTAMP)
    rrd.add('rtkrcv_fltsz',rcv.ROVER.FLTSZ,rcv.TIMESTAMP)
    rrd.add('rtkrcv_rsat',rcv.ROVER.SATS,rcv.TIMESTAMP)
    rrd.add('rtkrcv_bsat',rcv.BASE.SATS,rcv.TIMESTAMP)
    rrd.add('rtkrcv_vsat',rcv.VALIDSATS,rcv.TIMESTAMP)
    rrd.add('rtkrcv_arr',rcv.ARRATIO,rcv.TIMESTAMP)
    rrd.add('rtkrcv_bline',rcv.BASELINEFLT,rcv.TIMESTAMP)
    rrd.add('rtkrcv_dage',rcv.DIFFAGE,rcv.TIMESTAMP)
    rrd.add('rtkrcv_rtime',rcv.RUNTIME.total_seconds(),rcv.TIMESTAMP)

  rrd=RRDcached()
  rcv=RTKRCVtelnet()
  rcv.send("status 1")
  rcv.readStatus(2,updateRRD)
  rcv.close()
  print("Latitude: "+rcv.ROVER.LAT)
  print("Longitutde: "+rcv.ROVER.LON)
  print("Height: "+rcv.ROVER.HGHT)

