# gui_app.py

import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import socket
import threading
from queue import Queue

# Server setup
def server(queue, host='localhost', port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Listening on {host}:{port}")

        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, queue)).start()

def handle_client(client_socket, queue):
    with client_socket:
        print(f"Connected by {client_socket.getpeername()}")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            queue.put(data.decode())

def gui_process(queue):
    root = tk.Tk()
    root.title("Robot Output")

    text_widgets = {}
    text_tags = {}

    def update_text():
        while not queue.empty():
            try:
                message = queue.get_nowait()
                robot_id, text = message.split(' ', 1)
                robot_id = int(robot_id)
                
                if robot_id not in text_widgets:
                    # Determine the row and column for grid placement
                    row = robot_id // 2
                    col = robot_id % 2

                    frame = tk.Frame(root)
                    frame.grid(row=row, column=col, sticky='nsew')
                    label = tk.Label(frame, text=f"Robot {robot_id+1}")
                    label.pack()
                    text_widget = ScrolledText(frame, wrap=tk.WORD)
                    text_widget.pack(fill=tk.BOTH, expand=True)
                    text_widgets[robot_id] = text_widget

                    # Create a tag for red text
                    text_widget.tag_configure("red", foreground="red")
                    text_tags[robot_id] = "default"

                # Check for a special command to change text color
                if text.strip() == "!change_color":
                    text_tags[robot_id] = "red" if text_tags[robot_id] == "default" else "default"
                    continue  # Skip adding this command to the text box

                # Insert text with the appropriate tag
                text_tag = text_tags[robot_id]
                text_widgets[robot_id].insert(tk.END, text, text_tag)
                text_widgets[robot_id].see(tk.END)
            except Exception as e:
                print(f"Error: {e}")

        root.after(100, update_text)

    root.after(100, update_text)
    root.mainloop()

if __name__ == "__main__":
    queue = Queue()

    # Start the server in a separate thread
    server_thread = threading.Thread(target=server, args=(queue,))
    server_thread.daemon = True
    server_thread.start()

    # Start the GUI process
    gui_process(queue)
