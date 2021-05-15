var urlDir = "./";
var lightOnButtonObj, lightOffButtonObj;

function requestPage(fileName, procFunc){

	document.getElementById(fileName).disabled = true;

	fetch(urlDir + fileName + ".html")
	.then((res) => {
		if (!res.ok) {
			throw new Error(`${res.status} ${res.statusText}`);
		}
		return res.blob();
	})
	.then((blob) => {
		procFunc();
	})
	.catch((reason) => {
		console.log(reason);
	});

}

function requestCommandPage(){

	document.getElementById("comRetVal").value = "Processing : " + document.getElementById("command").value;
	command = document.getElementById('command').value; 
	document.getElementById("command").value = "";
	data = "command=" + command
	
	fetch(urlDir + "getCommand.html",
		{
			method: 'POST',
			cache: 'no-cache',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
				},
			body: data
		})
	.then((res) => {
		if (!res.ok) {
			throw new Error(`${res.status} ${res.statusText}`);
		}
		return res.text();
	})
	.then((text) => {
		document.getElementById("comRetVal").value = text;
	})
	.catch((reason) => {
		console.log(reason);
	});
}

function lightOnProc(){
	lightOnButtonObj.style.backgroundColor = 'yellow';
	lightOffButtonObj.style.backgroundColor = 'gray';
	lightOffButtonObj.disabled = false;				
}
			
function lightOffProc(){
	lightOnButtonObj.style.backgroundColor = 'gray';
	lightOffButtonObj.style.backgroundColor = 'yellow';
	lightOnButtonObj.disabled = false;
}

function zoomInProc(){
	//do nothing
}

function zoomOutProc(){
	//do nothing
}

function zoomIn(){
	requestPage("zoomIn", zoomInProc);
	document.getElementById("zoomIn").disabled = false;
}

function zoomOut(){
	requestPage("zoomOut", zoomOutProc);
	document.getElementById("zoomOut").disabled = false;
}

function lightOn(){
	requestPage("lightOn", lightOnProc);
}
			
function lightOff(){
	requestPage("lightOff", lightOffProc);
}

function comSend(){
	requestCommandPage();
}

window.onload = function(){
	lightOnButtonObj = document.getElementById("lightOn");
	lightOffButtonObj = document.getElementById("lightOff");

	if(lightOnButtonObj != null && lightOffButtonObj != null){			
		lightOff();
				
		document.getElementById("lightOn").onclick = lightOn;
		document.getElementById("lightOff").onclick = lightOff;
		document.getElementById("comSend").onclick = comSend;
	}
}

