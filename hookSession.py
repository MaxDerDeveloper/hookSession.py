from requests.packages.urllib3 import PoolManager, HTTPConnectionPool
from requests.adapters         import HTTPAdapter
from http.client               import HTTPConnection
from copy                      import deepcopy

import requests
import socket

__author__ = "Maximilian Weiser"
__email__ = "admin@max-weiser.de"

def hookSession(old_session:requests.Session, new_sock:socket.socket, scheme:str="http://") -> requests.Session:
	class HookedAdapter(HTTPAdapter):
		def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
			self._pool_connections = connections
			self._pool_maxsize     = maxsize
			self._pool_block       = block

			self.poolmanager = HookedPoolManager(
				num_pools = connections,
				maxsize   = maxsize,
				block     = block,
				strict    = True,
				**pool_kwargs
			)

	class HookedPoolManager(PoolManager):	
		def _new_pool(self, scheme, host, port, request_context=None):
			SSL_KEYWORDS = (
				"key_file",
				"cert_file",
				"cert_reqs",
				"ca_certs",
				"ssl_version",
				"ssl_minimum_version",
				"ssl_maximum_version",
				"ca_cert_dir",
				"ssl_context",
				"key_password",
			)

			if request_context is None:
				request_context = self.connection_pool_kw.copy()

			if request_context.get("blocksize") is None:
				request_context["blocksize"] = 16384

			for key in ("scheme", "host", "port"):
				request_context.pop(key, None)

			if scheme == "http":
				for kw in SSL_KEYWORDS:
					request_context.pop(kw, None)

			return HookedHTTPConnectionPool(host, port, **request_context)

	class HookedHTTPConnectionPool(HTTPConnectionPool):
		def _new_conn(self) -> HTTPConnection:
			self.num_connections += 1

			return HookedHTTPConnection(
				host    = self.host,
				port    = self.port,
				timeout = self.timeout.connect_timeout,
				**self.conn_kw,
			)

	class HookedHTTPConnection(HTTPConnection):
		def connect(self):
			self.sock = new_sock
			
			if self._tunnel_host:
				self._tunnel()

	new_session = deepcopy(old_session)
	new_session.mount(scheme, HookedAdapter())

	return new_session

if __name__ == '__main__':
	# Create new socket, to be inserted
	new_sockeet = socket.create_connection(("api.ipify.org", 80))

	# Create copy of session and swap socket
	old_session = requests.Session()
	new_session = hookSession(old_session, new_sockeet)
	
	### Lets test it!
	# Initally, we send a request to google's servers,
	# but we exchange the session's socket, so our request
	# will be sent to the ipify.org servers instead.

	resp = old_session.get(
		"http://google.com",
		headers={"Host": "api.ipify.org"} # Make sure HOST-header is correct, too.
	)
	
	# Now lets see, wether the HTTP-request has been redirected to ipify.org
	print(resp.text)
	# As expected, the corresponding IPv4 is printed
	# This proves, the hookSession-method works!
