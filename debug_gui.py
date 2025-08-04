#!/usr/bin/env python3
"""
Debug version of X32 Scene Monitor to identify GUI issues
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os

def main():
    print("Starting debug GUI...")
    
    root = tk.Tk()
    print("Tk root created")
    
    root.title("X32 Scene File Monitor - Debug")
    root.geometry("800x600")
    print("Window configured")
    
    # Test basic widgets
    print("Creating test widgets...")
    
    # Main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    print("Main frame created")
    
    # Test label
    test_label = ttk.Label(main_frame, text="X32 Scene File Monitor - Debug Mode")
    test_label.pack(pady=10)
    print("Label created")
    
    # Test button
    def test_button_click():
        print("Test button clicked!")
        messagebox.showinfo("Test", "Button is working!")
    
    test_button = ttk.Button(main_frame, text="Test Button", command=test_button_click)
    test_button.pack(pady=10)
    print("Button created")
    
    # Test entry
    test_entry = ttk.Entry(main_frame, width=30)
    test_entry.pack(pady=10)
    test_entry.insert(0, "Test entry field")
    print("Entry created")
    
    # Test text area
    test_text = scrolledtext.ScrolledText(main_frame, height=10, width=60)
    test_text.pack(pady=10, fill=tk.BOTH, expand=True)
    test_text.insert("1.0", "Debug log will appear here...\n")
    print("Text area created")
    
    # Add some debug info
    test_text.insert(tk.END, f"Python version: {os.sys.version}\n")
    test_text.insert(tk.END, f"Tkinter version: {tk.TkVersion}\n")
    test_text.insert(tk.END, f"Tcl version: {tk.TclVersion}\n")
    test_text.insert(tk.END, "GUI should be visible now!\n")
    
    print("All widgets created, starting mainloop...")
    root.mainloop()
    print("Mainloop ended")

if __name__ == "__main__":
    main() 