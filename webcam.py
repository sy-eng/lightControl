#Copyright (c) 2018-2019 Jeremy Lainé.
#All rights reserved.
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

# sy-eng modified webcam.py on https://github.com/aiortc/aiortc for my application.

import argparse
import asyncio
import json
import logging
import os
import platform
import ssl
import serial
import sys
import time

from aiohttp import web

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

ROOT = os.path.dirname(__file__)
busyFlag = False

def sendData(data):
	ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
	time.sleep(5)
	ser.write(data)
	ser.flush()
	time.sleep(1)
	ser.write(data)
	ser.flush()
	time.sleep(1)
	ser.write(data)
	ser.flush()
	ser.close()

def setBusyFlag(flag):
	global busyFlag
#	busyFlag = flag

def getBusyFlag():
	global busyFlag
	return busyFlag

async def lightOn(request):
	sendData(b'n')
	return web.Response(content_type="text/html", text="OK")

async def lightOff(request):
	sendData(b'f')
	return web.Response(content_type="text/html", text="OK")

async def index(request):
	if not getBusyFlag():
		setBusyFlag(True)
		content = open(os.path.join(ROOT, "light.html"), "r").read()
		print("This request is approved")
		return web.Response(content_type="text/html", text=content)
	else:
		content = open(os.path.join(ROOT, "lightBusy.html"), "r").read()
		print("Reject a request")
		return web.Response(content_type="text/html", text=content)
    
async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

async def javascriptLight(request):
    content = open(os.path.join(ROOT, "light.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)
    
#    print("a")

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print("ICE connection state is %s" % pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # open media source
    if args.play_from:
        player = MediaPlayer(args.play_from)
    else:
        options = {"framerate": "30", "video_size": "640x480"}
        if platform.system() == "Darwin":
            player = MediaPlayer("default:none", format="avfoundation", options=options)
        else:
            player = MediaPlayer("/dev/video0", format="v4l2", options=options)

    await pc.setRemoteDescription(offer)
    for t in pc.getTransceivers():
        if t.kind == "audio" and player.audio:
            pc.addTrack(player.audio)
        elif t.kind == "video" and player.video:
            pc.addTrack(player.video)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


pcs = set()

async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
    setBusyFlag(False)
    print("The resource is released")

async def shutDown(app):
	print("shutdown")
	await on_shutdown(app)
	return web.Response(content_type="text/html", text="<html><body><h2>This page has been shut down</h2></body></html>")	

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

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/lightOn.html", lightOn)
    app.router.add_get("/lightOff.html", lightOff)
    app.router.add_get("/shutdown.html", shutDown)
    app.router.add_get("/client.js", javascript)
    app.router.add_get("/light.js", javascriptLight)
    app.router.add_post("/offer", offer)
    web.run_app(app, host=args.host, port=args.port, ssl_context=ssl_context)
    
