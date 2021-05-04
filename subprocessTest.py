import subprocess
import signal

command = ["python", "loopbackForSubprocess.py"]
proc = subprocess.Popen(command)
while True:
	c = input()
	if c == "q":
		proc.send_signal(signal.SIGINT)
		break;
	elif c == "p":
		proc.send_signal(signal.SIGUSR1)
	elif c == "m":
		proc.send_signal(signal.SIGUSR2)
	print("main loop")

