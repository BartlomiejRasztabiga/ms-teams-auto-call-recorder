## Built upon [Teams-Auto-Joiner](https://github.com/TobiasPankner/Teams-Auto-Joiner)

## This python script will automatically join and record [Microsoft Teams](https://www.microsoft.com/en-in/microsoft-365/microsoft-teams/group-chat-software) meetings appearing in your Teams groups.

## Features:

- This python script will automatically open a chrome tab, enter your username, your password, and then join an active meeting if available.
- After joining, it will record screen using Windows built in recording functionality [Game Bar](https://community.windows.com/en-us/stories/capture-and-share-videos-with-game-bar).
- Before joining any meeting, it will by default turn off your camera and microphone.
- After the organiser ends the meeting, it will open the teams tab to look for new meetings and join the next meeting if available.
- If the organiser does not end the meeting i.e. attendees are made to leave the meeting, the script will automatically leave the meeting after the number of participants present in the meeting falls below the minimum participants allowed set by the user (default is 10), but will rejoin the meeting if the meeting is still active. To not rejoin the same meeting user must stop the script by CTRL+C.

## Requirements:

- [Python3](https://www.python.org/downloads/)
- [Google Chrome browser](https://www.google.com/intl/en_in/chrome/)
- [Windows 10 (with Game Bar)](https://www.microsoft.com/pl-pl/software-download/windows10)

## Prerequisites:

### After cloning the repo, go in the repo directory and then follow below steps:

- Step 1:
  Install dependencies from [requirements.txt](requirements.txt):

  ```bash
  pip install -r requirements.txt
  ```

- Step 2:
  To set login credentials and other settings, rename [config.json.example](config.json.example) to config.json and modify certain fields as you wish:

## Configuration options

- **email/password:**  
  The email/password of your Microsoft account (can be left empty if you don't want to automatically login)

- **run_at_time:**  
  Time to start the script at. Input is a string of the hour and minute in 24h format, if you want it to start immediately leave this empty.
  If a time before the current time is given, the next day is used. Also make sure that "start_automatically" is set to true and that
  you entered your email and password.  
  For example, if you want the script to start searching meetings at 6 in the morning on the next day, you would input `06:00` in the config.

- **start_automatically:**  
  If true, skips the `Start [s], Reload teams [r], Quit [q]` dialog and starts on it's own. Useful if you schedule the script to start at a specific time.

- **organisation_num:**  
  If your Teams account is in multiple organisations, as seen in the example below, change the organisation_num to the number of the list item (counting starts from 1)  
  <img width="30%" src="https://imgur.com/CWpK4wk.png">

- **random_delay:**  
  If true, adds a random delay (10s-30s) before joining a meeting. Can be useful so the bot seems more "human like".

- **check_interval:**  
  The amount of seconds to wait before checking for meetings again. Only integer numbers greater than 1 are allowed.

- **auto_leave_after_min:**  
  If set to a value greater than zero, the bot leaves every meeting after the specified time (in minutes). Useful if you know the length of your meeting, if this is left a the default the bot will stay in the meeting until a new one is available.

- **leave_if_last:**  
  If true, leaves the meeting if you are the last person in it.

- **mute_audio:**  
  If true, mutes all the sounds.

- **chrome_type:**  
  Valid options: `google-chrome`, `chromium`, `msedge`. By default, google chrome is used, but the script can also be used with Chromium or Microsoft Edge.

- **blacklist:**  
  A list of Teams and their channels to ignore. Meetings ocurring in these channels will not be joined.  
  If you have a Team called "Test1" and, within that, two channels called "General" and "Channel1" and you don't want to join meetings in the "General" Channel:

```json
"blacklist": [
  {
    "team_name": "Test1",
    "channel_names": [
      "General"
    ]
  }
]
```

## Usage:

- Run [autoRecord.py](autoRecord.py):
  ```bash
  python autoRecord.py
  ```
- The script might not work as expected if the browser is minimised i.e you may open other windows above it but do not minimize the chrome window.

## Sample Scenario:

- You have a meeting at 9 A.M, you may run the script anytime before 9 A.M. and the script will automatically join the meeting when the join button is available.
- The script will then automatically join the next meeting scheduled at e.g.:- 10 A.M. AFTER the organiser ends the meeting.
- If the organiser does not end the meeting i.e the organiser leaves the meeting instead of ending the meeting and tells the attendee to leave the meeting, the script will leave the meeting after the strength of the meeting falls down to 10 or any minimum value set by user.

## Contributing:

- Feel free to contribute anytime!
