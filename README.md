# hookSession.py

This simple python script introduces a function to exchange a requests.Session-object's socket for another socket<br>
This is very useful in combination with wrapped sockets (TLS, Socks, Torpy, etc.)

## Usage
Rather self-explanatory usage:
```python3
# Take an existing requests.Session object,
old_session: requests.Session

# ... an existing (wrapped) socket to be inserted
new_socket: socket.socket

# and lastly, retrieve the newly created Session from the method
new_session = hookSession(old_session, new_socket)
```

## Credits
The base for this script was provided by this [post](https://pretagteam.com/question/using-python-requests-with-existing-socket-connection) on pretagteam.com.<br>
However, the code was outdated, so I considered it my duty to restore and partially improve some of the code.

## Contribution
Feel free to open an issue and suggest improvements.

## Donation
If this little projected helps you in any way, I'd be pleased by a donation.<br>
* ETH/BSC @ 0xbdecadb203d6950a5787e05250883c456c267fd5
