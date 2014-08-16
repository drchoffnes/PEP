# PEP
import httplib, os, string, random, time, socket

SERVER = "128.125.121.204"

def fprint(s):
	f_out.write(s + "\r\n")
	print s

# start to log TCP traces on |SERVER|, with filename |logfile|
def start_tcpdump(logfile):
	request(SERVER + ":9999", fileobject="tcpdump?start&" + logfile)
	return

# stop to log TCP traces |logfile|, and scp |logfile| from |SERVER| to local |local_filename|
def stop_tcpdump(logfile):
	request(SERVER + ":9999", fileobject="tcpdump?stop&" + logfile)
	time.sleep(2)
	os.system("wget " + SERVER + "/PEP/" + logfile + " -q -O " + label + "/" + logfile)
	if os.path.getsize(label + "/" + logfile) == 0:
		fprint("\t trace file retrieving fails.")
	return

def test_caching():
	fprint("Caching:")
	logfile = "log_c_" + label + ".pcap"

	start_tcpdump(logfile)

	f = "test_cache_" + str(random_id) + ".jpg"
	request(fileobject=f)
	time.sleep(3)
	request(fileobject=f)

	stop_tcpdump(logfile)
	return

def test_connection_persistence():
	fprint("Connection Persistence:")
	logfile = "log_cp_" + label + ".pcap"

	start_tcpdump(logfile)
	f = "non_exist_file_" + str(random_id) + ".jpg"
	request(fileobject=f, extra_headers={"Connection": "close"})
	stop_tcpdump(logfile)

# testing whether downloaded html is from our server, or carrier-choosed "www.cnn.com"
def test_redirection():
	fprint("Redirection:")
	request(hostname="www.cnn.com", saveto=label + "/redirection")
	if open(label + "/redirection").read() != "Fake!!!\n":
		fprint("\tredirecting!")

# testing whether TCP handshake will be delayed
def test_delayed_handshake():
	fprint("Delayed Handshaking:")
	logfile = "log_dh_" + label + ".pcap"
	start_tcpdump(logfile)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((SERVER, 80))
	time.sleep(3)
	s.send("GET /non_exist_file_" + str(random_id) + " HTTP/1.0\r\nHost: 128.125.121.204\r\nAccept-Encoding: identity\r\n\r\n")
	data = s.recv(1)
	stop_tcpdump(logfile)

# testing whether downloaded jpg, css, js, html files are of the same size of origins.
def test_contentrewriting():
 	fprint("Content Rewriting:")
	request(fileobject="test.jpg", saveto=label + "/jpg")
	if os.path.getsize(label + "/jpg") != 211258:
		fprint("\timage transcoding!")

	request(fileobject="test.css", saveto=label + "/css")
	if os.path.getsize(label + "/css") != 3999:
		fprint("\tcss transcoding!")

	request(fileobject="test.js", saveto=label + "/js")
	if os.path.getsize(label + "/js") != 7999:
		fprint("\tjavascript transcoding!")

	request(fileobject="test.html", saveto=label + "/html")
	if os.path.getsize(label + "/html") != 3999:
		fprint("\thtml transcoding!")

# Make a HTTP GET request to |ip|, with header Host field |hostname|, other headers |extra_headers|, the requested object is |fileobject|. Response will be saved to local file |saveto|.
def request(ip=SERVER, hostname="", fileobject="", saveto="temp", extra_headers=None):
	if extra_headers == None:
		extra_headers = {}
	web = httplib.HTTPConnection(ip)
	headers = extra_headers
	if len(hostname) > 0:
		headers["Host"] = hostname
	headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 4.2; Nexus 7 Build/JOP40C) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19"
	web.request("GET", "/" + fileobject, headers=headers)
	response = web.getresponse()
  # save to file |saveto|
	f = open(saveto, "w")
	f.write(response.read())

def test():
	test_redirection()
	test_contentrewriting()
	test_caching()
	test_connection_persistence()
	test_delayed_handshake()

if __name__ == "__main__":
	random.seed()
	os.system("sudo echo")
	print "Please only input [A-Za-z0-9] for below carrier & location info...\n"
	carrier = raw_input('\tInput experiment carrier:  ')
	location = raw_input('\tInput experiment location: ')
	
	random_id = random.randint(1, 1000)
	label = "PEP_" + carrier + "_" + location + "_" + str(random_id)
	os.system("mkdir " + label)
	f_out = open(label + "/result.txt", "w")
	test()
	keep = raw_input('\nDo you want to keep this experiment result? [y/n]')
	if keep != 'y':
		os.system("rm -rf " + label)
