# Copyright (c) 2025 ARIHANT KOTHARI
# Licensed under the MIT License - see LICENSE file for details.

import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import yt_dlp
from tkinter import filedialog

# Global references
progress = None
url_entry = None
status_label = None
download_button = None
root = None
download_path = None

def browse_location():
    global download_path
    selected_dir = filedialog.askdirectory()
    if selected_dir:
        download_path = selected_dir
        location_label.config(text=f"Download To: {download_path}")

def clear_placeholder(event):
    if url_entry.get() == "Enter Video or Playlist URL":
        url_entry.delete(0, tk.END)
        url_entry.config(fg='black')

def add_placeholder(event):
    if url_entry.get() == "":
        url_entry.insert(0, "Enter Video or Playlist URL")
        url_entry.config(fg='grey')

def update_status(text):
    status_label.config(text=text)
    root.update()

def start_download(event=None):
    url = url_entry.get().strip()
    if url and url != "Enter Video or Playlist URL":
        download_button.config(state='disabled')
        threading.Thread(target=download_video, args=(url,)).start()
    else:
        messagebox.showerror("Error", "Please enter a valid URL")

def download_video(url):
    try:
        # Create 'DOWNLOAD' directory if not exists
        if download_path:
            download_dir = download_path
        else:
            download_dir = os.path.join(os.getcwd(), 'DOWNLOAD')
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)


        # Progress hook
        def progress_hook(d):
            if d['status'] == 'downloading':
                if 'total_bytes' in d and 'downloaded_bytes' in d:
                    prog = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    if d.get('playlist_index') and d.get('playlist_count'):
                        update_status(
                            f"Downloading {d['playlist_index']}/{d['playlist_count']} - {prog:.1f}%"
                        )
                    else:
                        update_status(f"Downloading: {prog:.1f}%")
                    progress['value'] = prog
            elif d['status'] == 'finished':
                update_status("Download finished. Processing...")

        ydl_opts = {
            'format': 'bestvideo[height>=720]+bestaudio/best',
            'noplaylist': False,
            'ignoreerrors': True,
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(download_dir, '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'postprocessors': [
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                },
                {
                    'key': 'FFmpegMetadata',
                }
            ]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if info_dict.get('_type', '') == 'playlist':
                playlist_title = info_dict.get('title', 'Playlist')
                update_status(f"Playlist: {playlist_title} ({len(info_dict['entries'])} videos)")
            else:
                update_status("Single video detected.")

            progress['value'] = 0
            progress.start()
            ydl.download([url])
            progress.stop()
            update_status("Download Complete!")
            messagebox.showinfo("Success", "Download and Merge Completed!")

    except Exception as e:
        progress.stop()
        update_status("Error occurred during download!")
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        download_button.config(state='normal')
        progress['value'] = 0

def create_widgets():
    global progress, url_entry, status_label, download_button

    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 14), padding=10)
    style.configure('TProgressbar', thickness=10)

    url_entry = tk.Entry(root, font=('Helvetica', 16), width=40, fg='grey')
    url_entry.pack(pady=40)
    url_entry.insert(0, "Enter Video or Playlist URL")
    url_entry.bind('<FocusIn>', clear_placeholder)
    url_entry.bind('<FocusOut>', add_placeholder)
    url_entry.bind('<Return>', start_download)
    root.after(1000, lambda: url_entry.focus_set())

    progress = ttk.Progressbar(root, length=400, mode='determinate')
    progress.pack(pady=20)

    download_button = ttk.Button(root, text="Download", command=start_download)
    download_button.pack(pady=20)
        
    browse_button = ttk.Button(root, text="Select Download Location", command=browse_location)
    browse_button.pack(pady=5)

    # Display selected path
    global location_label
    location_label = tk.Label(root, text="Download To: Default (./DOWNLOAD)", font=("Helvetica", 10), bg='#2C3E50', fg='white')
    location_label.pack(pady=5)

    status_label = tk.Label(root, text="", font=("Helvetica", 12), bg='#2C3E50', fg='white')
    status_label.pack(pady=10)

    label = tk.Label(root, text="Youtube Video/Playlist Downloader", font=("Helvetica", 20), bg='#2C3E50', fg='white')
    label.pack(side=tk.BOTTOM, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Video Downloader")
    root.geometry("600x400")
    root.configure(bg='#2C3E50')
    create_widgets()
    root.mainloop()
