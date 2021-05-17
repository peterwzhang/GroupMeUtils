from groupy.client import Client


def print_group(group):
    """Print a singular group
    :param Group group: The group to print.
    """
    print(f'NAME: {group.name} ID: {group.id} MEMBERS: {len(group.members)}')


def print_groups(client):
    """Print all of a user's groups
    :param Client client: The client of the current user.
    """
    user = client.user.get_me()
    print("Your groups:")
    for group in client.groups.list():
        print_group(group)


def print_members(group):
    """Print the members of a group
        :param Group group: The group to get members from.
    """
    print(f'Members of {group.name}:')
    for member in group.members:
        # print(member.data)
        print(f'NAME: {member.name} ID: {member.id} GID: {member.user_id}')
