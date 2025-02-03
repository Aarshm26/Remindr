import tkinter as tk
from tkinter import ttk, messagebox
import schedule
import time
import threading
from plyer import notification
from datetime import datetime, timedelta
import json
import random
from tkinter.font import Font

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Remindr")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2D2D2D")
        
        self.colors = {
            "primary": "#8e7cc3",
            "secondary": "#45A049",
            "background": "#2D2D2D",
            "text": "#FFFFFF",
            "accent": "#FF5722",
            "list_bg": "#404040"
        }

        self.frequency = tk.IntVar()
        self.task = tk.StringVar()
        self.custom_time = tk.StringVar()

        self.reminders = []
        self.pomodoro_running = False
        self.pomodoro_paused = False
        self.pomodoro_time = 25 * 60
        self.original_time = 25 * 60

        self.create_widgets()
        self.load_reminders()
        self.create_progress_circle()

    def create_progress_circle(self):
        self.canvas = tk.Canvas(self.right_frame, width=250, height=250, 
                              bg=self.colors["background"], highlightthickness=0)
        self.canvas.pack(pady=20)
        self.progress_arc = self.canvas.create_arc(25, 25, 225, 225, start=90, 
                                                 extent=360, outline=self.colors["primary"],
                                                 width=8, style=tk.ARC)

    def update_progress(self):
        if self.pomodoro_running and not self.pomodoro_paused:
            progress = ((self.original_time - self.pomodoro_time) / self.original_time) * 360
            self.canvas.itemconfig(self.progress_arc, extent=360 - progress)
            self.root.after(1000, self.update_progress)

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("TFrame", background=self.colors["background"])
        style.configure("TButton", padding=12, relief="flat", 
                       font=("Helvetica", 12, "bold"))
        style.map("TButton", 
                background=[("active", self.colors["secondary"]), 
                           ("!active", self.colors["primary"])],
                foreground=[("!active", self.colors["text"])])
        style.configure("TLabel", background=self.colors["background"], 
                      foreground=self.colors["text"], font=("Helvetica", 12))
        style.configure("TEntry", font=("Helvetica", 12), 
                       fieldbackground="#404040", foreground=self.colors["text"])

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Panel (Reminders)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(left_frame, text="REMINDERS", font=("Helvetica", 16, "bold")).pack(pady=10)

        input_frame = ttk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=8)

        ttk.Label(input_frame, text="Daily Reminders:").pack(side=tk.LEFT)
        self.freq_entry = ttk.Entry(input_frame, textvariable=self.frequency, width=8)
        self.freq_entry.pack(side=tk.RIGHT)

        input_frame = ttk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=8)

        ttk.Label(input_frame, text="Task:").pack(side=tk.LEFT)
        self.task_entry = ttk.Entry(input_frame, textvariable=self.task)
        self.task_entry.pack(side=tk.RIGHT, fill=tk.X)

        input_frame = ttk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=8)

        ttk.Label(input_frame, text="Custom Times:").pack(side=tk.LEFT)
        self.time_entry = ttk.Entry(input_frame, textvariable=self.custom_time)
        self.time_entry.pack(side=tk.RIGHT, fill=tk.X)

        ttk.Button(left_frame, text="🕒 Set Reminders", command=self.set_reminders).pack(pady=15)

        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.reminder_listbox = tk.Listbox(list_frame, font=("Helvetica", 12),
                                         bg=self.colors["list_bg"], fg=self.colors["text"],
                                         selectbackground=self.colors["primary"])
        self.reminder_listbox.pack(fill=tk.BOTH, expand=True)

        ttk.Button(left_frame, text="Remove Selected", command=self.remove_reminder).pack(pady=10)

        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(self.right_frame, text="POMODORO TIMER", 
                font=("Helvetica", 16, "bold")).pack(pady=10)

        self.timer_label = ttk.Label(self.right_frame, text="25:00", 
                                   font=("Helvetica", 48, "bold"),
                                   foreground=self.colors["accent"])
        self.timer_label.pack(pady=20)

        control_frame = ttk.Frame(self.right_frame)
        control_frame.pack(pady=15)

        self.start_btn = ttk.Button(control_frame, text="▶ Start", command=self.start_pomodoro)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = ttk.Button(control_frame, text="⏸ Pause", 
                                  command=self.pause_resume_pomodoro, state=tk.DISABLED)
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="⏹ Stop", 
                                 command=self.stop_pomodoro, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=2, padx=5)

        self.motivation_label = ttk.Label(self.right_frame, text="", 
                                        font=("Helvetica", 14, "italic"),
                                        wraplength=300,
                                        foreground=self.colors["accent"])
        self.motivation_label.pack(pady=20)

    def set_reminders(self):
        try:
            frequency = self.frequency.get()
            task = self.task.get()
            custom_times = self.custom_time.get().split(',')

            if frequency <= 0 or not task:
                raise ValueError("Please enter valid values for both fields")

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
                        messagebox.showerror("Error", f"Invalid time: {custom_time}")
            else:
                interval = 24 / frequency
                start_time = datetime.now().replace(hour=0, minute=0, second=0)

                for i in range(frequency):
                    reminder_time = (start_time + timedelta(hours=i * interval)).time()
                    schedule_time = reminder_time.strftime("%H:%M")
                    schedule.every().day.at(schedule_time).do(self.show_notification, task=task)
                    reminder_info = f"{schedule_time} - {task}"
                    self.reminders.append(reminder_info)
                    self.reminder_listbox.insert(tk.END, reminder_info)

            self.save_reminders()
            messagebox.showinfo("Success", "Reminders set successfully")
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
            reminder = self.reminders[selected[0]]
            time_str, task_str = reminder.split(" - ")
            schedule.clear(task_str)
            self.reminder_listbox.delete(selected)
            self.reminders.pop(selected[0])
            self.save_reminders()
            messagebox.showinfo("Removed", f"Removed: {reminder}")

    def start_pomodoro(self):
        if not self.pomodoro_running:
            self.pomodoro_running = True
            self.pomodoro_paused = False
            self.original_time = self.pomodoro_time = 25 * 60
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.update_progress()
            self.run_pomodoro()

    def pause_resume_pomodoro(self):
        if self.pomodoro_running:
            self.pomodoro_paused = not self.pomodoro_paused
            self.pause_btn.config(text="⏸ Pause" if not self.pomodoro_paused else "▶ Resume")
            if not self.pomodoro_paused:
                self.run_pomodoro()

    def stop_pomodoro(self):
        self.pomodoro_running = False
        self.pomodoro_paused = False
        self.pomodoro_time = 25 * 60
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.timer_label.config(text="25:00")
        self.canvas.itemconfig(self.progress_arc, extent=360)

    def run_pomodoro(self):
        if self.pomodoro_running and not self.pomodoro_paused:
            if self.pomodoro_time > 0:
                mins, secs = divmod(self.pomodoro_time, 60)
                self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
                self.pomodoro_time -= 1
                self.root.after(1000, self.run_pomodoro)
            else:
                self.stop_pomodoro()
                notification.notify(
                    title="Pomodoro Complete",
                    message="Time for a break!",
                    timeout=10
                )
                self.show_motivation()

    def show_motivation(self):
        quotes = [
            "Great work! Keep crushing your goals!",
            "Productivity unlocked! Take a break!",
            "You're making progress! Stay focused!",
            "Well deserved break! Recharge now!",
            "Awesome work! Keep the momentum going!"
        ]
        self.motivation_label.config(text=random.choice(quotes))
        self.motivation_label.after(5000, lambda: self.motivation_label.config(text=""))

    def save_reminders(self):
        with open("reminders.json", "w") as f:
            json.dump(self.reminders, f)

    def load_reminders(self):
        try:
            with open("reminders.json", "r") as f:
                self.reminders = json.load(f)
                for reminder in self.reminders:
                    time_str, task_str = reminder.split(" - ")
                    schedule.every().day.at(time_str).do(self.show_notification, task=task_str)
                    self.reminder_listbox.insert(tk.END, reminder)
                self.run_schedule()
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def on_closing(self):
        if messagebox.askokcancel("Exit", "Save and quit?"):
            self.save_reminders()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
