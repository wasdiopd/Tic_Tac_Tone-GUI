# Tic-Tac-Toe GUI Game

A simple Tic-Tac-Toe game with a graphical user interface (GUI) developed using the Tkinter library in Python. The game allows players to connect as either a server or a client to play against each other.

## Features

- Two gameplay modes: Server and Client
- Server mode allows binding to a specific port for other players to connect
- Client mode enables connecting to a server using the server's IP address and port
- Responsive GUI with clear visual indicators for game state and current player turn
- Game logic implemented with support for game restart and win/tie conditions
- Threading used for handling server-client communication and gameplay synchronization

## Prerequisites

- Python 3.x
- Tkinter library
- Pillow (PIL) library

## How to Run

Run the script `myGUI.py` to start the Tic-Tac-Toe game. The script provides a graphical interface for selecting the server or client mode and initiating the game.

```bash
python myGUI.py