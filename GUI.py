from datetime import datetime
from groupy.client import Client
from groupy import exceptions
from io import BytesIO
from PIL import Image, ImageTk
import tkinter as tk
import requests
import webbrowser
import copy


def config_frame(canvas):
    canvas.configure(scrollregion=canvas.bbox(tk.ALL))


def make_return_btn(root, return_func):
    return_btn = tk.Button(
        root,
        text='Return'
    )
    return_btn.bind('<Button-1>', lambda e: return_func())
    return_btn.pack()


def make_scrollable_canvas(root, load_func, func_data=None):
    mem_canvas = tk.Canvas(
        root,
        borderwidth=0
    )
    mem_frame = tk.Frame(
        mem_canvas
    )
    vsb = tk.Scrollbar(root, orient=tk.VERTICAL, command=mem_canvas.yview)
    mem_canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    mem_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    mem_canvas.create_window((0, 0), window=mem_frame, anchor=tk.NW)
    mem_frame.bind('<Configure>', lambda e: config_frame(mem_canvas))
    if func_data is None:
        load_func(mem_frame)
    else:
        load_func(mem_frame, func_data)

# return a render of an image from a url TODO: find way to improve performance
def get_img_from_url(url, x, y):
    resp = requests.get(url)
    img = Image.open(BytesIO(resp.content))
    img = img.resize((x, y), Image.ANTIALIAS)
    render = ImageTk.PhotoImage(img)
    return render


def create_empty_img(x, y):
    img = Image.new(mode='RGB', size=(x, y))
    render = ImageTk.PhotoImage(img)
    return render


class MainGUI:
    client: Client = None
    main_frame: tk.Frame = None
    root: tk.Tk = None

    def __init__(self):
        self.root = tk.Tk()
        self.setup_login()
        self.root.mainloop()

    def clear_main(self):
        if self.main_frame is not None:
            self.main_frame.destroy()

    def setup_window(self, title, dimensions, x_resize, y_resize):
        self.root.title(title)
        self.root.geometry(dimensions)
        self.root.resizable(x_resize, y_resize)
        main_menu_frame = tk.Frame(
            self.root
        )
        main_menu_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame = main_menu_frame

    # TODO: figure out better size for window, improve handling for invalid tokens
    def setup_login(self):
        self.clear_main()
        self.setup_window('GroupMeUtils', '250x100', False, False)
        api_key_lbl = tk.Label(
            self.main_frame,
            text='Enter Access Token:'
        )
        api_key_lbl.pack()
        api_key_ent = tk.Entry(
            self.main_frame,
            width=25
        )
        api_key_ent.pack()
        go_btn = tk.Button(
            self.main_frame, text='Go',
            width=10,
            height=1
        )
        go_btn.bind('<Button-1>', lambda e: self.login(api_key_ent.get()))
        go_btn.pack()
        get_key_lbl = tk.Label(
            self.main_frame,
            text='Click here to get your Access Token'
        )
        get_key_lbl.bind('<Button-1>', lambda e: webbrowser.open('https://dev.groupme.com/session/new'))
        get_key_lbl.pack()

    def login(self, access_key):
        client = Client.from_token(access_key)
        try:
            client.user.get_me()
            self.client = client
            self.setup_main_menu()
        except exceptions.BadResponse:
            # tell user their access token is incorrect
            print('Bad Token')

    # TODO: make information copyable, make buttons work, make better loading
    def setup_main_menu(self):
        self.clear_main()
        self.setup_window('GroupMeUtils', '300x175', False, False)
        user_info = self.client.user.get_me()

        profile_info_lbl = tk.Label(
            self.main_frame,
            text=f'Id: {user_info["id"]}\n'
                 f'Name: {user_info["name"]}\n'
                 f'Email: {user_info["email"]}\n'
                 f'Phone: {user_info["phone_number"]}\n'
                 f'Creation Date: {datetime.fromtimestamp(user_info["created_at"])}'
        )
        profile_info_lbl.grid(row=0, column=0)
        prof_render = get_img_from_url(user_info['image_url'], 100, 100)
        profile_pic = tk.Label(
            self.main_frame,
            image=prof_render
        )
        profile_pic.image = prof_render
        profile_pic.grid(row=0, column=1)

        load_dms_btn = tk.Button(
            self.main_frame,
            text='Load DMs'
        )
        load_dms_btn.bind('<Button-1>', lambda e: self.setup_dms_menu())
        load_dms_btn.grid(row=1, column=0)

        load_groups_btn = tk.Button(
            self.main_frame,
            text='Load Groups'
        )
        load_groups_btn.bind('<Button-1>', lambda e: self.setup_groups_menu())
        load_groups_btn.grid(row=2, column=0)

        save_pfp_btn = tk.Button(
            self.main_frame,
            text='Save Picture'
        )
        save_pfp_btn.grid(row=1, column=1)

    def setup_dms_menu(self):
        self.clear_main()
        self.setup_window('GroupMeUtils', '300x600', False, False)
        make_return_btn(self.main_frame, self.setup_main_menu)
        # return_btn = tk.Button(
        #     self.main_frame,
        #     text='Return'
        # )
        # return_btn.bind('<Button-1>', lambda e: self.setup_main_menu())
        # return_btn.pack()
        make_scrollable_canvas(self.main_frame, self.load_dms)
        # dm_canvas = tk.Canvas(
        #     self.main_frame,
        #     borderwidth=0
        # )
        # dm_frame = tk.Frame(
        #     dm_canvas
        # )
        # vsb = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=dm_canvas.yview)
        # dm_canvas.configure(yscrollcommand=vsb.set)
        # vsb.pack(side=tk.RIGHT, fill=tk.Y)
        # dm_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # dm_canvas.create_window((0, 0), window=dm_frame, anchor=tk.NW)
        # dm_frame.bind('<Configure>', lambda e: config_frame(dm_canvas))
        # self.load_dms(dm_frame)

    # TODO: picture for no avatar
    def load_dms(self, frame):
        row = 0
        for chat in self.client.chats.list_all():
            if chat.other_user['avatar_url'] != '':
                pfp_render = get_img_from_url(chat.other_user['avatar_url'], 50, 50)
            else:
                pfp_render = create_empty_img(50, 50)
            pfp = tk.Label(frame, image=pfp_render)
            pfp.image = pfp_render
            pfp.grid(row=row, column=0)
            tk.Label(frame, text=chat.other_user['name']).grid(row=row, column=1)
            row += 1

    def setup_groups_menu(self):
        self.clear_main()
        self.setup_window('GroupMeUtils', '300x600', False, False)
        make_return_btn(self.main_frame, self.setup_main_menu)
        # return_btn = tk.Button(
        #     self.main_frame,
        #     text='Return'
        # )
        # return_btn.bind('<Button-1>', lambda e: self.setup_main_menu())
        # return_btn.pack()
        make_scrollable_canvas(self.main_frame, self.load_groups)
        # group_canvas = tk.Canvas(
        #     self.main_frame,
        #     borderwidth=0
        # )
        # group_frame = tk.Frame(
        #     group_canvas
        # )
        # vsb = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=group_canvas.yview)
        # group_canvas.configure(yscrollcommand=vsb.set)
        # vsb.pack(side=tk.RIGHT, fill=tk.Y)
        # group_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # group_canvas.create_window((0, 0), window=group_frame, anchor=tk.NW)
        # group_frame.bind('<Configure>', lambda e: config_frame(group_canvas))
        # self.load_groups(group_frame)

    # TODO: picture for no group avatar
    def load_groups(self, frame):
        row = 0
        for group in self.client.groups.list(omit='memberships'):
            if group.image_url is not None:
                pfp_render = get_img_from_url(group.image_url, 50, 50)
            else:
                pfp_render = create_empty_img(50, 50)
            pfp = tk.Label(frame, image=pfp_render)
            pfp.image = pfp_render
            pfp.grid(row=row, column=0)
            tk.Label(frame, text=group.name).grid(row=row, column=1)
            load_btn = tk.Button(
                frame,
                text='Open'
            )
            load_btn.bind('<Button-1>', lambda e, g=group: self.open_group_window(g))
            load_btn.grid(row=row, column=2)
            row += 1

    def open_group_window(self, group):
        group.refresh_from_server()
        new_group_win = tk.Toplevel(self.root)
        new_group_win.title(group.name)
        new_group_win.geometry('600x600')
        new_group_win.resizable(600, 600)
        action_frame = tk.Frame(
            new_group_win,
            width=300,
            height=600
        )
        action_frame.pack(anchor=tk.W, fill=tk.Y, expand=False, side=tk.LEFT)
        member_frame = tk.Frame(
            new_group_win,
            width=300,
            height=600
        )
        member_frame.pack(anchor=tk.N, fill=tk.BOTH, expand=True, side=tk.LEFT )
        if group.image_url is not None:
            pfp_render = get_img_from_url(group.image_url, 150, 150)
        else:
            pfp_render = create_empty_img(150, 150)
        pfp = tk.Label(action_frame, image=pfp_render)
        pfp.image = pfp_render
        pfp.pack(anchor=tk.CENTER)
        name_lbl = tk.Label(
            action_frame,
            text=group.name
        )
        name_lbl.pack(anchor=tk.CENTER)
        save_pfp_btn = tk.Button(
            action_frame,
            text='Save Picture'
        )
        save_pfp_btn.pack(anchor=tk.CENTER)
        make_scrollable_canvas(member_frame, self.load_members, group)
        # mem_canvas = tk.Canvas(
        #     member_frame,
        #     borderwidth=0
        # )
        # mem_frame = tk.Frame(
        #     mem_canvas
        # )
        # vsb = tk.Scrollbar(member_frame, orient=tk.VERTICAL, command=mem_canvas.yview)
        # mem_canvas.configure(yscrollcommand=vsb.set)
        # vsb.pack(side=tk.RIGHT, fill=tk.Y)
        # mem_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # mem_canvas.create_window((0, 0), window=mem_frame, anchor=tk.NW)
        # mem_frame.bind('<Configure>', lambda e: config_frame(mem_canvas))
        # self.load_members(mem_frame, group)
        self.load_messages(member_frame, group)
        new_group_win.mainloop()

    def load_members(self, frame, group):
        row = 0
        for mem in group.members:
            if mem.image_url != '' and mem.image_url is not None:
                pfp_render = get_img_from_url(mem.image_url, 50, 50)
            else:
                pfp_render = create_empty_img(50, 50)
            pfp = tk.Label(frame, image=pfp_render)
            pfp.image = pfp_render
            pfp.grid(row=row, column=0)
            tk.Label(frame, text=mem.nickname).grid(row=row, column=1)
            row += 1

    def load_messages(self, frame, dm_or_group):
        messages = list(dm_or_group.messages.list().autopage())
        for msg in messages[::-1]:
            print(f'[{msg.created_at}] {msg.name}: {msg.text} ({len(msg.favorited_by)} likes)')
