from tkinter import *
from tkinter import ttk
import webbrowser


def setup_login(root):
    login_frame = Frame(
        root
    )
    login_frame.pack()
    api_key_lbl = Label(
        login_frame,
        text="Enter Access Token:"
    )
    api_key_lbl.pack()
    api_key_ent = Entry(
        login_frame,
        width=25
    )
    api_key_ent.pack()
    go_btn = Button(
        login_frame,
        text="Go",
        width=10,
        height=1
    )
    go_btn.pack()
    go_btn.bind("<Button-1>", lambda e: login_frame.destroy())
    get_key_lbl = Label(
        login_frame,
        text="Click here to get your Access Token"
    )
    get_key_lbl.pack()
    get_key_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://dev.groupme.com/session/new"))


class LoginGUI:
    def __init__(self):
        root = Tk()
        root.title("GroupMeUtils")
        root.geometry("250x100")
        root.resizable(0, 0)
        setup_login(root)
        root.mainloop()
