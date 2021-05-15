#Copyright (c) 2018-2019 Jeremy Laine.
#All rights reserved.
# sy-eng modified webcam.py on https://github.com/aiortc/aiortc for my application.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#    * Neither the name of aiortc nor the names of its contributors may
#      be used to endorse or promote products derived from this software without
#      specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import asyncio
import json
import logging
import os
import platform
import ssl

#These 6 librarries are added
import serial
import sys
import time
import requests
import subprocess
import signal

from aiohttp import web

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

DIRECTORY = "./"
TIME_TO_EXPIRE = 120
ROOT = os.path.dirname(__file__) + DIRECTORY

relay = None
relayFilter = None
webcam = None
webcamFilter = None
userList = []

pcs = set()

#command1 = ["python", DIRECTORY + "loopbackForSubprocess.py", "0", "6", "0"]
#proc1 = subprocess.Popen(command1)
command2 = ["python", DIRECTORY + "loopbackForSubprocess.py", "2", "7", "0"]
proc2 = subprocess.Popen(command2)

#These flag is added
MAX_CONNECTION_NUM = 2

async def sendData(data):
	ser = serial.Serial('/dev/serial/by-path/pci-0000:02:00.0-usb-0:5.1.1:1.0-port0', 9600, timeout=0.5)
	await asyncio.sleep(3)
	ser.write(data)
	ser.flush()
	ser.write(data)
	ser.flush()
	ser.close()

async def lightOn(request):
	await sendData(b'n')
	return web.Response(content_type="text/html", text="OK")

async def lightOff(request):
	await sendData(b'f')
	return web.Response(content_type="text/html", text="OK")

def zoomIn(request):
#	print("zoomIn")
	proc2.send_signal(signal.SIGUSR1)
	return web.Response(content_type="text/html", text="OK")

def zoomOut(request):
#	print("zoomOut")
	proc2.send_signal(signal.SIGUSR2)
	return web.Response(content_type="text/html", text="OK")

def create_local_tracks(play_from, owner = False, camFilter = False):
    global relay, webcam
    global relayFilter, webcamFilter

    if play_from:
        player = MediaPlayer(play_from)
        return player.audio, player.video
    else:
#        options = {"framerate": "30", "video_size": "640x480"}
        if not owner:
            if relay is None:
                webcam = MediaPlayer("/dev/video0", format="v4l2")
#                webcam = MediaPlayer("/dev/video0", format="v4l2", options=options)
#                webcam = MediaPlayer("/dev/video6", format="v4l2", options=options)
                relay = MediaRelay()
            relayTmp = relay.subscribe(webcam.video)
        else:
            if relayFilter is None:
                webcamFilter = MediaPlayer("/dev/video7", format="v4l2")
#                webcamFilter = MediaPlayer("/dev/video7", format="v4l2", options=options)
                relayFilter = MediaRelay()
            relayTmp = relayFilter.subscribe(webcamFilter.video)

        if camFilter:
            proc2.send_signal(40)
        else:
            proc2.send_signal(41)
        
        return None, relayTmp

async def getCommand(request):
#	print(request)
	#"await" is necessary or data will be void
	data = await request.post()
	loop = asyncio.get_event_loop()
#	print(data)
#	print("http://192.168.7.2:8080?command=" + data['command'])
	url = "http://192.168.7.2:8080?command=" + data['command']
#	res = requests.get("http://192.168.7.2:8080?command=" + data['command'])
	res = await loop.run_in_executor(None, requests.get, url)
	
	return web.Response(content_type="text/html", text=res.text)

def getIdNum():
	retVal = 0
	
	if len(userList):
		while retVal in [r[1] for r in userList]:
			retVal += 1
		
	return retVal

def deleteOldUsers():
	timeNow = time.time()
	
	for usr in userList:
		#delete if the user does not have a video stream
		if (usr[2] == None) and (timeNow - usr[3] > TIME_TO_EXPIRE):
			userList.remove(usr)

async def index(request):
	global controlOwner
	global userList
	
	deleteOldUsers()
#	print(vars(request))
	idNum = getIdNum()
	print("idNum : %d" % idNum)
	if idNum == 0:
		userList.append([request.remote, idNum, None, time.time(), False])
		controlOwner = request.remote
		print("controlOwner : %s" % controlOwner)
		content = open(os.path.join(ROOT, "lightHeadHtml.txt"), "r").read() + "\t<script>const id = " + str(idNum) + open(os.path.join(ROOT, "lightOwnerHtml.txt"), "r").read()
		print("This request is approved(Owner)")
	else:
		userList.append([request.remote, idNum, None, time.time(), False])
		content = open(os.path.join(ROOT, "lightHeadHtml.txt"), "r").read() + "\t<script>const id = " + str(idNum) + open(os.path.join(ROOT, "lightHtml.txt"), "r").read()
		print("This request is approved")
	print(userList)
		
	return web.Response(content_type="text/html", text=content)
    
async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

async def javascriptLight(request):
    content = open(os.path.join(ROOT, "light.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

async def lightBusy(request):
    content = open(os.path.join(ROOT, "lightBusy.html"), "r").read()
    return web.Response(content_type="text/html", text=content)

async def javascriptCommand(request):
    content = open(os.path.join(ROOT, "command.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

def getIndexFromId(idNum):
    retIndex = -1
    
    if len(userList) > 0:
        idList = [r[1] for r in userList]
        if idNum in idList:
            retIndex = idList.index(idNum)
            
    return retIndex

def deleteAnObj(pc):
	index = [r[2] for r in userList].index(pc)
	del userList[index]

async def offer(request):
    if len(pcs) < MAX_CONNECTION_NUM:
        params = await request.json()
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        idNum = params["idNum"]
#        print("idNum(offer) : %d" % idNum)
    
#        print("offer func")
#        print("path : %s" % request.rel_url.path)
#        print(request.rel_url.path == "/offerFilter")
        camFilter = (request.rel_url.path == "/offerFilter")

        indexNum = getIndexFromId(idNum)
        if indexNum >= 0:
            if userList[indexNum][0] == request.remote:
                pc = RTCPeerConnection()
                pcs.add(pc)
                userList[indexNum][2] = pc
                userList[indexNum][4] = camFilter
#                print(pc)
#                print(vars(request))
    
                @pc.on("iceconnectionstatechange")
                async def on_connectionstatechange():
                    print("Connection state is %s" % pc.connectionState)
                    if pc.connectionState == "failed":
                        deleteAnObj(pc)
                        await pc.close()
                        pcs.discard(pc)

                owner = False
                if userList[indexNum][1] == 0:
                    owner = True

                # open media source
                audio, video = create_local_tracks(args.play_from, owner = owner, camFilter = camFilter)

                await pc.setRemoteDescription(offer)
                for t in pc.getTransceivers():
                    if t.kind == "audio" and audio:
                        pc.addTrack(audio)
                    elif t.kind == "video" and video:
                        pc.addTrack(video)

                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)

                return web.Response(
                    content_type="application/json",
                    text=json.dumps(
                        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
                          ),
                    )
            else:
                print("request remote : %s" % request.remote)
                return web.Response(content_type="text/html", text="busy")
        else:
            print("indexNum error : %d" % indexNum)
            return web.Response(content_type="text/html", text="busy")
    else:
        return web.Response(content_type="text/html", text="busy")

# This application is shutdown with this function(destructor)
async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
    print("The resource is released")
    #proc.send_signal(signal.SIGINT)
    #print("Virtual camera is closed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC webcam demo")
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument("--play-from", help="Read the media from a file and sent it."),
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/zoomIn.html", zoomIn)
    app.router.add_get("/zoomOut.html", zoomOut)
    app.router.add_get("/lightOn.html", lightOn)
    app.router.add_get("/lightOff.html", lightOff)
    app.router.add_get("/client.js", javascript)
    app.router.add_get("/light.js", javascriptLight)
    app.router.add_get("/lightBusy.html", lightBusy)
    app.router.add_post("/getCommand.html", getCommand)
    app.router.add_post("/offer", offer)
    app.router.add_post("/offerFilter", offer)
    web.run_app(app, host=args.host, port=args.port, ssl_context=ssl_context)
    
