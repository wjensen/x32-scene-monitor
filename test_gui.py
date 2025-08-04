#!/usr/bin/env python3
"""
Simple GUI test to check if tkinter is working properly
"""

import tkinter as tk
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("GUI Test")
    root.geometry("400x300")
    
    # Add some basic widgets
    label = ttk.Label(root, text="If you can see this, tkinter is working!")
    label.pack(pady=20)
    
    button = ttk.Button(root, text="Test Button", command=lambda: print("Button clicked!"))
    button.pack(pady=10)
    
    entry = ttk.Entry(root)
    entry.pack(pady=10)
    entry.insert(0, "Test entry field")
    
    text = tk.Text(root, height=5, width=40)
    text.pack(pady=10)
    text.insert("1.0", "Test text area\nYou should see this text.")
    
    print("GUI test window should be visible now")
    root.mainloop()

if __name__ == "__main__":
    main() 