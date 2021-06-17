### GroupMe Utils
A tool that help accomplish some tedious tasks on [GroupMe](https://groupme.com)
by using the GroupMe API.

## Setup
In order to setup GroupMeUtils you need the following:  
- Your GroupMe Access Token (You can get this [here](https://dev.groupme.com/session/new), click access token at the top right)
- Python3.4 or above (You can get this [here](https://www.python.org/downloads/)) 

Once you have the items above, you can follow the instructions below:
1. Clone the repository: `$ git clone https://github.com/PeterTheAmazingAsian/GroupMeUtils.git`
2. Go into the new cloned directory: `$  cd GroupMeUtils/`
3. Make a [virtual environment](https://docs.python.org/3/library/venv.html) (optional): `$ python -m venv venv`
   - Activate the virtual environment ([click here for help](https://docs.python.org/3/library/venv.html))
4. Install requirements: `$ pip install -r requirements.txt`
5. Run: `$ python main.py`

## Features
- View your account data such as account id, account name, email, phone number, and creation date
- View group info that is not displaced in the app such as phone number and creation date
- Save profile pictures of groups, other users in your dms, and even your own
- Save messages in groups or direct messages to test files
- Like/unlike all messages in a dm or group
- Copy the share url of a group to your clipboard
- Mention everyone in a group
- Spam messages in a group
- Transfer the members of one group to another group

## Note
- I recommend leaving "Load Pictures?" off as turning it on significantly increases loading time. 
  GroupMeUtils will still load pictures when it will not significantly increase load time when this
  option is left off.
- The save message and save picture will save the files to a "downloads" folder in the current working directory.
- On some systems the GUI might not be sized perfectly, but you can resize the window to make everything fit.

## Group Feature Guide
Below is a picture of an opened group with some descriptions of what each button does:
![Example Image](https://petertheamazingasian.github.io/assets/groupmeutils.png)
1. Saves the group picture into the downloads folder, the file will be titled with the group id
2. Saves the group messages into the downloads folder, the file will be titled with group id_log
3. Likes all messages in the group starting from the most recent message
4. Unlikes all messages in the group starting from the most recent message
5. Copies the share url of the group to your clipboard
6. Sends a message containing "@everyone" which will mention everyone in the group
7. Spams the specified message in the group, type the message in the entry right above this button, you can set how many messages in the slider above also
8. Transfers all the members of the current group to another group, you can select the other group in the drop down above this button