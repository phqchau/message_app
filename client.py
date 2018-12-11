#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter

# Add logic to determine whether to handle it as a private mesage or not
def isPrivate(msg):
	# print(msg)
	strMsg = msg.split(": ")
	#print(strMsg)  """This checked to see what was being saved in the split.Turns out it was an array"""
	try:
		return strMsg[1].startswith("@")
	except:
		return False

def getPrivUsername(msg):
    # return msg.split(" ")[1][1:]
	return msg.split(":")[0]

def receive():
	"""Handles receiving of messages."""
	while True:
		try:
			msg = client_socket.recv(BUFSIZ).decode("utf8")
			# print(isPrivate(msg))
			# if msg:
			# 	print(msg)
			if isPrivate(msg):
				# print("Is Private")
				splitAtSym = msg.split(": ")
				splitAfterAt = msg.split(" ")
				# print(splitAfterAt)
				if ":" in splitAtSym[0]:
					cmdSplit = splitAtSym[0].split(":")
					# print(cmdSplit)
					cmd = cmdSplit[0]
					if cmd == "{self}":
						target = splitAfterAt[1][1:]
						del splitAfterAt[1]
						splitAfterAt[0] = cmdSplit[1] + ":"
						msgToSend = ' '.join(splitAfterAt)
						# print (privFrames)
						if not target in privFrames:
							privFrames[target] = tkinter.Frame(top)
							# print(privFrames)
							newScrollbar = tkinter.Scrollbar(privFrames[target])
							privLists[target] = tkinter.Listbox(privFrames[target], yscrollcommand=newScrollbar.set)
							newScrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
							privLists[target].pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
							privLists[target].pack()
							privFrames[target].pack(expand=True, fill=tkinter.BOTH)
							privLists[target].insert(tkinter.END, "PM: " + target)
						privLists[target].insert(tkinter.END, msgToSend)
				else:	
					del splitAfterAt[1]
					msgToSend = ' '.join(splitAfterAt)
					# print(msgToSend)
					privUser = getPrivUsername(msg)
					# pmsg_list.insert(tkinter.END, msg)
					if not privUser in privFrames:
						privFrames[privUser] = tkinter.Frame(top)
						newScrollbar = tkinter.Scrollbar(privFrames[privUser])
						privLists[privUser] = tkinter.Listbox(privFrames[privUser], yscrollcommand=newScrollbar.set)
						newScrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
						privLists[privUser].pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
						privLists[privUser].pack()
						privFrames[privUser].pack(expand=True, fill=tkinter.BOTH)
						privLists[privUser].insert(tkinter.END, "PM: " + splitAtSym[0])
					privLists[privUser].insert(tkinter.END, msgToSend)
			else:
				msg_list.insert(tkinter.END, msg)
		except OSError:  # Possibly client has left the chat.
			break

def send(event=None):  # event is passed by binders.
	"""Handles sending of messages."""
	msg = my_msg.get()
	my_msg.set("")  # Clears input field.
	try:
		client_socket.send(bytes(msg, "utf8"))
	except:
		print("No client socket set")
	if msg == "{quit}":
		try:
			client_socket.close()
		except:
			pass
		top.quit()


def on_closing(event=None):
	"""This function is to be called when the window is closed."""
	my_msg.set("{quit}")
	send()
	# top.quit()
	


if __name__ == "__main__":
	top = tkinter.Tk()
	top.title("Chatter")

	messages_frame = tkinter.Frame(top)
	my_msg = tkinter.StringVar()  # For the messages to be sent.
	my_msg.set("Type your messages here.")
	scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
	# Following will contain the messages.
	msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
	scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
	msg_list.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
	msg_list.pack()
	messages_frame.pack(expand=True, fill=tkinter.BOTH)

	# privateMsg_frame = tkinter.Frame(top)
	# my_pmsg = tkinter.StringVar()
	# my_pmsg.set("Type your private message here.")
	# scrollbar2 = tkinter.Scrollbar(privateMsg_frame)
	# pmsg_list = tkinter.Listbox(privateMsg_frame, height=15, width=50, yscrollcommand=scrollbar2.set)
	# scrollbar2.pack(side=tkinter.RIGHT, fill=tkinter.Y)
	# pmsg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
	# pmsg_list.pack()
	# privateMsg_frame.pack()

	privLists = {}
	privFrames = {}

	entry_field = tkinter.Entry(top, textvariable=my_msg, width=45)
	entry_field.bind("<Return>", send)
	entry_field.pack()
	send_button = tkinter.Button(top, text="Send", command=send)
	send_button.pack()

	top.protocol("WM_DELETE_WINDOW", on_closing)


	#----Now comes the sockets part----
	HOST = input('Enter host: ')
	PORT = input('Enter port: ')
	if not PORT:
		PORT = 33000
	else:
		PORT = int(PORT)

	BUFSIZ = 1024
	ADDR = (HOST, PORT)

	client_socket = socket(AF_INET, SOCK_STREAM)
	client_socket.connect(ADDR)

	receive_thread = Thread(target=receive)
	receive_thread.start()
	tkinter.mainloop()  # Starts GUI execution.
