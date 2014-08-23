# PEP
import httplib, os, string, random, time, socket, subprocess
from multiprocessing import Process

SERVER = '128.125.121.204'

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
	
def request(ip=SERVER, hostname="", fileobject="", saveto="temp", extra_headers=None):
	if extra_headers == None:
		extra_headers = {}
	web = httplib.HTTPConnection(ip)
	headers = extra_headers
	if len(hostname) > 0:
		headers["Host"] = hostname
	#headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 4.2; Nexus 7 Build/JOP40C) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19"
	web.request("GET", "/" + fileobject, headers=headers)
	response = web.getresponse()
  # save to file |saveto|
	f = open(saveto, "w")
	f.write(response.read())

def test():
	urls = {}
	request(ip="www.youtube.com")
	lines = open("temp").readlines()
	for l in lines:
		s = l.find("watch?")
		if s != -1:
			e = l.find("\"", s + 1)
			urls[l[s:e]] = 0

	if len(urls) == 0:
		print "Youtube is not responding, please retry"
		exit()
	ips = {}
	for url in urls:
		print url
		request(ip="www.youtube.com", fileobject=url)
		lines = open("temp").readlines()
		for l in lines:
			s = l.find("googlevideo.com\/generate_204")
			ss = l.rfind("/", 0, s - 1)
			if s != -1:
				ips[l[ss + 1:s] + "googlevideo.com"] = 0
	start_tcpdump(label + "/youtube.pcap")
	time.sleep(3)
	hand_shake(SERVER)
	for ip in ips:
		print ip
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
