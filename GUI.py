from datetime import datetime
from groupy.api import memberships
from groupy.client import Client
from groupy import attachments, exceptions
from io import BytesIO
from PIL import Image, ImageTk
import os
import requests
import tkinter as tk
import webbrowser


def mention_all(group):
    loci_list = []
    g_id_list = []
    for m in group.members:
        loci_list.append((0, 9))
        g_id_list.append(m.user_id)
    mentions = [attachments.Mentions(loci=loci_list, user_ids=g_id_list)]
    group.post(text='@everyone', attachments=mentions)


def setup_picture_name(name, g_dm_id, avatar_url, frame, row, load):
    if load == 1 and avatar_url != '' and avatar_url is not None:
        pfp_render = get_img_from_url(avatar_url, 50, 50)
    else:
        pfp_render = create_empty_img(50, 50)
    pfp = tk.Label(frame, image=pfp_render)
    pfp.image = pfp_render
    pfp.grid(row=row, column=0)
    tk.Label(frame, text=f'{name}\n{g_dm_id}').grid(row=row, column=1)


def groups_to_id_list(g_list):
    id_list = []
    for g in g_list:
        id_list.append(g.id)
    return id_list


def mem_to_dict(m):
    member = {
        'nickname': m.nickname,
        'user_id': m.user_id
    }
    return member


def transfer_members(n_group_id, members, client):
    try:
        group = memberships.Memberships(client.session, n_group_id)
        m_list = []
        for m in members:
            m_list.append(mem_to_dict(m))
        group.add_multiple(*m_list)
    except exceptions.BadResponse:
        print('Group not found')


def spam_message(message, group_or_dm, num):
    for i in range(num):
        group_or_dm.post(text=message)


def save_to_clip(text):
    clip = tk.Tk()
    clip.withdraw()
    clip.clipboard_clear()
    clip.clipboard_append(text)
    clip.update()
    clip.destroy()


def make_folder(name):
    directory = os.path.join(os.getcwd(), name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def save_messages(dm_or_group, filename):
    downloads_path = make_folder('downloads')
    filename = filename + '_log.txt'
    path = os.path.join(downloads_path, filename)
    f = open(path, 'w')
    messages = list(dm_or_group.messages.list().autopage())
    for msg in messages[::-1]:
        f.write(f'[{msg.created_at}] {msg.name}: {msg.text} ({len(msg.favorited_by)} likes)\n')
    f.close()


def like_all(dm_or_group):
    messages = list(dm_or_group.messages.list().autopage())
    for msg in messages:
        msg.like()


def unlike_all(dm_or_group):
    messages = list(dm_or_group.messages.list().autopage())
    for msg in messages:
        msg.unlike()


def save_picture(url, name):
    resp = requests.get(url)
    if resp.status_code == 200:
        directory = make_folder('downloads')
        filename = name + '.png'
        path = os.path.join(directory, filename)
        f = open(path, 'wb')
        f.write(resp.content)
        f.close()


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


# return a render of an image from a url
def get_img_from_url(url, x, y):
    resp = requests.get(url)
    if resp.status_code == 200:
        img = Image.open(BytesIO(resp.content))
        img = img.resize((x, y), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(img)
        return render


def create_empty_img(x, y):
    img = Image.new(mode='RGB', size=(x, y))
    render = ImageTk.PhotoImage(img)
    return render


class MainGUI:

    def __init__(self):
        self.client = None
        self.main_frame = None
        self.root = tk.Tk()
        self.setup_login()
        self.picture_bool = tk.IntVar(self.root)
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

    # TODO: improve handling for invalid tokens
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
                 f'Creation Date: {datetime.fromtimestamp(user_info["created_at"])}',
            justify=tk.LEFT
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
        save_pfp_btn.bind('<Button-1>', lambda e: save_picture(user_info['image_url'], user_info['id']))
        save_pfp_btn.grid(row=1, column=1)
        img_load_box = tk.Checkbutton(self.main_frame, text='Load Pictures?', var=self.picture_bool)
        img_load_box.grid(row=2, column=1)

    def setup_dms_menu(self):
        self.clear_main()
        self.setup_window('GroupMeUtils', '300x600', False, False)
        make_return_btn(self.main_frame, self.setup_main_menu)
        make_scrollable_canvas(self.main_frame, self.load_dms)

    def load_dms(self, frame):
        row = 0
        for chat in self.client.chats.list_all():
            setup_picture_name(chat.other_user["name"], chat.other_user["id"], chat.other_user['avatar_url'], frame,
                               row, self.picture_bool.get())
            load_btn = tk.Button(
                frame,
                text='Open'
            )
            load_btn.bind('<Button-1>', lambda e, c=chat: self.open_dm_window(c))
            load_btn.grid(row=row, column=2)
            row += 1

    def setup_groups_menu(self):
        self.clear_main()
        self.setup_window('GroupMeUtils', '300x600', False, False)
        make_return_btn(self.main_frame, self.setup_main_menu)
        make_scrollable_canvas(self.main_frame, self.load_groups)

    def load_groups(self, frame):
        row = 0
        for group in self.client.groups.list(omit='memberships'):
            setup_picture_name(group.name, group.id, group.image_url, frame, row, self.picture_bool.get())
            load_btn = tk.Button(
                frame,
                text='Open'
            )
            load_btn.bind('<Button-1>', lambda e, g=group: self.open_group_window(g))
            load_btn.grid(row=row, column=2)
            row += 1

    def open_dm_window(self, chat):
        self.setup_dm_win(chat)

    def open_group_window(self, group):
        self.setup_group_win(group)

    def load_members(self, frame, group):
        row = 0
        for mem in group.members:
            setup_picture_name(mem.nickname, mem.id, mem.image_url, frame, row, self.picture_bool.get())
            row += 1

    def setup_group_win(self, group):
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
        member_frame.pack(anchor=tk.N, fill=tk.BOTH, expand=True, side=tk.LEFT)
        if group.image_url is not None:
            pfp_render = get_img_from_url(group.image_url, 150, 150)
        else:
            pfp_render = create_empty_img(150, 150)
        pfp = tk.Label(action_frame, image=pfp_render)
        pfp.image = pfp_render
        pfp.pack(anchor=tk.CENTER)
        name_lbl = tk.Label(
            action_frame,
            text=f'Id: {group.id}\n'
                 f'Name: {group.name}\n'
                 f'Phone: {group.phone_number}\n'
                 f'Creation Date:\n {group.created_at}',
            width=20,
            wraplength=125,
            justify=tk.LEFT
        )
        name_lbl.pack(anchor=tk.E)
        save_pfp_btn = tk.Button(
            action_frame,
            text='Save Picture',
            width=20
        )
        save_pfp_btn.bind('<Button-1>', lambda e: save_picture(group.image_url, group.id))
        save_pfp_btn.pack(anchor=tk.CENTER)
        save_msg_btn = tk.Button(
            action_frame,
            text='Save Messages',
            width=20
        )
        save_msg_btn.bind('<Button-1>', lambda e: save_messages(group, group.id))
        save_msg_btn.pack(anchor=tk.CENTER)
        like_all_btn = tk.Button(
            action_frame,
            text='Like All Messages',
            width=20
        )
        like_all_btn.bind('<Button-1>', lambda e: like_all(group))
        like_all_btn.pack(anchor=tk.CENTER)
        unlike_all_btn = tk.Button(
            action_frame,
            text='Unlike All Messages',
            width=20
        )
        unlike_all_btn.bind('<Button-1>', lambda e: unlike_all(group))
        unlike_all_btn.pack(anchor=tk.CENTER)
        copy_share_btn = tk.Button(
            action_frame,
            text='Copy Share URL',
            width=20
        )
        copy_share_btn.bind('<Button-1>', lambda e: save_to_clip(group.share_url))
        copy_share_btn.pack(anchor=tk.CENTER)
        mention_btn = tk.Button(
            action_frame,
            text='Mention All',
            width=20
        )
        mention_btn.bind('<Button-1>', lambda e: mention_all(group))
        mention_btn.pack(anchor=tk.CENTER)
        msg_scale = tk.Scale(
            action_frame,
            from_=1,
            to_=100,
            length=150,
            orient=tk.HORIZONTAL
        )
        msg_scale.pack(anchor=tk.CENTER)
        msg_ent = tk.Entry(
            action_frame,
            width=25
        )
        msg_ent.pack(anchor=tk.CENTER)
        spam_msg_btn = tk.Button(
            action_frame,
            text='Spam Message',
            width=20
        )
        spam_msg_btn.bind('<Button-1>', lambda e: spam_message(msg_ent.get(), group, msg_scale.get()))
        spam_msg_btn.pack(anchor=tk.CENTER)
        options = groups_to_id_list(self.client.groups.list(omit='memberships'))
        var = tk.StringVar(self.root)
        var.set(options[0])
        transfer_option_menu = tk.OptionMenu(
            action_frame,
            var,
            *options
        )
        transfer_option_menu.config(width=18)
        transfer_option_menu.pack()

        transfer_btn = tk.Button(
            action_frame,
            text='Transfer Members',
            width=20
        )
        transfer_btn.bind('<Button-1>', lambda e: transfer_members(var.get(), group.members,
                                                                   self.client))
        transfer_btn.pack(anchor=tk.CENTER)
        make_scrollable_canvas(member_frame, self.load_members, group)
        new_group_win.mainloop()

    def setup_dm_win(self, chat):
        new_group_win = tk.Toplevel(self.root)
        new_group_win.title(chat.other_user['name'])
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
        member_frame.pack(anchor=tk.N, fill=tk.BOTH, expand=True, side=tk.LEFT)
        if chat.other_user['avatar_url'] != '':
            pfp_render = get_img_from_url(chat.other_user['avatar_url'], 150, 150)
        else:
            pfp_render = create_empty_img(150, 150)
        pfp = tk.Label(action_frame, image=pfp_render)
        pfp.image = pfp_render
        pfp.pack(anchor=tk.CENTER)
        name_lbl = tk.Label(
            action_frame,
            text=f'Id: {chat.other_user["id"]}\n'
                 f'Name: {chat.other_user["name"]}\n',
            width=20,
            wraplength=125,
            justify=tk.LEFT
        )
        name_lbl.pack(anchor=tk.E)
        save_pfp_btn = tk.Button(
            action_frame,
            text='Save Picture',
            width=20
        )
        save_pfp_btn.bind('<Button-1>', lambda e: save_picture(chat.other_user['avatar_url'], chat.other_user["id"]))
        save_pfp_btn.pack(anchor=tk.CENTER)
        save_msg_btn = tk.Button(
            action_frame,
            text='Save Messages',
            width=20
        )
        save_msg_btn.bind('<Button-1>', lambda e: save_messages(chat, chat.other_user['id']))
        save_msg_btn.pack(anchor=tk.CENTER)
        like_all_btn = tk.Button(
            action_frame,
            text='Like All Messages',
            width=20
        )
        like_all_btn.bind('<Button-1>', lambda e: like_all(chat))
        like_all_btn.pack(anchor=tk.CENTER)
        unlike_all_btn = tk.Button(
            action_frame,
            text='Unlike All Messages',
            width=20
        )
        unlike_all_btn.bind('<Button-1>', lambda e: unlike_all(chat))
        unlike_all_btn.pack(anchor=tk.CENTER)
        make_scrollable_canvas(member_frame, self.load_chat_members, chat)
        new_group_win.mainloop()

    def load_chat_members(self, frame, c):
        row = 0
        if self.picture_bool.get() == 1 and c.other_user['avatar_url'] != '':
            pfp_render = get_img_from_url(c.other_user['avatar_url'], 50, 50)
        else:
            pfp_render = create_empty_img(50, 50)
        pfp = tk.Label(frame, image=pfp_render)
        pfp.image = pfp_render
        pfp.grid(row=row, column=0)
        tk.Label(frame, text=f'{c.other_user["name"]}\n{c.other_user["id"]}').grid(row=row, column=1)
        row += 1
        me = self.client.user.get_me()
        if self.picture_bool.get() == 1 and me['image_url'] != '':
            pfp_render = get_img_from_url(me['image_url'], 50, 50)
        else:
            pfp_render = create_empty_img(50, 50)
        pfp = tk.Label(frame, image=pfp_render)
        pfp.image = pfp_render
        pfp.grid(row=row, column=0)
        tk.Label(frame, text=f'{me["name"]}\n{me["id"]}').grid(row=row, column=1)


