import thread,sys,subprocess,os
import struct

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtNetwork import QTcpSocket, QHostAddress

from pytracer.core import PtCommon
from pytracer.core import PtDriver
import core.PtWorld as PtWorld

class display_driver(PtDriver.PtDriver):
    def __init__(self,name=None):
        PtDriver.PtDriver.__init__(self,name=name)


    def open(self,options):
        self.options = options
        self.tcpSocket = QTcpSocket()
        # try to connect to the server
        self.tcpSocket.connectToHost(QHostAddress("0.0.0.0"), 5006)
        self.tcpSocket.waitForConnected(2000)

        if self.tcpSocket.state() != 3:
            self._launchWindow()
            #thread.start_new_thread(self._launchWindow,(xres,yres))
            QObject.connect(self.tcpSocket, SIGNAL("connected()"), self.tcpSocketConnected)

            #print "connecting now"
            while self.tcpSocket.state() != 3:
                self.tcpSocket.connectToHost(QHostAddress("0.0.0.0"), 5006)
                self.tcpSocket.waitForConnected(5000)


    def tcpSocketConnected(self):
        #txt = "Successfully connected to Server!!!"
        self.xres = self.options.xres.value
        self.yres = self.options.yres.value
        # send resolution
        txt = struct.pack("6sII","imgnfo",self.xres,self.yres)
        self.tcpSocket.write(QByteArray(txt))
        self.tcpSocket.waitForBytesWritten()
        

    def prepareBucket(self,bucket):
        bu = struct.pack("6sIIII","bucket",
                                    bucket.pos.x,
                                    bucket.pos.y,
                                    bucket.width,
                                    bucket.height)

        for i,p in enumerate(bucket.pixels):


            if i < bucket.width or \
            i > ((bucket.height * bucket.width) - bucket.width) or \
            (i % bucket.width) == 0 or\
            (((i+1) % bucket.width) + bucket.width) == bucket.width:
                bu += struct.pack("3I",255,255,0)
            else:
                bu += struct.pack("3I",0,0,0)

        self.tcpSocket.write(QByteArray(bu))
        self.tcpSocket.waitForBytesWritten()
    
    def writeBucket(self,bucket):
        bu = struct.pack("6sIIII","bucket",
                                    bucket.pos.x,
                                    bucket.pos.y,
                                    bucket.width,
                                    bucket.height)
        #print "wrote ",len(bucket.pixels)
        #print "x ",bucket.width," y ",bucket.height, " len ",len(bucket.pixels)
        #j = 0
        for i in bucket.pixels:
            #bu += struct.pack("3I",i.r,i.g,i.b)
            bu += struct.pack("3I",int(i.r),int(i.g),int(i.b))
            #j +=1
        #print "size sent ",j

        self.tcpSocket.write(QByteArray(bu))
        self.tcpSocket.waitForBytesWritten()

    def close(self):
        self.tcpSocket.close()

    def _launchWindow(self):
        file = os.path.dirname(__file__)
        cmd = "python %s"%os.path.join(file,"framebuffer.py")
        subprocess.Popen(cmd.split())
