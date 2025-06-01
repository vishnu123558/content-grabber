import tkinter as tk
from tkinter import Canvas, ttk, messagebox, filedialog
from threading import Thread
from script import Scraper
from downloader import save_images, save_pdfs
import os
from styles import configure_styles, HoverButton, COLORS
from ttkthemes import ThemedTk  # Add this import
import json
from datetime import datetime

class ContentGrabberApp:
    def __init__(self, root):
        self.root = root
        self.scraper = Scraper()
        configure_styles()
        self.setup_ui()
        self.create_menu()
        self.running = False
        self.setup_summary_window()
        self.summaries = {}

    def setup_summary_window(self):
        self.summary_window = None

    def setup_ui(self):
        # Apply modern theme
        self.root.configure(bg=COLORS['background'])
        self.root.title("Content Grabber")
        self.root.geometry("800x600")  # Larger default size
        
        # Main container with shadow effect
        main_frame = ttk.Frame(self.root, style="Custom.TFrame", padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search frame with rounded corners
        search_frame = ttk.LabelFrame(
            main_frame,
            text="Search Settings",
            style="Custom.TLabelframe",
            padding=15
        )
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Styled search entry
        tk.Label(
            search_frame,
            text="Search Query:",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['frame_bg'],
            fg=COLORS['text']
        ).pack(anchor='w')
        
        self.search_entry = ttk.Entry(
            search_frame,
            style="Rounded.TEntry",
            font=('Segoe UI', 11)
        )
        self.search_entry.pack(fill=tk.X, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(
            main_frame,
            text="Download Options",
            style="Custom.TLabelframe"
        )
        options_frame.pack(fill=tk.X, pady=10)
        
        # Styled checkbuttons
        self.download_images = tk.BooleanVar(value=True)
        self.download_pdfs = tk.BooleanVar(value=True)
        
        for var, text in [(self.download_images, "Download Images"),
                          (self.download_pdfs, "Download PDFs")]:
            cb = tk.Checkbutton(
                options_frame,
                text=text,
                variable=var,
                bg=COLORS['frame_bg'],
                activebackground=COLORS['frame_bg'],
                font=('Segoe UI', 10),
                cursor='hand2'
            )
            cb.pack(anchor='w', pady=2)
        
        # Location frame with browse button
        location_frame = ttk.LabelFrame(
            main_frame,
            text="Download Location",
            style="Custom.TLabelframe"
        )
        location_frame.pack(fill=tk.X, pady=10)
        
        self.location_var = tk.StringVar(value=os.path.abspath("storage"))
        location_entry = ttk.Entry(
            location_frame,
            textvariable=self.location_var,
            state='readonly',
            style="Rounded.TEntry"
        )
        location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = HoverButton(
            location_frame,
            text="📂 Browse",
            command=self.select_download_location
        )
        browse_btn.pack(side=tk.RIGHT)

        # Split the results area into two panes
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Results frame (left pane)
        self.results_frame = ttk.LabelFrame(paned_window, text="Results", style="Custom.TLabelframe")
        paned_window.add(self.results_frame, weight=1)
        
        self.results_text = tk.Text(self.results_frame, height=10, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        results_scrollbar = tk.Scrollbar(self.results_text)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        results_scrollbar.config(command=self.results_text.yview)

        # Summary frame (right pane)
        self.summary_frame = ttk.LabelFrame(paned_window, text="PDF Summary", style="Custom.TLabelframe")
        paned_window.add(self.summary_frame, weight=1)
        
        # Summary frame with save button
        summary_header = ttk.Frame(self.summary_frame)
        summary_header.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            summary_header,
            text="PDF Summary",
            font=('Segoe UI', 10, 'bold')
        ).pack(side=tk.LEFT)
        
        save_summary_btn = HoverButton(
            summary_header,
            text="💾 Save Summaries",
            command=self.save_summaries
        )
        save_summary_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add summarization progress
        self.summary_progress_var = tk.StringVar(value="")
        self.summary_progress_label = ttk.Label(
            summary_header,
            textvariable=self.summary_progress_var,
            font=('Segoe UI', 9)
        )
        self.summary_progress_label.pack(side=tk.LEFT, padx=5)
        
        self.summary_text = tk.Text(self.summary_frame, height=10, wrap=tk.WORD)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        summary_scrollbar = tk.Scrollbar(self.summary_text)
        summary_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.summary_text.config(yscrollcommand=summary_scrollbar.set)
        summary_scrollbar.config(command=self.summary_text.yview)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, orient='horizontal', length=300, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(0,5))

        # Action buttons with new styling
        button_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        button_frame.pack(fill=tk.X, pady=10)
        
        self.search_btn = HoverButton(
            button_frame,
            text="🔍 Search",
            button_type='search',
            command=self.start_process
        )
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_btn = HoverButton(
            button_frame,
            text="🗑 Clear",
            command=self.clear_results
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        self.exit_btn = HoverButton(
            button_frame,
            text="❌ Exit",
            button_type='exit',
            command=self.confirm_exit
        )
        self.exit_btn.pack(side=tk.RIGHT, padx=5)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Storage Folder", command=self.open_storage_folder)
        file_menu.add_command(label="Load Summary", command=self.load_summary)  # Add this line
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        self.root.config(menu=menubar)

    def open_storage_folder(self):
        storage_path = os.path.abspath("storage")
        if os.path.exists(storage_path):
            os.startfile(storage_path)
        else:
            messagebox.showwarning("Warning", "Storage folder not found!")

    def clear_results(self):
        """Clear results, summary, and stored summaries"""
        self.results_text.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)
        self.summary_progress_var.set("")
        self.summaries = {}
        self.status_var.set("Ready")

    def confirm_exit(self):
        """Show confirmation dialog before exiting"""
        if self.running:
            if messagebox.askyesno("Warning", "A process is running. Do you want to exit anyway?"):
                self.stop_process()
                self.root.quit()
        else:
            if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
                self.root.quit()

    def stop_process(self):
        """Stop the running process"""
        self.running = False
        self.status_var.set("Process stopped by user")
        self.set_ui_state(disabled=False)

    def select_download_location(self):
        """Allow user to select download location"""
        folder = filedialog.askdirectory(
            title="Select Download Location",
            initialdir=self.location_var.get()
        )
        if folder:
            self.location_var.set(folder)

    def start_process(self):
        """Handle the start button click with improved error handling"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search query!")
            return

        if self.running:
            messagebox.showwarning("Warning", "A process is already running!")
            return

        # Create query-specific folder
        base_dir = self.location_var.get()
        query_folder = "_".join(query.split())[:50]  # Limit folder name length
        query_dir = os.path.join(base_dir, query_folder)
        
        try:
            os.makedirs(query_dir, exist_ok=True)
            os.makedirs(os.path.join(query_dir, "images"), exist_ok=True)
            os.makedirs(os.path.join(query_dir, "pdfs"), exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create download folders: {e}")
            return

        # Update scraper storage locations
        self.scraper.set_storage_locations(
            image_dir=os.path.join(query_dir, "images"),
            pdf_dir=os.path.join(query_dir, "pdfs")
        )

        # Clear previous results
        self.clear_results()
        self.running = True
        
        # Disable UI during processing
        self.set_ui_state(disabled=True)
        self.status_var.set("Processing...")
        self.progress["value"] = 0

        # Start processing in a separate thread
        Thread(target=self.run_scraping, args=(query,), daemon=True).start()

    def run_scraping(self, query):
        try:
            self.append_result(f"🔍 Searching for: {query}\n")
            images, pdfs = self.scraper.scrape_images_and_pdfs(query)

            total_items = 0
            if self.download_images.get() and images:
                total_items += len(images)
            if self.download_pdfs.get() and pdfs:
                total_items += len(pdfs)

            if total_items == 0:
                self.append_result("\n❌ No content found to download!")
                self.update_status("No content found")
                return

            self.append_result(f"\nFound {len(images)} images and {len(pdfs)} PDFs\n")

            downloaded = 0
            if self.download_images.get() and images:
                self.append_result("\n📸 Downloading images...\n")
                save_images(images)
                downloaded += len(images)
                self.progress["value"] = (downloaded / total_items) * 100
                self.append_result(f"\n✅ Downloaded {len(images)} images\n")

            if self.download_pdfs.get() and pdfs:
                self.append_result("\n📄 Downloading PDFs...\n")
                pdf_files, pdf_summaries = save_pdfs(pdfs)
                downloaded += len(pdf_files)
                self.progress["value"] = 100
                self.append_result(f"\n✅ Downloaded {len(pdf_files)} PDFs\n")
                self.append_result(f"\n📝 Summarized {len(pdf_summaries)} PDFs\n")

                # FIXED: Use basename of full path keys
                self.summaries = {
                    os.path.basename(path): {
                        'path': path,
                        'summary': summary
                    }
                    for path, summary in pdf_summaries.items()
                }

                if self.summaries:
                    self.display_summaries()
                else:
                    self.summary_text.delete(1.0, tk.END)
                    self.summary_text.insert(tk.END, "No PDF summaries were generated.")

            self.update_status(f"Download completed - {downloaded} items")

        except Exception as e:
            self.append_result(f"\n❌ Error: {str(e)}\n")
            self.update_status(f"Error: {str(e)}")
        finally:
            self.set_ui_state(disabled=False)
            self.running = False

    def display_summaries(self):
        """Display summaries in the summary text widget"""
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, "📑 PDF Summaries:\n\n")
        
        if not self.summaries:
            self.summary_text.insert(tk.END, "No summaries available.")
            return
            
        for filename, info in self.summaries.items():
            self.summary_text.insert(tk.END, f"📄 {filename}\n", "header")
            self.summary_text.insert(tk.END, "-" * 50 + "\n")
            summary = info.get('summary', "⚠️ No summary available")
            self.summary_text.insert(tk.END, f"{summary}\n\n")
        
        self.summary_text.see(tk.END)
        self.summary_text.tag_configure("header", font=('Segoe UI', 10, 'bold'))

    def process_pdf_summaries(self, pdf_files, pdf_summaries):
        """Process and display PDF summaries with progress"""
        self.summaries = {}
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, "📑 PDF Summaries:\n\n")
        
        total_files = len(pdf_files)
        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                # Update progress
                progress_msg = f"Summarizing PDF {i}/{total_files}"
                self.summary_progress_var.set(progress_msg)
                self.update_status(progress_msg)
                
                filename = os.path.basename(pdf_file)
                self.summary_text.insert(tk.END, f"📄 {filename}\n", "header")
                self.summary_text.insert(tk.END, "-" * 50 + "\n")
                
                summary = pdf_summaries.get(pdf_file, "⚠️ No summary available")
                if summary and not summary.startswith("⚠️"):
                    self.summary_text.insert(tk.END, f"{summary}\n\n")
                    self.summaries[filename] = {
                        'path': pdf_file,
                        'summary': summary
                    }
                else:
                    self.summary_text.insert(tk.END, f"{summary}\n\n")
                
                # Update UI
                self.summary_text.see(tk.END)
                self.root.update_idletasks()
                
            except Exception as e:
                self.summary_text.insert(tk.END, f"⚠️ Error displaying summary: {str(e)}\n\n")
        
        # Clear progress when done
        self.summary_progress_var.set("")
        self.update_status("Summaries completed")
        
        # Configure text tags for styling
        self.summary_text.tag_configure("header", font=('Segoe UI', 10, 'bold'))
        self.summary_text.see(tk.END)

    def save_summaries(self):
        if not self.summaries:
            messagebox.showinfo("Info", "No summaries available to save!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summaries_{timestamp}.json"

        try:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                initialfile=filename,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Summaries"
            )

            if not save_path:
                return

            save_data = {
                'timestamp': timestamp,
                'query': self.search_entry.get().strip(),
                'total_files': len(self.summaries),
                'summaries': self.summaries
            }

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)

            self.save_summaries_as_pdf(save_path.replace('.json', '.pdf'))

            messagebox.showinfo("Success", f"Summaries saved to:{save_path}")
            self.status_var.set("Summaries saved successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save summaries: {e}")
    def save_summaries_as_pdf(self, pdf_path):
        try:
            c = Canvas.Canvas(pdf_path)
            width, height = 600, 800
            y = height - 50

            for filename, info in self.summaries.items():
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, f"📄 {filename}")
                y -= 20
                c.setFont("Helvetica", 9)

                for line in info['summary'].splitlines():
                    if y < 50:
                        c.showPage()
                        y = height - 50
                    c.drawString(50, y, line)
                    y -= 15

                y -= 20

            c.save()
            print(f"✅ PDF saved to: {pdf_path}")

        except Exception as e:
            print(f"❌ Failed to export PDF: {e}")
    def load_summary(self):
        """Load saved summary from JSON file"""
        try:
            file_path = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Summary"
            )
            
            if not file_path:
                return
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if 'summaries' not in data:
                raise ValueError("Invalid summary file format")
                
            self.summaries = data['summaries']
            self.display_loaded_summary(data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load summary: {e}")

    def display_loaded_summary(self, data):
        """Display loaded summary in the UI"""
        try:
            # Clear existing summary
            self.summary_text.delete(1.0, tk.END)
            
            # Show metadata
            self.summary_text.insert(tk.END, "📑 Loaded Summary\n", "header")
            self.summary_text.insert(tk.END, f"Query: {data.get('query', 'Unknown')}\n")
            self.summary_text.insert(tk.END, f"Created: {data.get('timestamp', 'Unknown')}\n")
            self.summary_text.insert(tk.END, "-" * 50 + "\n\n")
            
            # Display summaries
            for filename, info in data['summaries'].items():
                self.summary_text.insert(tk.END, f"📄 {filename}\n", "header")
                self.summary_text.insert(tk.END, "-" * 50 + "\n")
                self.summary_text.insert(tk.END, f"{info['summary']}\n\n")
            
            self.summary_text.see(tk.END)
            self.status_var.set("Summary loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display summary: {e}")

    def append_result(self, message):
        """Thread-safe way to append text to results"""
        self.results_text.after(0, self._append_text, message)

    def _append_text(self, message):
        self.results_text.insert(tk.END, message)
        self.results_text.see(tk.END)

    def update_status(self, message):
        """Update status label thread-safely"""
        self.status_var.set(message)

    def set_ui_state(self, disabled=True):
        """Enable/disable UI controls with better handling"""
        state = tk.DISABLED if disabled else tk.NORMAL
        self.search_entry.config(state=state)
        self.search_btn.config(state=state)
        self.clear_btn.config(state=state)
        self.download_images.set(self.download_images.get())  # Preserve checkbox states
        self.download_pdfs.set(self.download_pdfs.get())

        # Keep exit button always enabled
        self.exit_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    try:
        root = ThemedTk(theme="arc")
        try:
            root.set_theme("arc")
        except:
            pass
    except:
        root = tk.Tk()
        root.configure(bg=COLORS['background'])

    app = ContentGrabberApp(root)
    root.mainloop()