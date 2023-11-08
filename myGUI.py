import sys
import tkinter as tk
from tkinter import messagebox
import socket
from random import randint
import threading
from PIL import ImageTk
import db_renji_qi as qi


class TicTacToneGUI:
    def __init__(self):
        """
        窗口初始化
        """
        self.root = None
        self.select_window = tk.Tk()
        self.selection = tk.IntVar()
        """
        服务器还是客户端 以及ip和端口数据的存储
        """
        self.is_sever = 1
        self.is_client = 2
        self.host = None
        self.port = None

        self.board_image = None
        self.bai_image = None
        self.hei_image = None

        self.buttons = [[tk.Button() for _ in range(3)] for _ in range(3)]

        self.current_player = None

        self.position = None  # 记录下棋的位置 同步到两端

        """
        两端的连接和游戏顺序的实现，错误操作的禁止
        """
        self.sockobj = None
        self.connection = None
        self.address = None
        self.is_send_data = None
        self.is_your_turn = None

        self.game_state = threading.Event()
        self.game_state.set()
        self.th_sever_send = None
        self.th_sever_receive = None

        self.th_client_send = None
        self.th_client_receive = None

        self.turn = None
        self.turn_flag = False

        self.connect_button = None

        self.start_button = None
        self.start_button_count = 0

        self.select_pack()
        self.select_window.resizable(False, False)

        TicTacToneGUI.center_window(self.select_window)

        # self.thread = threading.Thread(target=self.main_threading)  # 或者使用带超时时间的recv
        # self.thread.start()

        self.select_window.mainloop()

    # @staticmethod
    # def close_window():
    #     # 终止所有进程
    #     os._exit(0)

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title('Tic_Tac_Toe')
        self.board_pack()
        self.manu_pack()
        self.root.resizable(False, False)
        TicTacToneGUI.center_window(self.root)
        self.root.mainloop()

    @staticmethod
    def center_window(window, width=0, height=0):
        window.update_idletasks()
        window_width = window.winfo_reqwidth()
        window_height = window.winfo_reqheight()

        screenwidth = window.winfo_screenwidth()
        screenheight = window.winfo_screenheight()
        size = '+%d+%d' % ((screenwidth - window_width) // 2, (screenheight - window_height) // 2 - window_height // 2)
        window.geometry(size)

    """
    The name of function which ends with '_click' deals with click event
    """

    def select_button_click(self):
        self.select_window.destroy()
        self.create_gui()

    def chess_click(self, row, col, is_change_chess=False):
        if self.start_button['state'] == 'disabled':
            tk.messagebox.showinfo(title='Warning', message='Please input ip and port!')
            return

        if self.start_button_count == 0:
            tk.messagebox.showinfo(title='Warning', message="Please press Start Game button!")
            return

        if not self.game_state.is_set():
            tk.messagebox.showinfo(title='Warning',
                                   message="Want more?\nPress the Start Game button for another round of the game.")
            return

        if not self.is_your_turn:
            tk.messagebox.showinfo(title='Warning', message="Not your turn yet!")
            return

        if not is_change_chess:  # 己方正常下棋
            cur_player = self.current_player
        else:
            cur_player = 2 if self.current_player == 1 else 1
        image = self.hei_image if cur_player == 1 else self.bai_image

        if qi.nextSet(row, col, cur_player)[0]:
            self.position = row, col
            if not is_change_chess:
                self.is_send_data = True
            self.buttons[row][col].config(image=image)
        else:
            tk.messagebox.showinfo(title='Warning', message='Wrong Position!')
            return

        if qi.isSuccess(1):
            self.game_state.clear()
            self.turn_flag = False
            tk.messagebox.showinfo(title='Game Over', message='Player1 Win!')
            return
        if qi.isSuccess(2):
            self.game_state.clear()
            self.turn_flag = False
            tk.messagebox.showinfo(title='Game Over', message='Player2 Win!')
            return
        if qi.noFree():
            self.game_state.clear()
            self.turn_flag = False
            tk.messagebox.showinfo(title='Game Over', message="It's a tie!")
            return

    def connect_click(self):
        if self.selection.get() == self.is_client:
            host = self.host.get()
            port = int(self.port.get())
            self.creat_client(host, port)

        else:
            port = int(self.port.get())
            self.creat_sever(port)
        self.connect_button['state'] = tk.DISABLED
        self.start_button['state'] = tk.NORMAL

    def start_click(self):
        if self.start_button_count == 0:
            if self.selection.get() == self.is_sever:
                self.th_sever_send = threading.Thread(target=self.sever_sending)
                self.th_sever_receive = threading.Thread(target=self.sever_receiving)
                self.th_sever_send.setDaemon(True)
                self.th_sever_receive.setDaemon(True)
                self.th_sever_send.start()
                self.th_sever_receive.start()
                self.who_go_first_sever()
            else:
                self.th_client_send = threading.Thread(target=self.client_sending)
                self.th_client_receive = threading.Thread(target=self.client_receiving)
                self.th_client_send.setDaemon(True)
                self.th_client_receive.setDaemon(True)
                self.th_client_send.start()
                self.th_client_receive.start()
                self.who_go_first_client()
        else:
            if self.game_state.is_set():
                tk.messagebox.showinfo(title='Warning', message="Current game is going on!")
                return

            qi.reset()
            for i in range(3):
                for j in range(3):
                    self.buttons[i][j].config(image=self.board_image)

            self.game_state.set()

            if self.selection.get() == self.is_sever:
                self.who_go_first_sever()
            else:
                self.who_go_first_client()
        self.start_button_count += 1

    """
    threading start
    """

    def creat_sever(self, port):
        """
        using IPV4 connection and UDP to communicate
        """
        self.sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockobj.bind(('', port))  # 在使用socket.bind()方法时，你需要传入一个元组作为参数，包含主机地址和端口号。
        self.sockobj.listen(1)

        self.connection, self.address = self.sockobj.accept()
        print('Server connected by', self.address)

    def creat_client(self, host, port):
        self.sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockobj.connect((host, port))
        self.connect_button.config(text='Connect Successfully!')
        # th_client_receive = threading.Thread(target=self.client_receiving)
        # th_client_receive.start()

    """
    communication between sever and client
    """

    def sever_receiving(self):
        while True:
            try:
                data = self.connection.recv(1024).decode('utf-8')  # read next line on client socket
            except socket.error:
                sys.exit()
            data = eval(data)
            if data[-1] == 'ok':
                self.turn = int(data[0])
                self.turn_flag = True

            else:
                print(f'Client {data}')
                self.is_your_turn = True
                self.chess_click(*data, True)

    def sever_sending(self):
        while True:
            if self.is_send_data:
                position = str(self.position)
                sending = position.encode('utf-8')
                self.connection.send(sending)
                self.is_send_data = False
                self.is_your_turn = False

    def client_receiving(self):
        while True:
            try:
                data = self.sockobj.recv(1024).decode('utf-8')  # read next line on client socket
            except socket.error:
                sys.exit()
            data = eval(data)
            if data[-1] == 'ok':
                if not self.turn_flag:
                    self.turn = int(data[0])
                    self.turn_flag = True

            else:
                print('Server:', data)
                self.is_your_turn = True
                self.chess_click(*data, True)

    def client_sending(self):
        while True:
            if self.is_send_data:
                position = str(self.position)
                sending = position.encode('utf-8')
                self.sockobj.send(sending)
                self.is_send_data = False
                self.is_your_turn = False

    def who_go_first_sever(self):
        if self.selection.get() == self.is_sever:
            if not self.turn_flag:
                self.turn = randint(1, 2)
                self.connection.send(str((1 if self.turn == 2 else 2, 'ok')).encode('utf-8'))
                self.turn_flag = True

            self.current_player = 1 if self.turn == 1 else 2
            self.is_your_turn = True if self.turn == 1 else False

            # data = self.connection.recv(1024).decode('utf-8')  # read next line on client socket
            # if data == 'start':
            if self.turn == 1:
                tk.messagebox.showinfo(title='Game Start', message='You go first!')
            else:
                tk.messagebox.showinfo(title='Game Start', message='You go second!')

    def who_go_first_client(self):
        if self.selection.get() == self.is_client:
            if not self.turn_flag:
                self.turn = randint(1, 2)
                self.sockobj.send(str((1 if self.turn == 2 else 2, 'ok')).encode('utf-8'))
                self.turn_flag = True

            # self.turn = int(self.sockobj.recv(1024).decode('utf-8'))
            # print(self.turn)
            self.current_player = 1 if self.turn == 1 else 2
            self.is_your_turn = True if self.turn == 1 else False
            if self.turn == 1:
                tk.messagebox.showinfo(title='Game Start', message='You go first!')
            else:
                tk.messagebox.showinfo(title='Game Start', message='You go second!')

    def board_pack(self):
        board_frame = tk.Frame(self.root)

        self.board_image = ImageTk.PhotoImage(file='photo/ban.jpg')
        self.bai_image = ImageTk.PhotoImage(file='photo/bai.jpg')
        self.hei_image = ImageTk.PhotoImage(file='photo/hei.jpg')

        width = self.board_image.width()
        height = self.board_image.height()

        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = tk.Button(board_frame, text='', compound=tk.CENTER, image=self.board_image,
                                               font=('Arial', 40),
                                               width=width, height=height,
                                               command=lambda row=i, col=j: self.chess_click(row, col))
                self.buttons[i][j].grid(row=i + 1, column=j + 1)

        board_frame.pack(anchor=tk.CENTER, side=tk.LEFT)

    def manu_pack(self):
        manu_frame = tk.Frame(self.root)

        if self.selection.get() == self.is_client:
            ip_label = tk.Label(manu_frame, text="Sever's ip address:", justify=tk.RIGHT)
            ip_label.pack(pady=10)

            self.host = tk.StringVar(value='127.0.0.1')
            host_box = tk.Entry(manu_frame, width=20, textvariable=self.host)
            host_box.pack()

        port_label = tk.Label(manu_frame, text="Sever's port:", justify=tk.RIGHT)
        port_label.pack(pady=10)

        self.port = tk.StringVar(value='50005')
        port_box = tk.Entry(manu_frame, width=20, textvariable=self.port)
        port_box.pack()

        self.connect_button = tk.Button(manu_frame,
                                        text='Connect to Sever' if self.selection.get() == self.is_client else 'Bond port',
                                        command=lambda: self.connect_click())
        self.connect_button.pack(pady=20, ipadx=5, ipady=5)

        self.start_button = tk.Button(manu_frame, text='Start Game', font=('Arial', 10),
                                      command=lambda: self.start_click())
        self.start_button.pack(pady=10, ipadx=10, ipady=10)

        self.start_button['state'] = tk.DISABLED

        manu_frame.pack(anchor=tk.CENTER, side=tk.LEFT)

    def select_pack(self):
        select_frame = tk.Frame(self.select_window)

        self.select_window.title("Mode Selector")

        label = tk.Label(select_frame, text="Sever OR Client?")
        label.pack(padx=80)

        server_button = tk.Radiobutton(select_frame, text="Sever", variable=self.selection, value=self.is_sever)
        server_button.pack(padx=80, pady=5)

        client_button = tk.Radiobutton(select_frame, text="Client", variable=self.selection, value=self.is_client)
        client_button.pack(padx=80)

        select_button = tk.Button(select_frame, text="OK", command=self.select_button_click)
        select_button.pack(padx=80, pady=10)

        select_frame.pack(anchor=tk.CENTER)


if __name__ == '__main__':
    game = TicTacToneGUI()
    sys.exit()
