var urlDir = "./";
var lightOnButtonObj, lightOffButtonObj;

function createXMLHttpRequest() {
	if (window.XMLHttpRequest) {
		return new XMLHttpRequest()
	} else if (window.ActiveXObject) {
		try {
			return new ActiveXObject("Msxml2.XMLHTTP")
		} catch (e) {
			try {
				return new ActiveXObject("Microsoft.XMLHTTP")
			} catch (e2) {
				return null
			}
		}
	} else {
		return null
	}
}

function requestPage(fileName, procFunc){
	var request = createXMLHttpRequest();
	
	document.getElementById(fileName).disabled = true;
	request.open("GET", urlDir + fileName + ".html", true);
	request.onreadystatechange = function(){
		if(request.readyState == 4 && request.status == 200){
			procFunc();						
		}
	}
				
	request.send("");
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

function lightOn(){
	requestPage("lightOn", lightOnProc);
}
			
function lightOff(){
	requestPage("lightOff", lightOffProc);
}

window.onload = function(){
	lightOnButtonObj = document.getElementById("lightOn");
	lightOffButtonObj = document.getElementById("lightOff");
			
	lightOff();
				
	document.getElementById("lightOn").onclick = lightOn;
	document.getElementById("lightOff").onclick = lightOff;
}

