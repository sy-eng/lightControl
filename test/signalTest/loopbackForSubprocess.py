#This program run on linux
import cv2
from myV4L2Lib import *
import sys
import signal

READ_DEVICE = 2
WRITE_DEVICE_NAME = "/dev/video7"

capture = cv2.VideoCapture(READ_DEVICE)

def terminate():
	writeFile.close()
	capture.release()
	cv2.destroyAllWindows()

def zoomPlus():
	focusData = capture.get(cv2.CAP_PROP_FOCUS)
	focusData += 17;
	if focusData > 255:
		focusData = 255
		
	capture.set(cv2.CAP_PROP_FOCUS, focusData)
	print(capture.get(cv2.CAP_PROP_FOCUS))

def zoomMinus():
	focusData = capture.get(cv2.CAP_PROP_FOCUS)
	focusData -= 17;
	if focusData < 0:
		focusData = 0
			
	capture.set(cv2.CAP_PROP_FOCUS, focusData)
	print(capture.get(cv2.CAP_PROP_FOCUS))

def handlerPlus(signum, frame):
	zoomPlus()
	
def handlerMinus(signum, frame):
	zoomMinus()

def handlerTerminate(signum, frame):
	terminate()
	
capture.set(cv2.CAP_PROP_AUTOFOCUS, 0.0)
capture.set(cv2.CAP_PROP_FOCUS, 51)
#print(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
writeFile = V4L2Write(WRITE_DEVICE_NAME, int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)), v4l2.V4L2_PIX_FMT_RGB24)

signal.signal(signal.SIGINT, handlerTerminate)
signal.signal(signal.SIGUSR1, handlerPlus)
signal.signal(signal.SIGUSR2, handlerMinus)

while(True):
	ret, frame = capture.read()

	if ret:	
		windowsize = (800, 600)
		#frame = cv2.resize(frame, windowsize)
		grayImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		blur = cv2.GaussianBlur(grayImage,(7,7), 1.5, 1.5)
		canny = cv2.Canny(blur, 0, 15, 3)
		colorImage = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
		cv2.imshow('frame', colorImage)
	#	cv2.imshow('frame', frame)
	
	#	writeData(write_fd, result.data, result.cols * result.rows * 3);
		writeFile.writeData(colorImage);
	#	writeFile.writeData(frame);
	#	writeFile.writeData(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB));
	
	keyData = cv2.waitKey(1) & 0xff
	if keyData == ord('q'):
		break
	elif keyData == ord('p'):
		zoomPlus()
	elif keyData == ord('m'):
		zoomMinus()		
	else:
		None
		
terminate()

