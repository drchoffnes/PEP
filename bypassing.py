# PEP
import httplib, os, string, random, time, socket, subprocess
from multiprocessing import Process

SERVER = '128.125.121.204'
HOSTS = {'r14---sn-nx57yn76.googlevideo.com': ['208.54.39.44', '208.54.5.44', '208.54.5.45']} # Youtubey
TIMER = 10

def fprint(s):
	f_out.write(s + "\r\n")
	print s

def tcpdump_on_another_process(filename):
	os.system('sudo tcpdump -i ' + tcpdump_interface + ' -s0 -v port 80 -q -w ' + filename)
	
def start_tcpdump(filename):
	p = Process(target=tcpdump_on_another_process, args=(filename,))
	p.start()

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
	s.send("GET /non_exist_file_")
	s.close()

def test():	
	for h in HOSTS:
		start_tcpdump(label + "/" + h)
		time.sleep(3)
		hand_shake(SERVER)

		for d in HOSTS[h]:
			hand_shake(d)
				
		ips = {}
		time_start = time.time()
		while True:
			ip = socket.gethostbyname(h)
			while ip in ips:
				if time.time() - time_start > TIMER:
					break
				ip = socket.gethostbyname(h)
				print ip
			if time.time() - time_start > TIMER:
				break	
			print ip
			ips[ip] = 0
			hand_shake(ip)
		time.sleep(3)
		stop_tcpdump()

if __name__ == "__main__":
	random.seed()
	os.system("sudo echo")
	print "Please only input [A-Za-z0-9] for below carrier & location info...\n"
	tcpdump_interface = raw_input('\tTCPDUMP command interface? e.g., \"usb0\", \"wlan0\", or \"eth0\": ')
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
