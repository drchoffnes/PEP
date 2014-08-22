# PEP
import httplib, os, string, random, time, socket, subprocess
from multiprocessing import Process

SERVER = '128.125.121.204'
HOSTS = {'youtube.com': ['208.54.39.44']}
TCPDUMP_CMD = 'sudo tcpdump -i usb0 -s0 -v port 80 -q -w '

def fprint(s):
	f_out.write(s + "\r\n")
	print s

def tcpdump_on_another_process(filename):
	os.system(TCPDUMP_CMD + filename)
	
def start_tcpdump(filename):
	p = Process(target=tcpdump_on_another_process, args=(filename,))
	p.start()	
	return

def stop_tcpdump():
	p = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
	out, err = p.communicate()

	for line in out.splitlines():
		if "tcpdump" in line:
			pid = int(line.split(None, 2)[1])
			os.system("sudo kill " + str(pid))
			
def hand_shake(dest):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((dest, 80))
	time.sleep(1)
	s.close()

def test():	
	for h in HOSTS:
		start_tcpdump(label + "/" + h)
		time.sleep(3)
		hand_shake(SERVER)

		for d in HOSTS[h]:
			print d
			hand_shake(d)
				
		ips = {}
		for t in range(20):
			hand_shake(h)

		time.sleep(3)			
		stop_tcpdump()

if __name__ == "__main__":
	random.seed()
	os.system("sudo echo")
	print "Please only input [A-Za-z0-9] for below carrier & location info...\n"
	carrier = raw_input('\tInput experiment carrier:  ')
	location = raw_input('\tInput experiment location: ')
	
	random_id = random.randint(1, 1000)
	label = "PEP_bypass_" + carrier + "_" + location + "_" + str(random_id)
	os.system("mkdir " + label)
	f_out = open(label + "/result.txt", "w")
	test()
	keep = raw_input('\nDo you want to keep this experiment result? [y/n]')
	if keep != 'y':
		os.system("rm -rf " + label)
