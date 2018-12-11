#Sari, Laurence, Chau, CS410
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

def accept_incoming_connections():
	while True:
		client, client_address = SERVER.accept()
		print("%s:%s has connected." % client_address)
		client.send(bytes("Hello! First type your NAME and press Enter!", "utf8"))
		addresses[client] = client_address
		Thread(target=handle_client, args=(client,)).start()

def handle_client(client):
	name = client.recv(BUFSIZ).decode("utf8")
	welcome = 'Welcome %s! Type {quit} or click the x button to quit the application.' % name
	client.send(bytes(welcome, "utf8"))
	msg = "%s has joined the chat!" % name
	broadcast(bytes(msg, "utf8"))
	clients[client] = name
	names[name] = client
	msg = "{namelist}:"+":".join(names.keys())
	broadcast(bytes(msg, "utf8"))

	while True:
		msg = client.recv(BUFSIZ)
		if msg != bytes("{quit}", "utf8") and msg != bytes("{names}", "utf8"):
			print(msg)
			if msg.decode("utf8").startswith("@"):
				receiver = msg.decode("utf8").split(" ")[0][1:]
				private_msg(msg, receiver, name+": ")
				private_msg(msg, name, "{self}:"+name+": ") #so that the PM shows up for both the sender and receiver
			else:
				broadcast(msg, name+": ")
		elif msg == bytes("{names}", "utf8"):
			client.send(bytes("{namelist}:"+":".join(names.keys()), "utf8"))
		else:
			client.send(bytes("{quit}", "utf8"))
			client.close()
			broadcast(bytes("%s has left the chat." % name, "utf8"))
			del clients[client]
			del names[name]
			broadcast(bytes("{namelist}:"+":".join(names.keys()), "utf8"))
			break

def broadcast(msg, prefix=""): #sends a message to all active users
	for sock in clients:
		sock.send(bytes(prefix, "utf8")+msg)

def private_msg(msg, receiver, prefix=""): #sends a message to a specified user
	if receiver in names:
		names[receiver].send(bytes(prefix, "utf8")+msg)

clients = {}
names = {}
addresses = {}

HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
	SERVER.listen(5)
	print("Waiting for connection...")
	ACCEPT_THREAD = Thread(target=accept_incoming_connections)
	ACCEPT_THREAD.start()
	ACCEPT_THREAD.join()
	SERVER.close()
