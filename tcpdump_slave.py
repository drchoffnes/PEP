import os, sys, threading, errno, signal, subprocess, time, BaseHTTPServer, urlparse, cgi,urllib, urllib2, time, copy
from multiprocessing import Process
from SocketServer import ThreadingMixIn

HOST_NAME = '128.125.121.204'
HOST_PORT = 8888

tcpdumps = {}
tcpdump_cleaner_run = True
def tcpdump_cleaner():
	while(tcpdump_cleaner_run):
		time.sleep(10)
		to_kill = []
		tcpdumps_ = copy.deepcopy(tcpdumps)
		for x in tcpdumps_:
			if int(time.time()) - tcpdumps[x] > 300:
				kill_tcpdump(x)
				to_kill.append(x)

def tcpdump_on_another_process(filename):
	os.system("tcpdump -s0 -v port 80 -q -w " + filename)

def kill_tcpdump(filename):
	p = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
	out, err = p.communicate()

	for line in out.splitlines():
		if filename in line:
			pid = int(line.split(None, 2)[1])
			os.system("kill " + str(pid))
	tcpdumps_lock.acquire()
	del tcpdumps[filename]
	tcpdumps_lock.release()

def start_log(filename):
	tcpdumps_lock.acquire()
	tcpdumps[filename] = int(time.time())
	tcpdumps_lock.release()
	p = Process(target=tcpdump_on_another_process, args=(filename,))
	p.start()
	
def stop_log(filename):
	kill_tcpdump(filename)
	os.system("mv " + filename + " /var/www/PEP/")

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		url_content = urlparse.urlparse(self.path)
		query = url_content.query
		path = url_content.path
		if path != "/tcpdump":
			return
		args = query.split("&")

		if args[0] == "start":
			start_log(args[1])
			time.sleep(2)
		else:
			stop_log(args[1])
		self.send_response(200)
		self.end_headers()
		self.wfile.write("")

class ThreadedHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
	"""Handle requests in a separate thread."""

if __name__ == '__main__':
	tcpdumps_lock = threading.Lock()
	thread = threading.Thread(target=tcpdump_cleaner)
	server = ThreadedHTTPServer((HOST_NAME, HOST_PORT), MyHandler)

        try:
		thread.start()
                server.serve_forever()
        except KeyboardInterrupt:
                pass

	tcpdump_cleaner_run = False

