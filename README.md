#Remindr
# Reminder App
The Reminder App is a Python application built using the tkinter library for creating a simple GUI, schedule library for scheduling tasks, and plyer library for displaying notifications. This app allows users to set reminders throughout the day and also includes a Pomodoro timer feature for improved productivity.

Features
Set Reminders: Users can set multiple reminders per day by specifying the frequency and task to be reminded of.
Custom Reminder Time: Users can set custom reminder times in HH:MM format or use default intervals based on the frequency.
Scheduled Reminders: Displays a list of all scheduled reminders with the option to remove selected reminders.
Pomodoro Timer: Includes a Pomodoro timer feature with start, pause, and resume functionality to help users stay focused.
Notifications: Shows desktop notifications for reminders and Pomodoro timer alerts for a seamless user experience.
How to Use
Set Reminders:

Enter the number of reminders per day in the provided field.
Input the task to be reminded of in the task entry.
Optionally, specify custom reminder times in HH:MM format separated by commas.
Click on the "Set Reminders" button to save and schedule the reminders.
Pomodoro Timer:

Click on the "Start Pomodoro" button to begin a 25-minute Pomodoro session.
Use the "Pause" button to pause the timer and "Resume" to continue the session.
Upon completion, a notification will be displayed to indicate the end of the session.
Managing Reminders:

View all scheduled reminders in the listbox and select specific reminders to remove.
Click on the "Remove Selected" button to delete the chosen reminder.
Closing the App:

The app will automatically save scheduled reminders when closed using the window close button.
Installation
Ensure you have Python 3 installed on your system.
Install required libraries using pip:
pip install tk schedule plyer
Run the Reminder App script:
python reminder_app.py

Enjoy using the Reminder App to stay organized and boost your productivity!
