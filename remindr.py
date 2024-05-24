import tkinter as tk
from tkinter import ttk, messagebox
import schedule
import time
import threading
from plyer import notification
from datetime import datetime, timedelta
import json

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Remindr")
        self.root.geometry("500x600")

        self.frequency = tk.IntVar()
        self.task = tk.StringVar()
        self.custom_time = tk.StringVar()

        self.reminders = []
        self.pomodoro_running = False
        self.pomodoro_paused = False
        self.pomodoro_time = 25 * 60
        self.pause_time = 0

        self.create_widgets()
        self.load_reminders()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Set number of reminders per day:").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.freq_entry = ttk.Entry(frame, textvariable=self.frequency)
        self.freq_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Enter the task:").grid(row=1, column=0, pady=5, sticky=tk.W)
        self.task_entry = ttk.Entry(frame, textvariable=self.task)
        self.task_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Custom reminder time (HH:MM, optional, comma separated):").grid(row=2, column=0, pady=5, sticky=tk.W)
        self.time_entry = ttk.Entry(frame, textvariable=self.custom_time)
        self.time_entry.grid(row=2, column=1, pady=5)

        self.set_btn = ttk.Button(frame, text="Set Reminders", command=self.set_reminders)
        self.set_btn.grid(row=3, columnspan=2, pady=20)

        ttk.Label(frame, text="Scheduled Reminders:").grid(row=4, columnspan=2, pady=5)

        self.reminder_listbox = tk.Listbox(frame, height=8, width=50)
        self.reminder_listbox.grid(row=5, columnspan=2, pady=5)

        self.remove_btn = ttk.Button(frame, text="Remove Selected", command=self.remove_reminder)
        self.remove_btn.grid(row=6, columnspan=2, pady=5)

        self.pomodoro_btn = ttk.Button(frame, text="Start Pomodoro", command=self.start_pomodoro)
        self.pomodoro_btn.grid(row=7, columnspan=2, pady=10)

        self.pause_resume_btn = ttk.Button(frame, text="Pause", command=self.pause_resume_pomodoro)
        self.pause_resume_btn.grid(row=8, columnspan=2, pady=5)
        self.pause_resume_btn.config(state=tk.DISABLED)

        self.pomodoro_label = ttk.Label(frame, text="", font=('Helvetica', 14))
        self.pomodoro_label.grid(row=9, columnspan=2, pady=5)

    def set_reminders(self):
        try:
            frequency = self.frequency.get()
            task = self.task.get()
            custom_times = self.custom_time.get().split(',')

            if frequency <= 0 or not task:
                raise ValueError("Invalid input. Please enter a positive integer for frequency and a non-empty task.")

            self.reminders = []
            self.reminder_listbox.delete(0, tk.END)

            if custom_times and custom_times[0]:
                for custom_time in custom_times:
                    custom_time = custom_time.strip()
                    try:
                        datetime.strptime(custom_time, "%H:%M")
                        schedule.every().day.at(custom_time).do(self.show_notification, task=task)
                        reminder_info = f"{custom_time} - {task}"
                        self.reminders.append(reminder_info)
                        self.reminder_listbox.insert(tk.END, reminder_info)
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid time format: {custom_time}. Please use HH:MM.")
            else:
                interval = 24 / frequency
                start_time = datetime.now().replace(minute=0, second=0, microsecond=0)

                for i in range(frequency):
                    reminder_time = (start_time + timedelta(hours=i * interval)).time()
                    schedule_time = reminder_time.strftime("%H:%M")
                    schedule.every().day.at(schedule_time).do(self.show_notification, task=task)
                    reminder_info = f"{schedule_time} - {task}"
                    self.reminders.append(reminder_info)
                    self.reminder_listbox.insert(tk.END, reminder_info)

            self.save_reminders()
            messagebox.showinfo("Success", "Reminders have been set!")
            self.run_schedule()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def show_notification(self, task):
        notification.notify(
            title="Reminder",
            message=f"Time to: {task}",
            timeout=10
        )

    def run_schedule(self):
        def run():
            while True:
                schedule.run_pending()
                time.sleep(1)

        self.schedule_thread = threading.Thread(target=run, daemon=True)
        self.schedule_thread.start()

    def remove_reminder(self):
        selected = self.reminder_listbox.curselection()
        if selected:
            reminder_to_remove = self.reminders[selected[0]]
            time_to_remove, task_to_remove = reminder_to_remove.split(" - ")
            schedule.clear(task_to_remove)
            self.reminder_listbox.delete(selected)
            self.reminders.pop(selected[0])
            self.save_reminders()
            messagebox.showinfo("Success", f"Removed reminder: {reminder_to_remove}")
        else:
            messagebox.showwarning("Warning", "No reminder selected")

    def start_pomodoro(self):
        if not self.pomodoro_running:
            self.pomodoro_running = True
            self.pomodoro_paused = False
            self.pause_resume_btn.config(state=tk.NORMAL)
            self.pomodoro_time = 25 * 60
            self.run_pomodoro()

    def pause_resume_pomodoro(self):
        if self.pomodoro_running:
            if self.pomodoro_paused:
                self.pomodoro_paused = False
                self.pause_resume_btn.config(text="Pause")
                self.run_pomodoro()
            else:
                self.pomodoro_paused = True
                self.pause_resume_btn.config(text="Resume")

    def run_pomodoro(self):
        if self.pomodoro_running and not self.pomodoro_paused:
            if self.pomodoro_time > 0:
                mins, secs = divmod(self.pomodoro_time, 60)
                time_format = '{:02d}:{:02d}'.format(mins, secs)
                self.pomodoro_label.config(text=f"Pomodoro: {time_format}")
                self.pomodoro_time -= 1
                self.root.after(1000, self.run_pomodoro)
            else:
                self.pomodoro_running = False
                self.pause_resume_btn.config(state=tk.DISABLED)
                self.pomodoro_label.config(text="Pomodoro session completed!")
                notification.notify(
                    title="Pomodoro Timer",
                    message="Time to take a break!",
                    timeout=10
                )
                self.show_motivation()

    def show_motivation(self):
        top = tk.Toplevel(self.root)
        top.title("Motivation")
        top.geometry("300x200")
        msg = tk.Label(top, text="You're winning!!", font=('Helvetica', 16, 'bold'))
        msg.pack(expand=True)
        top.after(5000, top.destroy)

    def save_reminders(self):
        with open("reminders.json", "w") as f:
            json.dump(self.reminders, f)

    def load_reminders(self):
        try:
            with open("reminders.json", "r") as f:
                self.reminders = json.load(f)
                for reminder in self.reminders:
                    time, task = reminder.split(" - ")
                    schedule.every().day.at(time).do(self.show_notification, task=task)
                    self.reminder_listbox.insert(tk.END, reminder)
                self.run_schedule()
        except FileNotFoundError:
            pass

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.save_reminders()
            self.root.destroy()
            self.schedule_thread.join()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
