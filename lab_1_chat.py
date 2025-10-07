import socket
import threading
from tkinter import simpledialog
from queue import Queue
from time import sleep
import tkinter as tk

HOST = '127.0.0.1'
PORT = 65500


class ChatException(Exception):
    """A custom exception for chat-related errors that also stores a queue."""

    def __init__(self, queue: Queue):
        super().__init__(Queue)
        self.queue = queue


class Server:
    def __init__(self, master):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master = master
        self.master.title('Python Chat Server')

        # Creating a display for server activity
        self.server_log = tk.Text(self.master, state='disabled', height=10)
        self.server_log.pack(side='top', fill='both', expand=True, padx=10, pady=10)

        self.clients = {}
        self.message_history = []
        self.queue = Queue()

        self.log('Server started.')

        # Start a thread to handle incoming connections
        threading.Thread(target=self.start_server_thread, daemon=True).start()
        # Start a thread to process messages from the queue and update the GUI
        self.master.after(100, self.process_queue)

    def log(self, message):
        """Thread-safe logging to the server GUI."""
        self.queue.put(message)

    def process_queue(self):
        """Periodically check the queue for new messages and update the GUI."""
        try:
            while True:
                message = self.queue.get_nowait()
                self.server_log.config(state='normal')
                self.server_log.insert(tk.END, message + '\n')
                self.server_log.see(tk.END)
                self.server_log.config(state='disabled')
        except Exception as e:
            if isinstance(e, ChatException):
                self.queue = e.queue
        finally:
            self.master.after(100, self.process_queue)

    def start_server_thread(self):
        """Start the main server loop in a separate thread."""
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(5)
        self.log('Server is listening...')
        while True:
            conn, addr = self.server_socket.accept()
            name = conn.recv(1024).decode('utf-8')
            if name:
                self.log(f'{name} has joined the chat.')
                self.clients[conn] = [name]

            # Send the message history to the newly connected client
            for msg in self.message_history:
                conn.send(msg.encode('utf-8'))

            # Start a new thread for the client
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        """Handle a single client connection."""
        while True:
            try:
                message = conn.recv(1024).decode('utf-8')
                if not message:
                    break

                # Store message and broadcast to all clients
                # formatted_message = f'{self.clients[conn]}: {message}'
                formatted_message = message
                self.message_history.append(formatted_message + '\n')
                self.log(formatted_message)
                self.broadcast(formatted_message)
            except:
                break

        # Clean up on disconnection
        del self.clients[conn]
        conn.close()
        self.log(f'Connection from {addr} closed.')

    def broadcast(self, message):
        """Send a message to all connected clients."""
        for client in self.clients.keys():
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                del self.clients[client]


class ChatClient:
    def __init__(self, master):
        self.master = master
        self.name = 'Chat Client'
        master.title(f'Chat Client - {self.name}')

        self.chat_display = tk.Text(master, state='disabled', height=10)
        self.chat_display.pack(fill='both', expand=True, padx=10, pady=10)

        input_frame = tk.Frame(master)
        input_frame.pack(fill='x', padx=10, pady=5)

        self.message_entry = tk.Entry(input_frame)
        self.message_entry.pack(side='left', fill='x', expand=True)

        self.send_button = tk.Button(input_frame, text='Send', command=self.send_message)
        self.send_button.pack(side='right')
        self.master.bind('<Return>', lambda event: self.send_button.invoke())

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Queue for thread-safe GUI updates
        self.queue = Queue()
        self.master.after(100, self.process_queue)

    def connect(self):
        try:
            self.client_socket.connect((HOST, PORT))
            self.register_name()
        except ConnectionRefusedError:
            sleep(0.5)
            self.client_socket.connect((HOST, PORT))
        finally:
            threading.Thread(target=self.receive_messages, daemon=True).start()

    def process_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, message + '\n')
                self.chat_display.see(tk.END)
                self.chat_display.config(state='disabled')
        except Exception as e:
            if isinstance(e, ChatException):
                self.queue = e.queue
            else:
                pass
        finally:
            self.master.after(100, self.process_queue)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.client_socket.sendall(f'{self.name}: {message} '
                                       .encode('utf-8'))
            self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.queue.put(message)
            except:
                self.queue.put(' Disconnected from server.')
                break

    def register_name(self):
        name = simpledialog.askstring('Register', 'Enter your name: ')
        self.name = name
        self.queue.put(f'{self.name} has joined the chat.')
        self.client_socket.send(f'{self.name}'.encode('utf-8'))
        self.master.title(f'Chat Client - {self.name}')


server_root = tk.Tk()
server = Server(server_root)
sleep(0.2)
client_num = int(input('Enter number of clients: '))
for i in range(1, client_num + 1):
    client_root = tk.Toplevel(server_root)
    client = ChatClient(client_root)
    client_root.title(f'Chat Client_{i}')
    client.connect()

server_root.mainloop()
