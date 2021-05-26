from datetime import datetime
from groupy.client import Client
from groupy import exceptions
from io import BytesIO
from PIL import Image, ImageTk
import tkinter as tk
import requests
import webbrowser


# return a render of an image from a url
def get_img_from_url(url):
    resp = requests.get(url)
    img = Image.open(BytesIO(resp.content))
    img = img.resize((100, 100), Image.ANTIALIAS)  # TODO: find good size for images
    render = ImageTk.PhotoImage(img)
    return render


class GUI:
    main_frame = None
    root = None

    def __init__(self):
        self.root = tk.Tk()
        self.setup_login()
        self.root.mainloop()

    def clear_main(self):
        if self.main_frame is not None:
            self.main_frame.destroy()

    def setup_login(self):
        self.clear_main()
        self.root.title("GroupMeUtils")
        self.root.geometry("250x100")
        self.root.resizable(0, 0)
        login_frame = tk.Frame(
            self.root,
        )
        login_frame.pack()
        self.main_frame = login_frame
        api_key_lbl = tk.Label(
            login_frame,
            text="Enter Access Token:"
        )
        api_key_lbl.pack()
        api_key_ent = tk.Entry(
            login_frame,
            width=25
        )
        api_key_ent.pack()
        go_btn = tk.Button(
            login_frame, text="Go",
            width=10,
            height=1
        )
        go_btn.pack()
        go_btn.bind("<Button-1>", lambda e: self.login(api_key_ent.get()))
        get_key_lbl = tk.Label(
            login_frame,
            text="Click here to get your Access Token"
        )
        get_key_lbl.pack()
        get_key_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://dev.groupme.com/session/new"))

    def login(self, access_key):
        client = Client.from_token(access_key)
        try:
            client.user.get_me()
            self.setup_main_menu(client)
        except exceptions.BadResponse:
            # tell user their access token is incorrect
            print("Bad Token")

    def setup_main_menu(self, client):
        self.root.geometry("300x100")
        user_info = client.user.get_me()
        self.clear_main()
        main_menu_frame = tk.Frame(
            self.root,
        )
        main_menu_frame.pack()
        self.main_frame = main_menu_frame
        profile_info_lbl = tk.Label(
            main_menu_frame,
            text=f'Id: {user_info["id"]}\n'
                 f'Name: {user_info["name"]}\n'
                 f'Email: {user_info["email"]}\n'
                 f'Phone: {user_info["phone_number"]}\n'
                 f'Creation Date: {datetime.fromtimestamp(user_info["created_at"])}'
        )
        profile_info_lbl.grid(row=0, column=0)
        prof_render = get_img_from_url(client.user.get_me()['image_url'])
        profile_pic = tk.Label(
            main_menu_frame,
            image=prof_render
        )
        profile_pic.image = prof_render
        profile_pic.grid(row=0, column=1)
