import tkinter as tk
import socket
import threading

class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("300x150")
        self.root.title("选择模式")

        self.selection = tk.IntVar()

        label = tk.Label(self.root, text="请选择模式:")
        label.pack()

        server_button = tk.Radiobutton(self.root, text="服务器端", variable=self.selection, value=1)
        server_button.pack()

        client_button = tk.Radiobutton(self.root, text="客户端", variable=self.selection, value=2)
        client_button.pack()

        button = tk.Button(self.root, text="确认", command=self.on_button_click)
        button.pack()

    def on_button_click(self):
        self.root.destroy()
        if self.selection.get() == 1:
            self.start_server()
        else:
            self.start_client()


    def start_server(self):
        def handle_client(client_socket, address):
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                msg = data.decode()
                text.insert(tk.END, f"Received: {msg}\n")
                client_socket.send(msg.encode())
            client_socket.close()

        def start_server_thread():
            host = '127.0.0.1'
            port = 50005

            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen(5)
            text.insert(tk.END, "Server is listening...\n")

            while True:
                client_socket, address = server_socket.accept()
                text.insert(tk.END, f"Connection from: {address}\n")
                client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
                client_handler.start()

        server_window = tk.Tk()
        server_window.geometry("400x300")
        server_window.title("服务器端")

        text = tk.Text(server_window)
        text.pack()

        start_server_thread()
        server_window.mainloop()

    def start_client(self):
        def send_message():
            message = input_entry.get()
            client_socket.send(message.encode())
            response = client_socket.recv(1024).decode()
            text.insert(tk.END, f"Received: {response}\n")

        client_window = tk.Tk()
        client_window.geometry("400x300")
        client_window.title("客户端")

        text = tk.Text(client_window)
        text.pack()

        input_entry = tk.Entry(client_window)
        input_entry.pack()

        send_button = tk.Button(client_window, text="发送", command=send_message)
        send_button.pack()

        # host = '127.0.0.1'
        # port = 50005
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client_socket.connect((host, port))

        client_window.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()
