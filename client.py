from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter

def isPrivate(msg): #add logic to determine whether to handle a message as a private message
	strMsg = msg.split(": ")
	try:
		return strMsg[1].startswith("@")
	except:
		return False

def getPrivUsername(msg):
	return msg.split(":")[0]

def receive():
	while True:
		try:
			msg = client_socket.recv(BUFSIZ).decode("utf8")
			if msg.split(":")[0] == "{namelist}":
				user_list.delete(0, tkinter.END)
				for i in msg.split(":")[1:]:
					user_list.insert(tkinter.END, i)
			elif isPrivate(msg):
				splitAtSym = msg.split(": ")
				splitAfterAt = msg.split(" ")
				if ":" in splitAtSym[0]:
					#display the PM to the sender so that they can see their conversation history
					cmdSplit = splitAtSym[0].split(":")
					cmd = cmdSplit[0]
					if cmd == "{self}":
						target = splitAfterAt[1][1:]
						del splitAfterAt[1]
						splitAfterAt[0] = cmdSplit[1] + ":"
						msgToSend = ' '.join(splitAfterAt)
						display_private_window(target)
						privLists[target].insert(tkinter.END, msgToSend)
				else: #display the PM to the receiver
					del splitAfterAt[1]
					msgToSend = ' '.join(splitAfterAt)
					privUser = getPrivUsername(msg)
					display_private_window(privUser)
					privLists[privUser].insert(tkinter.END, msgToSend)
			else:
				msg_list.insert(tkinter.END, msg)
		except OSError:
			break

def display_private_window(user):
	if not user in privFrames:
		privFrames[user] = tkinter.Frame(top)
		newScrollbar = tkinter.Scrollbar(privFrames[user])
		privLists[user] = tkinter.Listbox(privFrames[user], yscrollcommand=newScrollbar.set)
		newScrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
		privLists[user].pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
		privLists[user].pack()
		privFrames[user].pack(expand=True, fill=tkinter.BOTH)
		privLists[user].insert(tkinter.END, "PM: " + user)
		close_button = tkinter.Button(privFrames[user], text="Close", command=privFrames[user].pack_forget)
		close_button.pack()
	else:
		if not privFrames[user].winfo_ismapped():
			privFrames[user].pack(expand=True, fill=tkinter.BOTH)

def send(event=None):
	msg = my_msg.get()
	my_msg.set("")
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
	my_msg.set("{quit}")
	send()

if __name__ == "__main__":
	top = tkinter.Tk()
	top.title("Group Messaging")

	groupUser_frame = tkinter.Frame(top)
	groupUser_frame.pack(expand=True, fill=tkinter.BOTH)


	messages_frame = tkinter.Frame(groupUser_frame)
	groupMsgLabel = tkinter.Label(messages_frame, text="Group Chat")
	groupMsgLabel.pack(expand=True, fill=tkinter.X)

	my_msg = tkinter.StringVar()
	my_msg.set("Type your message here.")
	scrollbar = tkinter.Scrollbar(messages_frame)
	msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
	scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
	msg_list.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
	msg_list.pack()
	messages_frame.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)

	userlist_frame = tkinter.Frame(groupUser_frame)
	userListLabel = tkinter.Label(userlist_frame, text="Available Users")
	userListLabel.pack(expand=True, fill=tkinter.X)
	scrollbar2 = tkinter.Scrollbar(userlist_frame)
	user_list = tkinter.Listbox(userlist_frame, height=15, width=25, yscrollcommand=scrollbar2.set)
	user_list.insert(tkinter.END, "Type @ followed by an username in the list to Private Message")
	user_list.insert(tkinter.END, "------------------------")
	scrollbar2.pack(side=tkinter.RIGHT, fill=tkinter.Y)
	user_list.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
	user_list.pack()
	userlist_frame.pack(side=tkinter.RIGHT, expand=True, fill=tkinter.BOTH)

	privateMsg_frame = tkinter.Frame(top)
	pmSectionLabel = tkinter.Label(privateMsg_frame, text="Private Messages:")
	pmSectionLabel.pack(expand=True, fill=tkinter.X)
	privateMsg_frame.pack(expand=True, fill=tkinter.BOTH)

	privLists = {}
	privFrames = {}

	entry_frame = tkinter.Frame(top)
	entry_field = tkinter.Entry(entry_frame, textvariable=my_msg, width=45)
	entry_field.bind("<Return>", send)
	entry_field.pack()
	send_button = tkinter.Button(entry_frame, text="Send", command=send)
	send_button.pack()
	entry_frame.pack(side=tkinter.BOTTOM, expand=True, fill=tkinter.X)

	top.protocol("WM_DELETE_WINDOW", on_closing)

	HOST = input('Enter host: ')
	PORT = int(input('Enter port: '))

	BUFSIZ = 1024
	ADDR = (HOST, PORT)

	client_socket = socket(AF_INET, SOCK_STREAM)
	client_socket.connect(ADDR)

	receive_thread = Thread(target=receive)
	receive_thread.start()
	tkinter.mainloop()
