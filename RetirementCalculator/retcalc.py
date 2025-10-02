import tkinter as tk
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ---------------- FUNCTIONS ----------------

def update_countdown():
    now = datetime.now()

    if now >= end_date:
        countdown_label.config(text="🎉 Retirement Reached! 🎉", fg="green")
        elapsed_label.config(text="")
        draw_progress(100)
    else:
        # Countdown
        delta = relativedelta(end_date, now)
        diff = end_date - now
        years, months, days = delta.years, delta.months, delta.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder % 3600, 60)

        countdown_text = f"Countdown:\n {years}y {months}m {days}d {hours}h {minutes}m {seconds}s"
        countdown_label.config(text=countdown_text, fg="white")

        # Elapsed time
        elapsed_delta = relativedelta(now, start_date)
        e_years, e_months, e_days = elapsed_delta.years, elapsed_delta.months, elapsed_delta.days
        total_elapsed_sec = int((now - start_date).total_seconds())
        e_hours, rem = divmod(total_elapsed_sec % 86400, 3600)
        e_minutes, e_seconds = divmod(rem % 3600, 60)

        elapsed_text = f"Elapsed:\n {e_years}y {e_months}m {e_days}d {e_hours}h {e_minutes}m {e_seconds}s"
        elapsed_label.config(text=elapsed_text)

        # Progress
        total_time = (end_date - start_date).total_seconds()
        elapsed_time = (now - start_date).total_seconds()
        percentage = (elapsed_time / total_time) * 100
        draw_progress(percentage)

    root.after(1000, update_countdown)


def draw_progress(percentage):
    progress_canvas.delete("all")
    w = int(root.winfo_width() * 0.9)
    h = max(int(root.winfo_height() * 0.08), 15)
    margin = 2

    # Background
    progress_canvas.config(width=w, height=h)
    progress_canvas.create_rectangle(0, 0, w, h, fill="gray20", outline="white", width=1)

    # Elapsed
    elapsed_w = (percentage / 100) * (w - margin * 2)
    progress_canvas.create_rectangle(margin, margin, margin + elapsed_w, h - margin, fill="cyan", outline="")

    # Remaining
    progress_canvas.create_rectangle(margin + elapsed_w, margin, w - margin, h - margin, fill="red", outline="")

    # Text overlay
    font_size = max(int(h * 0.6), 8)
    progress_canvas.create_text(
        w // 2, h // 2,
        text=f"{percentage:.2f}% elapsed / {100-percentage:.2f}% remaining",
        fill="white",
        font=("Helvetica", font_size, "bold")
    )


def adjust_layout(event=None):
    w = root.winfo_width()
    h = root.winfo_height()

    # Detect orientation
    if w >= h:  # landscape
        countdown_label.pack_configure(side="top", fill="both", expand=True, pady=5)
        elapsed_label.pack_configure(side="top", fill="both", expand=True, pady=5)
        progress_canvas.pack_configure(side="bottom", fill="x", pady=10)
    else:  # portrait
        countdown_label.pack_configure(side="top", fill="both", expand=True, pady=2)
        elapsed_label.pack_configure(side="top", fill="both", expand=True, pady=2)
        progress_canvas.pack_configure(side="bottom", fill="x", pady=5)

    # Adjust fonts based on height
    font_size_main = max(int(h * 0.07), 10)
    countdown_label.config(font=("Helvetica", font_size_main, "bold"))
    elapsed_label.config(font=("Helvetica", font_size_main, "bold"))
    draw_progress((elapsed_time_percentage() if root.winfo_exists() else 0))


def elapsed_time_percentage():
    total_time = (end_date - start_date).total_seconds()
    elapsed_time = (datetime.now() - start_date).total_seconds()
    return (elapsed_time / total_time) * 100


# ---------------- MAIN APP ----------------
start_date = datetime.strptime("2007-09-04 00:00:00", "%Y-%m-%d %H:%M:%S")
end_date = datetime.strptime("2028-06-01 00:00:00", "%Y-%m-%d %H:%M:%S")

root = tk.Tk()
root.title("Retirement Countdown")
root.configure(bg="black")
root.attributes("-fullscreen", True)

# Countdown label
countdown_label = tk.Label(root, text="", fg="white", bg="black", justify="center", wraplength=800)
countdown_label.pack(expand=True, fill="both", pady=5)

# Elapsed time label
elapsed_label = tk.Label(root, text="", fg="cyan", bg="black", justify="center", wraplength=800)
elapsed_label.pack(expand=True, fill="both", pady=5)

# Progress bar
progress_canvas = tk.Canvas(root, bg="black", highlightthickness=0)
progress_canvas.pack(pady=10, fill="x")

# Bind resize/orientation change
root.bind("<Configure>", adjust_layout)
root.bind("<Escape>", lambda e: root.destroy())

# Start countdown
update_countdown()
adjust_layout()
root.mainloop()
