import time
import psutil
import threading
import ctypes
import tkinter as tk

class NetSpeedWidget:
    def __init__(self):
        self.running = True

        self.root = tk.Tk()
        self.root.title("Net Speed")
        self.root.overrideredirect(True)  # Remove title bar
        self.root.attributes("-topmost", True)  # Always on top
        self.root.configure(bg="black")

        # Label to display upload/download speed
        self.label = tk.Label(self.root, text="Initializing...", fg="white", bg="black", font=("Consolas", 10))
        self.label.pack(padx=10, pady=5)

        # Right-click menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Close", command=self.quit)

        # Bind right-click to show menu
        self.root.bind("<Button-3>", self.show_menu)  # Right-click

        # Bind mouse events for dragging
        self.root.bind("<ButtonPress-1>", self.start_move)  # Left mouse button pressed
        self.root.bind("<B1-Motion>", self.do_move)        # Mouse moved with left button held

        self.set_position_half_inch_from_bottom_right()

        # Force stay-on-top, even over taskbar
        self.make_window_topmost_tool()

        # Handle close event
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # Start update thread
        self.update_thread = threading.Thread(target=self.update_speed)
        self.update_thread.daemon = True
        self.update_thread.start()

    def show_menu(self, event):
        # Display right-click menu
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def start_move(self, event):
        # Record the current mouse position on window for dragging
        self.x_click = event.x
        self.y_click = event.y

    def do_move(self, event):
        # Calculate new position of the window
        x = event.x_root - self.x_click
        y = event.y_root - self.y_click
        self.root.geometry(f"+{x}+{y}")

    def set_position_half_inch_from_bottom_right(self):
        dpi = 96  # Typical Windows DPI (adjust if needed)
        offset = int(0.5 * dpi)  # Half inch in pixels

        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        window_width = 120
        window_height = 40

        x = screen_width - window_width - offset
        y = screen_height - window_height - offset

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def make_window_topmost_tool(self):
        GWL_EXSTYLE = -20
        WS_EX_TOOLWINDOW = 0x00000080
        WS_EX_TOPMOST = 0x00000008

        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        new_style = current_style | WS_EX_TOOLWINDOW | WS_EX_TOPMOST
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)

    def update_speed(self):
        last_sent = psutil.net_io_counters().bytes_sent
        last_recv = psutil.net_io_counters().bytes_recv

        while self.running:
            time.sleep(1)
            counters = psutil.net_io_counters()
            upload = (counters.bytes_sent - last_sent) / 1024  # KB/s
            download = (counters.bytes_recv - last_recv) / 1024

            last_sent = counters.bytes_sent
            last_recv = counters.bytes_recv

            speed_text = f"U: {upload:.0f} KB/s\nD: {download:.0f} KB/s"
            self.label.after(0, self.label.config, {"text": speed_text})

    def quit(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    NetSpeedWidget().run()
