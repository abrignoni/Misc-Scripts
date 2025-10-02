import tkinter as tk
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math

def update_countdown():
    now = datetime.now()
    
    # Countdown to retirement
    if now >= end_date:
        countdown_text = "🎉 Congratulations! You've reached retirement! 🎉"
        label.config(text=countdown_text, font=("Helvetica", 32, "bold"), fg="green")
        elapsed_label.config(text="")
        draw_progress(100)
    else:
        # Remaining time
        delta = relativedelta(end_date, now)
        diff = end_date - now
        years, months, days = delta.years, delta.months, delta.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        countdown_text = (
            f"RETIREMENT COUNTDOWN\n\n"
            f"Years   : {years}\n"
            f"Months  : {months}\n"
            f"Days    : {days}\n"
            f"Hours   : {hours}\n"
            f"Minutes : {minutes}\n"
            f"Seconds : {seconds}\n"
        )
        label.config(text=countdown_text, fg="white")
        
        # Elapsed time
        elapsed_delta = relativedelta(now, start_date)
        e_years, e_months, e_days = elapsed_delta.years, elapsed_delta.months, elapsed_delta.days
        total_elapsed_sec = int((now - start_date).total_seconds())
        e_hours, rem = divmod(total_elapsed_sec % 86400, 3600)
        e_minutes, e_seconds = divmod(rem % 3600, 60)
        
        elapsed_text = (
            f"TIME SINCE START\n\n"
            f"Years   : {e_years}\n"
            f"Months  : {e_months}\n"
            f"Days    : {e_days}\n"
            f"Hours   : {e_hours}\n"
            f"Minutes : {e_minutes}\n"
            f"Seconds : {e_seconds}\n"
        )
        elapsed_label.config(text=elapsed_text)
        
        # Progress
        total_time = (end_date - start_date).total_seconds()
        elapsed_time = (now - start_date).total_seconds()
        percentage = (elapsed_time / total_time) * 100
        draw_progress(percentage)
        
    # Analog clock
    draw_clock(now)
    root.after(1000, update_countdown)
    
    
def draw_progress(percentage):
    progress_canvas.delete("all")
    w, h = 800, 40
    margin = 4
    
    # Background
    progress_canvas.create_rectangle(0, 0, w, h, fill="gray20", outline="white", width=2)
    
    # Elapsed segment
    elapsed_w = (percentage / 100) * (w - margin * 2)
    progress_canvas.create_rectangle(margin, margin, margin + elapsed_w, h - margin, fill="cyan", outline="")
    
    # Remaining segment
    progress_canvas.create_rectangle(margin + elapsed_w, margin, w - margin, h - margin, fill="red", outline="")
    
    # Text
    progress_canvas.create_text(
        w // 2, h // 2,
        text=f"{percentage:.2f}% elapsed / {100-percentage:.2f}% remaining",
        fill="white",
        font=("Helvetica", 16, "bold")
    )
    
    
def draw_clock(now):
    clock_canvas.delete("all")
    w, h = 300, 300
    cx, cy = w // 2, h // 2
    r = 120
    
    clock_canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="white", width=4)
    
    for i in range(12):
        angle = math.radians(i * 30)
        x1 = cx + (r - 10) * math.sin(angle)
        y1 = cy - (r - 10) * math.cos(angle)
        x2 = cx + r * math.sin(angle)
        y2 = cy - r * math.cos(angle)
        clock_canvas.create_line(x1, y1, x2, y2, fill="white", width=3)
        
    # Hands
    sec_angle = math.radians(now.second * 6)
    min_angle = math.radians(now.minute * 6 + now.second * 0.1)
    hr_angle = math.radians((now.hour % 12) * 30 + now.minute * 0.5)
    
    hx = cx + (r * 0.5) * math.sin(hr_angle)
    hy = cy - (r * 0.5) * math.cos(hr_angle)
    clock_canvas.create_line(cx, cy, hx, hy, fill="white", width=6)
    
    mx = cx + (r * 0.7) * math.sin(min_angle)
    my = cy - (r * 0.7) * math.cos(min_angle)
    clock_canvas.create_line(cx, cy, mx, my, fill="white", width=4)
    
    sx = cx + (r * 0.9) * math.sin(sec_angle)
    sy = cy - (r * 0.9) * math.cos(sec_angle)
    clock_canvas.create_line(cx, cy, sx, sy, fill="red", width=2)
    
    clock_canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="red")
    
    
# ---------------- MAIN APP ----------------
start_date = datetime.strptime("2007-09-04 00:00:00", "%Y-%m-%d %H:%M:%S")
end_date = datetime.strptime("2028-06-01 01:00:00", "%Y-%m-%d %H:%M:%S")

root = tk.Tk()
root.title("Retirement Countdown Dashboard")
root.configure(bg="black")
root.attributes("-fullscreen", True)

# Left frame for countdown and elapsed time
left_frame = tk.Frame(root, bg="black")
left_frame.pack(side="left", expand=True, fill="both", padx=40, pady=40)

label = tk.Label(left_frame, text="", font=("Helvetica", 36, "bold"), fg="white", bg="black", justify="center")
label.pack(side="top", expand=True, fill="both")

elapsed_label = tk.Label(left_frame, text="", font=("Helvetica", 24, "bold"), fg="cyan", bg="black", justify="center")
elapsed_label.pack(side="top", expand=True, fill="both", pady=20)

# Right frame for analog clock
clock_canvas = tk.Canvas(root, width=300, height=300, bg="black", highlightthickness=0)
clock_canvas.pack(side="right", padx=60, pady=60)

# Bottom progress bar
progress_canvas = tk.Canvas(root, width=800, height=40, bg="black", highlightthickness=0)
progress_canvas.pack(side="bottom", pady=40)

# Escape key to quit
root.bind("<Escape>", lambda e: root.destroy())

# Start the countdown loop
update_countdown()
root.mainloop()

