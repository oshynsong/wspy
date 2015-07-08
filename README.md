#Websocket protocol version 13.0 - Implement by python 2.7
##1.Introduction
This is the new immediately communication between client and server. Only for the HTML5 javascript api referering to RFC6455.
##2.Usage
It is a package for python 2.7, and you can apply it to your own application to construct the immediately communication between server and browser(best for new version of Chrome,Firefox).
>>>from wspy import server
>>>ws = server.WS('127.0.0.1', 5005, 'select')  #Use the default multi-connection strategy of select
>>>ws.run()
You should derive from WS class and reconstruct the process method for you own app. The default process method just return the message from client.
**send(cli, msg, isLast=True, opcode=1)**(method for sending message to client)
*cli*: The client object specified one connection from client
*msg*: The message to send to the client
*isLast*: if it is the last frame of the msg, default is True
*opcode*: The opcode of the frame
##3. Structure
*util.py*: The lower level and utility class and method for the package.
*error.py*: Define the specific error for this package.
*server.py*: The real implementation of the protocol, and you just import this module for usage commonly.

Copyright &copy; OshynSong<dualyangsong@gmail.com>
