import cv2
from myV4L2Lib import *
import sys
import signal

args = sys.argv

READ_DEVICE = int(args[1])
WRITE_DEVICE_NAME = "/dev/video" + args[2]

#print(READ_DEVICE)
#print(WRITE_DEVICE_NAME)
#print(FILTER_FLAG)

capture = cv2.VideoCapture(READ_DEVICE)
cannyFlag = False

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
	print(WRITE_DEVICE_NAME + " is closed")
	
def handlerCannyOn(signum, frame):
	global cannyFlag
	cannyFlag = True
	
def handlerCannyOff(signum, frame):
	global cannyFlag
	cannyFlag = False
	
capture.set(cv2.CAP_PROP_AUTOFOCUS, 0.0)
capture.set(cv2.CAP_PROP_FOCUS, 51)
#print(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
writeFile = V4L2Write(WRITE_DEVICE_NAME, int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)), v4l2.V4L2_PIX_FMT_RGB24)

signal.signal(signal.SIGINT, handlerTerminate)
signal.signal(signal.SIGUSR1, handlerPlus)
signal.signal(signal.SIGUSR2, handlerMinus)
signal.signal(40, handlerCannyOn)
signal.signal(41, handlerCannyOff)

print(WRITE_DEVICE_NAME + " is opened")
while(True):
	ret, frame = capture.read()

	if ret:	
		#windowsize = (800, 600)
		if cannyFlag:
			grayImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			blur = cv2.GaussianBlur(grayImage,(7,7), 1.5, 1.5)
			canny = cv2.Canny(blur, 0, 15, 3)
			colorImage = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
	
			writeFile.writeData(colorImage);
		else:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			writeFile.writeData(frame);
			
terminate()

