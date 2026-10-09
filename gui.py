import tkinter as tk
from PIL import Image
from PIL import Image, ImageTk
import os, threading
from storage import mark_today_done, load_habits, get_streak
from datetime import datetime
import pystray
from pystray import MenuItem as item
from PIL import Image as PILImage

def show_toast(message):
    toast=tk.Toplevel()
    toast.overrideredirect(True)  #No titlebar
    toast.geometry("250x50+100+50") # size and position

    label= tk.Label(
        toast,
        text=message,
        font=("Arial",10),
        bg="black",
        fg="white",
        padx=10,
        pady=10
    )
    label.pack(fill="both",expand=True)

    toast.after(2000,toast.destroy)

def get_mascot_image(mood, max_width=100):
    import sys
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, "assets", f"{mood}.png")
    image = Image.open(path)

    w_percent = max_width / float(image.size[0])
    new_height = int((float(image.size[1]) * float(w_percent)))

    # 🟢 Updated line (no more ANTIALIAS)
    resized_image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(resized_image)


def launch_app():
    root = tk.Tk()
    root.title("HabiTurtle 🐢")
    root.geometry("400x400")
    
    # Make window act like a floating widget
    root.attributes("-topmost", True)
    root.overrideredirect(False)  # True removes title bar completely

    def update_streak():
        habits=load_habits()
        streak= get_streak(habits)
        streak_label.config(text=f"🔥 Current Streak: {streak} day(s")


    #Step 1 : Welcome message
    welcome_label = tk.Label(
        root,
        text="Did you complete your habit today?",
        font=("Arial",14),
        pady=10
    )
    welcome_label.pack()
    
    # Checking todays status
    habits = load_habits()
    today= datetime.now().strftime("%Y-%m-%d")
    done_today = habits.get(today,False)

    #Step 2 : Mascot PlaceHolder
    habits = load_habits()
    today= datetime.now().strftime("%Y-%m-%d")
    mood="happy" if habits.get(today) else "nervous"

    mascot_img=get_mascot_image(mood)

    mascot_label=tk.Label(root, image=mascot_img)
    mascot_label.image = mascot_img #keep a reference to image

    mascot_label.pack()

    #HEATMAP
    heatmap_label = tk.Label(
        root,
        text="Last 21 Days:",
        font=("Arial",10),
    )
    heatmap_label.pack()

    #heatmap frame
    heatmap_frame = tk.Frame(root)
    heatmap_frame.pack()

    draw_heatmap(heatmap_frame,habits)

    #Step 3 : Button Action (called when button is clicked)
    def mark_habit_done():
        habits=load_habits()
        today= datetime.now().strftime("%Y-%m-%d")

        if(habits.get(today)):
            show_toast("🔁 Already marked today!")
            return
        
        mark_today_done()
        update_streak()
        
        new_img = get_mascot_image("happy")
        mascot_label.config(image=new_img)
        mascot_label.image=new_img
        
        for widget in heatmap_frame.winfo_children():
            widget.destroy()
        draw_heatmap(heatmap_frame,load_habits())

        show_toast("✅ Habit recorded!")
        print("✅ Saved today's habit status.")

        root.withdraw()

    #Streak
    streak = get_streak(habits)

    streak_label = tk.Label(
        root,
        text=f"",
        font=("Arial",12)
    )
    update_streak()
    streak_label.pack()

    #Step 4 : Add button
    mark_button = tk.Button(
        root,
        text="✅ Mark as done",
        font=("Arial",12),
        command=mark_habit_done, #connect function to button click
        pady=5
    )
    mark_button.pack(pady=15) #Space around the button

        # === 🔴 NEW: Tray Integration ===
    def show_window(icon, item):
        root.deiconify()   # restores window if hidden

    def quit_app(icon, item):
        icon.stop()
        root.destroy()

    # Simple placeholder icon (green square) — replace with turtle later
    icon_image = PILImage.new("RGB", (64, 64), (0, 200, 0))
    menu = (item('Open HabitTurtle', show_window), item('Quit', quit_app))
    icon = pystray.Icon("habiturtle", icon_image, "HabitTurtle", menu)

    threading.Thread(target=icon.run, daemon=True).start()

    
    root.mainloop()

def draw_heatmap(frame, habits):
    from datetime import timedelta

    today= datetime.now().date()

    for row in range(3):
        for col in range(7):
            days_ago=row*7 + col
            day=today-timedelta(days=days_ago)
            key = day.strftime("%Y-%m-%d")

            done = habits.get(key,False)
            color = "green" if done else "lightgray"

            cell = tk.Label(
                frame,
                text = "  ",
                bg=color,
                width=2,
                height=1,
                borderwidth=1,
                relief="solid"
            )
            cell.grid(row=row, column=col , padx=2, pady=2)
