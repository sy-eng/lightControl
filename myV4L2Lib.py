import v4l2ForPython3 as v4l2
import fcntl
import numpy as np
import os

class V4L2Write:	
	def __init__(self, fileName, width, height, pixelFormat):
		#print("width : " + str(width))
		#print("height : " + str(height))
		self.fileName = fileName
		self.format = v4l2.v4l2_format()
		
		self.format.type = v4l2.V4L2_BUF_TYPE_VIDEO_OUTPUT 
		self.format.fmt.pix.width = width
		self.format.fmt.pix.height = height
		self.format.fmt.pix.pixelformat = pixelFormat
		self.format.fmt.pix.field = v4l2.V4L2_FIELD_NONE
		self.format.fmt.pix.priv = 0
		self.format.fmt.pix.colorspace = v4l2.V4L2_COLORSPACE_JPEG
		
		if pixelFormat == v4l2.V4L2_PIX_FMT_RGB24 or pixelFormat == v4l2.V4L2_PIX_FMT_BGR24:
			self.format.fmt.pix.bytesperline = width * 3
			self.format.fmt.pix.sizeimage = width * height * 3
			#print("RGB24? : " + str(v4l2.V4L2_PIX_FMT_RGB24) + " : " + str(pixelFormat))
		elif pixclFormat == v4l2.V4L2_PIX_FMT_UYVY:
			self.format.fmt.pix.bytesperline = width * 2
			self.format.fmt.pix.sizeimage = width * height * 2
		else:
			print("ERROR!!!!!!!!!!! : " + str(pixelFormat))
		
		self.fd = os.open(fileName, os.O_RDWR, os.O_NONBLOCK)
		self.open = True
		flag = fcntl.fcntl(self.fd, fcntl.F_GETFL)
		#print(flag)
		#fcntl.fcntl(self.fd, fcntl.F_SETFL, 32770)#flag | os.O_NONBLOCK)
		flag = fcntl.fcntl(self.fd, fcntl.F_GETFL)
		#if flag == 32770:
		#	print("O_NONBLOCK")
		#print(flag)
			
		self.capability = v4l2.v4l2_capability()
		#print("init capability: " + str(fcntl.ioctl(self.fd, v4l2.VIDIOC_QUERYCAP, self.capability)))
		fcntl.ioctl(self.fd, v4l2.VIDIOC_QUERYCAP, self.capability)
		#print("v4l2 driver: " + str(self.capability.driver))
		
		#print("fmt.pixelFormat : " + str(self.format.fmt.pix.pixelformat))
		#print("set format : " + str(fcntl.ioctl(self.fd, v4l2.VIDIOC_S_FMT, self.format)))
		fcntl.ioctl(self.fd, v4l2.VIDIOC_S_FMT, self.format)
		#tmpFormat = v4l2.v4l2_format()
		#fcntl.ioctl(self.fd, v4l2.VIDIOC_G_FMT, self.format)
		#print("fmt.sizeimage : " + str(self.format.fmt.pix.sizeimage))
		#print("fmt.pixelFormat : " + str(self.format.fmt.pix.pixelformat))
		
	def writeData(self, image):
		#print(len(np.array(image).tostring()))
		os.write(self.fd, np.array(image).tostring())
		
	def close(self):
		if self.open:
			os.close(self.fd)
			self.open = False
		
#	vd = open('/dev/video0', 'w')
#	cp = v4l2.v4l2_capability()
#	print(fcntl.ioctl(vd, v4l2.VIDIOC_QUERYCAP, cp))
#	print(cp.driver)
#	print(cp.card)
