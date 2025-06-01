from tkinter import ttk
import tkinter as tk

# Color scheme
COLORS = {
    'primary': '#2962ff',
    'secondary': '#455a64',
    'success': '#4caf50',
    'warning': '#ff9800',
    'error': '#f44336',
    'background': '#f5f5f5',
    'surface': '#ffffff',
    'text': '#212121',
    'text_secondary': '#757575',
    'search': '#4CAF50',    # Green for search
    'exit': '#f44336',      # Red for exit
    'hover_shadow': '#00000022',
    'gradient_start': '#2962ff',
    'gradient_end': '#1565C0',
    'button_radius': 20,
    'frame_bg': '#f8f9fa'
}

# Custom styles
def configure_styles():
    style = ttk.Style()
    
    try:
        # Try to use the themed style
        style.theme_use('arc')
    except:
        # Fallback styling
        style.configure(".",
                       font=('Segoe UI', 10),
                       background=COLORS['background'])
    
    # Configure general theme settings
    style.configure(".",
                   font=('Segoe UI', 10),
                   background=COLORS['background'])
    
    # Configure Progressbar
    style.configure("Custom.Horizontal.TProgressbar",
                   troughcolor=COLORS['background'],
                   background=COLORS['primary'],
                   thickness=10,
                   borderwidth=0)
    
    # Configure Button
    style.configure("Custom.TButton",
                   background=COLORS['primary'],
                   foreground=COLORS['surface'],
                   padding=(20, 10),
                   font=('Segoe UI', 10),
                   borderwidth=0)
    
    style.map("Custom.TButton",
              background=[('active', COLORS['secondary'])])
    
    # Configure Entry
    style.configure("Custom.TEntry",
                   fieldbackground=COLORS['surface'],
                   borderwidth=1,
                   padding=5)
    
    # Configure Search Button
    style.configure("Search.TButton",
                   background=COLORS['search'],
                   foreground=COLORS['surface'],
                   padding=(20, 10),
                   font=('Segoe UI', 10, 'bold'),
                   borderwidth=0)
    
    style.map("Search.TButton",
              background=[('active', '#388E3C')])
    
    # Configure Exit Button
    style.configure("Exit.TButton",
                   background=COLORS['exit'],
                   foreground=COLORS['surface'],
                   padding=(20, 10),
                   font=('Segoe UI', 10, 'bold'),
                   borderwidth=0)
    
    style.map("Exit.TButton",
              background=[('active', '#D32F2F')])
    
    # Configure Frame
    style.configure("Custom.TFrame",
                   background=COLORS['frame_bg'],
                   relief='flat',
                   borderwidth=1)
    
    # Configure LabelFrame
    style.configure("Custom.TLabelframe",
                   background=COLORS['frame_bg'],
                   relief='groove',
                   borderwidth=1,
                   padding=10)
    
    style.configure("Custom.TLabelframe.Label",
                   font=('Segoe UI', 10, 'bold'),
                   foreground=COLORS['primary'])
    
    # Configure Entry with rounded corners
    style.configure("Rounded.TEntry",
                   fieldbackground=COLORS['surface'],
                   borderwidth=0,
                   relief='flat',
                   padding=8)
    
    # Configure Buttons
    style.configure("Rounded.TButton",
                   padding=(20, 10),
                   font=('Segoe UI', 10, 'bold'),
                   borderwidth=0,
                   relief='flat')
    
    # Configure Search Button
    style.configure("Search.Rounded.TButton",
                   background=COLORS['search'],
                   foreground=COLORS['surface'])
    
    # Configure Exit Button
    style.configure("Exit.Rounded.TButton",
                   background=COLORS['exit'],
                   foreground=COLORS['surface'])
    
    # Configure PanedWindow
    style.configure("TPanedwindow",
                   background=COLORS['background'])
    
    # Configure Summary Text
    style.configure("Summary.TLabelframe",
                   background=COLORS['surface'],
                   foreground=COLORS['text'],
                   padding=10)
    
    style.configure("Summary.TLabelframe.Label",
                   font=('Segoe UI', 10, 'bold'),
                   foreground=COLORS['primary'])

# Custom widgets
class HoverButton(tk.Button):
    def __init__(self, master, button_type='default', **kwargs):
        super().__init__(master, **kwargs)
        
        # Set colors based on button type
        if button_type == 'search':
            self.default_bg = COLORS['search']
            self.hover_bg = '#388E3C'
            self.shadow_color = '#2E7D32'
        elif button_type == 'exit':
            self.default_bg = COLORS['exit']
            self.hover_bg = '#D32F2F'
            self.shadow_color = '#B71C1C'
        else:
            self.default_bg = kwargs.get('bg', COLORS['primary'])
            self.hover_bg = COLORS['secondary']
            self.shadow_color = '#1565C0'
        
        # Configure basic button appearance
        self.configure(
            bg=self.default_bg,
            fg=COLORS['surface'],
            font=('Segoe UI', 10, 'bold'),
            borderwidth=0,
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            activebackground=self.hover_bg,
            activeforeground=COLORS['surface']
        )
        
        # Bind events
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)
    
    def create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle on the canvas"""
        points = [
            x1 + radius, y1,  # Top left
            x2 - radius, y1,  # Top right
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,  # Bottom right
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,  # Bottom left
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, e):
        """Mouse enter effect"""
        self.configure(
            bg=self.hover_bg,
            relief='flat'
        )
    
    def on_leave(self, e):
        """Mouse leave effect"""
        self.configure(
            bg=self.default_bg,
            relief='flat'
        )
    
    def on_press(self, e):
        """Button press effect"""
        self.configure(
            bg=self.shadow_color,
            relief='sunken'
        )
    
    def on_release(self, e):
        """Button release effect"""
        self.configure(
            bg=self.default_bg,
            relief='flat'
        )
        self.on_enter(e)  # Keep hover effect if mouse is still over button
