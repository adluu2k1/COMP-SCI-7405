from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from plyer import notification
from kivy.clock import Clock

from datetime import datetime
import json
import os

class MainScreen(Screen):
    pass

class AddTaskScreen(Screen):
    pass

class ToDoApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.load_tasks()
        return Builder.load_file("main.kv")

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as f:
                self.tasks = json.load(f)
        else:
            self.tasks = []

    def save_tasks(self):
        with open("tasks.json", "w") as f:
            json.dump(self.tasks, f)

    def add_task(self):
        title = self.root.ids.add_task_screen.ids.task_title.text
        date_str = self.root.ids.add_task_screen.ids.date_input.text

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            self.show_dialog("Invalid date format. Use YYYY-MM-DD.")
            return

        if not title:
            self.show_dialog("Task title cannot be empty.")
            return

        task = {"title": title, "date": date_str, "completed": False}
        self.tasks.append(task)
        self.save_tasks()
        self.root.ids.add_task_screen.ids.task_title.text = ""
        self.root.ids.add_task_screen.ids.date_input.text = ""
        self.show_dialog("Task added successfully.")
        self.root.current = "main_screen"
        self.update_task_list()

    def update_task_list(self):
        self.root.ids.main_screen.ids.task_list.clear_widgets()
        for task in self.tasks:
            task_str = f"[{'x' if task['completed'] else ' '}] {task['title']} ({task['date']})"
            self.root.ids.main_screen.ids.task_list.add_widget(
                MDFlatButton(text=task_str, on_release=lambda btn, t=task: self.toggle_task(t))
            )

    def toggle_task(self, task):
        task["completed"] = not task["completed"]
        self.save_tasks()
        self.update_task_list()

    def show_dialog(self, text):
        if hasattr(self, "dialog") and self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()

    def on_start(self):
        self.update_task_list()
        Clock.schedule_once(lambda dt: self.send_notification("To-Do App Ready!", "Stay productive!"), 5)

    def send_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            timeout=5
        )

    def switch_to_main(self):
        self.root.current = "main_screen"

ToDoApp().run()
