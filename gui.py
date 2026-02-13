import tkinter as tk
from board import XiangqiBoard
from engine import StockfishEngine
from translator import tr
import threading
import sys
import webbrowser

class MainGUI:
    """
    Main GUI class for Xiangqi analysis application.
    Handles all UI elements, user interactions, and engine communication.
    """
    def __init__(self, root):
        """
        Initialize the main GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.engine = StockfishEngine()
        self.setup_mode = False
        self.selected_piece_for_setup = None
        self.setup_window = None
        self.debug = False
        self.setup_ui()

    def setup_ui(self):
        """Set up all UI elements."""
        self.root.title("XiangqiMO")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1E1E1E')
        self.root.resizable(False, False)
        main_container = tk.Frame(self.root, bg='#1E1E1E')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        top_frame = tk.Frame(main_container, bg='#1E1E1E')
        top_frame.pack(fill=tk.X, pady=(0, 15))
        self.title_label = tk.Label(
            top_frame,
            text="XiangqiMO",
            font=('Inter', 26, 'bold'),
            bg='#1E1E1E',
            fg='#FFFFFF'
        )
        self.title_label.pack(side=tk.LEFT)
        right_icons = tk.Frame(top_frame, bg='#1E1E1E')
        right_icons.pack(side=tk.RIGHT)
        self.info_frame = tk.Frame(right_icons, bg='#1E1E1E')
        self.info_frame.pack(side=tk.LEFT, padx=(0, 15))
        self.info_label = tk.Label(
            self.info_frame,
            text="INFO",
            font=('Inter', 12, 'bold'),
            bg='#1E1E1E',
            fg='#E0E0E0',
            cursor='hand2'
        )
        self.info_label.pack()
        self.info_label.bind("<Button-1>", self.show_info_window)
        self.lang_frame = tk.Frame(right_icons, bg='#1E1E1E')
        self.lang_frame.pack(side=tk.LEFT, padx=(0, 15))
        self.lang_icon = tk.Label(
            self.lang_frame,
            text="🌐",
            font=('Segoe UI', 20),
            bg='#1E1E1E',
            fg='#E0E0E0',
            cursor='hand2'
        )
        self.lang_icon.pack()
        self.current_lang_label = tk.Label(
            self.lang_frame,
            text="EN",
            font=('Inter', 9, 'bold'),
            bg='#1E1E1E',
            fg='#90EE90',
            cursor='hand2'
        )
        self.current_lang_label.pack(anchor='center')
        self.setup_frame = tk.Frame(right_icons, bg='#1E1E1E')
        self.setup_frame.pack(side=tk.LEFT)
        self.setup_icon = tk.Label(
            self.setup_frame,
            text="📌",
            font=('Segoe UI', 20),
            bg='#1E1E1E',
            fg='#E0E0E0',
            cursor='hand2'
        )
        self.setup_icon.pack()
        self.setup_label = tk.Label(
            self.setup_frame,
            text=tr.get("setup"),
            font=('Inter', 9),
            bg='#1E1E1E',
            fg='#B0B0B0',
            cursor='hand2'
        )
        self.setup_label.pack(anchor='center')
        self.lang_icon.bind("<Button-1>", self.show_language_menu)
        self.current_lang_label.bind("<Button-1>", self.show_language_menu)
        self.setup_icon.bind("<Button-1>", self.open_setup_window)
        self.setup_label.bind("<Button-1>", self.open_setup_window)
        self.create_language_menu()
        content_frame = tk.Frame(main_container, bg='#1E1E1E')
        content_frame.pack(fill=tk.BOTH, expand=True)
        board_frame = tk.Frame(content_frame, bg='#2D2D2D', relief=tk.FLAT, bd=0)
        board_frame.pack(side=tk.LEFT, padx=(0, 20))
        canvas_width = 8 * 60 + 100
        canvas_height = 9 * 60 + 120
        self.canvas = tk.Canvas(
            board_frame,
            width=canvas_width,
            height=canvas_height,
            bg='#2D2D2D',
            highlightthickness=0
        )
        self.canvas.pack(padx=15, pady=15)
        self.canvas.tag_raise("all")
        self.board = XiangqiBoard(self.canvas, x=50, y=60, cell=60)
        self.board.on_move_made = self.update_move_list
        self.board.reset_history()
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.bind("<Button-1>", self.on_board_click)
        self.canvas.focus_set()
        control_panel = tk.Frame(
            content_frame,
            bg='#2D2D2D',
            relief=tk.FLAT,
            bd=0,
            width=340
        )
        control_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        control_panel.pack_propagate(False)
        self.panel_title = tk.Label(
            control_panel,
            text=tr.get("control_panel"),
            font=('Inter', 16, 'normal'),
            bg='#2D2D2D',
            fg='#E0E0E0'
        )
        self.panel_title.pack(pady=(15, 10))
        btn_frame = tk.Frame(control_panel, bg='#2D2D2D')
        btn_frame.pack(pady=(0, 15))
        btn_style = {
            'font': ('Inter', 11),
            'fg': '#FFFFFF',
            'activeforeground': '#FFFFFF',
            'relief': tk.FLAT,
            'bd': 0,
            'width': 20,
            'height': 1,
            'pady': 6,
            'cursor': 'hand2'
        }
        self.analyze_btn = tk.Button(btn_frame, text=tr.get("analyze"), bg='#3A3A3A', activebackground='#4A4A4A', command=self.analyze, **btn_style)
        self.analyze_btn.pack(pady=3)
        self.flip_btn = tk.Button(btn_frame, text=tr.get("flip"), bg='#3A3A3A', activebackground='#4A4A4A', command=self.flip_board, **btn_style)
        self.flip_btn.pack(pady=3)
        self.reset_btn = tk.Button(btn_frame, text=tr.get("reset"), bg='#3A3A3A', activebackground='#4A4A4A', command=self.reset_board, **btn_style)
        self.reset_btn.pack(pady=3)
        self.undo_btn = tk.Button(btn_frame, text=tr.get("undo"), bg='#3A3A3A', activebackground='#4A4A4A', command=self.undo_move, **btn_style)
        self.undo_btn.pack(pady=3)
        analysis_frame = tk.Frame(control_panel, bg='#252525', relief=tk.FLAT, bd=0, height=90)
        analysis_frame.pack(pady=(0, 10), padx=15, fill=tk.X)
        analysis_frame.pack_propagate(False)
        self.analysis_title = tk.Label(analysis_frame, text=tr.get("best_moves"),
                                      font=('Inter', 10, 'bold'), bg='#252525', fg='#B0B0B0')
        self.analysis_title.pack(pady=(6, 4))
        line1 = tk.Frame(analysis_frame, bg='#252525')
        line1.pack(fill=tk.X, padx=12, pady=2)
        tk.Label(line1, text="1.", font=('Inter', 10, 'bold'), bg='#252525', fg='#FFD700', width=2).pack(side=tk.LEFT)
        self.best_move_text = tk.Label(line1, text="---", font=('Consolas', 11, 'bold'), bg='#252525', fg='#FFFFFF')
        self.best_move_text.pack(side=tk.LEFT, padx=(5, 10))
        self.best_score_text = tk.Label(line1, text="", font=('Consolas', 10, 'bold'),
                                       bg='#252525', fg='#90EE90')
        self.best_score_text.pack(side=tk.RIGHT, padx=(0, 5))
        line2 = tk.Frame(analysis_frame, bg='#252525')
        line2.pack(fill=tk.X, padx=12, pady=2)
        tk.Label(line2, text="2.", font=('Inter', 10, 'bold'), bg='#252525', fg='#C0C0C0', width=2).pack(side=tk.LEFT)
        self.second_move_text = tk.Label(line2, text="---", font=('Consolas', 11), bg='#252525', fg='#E0E0E0')
        self.second_move_text.pack(side=tk.LEFT, padx=(5, 10))
        self.second_score_text = tk.Label(line2, text="", font=('Consolas', 10), bg='#252525', fg='#B0B0B0')
        self.second_score_text.pack(side=tk.RIGHT, padx=(0, 5))
        info_frame = tk.Frame(control_panel, bg='#252525', relief=tk.FLAT, bd=0)
        info_frame.pack(pady=(0, 10), padx=15, fill=tk.X)
        score_line = tk.Frame(info_frame, bg='#252525')
        score_line.pack(pady=(8, 6), fill=tk.X, padx=12)
        self.eval_title = tk.Label(score_line, text=tr.get("evaluation"),
                                  font=('Inter', 10, 'bold'), bg='#252525', fg='#B0B0B0')
        self.eval_title.pack(side=tk.LEFT)
        self.score_value = tk.Label(score_line, text="0.00", font=('Inter', 12, 'bold'),
                                   bg='#252525', fg='#90EE90')
        self.score_value.pack(side=tk.RIGHT)
        separator = tk.Frame(info_frame, height=1, bg='#404040')
        separator.pack(fill=tk.X, padx=12, pady=6)
        moves_header = tk.Frame(info_frame, bg='#252525')
        moves_header.pack(fill=tk.X, padx=12, pady=(0, 4))
        self.moves_title = tk.Label(moves_header, text=tr.get("move_history"),
                                   font=('Inter', 10, 'bold'), bg='#252525', fg='#B0B0B0')
        self.moves_title.pack(side=tk.LEFT)
        moves_frame = tk.Frame(info_frame, bg='#252525', height=80)
        moves_frame.pack(pady=(0, 8), padx=12, fill=tk.X)
        moves_frame.pack_propagate(False)
        scrollbar = tk.Scrollbar(moves_frame, bg='#404040', troughcolor='#252525', width=6)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.move_listbox = tk.Listbox(
            moves_frame,
            yscrollcommand=scrollbar.set,
            bg='#1E1E1E',
            fg='#E0E0E0',
            font=('Consolas', 9),
            height=3,
            selectbackground='#404040',
            selectforeground='#FFFFFF',
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            activestyle='none'
        )
        self.move_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.move_listbox.yview)
        self.update_language_label()

    def show_info_window(self, event=None):
        """
        Show information window with program details and license.
        
        Args:
            event: Tkinter event (optional)
        """
        info_window = tk.Toplevel(self.root)
        info_window.title("XiangqiMO - Information")
        info_window.geometry("600x550")
        info_window.configure(bg='#2D2D2D')
        info_window.resizable(False, False)
        info_window.transient(self.root)
        info_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (600 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (550 // 2)
        info_window.geometry(f"+{x}+{y}")
        title_label = tk.Label(
            info_window,
            text="XiangqiMO",
            font=('Inter', 24, 'bold'),
            bg='#2D2D2D',
            fg='#FFD700'
        )
        title_label.pack(pady=(20, 10))
        desc_label = tk.Label(
            info_window,
            text=tr.get("info_description"),
            font=('Inter', 11),
            bg='#2D2D2D',
            fg='#E0E0E0',
            justify=tk.CENTER,
            wraplength=550
        )
        desc_label.pack(pady=(10, 20))
        separator1 = tk.Frame(info_window, height=1, bg='#404040')
        separator1.pack(fill=tk.X, padx=30, pady=5)
        license_title = tk.Label(
            info_window,
            text="GNU General Public License v3.0",
            font=('Inter', 14, 'bold'),
            bg='#2D2D2D',
            fg='#90EE90'
        )
        license_title.pack(pady=(10, 5))
        license_text = "This program is free software: you can redistribute it and/or modify\n"
        license_text += "it under the terms of the GNU General Public License as published by\n"
        license_text += "the Free Software Foundation, either version 3 of the License, or\n"
        license_text += "(at your option) any later version.\n\n"
        license_text += "This program is distributed in the hope that it will be useful,\n"
        license_text += "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
        license_text += "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\n"
        license_text += "GNU General Public License for more details."
        license_label = tk.Label(
            info_window,
            text=license_text,
            font=('Inter', 10),
            bg='#2D2D2D',
            fg='#B0B0B0',
            justify=tk.CENTER,
            wraplength=550
        )
        license_label.pack(pady=(10, 15))
        link_frame = tk.Frame(info_window, bg='#2D2D2D')
        link_frame.pack(pady=(0, 20))
        link_label = tk.Label(
            link_frame,
            text="Full license text:",
            font=('Inter', 10),
            bg='#2D2D2D',
            fg='#E0E0E0'
        )
        link_label.pack(side=tk.LEFT, padx=(0, 5))
        url_label = tk.Label(
            link_frame,
            text="https://www.gnu.org/licenses/gpl-3.0.txt",
            font=('Inter', 10, 'underline'),
            bg='#2D2D2D',
            fg='#4A7A9C',
            cursor='hand2'
        )
        url_label.pack(side=tk.LEFT)
        url_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.gnu.org/licenses/gpl-3.0.txt"))
        close_btn = tk.Button(
            info_window,
            text="CLOSE",
            font=('Inter', 11, 'bold'),
            bg='#4A7A9C',
            fg='#FFFFFF',
            activebackground='#5A8AAC',
            activeforeground='#FFFFFF',
            width=15,
            height=1,
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            command=info_window.destroy
        )
        close_btn.pack(pady=(10, 15))
        year_frame = tk.Frame(info_window, bg='#2D2D2D')
        year_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=(0, 10))
        year_label = tk.Label(
            year_frame,
            text="2026",
            font=('Inter', 10, 'bold'),
            bg='#2D2D2D',
            fg='#808080'
        )
        year_label.pack(side=tk.RIGHT)

    def open_setup_window(self, event=None):
        """
        Open the position setup window.
        
        Args:
            event: Tkinter event (optional)
        """
        if self.setup_window and self.setup_window.winfo_exists():
            self.setup_window.lift()
            return
        self.setup_window = tk.Toplevel(self.root)
        self.setup_window.title(tr.get("setup_panel"))
        self.setup_window.geometry("600x700")
        self.setup_window.configure(bg='#2D2D2D')
        self.setup_window.resizable(False, False)
        self.setup_window.transient(self.root)
        self.setup_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (600 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (700 // 2)
        self.setup_window.geometry(f"+{x}+{y}")
        title_label = tk.Label(
            self.setup_window,
            text=tr.get("setup_panel"),
            font=('Inter', 18, 'bold'),
            bg='#2D2D2D',
            fg='#FFD700'
        )
        title_label.pack(pady=(15, 5))
        info_label = tk.Label(
            self.setup_window,
            text=tr.get("setup_info"),
            font=('Inter', 11),
            bg='#2D2D2D',
            fg='#E0E0E0',
            wraplength=550
        )
        info_label.pack(pady=(0, 15))
        turn_frame = tk.Frame(self.setup_window, bg='#2D2D2D')
        turn_frame.pack(pady=(5, 15))
        turn_label = tk.Label(
            turn_frame,
            text=tr.get("turn_label"),
            font=('Inter', 12, 'bold'),
            bg='#2D2D2D',
            fg='#E0E0E0'
        )
        turn_label.pack(side=tk.LEFT, padx=(0, 10))
        self.turn_var = tk.StringVar(value="w")
        red_radio = tk.Radiobutton(
            turn_frame,
            text=tr.get("red"),
            variable=self.turn_var,
            value="w",
            bg='#2D2D2D',
            fg='#FF6B6B',
            selectcolor='#2D2D2D',
            activebackground='#2D2D2D',
            activeforeground='#FF6B6B',
            font=('Inter', 11),
            indicatoron=1
        )
        red_radio.pack(side=tk.LEFT, padx=(0, 15))
        black_radio = tk.Radiobutton(
            turn_frame,
            text=tr.get("black"),
            variable=self.turn_var,
            value="b",
            bg='#2D2D2D',
            fg='#FFFFFF',
            selectcolor='#2D2D2D',
            activebackground='#2D2D2D',
            activeforeground='#FFFFFF',
            font=('Inter', 11),
            indicatoron=1
        )
        black_radio.pack(side=tk.LEFT)
        separator = tk.Frame(self.setup_window, height=1, bg='#404040')
        separator.pack(fill=tk.X, padx=30, pady=5)
        red_frame = tk.Frame(self.setup_window, bg='#2D2D2D')
        red_frame.pack(pady=(10, 15), padx=20, fill=tk.X)
        red_label = tk.Label(
            red_frame,
            text=tr.get("red_pieces"),
            font=('Inter', 14, 'bold'),
            bg='#2D2D2D',
            fg='#FF6B6B'
        )
        red_label.pack(pady=(0, 10))
        red_pieces_frame = tk.Frame(red_frame, bg='#2D2D2D')
        red_pieces_frame.pack()
        red_pieces = [
            ('K', '帅'), ('A', '仕'), ('B', '相'), ('N', '马'),
            ('R', '车'), ('C', '炮'), ('P', '兵')
        ]
        for code, symbol in red_pieces:
            self.create_circular_piece_button(red_pieces_frame, code, symbol, '#FF6B6B', '#FFA07A')
        black_frame = tk.Frame(self.setup_window, bg='#2D2D2D')
        black_frame.pack(pady=(0, 15), padx=20, fill=tk.X)
        black_label = tk.Label(
            black_frame,
            text=tr.get("black_pieces"),
            font=('Inter', 14, 'bold'),
            bg='#2D2D2D',
            fg='#FFFFFF'
        )
        black_label.pack(pady=(0, 10))
        black_pieces_frame = tk.Frame(black_frame, bg='#2D2D2D')
        black_pieces_frame.pack()
        black_pieces = [
            ('k', '将'), ('a', '士'), ('b', '象'), ('n', '马'),
            ('r', '车'), ('c', '炮'), ('p', '卒')
        ]
        for code, symbol in black_pieces:
            self.create_circular_piece_button(black_pieces_frame, code, symbol, '#FFFFFF', '#E0E0E0')
        self.selected_piece_label = tk.Label(
            self.setup_window,
            text=tr.get("no_piece_selected"),
            font=('Inter', 12, 'bold'),
            bg='#2D2D2D',
            fg='#FFD700'
        )
        self.selected_piece_label.pack(pady=(15, 10))
        button_frame = tk.Frame(self.setup_window, bg='#2D2D2D')
        button_frame.pack(pady=(15, 20))
        start_pos_btn = tk.Button(
            button_frame,
            text=tr.get("start_position"),
            font=('Inter', 11, 'bold'),
            bg='#404040',
            fg='#FFFFFF',
            activebackground='#505050',
            activeforeground='#FFFFFF',
            width=14,
            height=1,
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            command=self.reset_to_start_position
        )
        start_pos_btn.pack(side=tk.LEFT, padx=5)
        clear_btn = tk.Button(
            button_frame,
            text=tr.get("clear_board"),
            font=('Inter', 11, 'bold'),
            bg='#404040',
            fg='#FFFFFF',
            activebackground='#505050',
            activeforeground='#FFFFFF',
            width=14,
            height=1,
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            command=self.clear_board
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        apply_btn = tk.Button(
            button_frame,
            text=tr.get("apply_position"),
            font=('Inter', 11, 'bold'),
            bg='#4A7A9C',
            fg='#FFFFFF',
            activebackground='#5A8AAC',
            activeforeground='#FFFFFF',
            width=14,
            height=1,
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            command=self.apply_setup_position
        )
        apply_btn.pack(side=tk.LEFT, padx=5)
        close_btn = tk.Button(
            button_frame,
            text=tr.get("close"),
            font=('Inter', 11, 'bold'),
            bg='#404040',
            fg='#FFFFFF',
            activebackground='#505050',
            activeforeground='#FFFFFF',
            width=14,
            height=1,
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            command=self.close_setup_window
        )
        close_btn.pack(side=tk.LEFT, padx=5)
        self.setup_mode = True
        self.setup_icon.config(fg='#FFD700')
        self.setup_label.config(fg='#FFD700', text=tr.get("setup_active"))
        self.board.selected_piece = None
        self.board.legal_moves.clear()
        self.canvas.delete("highlight", "legal", "arrow")
        self.canvas.focus_set()
        self.canvas.tag_raise("all")
        self.root.focus_force()
        self.root.lift()
        self.setup_window.protocol("WM_DELETE_WINDOW", self.close_setup_window)

    def create_circular_piece_button(self, parent, code, symbol, color, hover_color):
        """
        Create a circular button for piece selection in setup window.
        
        Args:
            parent: Parent frame
            code: Piece code
            symbol: Display symbol
            color: Text color
            hover_color: Hover color (unused)
            
        Returns:
            Canvas with the button
        """
        frame = tk.Frame(parent, bg='#2D2D2D')
        frame.pack(side=tk.LEFT, padx=5, pady=2)
        canvas = tk.Canvas(frame, width=50, height=50, bg='#2D2D2D', highlightthickness=0)
        canvas.pack()
        circle = canvas.create_oval(5, 5, 45, 45, fill='#3A3A3A', outline='#505050', width=2)
        text = canvas.create_text(25, 25, text=symbol, font=('SimSun', 18, 'bold'), fill=color)
        canvas.tag_bind(circle, "<Button-1>", lambda e, c=code: self.select_setup_piece(c))
        canvas.tag_bind(text, "<Button-1>", lambda e, c=code: self.select_setup_piece(c))
        return canvas

    def close_setup_window(self):
        """Close the setup window and exit setup mode."""
        if self.setup_window:
            self.setup_window.destroy()
            self.setup_window = None
        self.setup_mode = False
        self.selected_piece_for_setup = None
        self.setup_icon.config(fg='#E0E0E0')
        self.setup_label.config(fg='#B0B0B0', text=tr.get("setup"))
        self.canvas.focus_set()
        self.canvas.tag_raise("all")

    def select_setup_piece(self, piece_code):
        """
        Select a piece for placement in setup mode.
        
        Args:
            piece_code: Piece code to select
        """
        self.selected_piece_for_setup = piece_code
        piece_symbol = self.board.piece_symbols.get(piece_code, piece_code)
        color_text = tr.get("red") if piece_code.isupper() else tr.get("black")
        color_fg = '#FF6B6B' if piece_code.isupper() else '#FFFFFF'
        self.selected_piece_label.config(
            text=f"{tr.get('selected')}: {piece_symbol} ({color_text})",
            fg=color_fg
        )

    def on_board_click(self, event):
        """
        Handle mouse clicks on the board.
        
        Args:
            event: Tkinter mouse event
        """
        x, y = self.board.get_board_coords(event.x, event.y)
        if x is None or y is None:
            return
        if self.setup_mode:
            if self.selected_piece_for_setup:
                success, message = self.board.place_piece(x, y, self.selected_piece_for_setup)
                if success:
                    self.selected_piece_for_setup = None
                    if hasattr(self, 'selected_piece_label'):
                        self.selected_piece_label.config(text=tr.get("no_piece_selected"), fg='#FFD700')
                else:
                    if hasattr(self, 'selected_piece_label'):
                        self.selected_piece_label.config(text=message, fg='#FF6B6B')
            else:
                success, message = self.board.remove_piece(x, y)
                if success:
                    if hasattr(self, 'selected_piece_label'):
                        self.selected_piece_label.config(text=tr.get("no_piece_selected"), fg='#FFD700')
                else:
                    if hasattr(self, 'selected_piece_label'):
                        self.selected_piece_label.config(text=message, fg='#FF6B6B')
        else:
            self.board.on_click(event)

    def clear_board(self):
        """Clear all pieces from the board except kings."""
        kings = {}
        for (x, y), piece in list(self.board.pieces.items()):
            if piece.lower() == 'k':
                kings[(x, y)] = piece
        self.board.pieces.clear()
        for (x, y), piece in kings.items():
            self.board.pieces[(x, y)] = piece
        self.board.draw_pieces()
        self.selected_piece_for_setup = None
        if hasattr(self, 'selected_piece_label'):
            self.selected_piece_label.config(
                text=tr.get("no_piece_selected"),
                fg='#FFD700'
            )

    def reset_to_start_position(self):
        """Reset the board to the starting position."""
        self.board.set_position(self.board.start_fen)
        self.board.draw_pieces()
        self.selected_piece_for_setup = None
        if hasattr(self, 'selected_piece_label'):
            self.selected_piece_label.config(
                text=tr.get("no_piece_selected"),
                fg='#FFD700'
            )

    def apply_setup_position(self):
        """Apply the current setup position and close the setup window."""
        is_valid, message = self.board.is_position_valid()
        if not is_valid:
            if hasattr(self, 'selected_piece_label'):
                self.selected_piece_label.config(
                    text=message,
                    fg='#FF6B6B'
                )
            return
        self.board.current_turn = self.turn_var.get()
        self.board.move_history.clear()
        self.board.move_from_to_history.clear()
        self.update_move_list()
        self.clear_analysis_lines()
        self.canvas.delete("arrow")
        self.close_setup_window()

    def create_language_menu(self):
        """Create the language selection menu."""
        self.lang_menu = tk.Menu(self.root, tearoff=0, bg='#2D2D2D', fg='#E0E0E0',
                                activebackground='#404040', activeforeground='#FFFFFF',
                                font=('Inter', 10))
        self.lang_menu.add_command(label="🇬🇧 English", command=lambda: self.change_lang('en'))
        self.lang_menu.add_command(label="🇷🇺 Русский", command=lambda: self.change_lang('ru'))
        self.lang_menu.add_command(label="🇨🇳 中文", command=lambda: self.change_lang('zh'))
        self.lang_menu.add_command(label="🇻🇳 Tiếng Việt", command=lambda: self.change_lang('vi'))
        self.lang_menu.add_command(label="🇲🇾 Bahasa Melayu", command=lambda: self.change_lang('ms'))

    def show_language_menu(self, event):
        """
        Show the language selection menu.
        
        Args:
            event: Tkinter event
        """
        try:
            self.lang_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.lang_menu.grab_release()

    def update_language_label(self):
        """Update the language indicator label."""
        lang_codes = {
            'en': 'EN',
            'ru': 'RU',
            'zh': '中文',
            'vi': 'VI',
            'ms': 'MS'
        }
        self.current_lang_label.config(text=lang_codes.get(tr.lang, 'EN'))

    def undo_move(self):
        """Undo the last move."""
        if self.board.undo_move():
            self.update_move_list()
            self.canvas.delete("arrow")
            self.clear_analysis_lines()

    def clear_analysis_lines(self):
        """Clear all analysis display lines."""
        self.best_move_text.config(text="---")
        self.best_score_text.config(text="")
        self.second_move_text.config(text="---")
        self.second_score_text.config(text="")
        self.score_value.config(text="0.00")

    def update_move_list(self):
        """Update the move history listbox."""
        self.move_listbox.delete(0, tk.END)
        moves = self.board.move_history
        for i in range(0, len(moves), 2):
            move_num = i//2 + 1
            if i + 1 < len(moves):
                display = f"{move_num:2d}. {moves[i]:<6} {moves[i+1]:<6}"
            else:
                display = f"{move_num:2d}. {moves[i]:<6}"
            self.move_listbox.insert(tk.END, display)
        self.move_listbox.see(tk.END)

    def analyze(self):
        """Start position analysis in a separate thread."""
        self.analyze_btn.config(state=tk.DISABLED, bg='#505050', text=tr.get("thinking"))
        self.best_move_text.config(text="⚙ ...")
        self.best_score_text.config(text="")
        self.second_move_text.config(text="⚙ ...")
        self.second_score_text.config(text="")
        self.score_value.config(text="...")
        self.root.update()
        def run():
            try:
                current_fen = self.board.fen()
                if self.engine.start():
                    results = self.engine.analyze_multi(current_fen, depth=15, multipv=2)
                    self.engine.close()
                    if results and len(results) >= 2:
                        best_move, best_score = results[0]
                        second_move, second_score = results[1]
                        self.root.after(0, self.update_analysis,
                                      best_move, best_score, second_move, second_score)
                    else:
                        self.root.after(0, self.no_move_found)
                else:
                    self.root.after(0, self.analysis_error)
            except Exception as e:
                self.root.after(0, self.analysis_error)
        threading.Thread(target=run, daemon=True).start()

    def no_move_found(self):
        """Handle case when no move is found."""
        self.analyze_btn.config(state=tk.NORMAL, bg='#3A3A3A', text=tr.get("analyze"))
        self.best_move_text.config(text=tr.get("no_move"))
        self.best_score_text.config(text="")
        self.second_move_text.config(text="---")
        self.second_score_text.config(text="")
        self.score_value.config(text="0.00")

    def update_analysis(self, best_move, best_score, second_move, second_score):
        """
        Update UI with analysis results.
        
        Args:
            best_move: Best move UCI string
            best_score: Best move score
            second_move: Second best move UCI string
            second_score: Second best move score
        """
        self.analyze_btn.config(state=tk.NORMAL, bg='#3A3A3A', text=tr.get("analyze"))
        if best_move and len(best_move) >= 4:
            coords = self.board.convert_uci_to_move(best_move)
            if coords:
                from_x, from_y, to_x, to_y = coords
                if (from_x, from_y) in self.board.pieces:
                    notation = self.board.generate_move_notation(from_x, from_y, to_x, to_y)
                    score_str = ""
                    if best_score:
                        try:
                            score_val = float(best_score)
                            if score_val > 0:
                                score_str = f"(+{best_score})"
                            else:
                                score_str = f"({best_score})"
                        except:
                            score_str = f"({best_score})"
                    self.best_move_text.config(text=notation)
                    self.best_score_text.config(text=score_str)
                    self.score_value.config(text=best_score if best_score else "0.00")
                    self.board.draw_arrow(best_move)
                else:
                    self.best_move_text.config(text=tr.get("no_piece"))
                    self.best_score_text.config(text="")
            else:
                self.best_move_text.config(text=tr.get("invalid"))
                self.best_score_text.config(text="")
        else:
            self.best_move_text.config(text=tr.get("no_move"))
            self.best_score_text.config(text="")
        if second_move and len(second_move) >= 4:
            coords = self.board.convert_uci_to_move(second_move)
            if coords:
                from_x, from_y, to_x, to_y = coords
                if (from_x, from_y) in self.board.pieces:
                    notation = self.board.generate_move_notation(from_x, from_y, to_x, to_y)
                    score_str = ""
                    if second_score:
                        try:
                            score_val = float(second_score)
                            if score_val > 0:
                                score_str = f"(+{second_score})"
                            else:
                                score_str = f"({second_score})"
                        except:
                            score_str = f"({second_score})"
                    self.second_move_text.config(text=notation)
                    self.second_score_text.config(text=score_str)
                else:
                    self.second_move_text.config(text=tr.get("no_piece"))
                    self.second_score_text.config(text="")
            else:
                self.second_move_text.config(text=tr.get("invalid"))
                self.second_score_text.config(text="")
        else:
            self.second_move_text.config(text="---")
            self.second_score_text.config(text="")

    def analysis_error(self):
        """Handle engine analysis error."""
        self.analyze_btn.config(state=tk.NORMAL, bg='#3A3A3A', text=tr.get("analyze"))
        self.best_move_text.config(text=tr.get("engine_error"))
        self.best_score_text.config(text="")
        self.second_move_text.config(text="---")
        self.second_score_text.config(text="")
        self.score_value.config(text="0.00")

    def flip_board(self):
        """Flip the board orientation."""
        self.board.flip()
        self.canvas.delete("arrow")
        self.clear_analysis_lines()

    def reset_board(self):
        """Reset the board to starting position."""
        self.board.set_position(self.board.start_fen)
        self.board.reset_history()
        self.update_move_list()
        self.canvas.delete("arrow")
        self.clear_analysis_lines()
        if self.setup_mode:
            self.close_setup_window()

    def change_lang(self, lang):
        """
        Change the interface language.
        
        Args:
            lang: Language code ('en', 'ru', 'zh', 'vi', 'ms')
        """
        tr.lang = lang
        self.update_language_label()
        self.panel_title.config(text=tr.get("control_panel"))
        self.analyze_btn.config(text=tr.get("analyze"))
        self.flip_btn.config(text=tr.get("flip"))
        self.reset_btn.config(text=tr.get("reset"))
        self.undo_btn.config(text=tr.get("undo"))
        self.analysis_title.config(text=tr.get("best_moves"))
        self.eval_title.config(text=tr.get("evaluation"))
        self.moves_title.config(text=tr.get("move_history"))
        if self.setup_mode:
            self.setup_label.config(text=tr.get("setup_active"))
        else:
            self.setup_label.config(text=tr.get("setup"))