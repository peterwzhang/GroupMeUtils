from Group import *
from GUI import *
from config import TOKEN
from groupy.client import Client
from tkinter import *

# this is a temporary testing file
if __name__ == "__main__":
    client = Client.from_token(TOKEN)
    client.user.get_me()
    # group_list = list()
    # for group in client.groups.list(omit="memberships"):
    #     print(group.image_url)
    #     new_g = Group(group.id, group.name)
    #     group_list.append(new_g)
    # for g in group_list:
    #     g.print()
    # for chat in client.chats.list_all():
    #     print(chat.other_user["name"])

    # group = client.groups.get('61124351') this is an empty test group
    # print(group.data)
    # print(client.user.get_me())
    # for msg in group.messages.list_all():
    #     print(msg.text)
    #     print(msg.data)
    # print_groups(client)
    # print_members(group)

    LoginGUI()



