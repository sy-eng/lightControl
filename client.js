/*
Copyright (c) 2018-2019 Jeremy Lainé.
All rights reserved.
sy-eng modified webcam.py on https://github.com/aiortc/aiortc for my application.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of aiortc nor the names of its contributors may
      be used to endorse or promote products derived from this software without
      specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
© 2020 GitHub, Inc.
*/

var pc = null;

function negotiate() {
    pc.addTransceiver('video', {direction: 'recvonly'});
    pc.addTransceiver('audio', {direction: 'recvonly'});
    return pc.createOffer().then(function(offer) {
        return pc.setLocalDescription(offer);
    }).then(function() {
        // wait for ICE gathering to complete
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        var offer = pc.localDescription;
        var ret = null;
        if (document.getElementById('filter') != null && document.getElementById('filter').checked) {
            ret = fetch('/offerFilter', {
                body: JSON.stringify({
                    sdp: offer.sdp,
                    type: offer.type,
                    idNum: id,
                    }),
                headers: {
                    'Content-Type': 'application/json'
                    },
                method: 'POST'
                });
        }else{
            ret = fetch('/offer', {
                body: JSON.stringify({
                    sdp: offer.sdp,
                    type: offer.type,
                    idNum: id,
                    }),
                headers: {
                    'Content-Type': 'application/json'
                    },
                method: 'POST'
                });
          }

        return ret;
    }).then(function(response) {
        return response.json();
    }).then(function(answer) {
        return pc.setRemoteDescription(answer);
    }).catch(function(e) {
        console.log(e);
        if(e instanceof SyntaxError){
        	window.location.href = 'http://sy-eng.f5.si:8090/lightBusy.html';        	
        }else{
        	alert(e);
          }
    });
}

function start() {
    var config = {
        sdpSemantics: 'unified-plan'
    };

//    if (document.getElementById('use-stun').checked) {
        config.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];
//    }

    pc = new RTCPeerConnection(config);

    // connect audio / video
    pc.addEventListener('track', function(evt) {
        if (evt.track.kind == 'video') {
            document.getElementById('video').srcObject = evt.streams[0];
        } else {
            document.getElementById('audio').srcObject = evt.streams[0];
        }
    });

    document.getElementById('start').style.display = 'none';
    console.log("start negotiate");
    negotiate();
    console.log("end negotiate");
    document.getElementById('stop').style.display = 'inline-block';
}

function stop() {
    document.getElementById('stop').style.display = 'none';

    // close peer connection
    setTimeout(function() {
        pc.close();
    }, 500);
   //document.getElementById('start').style.display = 'inline-block';
   window.location.href = 'http://sy-eng.f5.si:8090';

}
