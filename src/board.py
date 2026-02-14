import tkinter as tk
from translator import tr

class XiangqiBoard:
    """
    Main class representing the Xiangqi board.
    Handles board drawing, piece movement, move validation, and position setup.
    """
    def __init__(self, canvas, x=50, y=20, cell=60):
        """
        Initialize the Xiangqi board.
        
        Args:
            canvas: Tkinter canvas to draw on
            x: X-coordinate of board top-left corner
            y: Y-coordinate of board top-left corner
            cell: Size of each board cell in pixels
        """
        self.canvas = canvas
        self.x = x
        self.y = y
        self.cell = cell
        self.start_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
        self.flipped = False
        self.selected_piece = None
        self.legal_moves = []
        self.pieces = {}
        self.current_turn = 'w'
        self.move_history = []
        self.position_history = []
        self.move_from_to_history = []
        self.piece_symbols = {
            'r': '车', 'R': '车',
            'n': '马', 'N': '马',
            'b': '象', 'B': '相',
            'a': '士', 'A': '仕',
            'k': '将', 'K': '帅',
            'c': '炮', 'C': '炮',
            'p': '卒', 'P': '兵'
        }
        self.piece_names_en = {
            'r': 'R', 'R': 'R',
            'n': 'N', 'N': 'N',
            'b': 'B', 'B': 'B',
            'a': 'A', 'A': 'A',
            'k': 'K', 'K': 'K',
            'c': 'C', 'C': 'C',
            'p': 'P', 'P': 'P'
        }
        self.max_pieces = {
            'K': 1, 'k': 1,
            'A': 2, 'a': 2,
            'B': 2, 'b': 2,
            'N': 2, 'n': 2,
            'R': 2, 'r': 2,
            'C': 2, 'c': 2,
            'P': 5, 'p': 5
        }
        self.colors = {
            'board': '#E8D5B5',
            'lines': '#5D3A1A',
            'river': '#4A7A9C',
            'red': '#B22222',
            'black': '#2F4F4F',
            'highlight': '#FF4500',
            'legal': '#32CD32',
            'notation': '#FFFFFF',
            'arrow': '#FF3333',
            'arrow_outline': '#FF0000',
            'check': '#FFD700',
            'checkmate': '#DC143C',
            'start_dot': '#8B4513'
        }
        self.start_dots = {
            (0, 6): 'P', (2, 6): 'P', (4, 6): 'P', (6, 6): 'P', (8, 6): 'P',
            (0, 3): 'p', (2, 3): 'p', (4, 3): 'p', (6, 3): 'p', (8, 3): 'p',
            (1, 7): 'C', (7, 7): 'C',
            (1, 2): 'c', (7, 2): 'c'
        }
        self.draw_board()
        self.set_position(self.start_fen)
        self.bind_events()

    def draw_board(self):
        """Draw the Xiangqi board with all visual elements."""
        self.canvas.delete("all")
        self.canvas.create_rectangle(
            self.x - 30, self.y - 30,
            self.x + 8 * self.cell + 30, self.y + 9 * self.cell + 35,
            fill=self.colors['board'], outline=self.colors['lines'], width=4
        )
        for i in range(9):
            x = self.x + i * self.cell
            self.canvas.create_line(
                x, self.y, x, self.y + 9 * self.cell,
                fill=self.colors['lines'], width=2
            )
        for i in range(10):
            y = self.y + i * self.cell
            self.canvas.create_line(
                self.x, y, self.x + 8 * self.cell, y,
                fill=self.colors['lines'], width=2
            )
        river_y = self.y + 4.5 * self.cell
        self.canvas.create_rectangle(
            self.x, self.y + 4 * self.cell,
            self.x + 8 * self.cell, self.y + 5 * self.cell,
            fill=self.colors['river'], stipple="gray50"
        )
        self.canvas.create_text(
            self.x + 4 * self.cell, river_y,
            text="楚  河\n汉  界",
            font=('Microsoft YaHei', 16, 'bold'),
            fill='white', justify='center'
        )
        self.canvas.create_line(
            self.x + 3 * self.cell, self.y,
            self.x + 5 * self.cell, self.y + 2 * self.cell,
            fill=self.colors['lines'], width=2
        )
        self.canvas.create_line(
            self.x + 5 * self.cell, self.y,
            self.x + 3 * self.cell, self.y + 2 * self.cell,
            fill=self.colors['lines'], width=2
        )
        self.canvas.create_line(
            self.x + 3 * self.cell, self.y + 7 * self.cell,
            self.x + 5 * self.cell, self.y + 9 * self.cell,
            fill=self.colors['lines'], width=2
        )
        self.canvas.create_line(
            self.x + 5 * self.cell, self.y + 7 * self.cell,
            self.x + 3 * self.cell, self.y + 9 * self.cell,
            fill=self.colors['lines'], width=2
        )
        self.draw_start_dots()
        black_numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        for i, num in enumerate(black_numbers):
            x = self.x + i * self.cell
            y = self.y - 25
            self.canvas.create_text(
                x, y, text=num,
                font=('Arial', 16, 'bold'),
                fill=self.colors['notation'], anchor='s'
            )
        red_numbers = ['9', '8', '7', '6', '5', '4', '3', '2', '1']
        for i, num in enumerate(red_numbers):
            x = self.x + i * self.cell
            y = self.y + 9 * self.cell + 29
            self.canvas.create_text(
                x, y, text=num,
                font=('Arial', 16, 'bold'),
                fill=self.colors['notation'], anchor='n'
            )

    def draw_start_dots(self):
        """Draw dots at starting positions for pawns and cannons."""
        self.canvas.delete("start_dots")
        for (x, y), piece_type in self.start_dots.items():
            if self.flipped:
                draw_x = 8 - x
                draw_y = 9 - y
            else:
                draw_x = x
                draw_y = y
            cx = self.x + draw_x * self.cell
            cy = self.y + draw_y * self.cell
            if (x, y) not in self.pieces:
                self.canvas.create_oval(
                    cx - 4, cy - 4, cx + 4, cy + 4,
                    fill=self.colors['start_dot'], outline='', width=0,
                    tags=("start_dots", f"dot_{x}_{y}")
                )

    def set_position(self, fen):
        """
        Set board position from FEN string.
        
        Args:
            fen: FEN string representing the position
        """
        self.pieces.clear()
        board_part = fen.split()[0]
        rows = board_part.split('/')
        for y, row in enumerate(rows):
            x = 0
            for char in row:
                if char.isdigit():
                    x += int(char)
                else:
                    self.pieces[(x, y)] = char
                    x += 1
        self.current_turn = fen.split()[1] if len(fen.split()) > 1 else 'w'
        self.draw_pieces()
        self.highlight_check_and_mate()

    def draw_pieces(self):
        """Draw all pieces on the board at their current positions."""
        self.canvas.delete("pieces")
        for (x, y), piece in self.pieces.items():
            if self.flipped:
                draw_x = 8 - x
                draw_y = 9 - y
            else:
                draw_x = x
                draw_y = y
            cx = self.x + draw_x * self.cell
            cy = self.y + draw_y * self.cell
            self.canvas.create_oval(
                cx - 23, cy - 23, cx + 23, cy + 23,
                fill='#FDF5E6', outline=self.colors['lines'], width=2,
                tags=("pieces", f"piece_{x}_{y}")
            )
            symbol = self.piece_symbols.get(piece, piece)
            color = self.colors['red'] if piece.isupper() else self.colors['black']
            self.canvas.create_text(
                cx, cy, text=symbol,
                font=('SimSun', 22, 'bold'),
                fill=color, tags=("pieces", f"piece_{x}_{y}")
            )
        self.draw_start_dots()

    def bind_events(self):
        """Bind mouse events to the canvas."""
        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        """
        Handle mouse click on the board.
        
        Args:
            event: Tkinter mouse event
        """
        x, y = self.get_board_coords(event.x, event.y)
        if x is not None and y is not None:
            if self.selected_piece:
                self.try_move(x, y)
            else:
                self.select_piece(x, y)

    def get_board_coords(self, canvas_x, canvas_y):
        """
        Convert canvas coordinates to board coordinates.
        
        Args:
            canvas_x: X-coordinate on canvas
            canvas_y: Y-coordinate on canvas
            
        Returns:
            Tuple (x, y) of board coordinates or (None, None) if outside board
        """
        dx = canvas_x - self.x
        dy = canvas_y - self.y
        if dx < -self.cell/2 or dx > 8 * self.cell + self.cell/2:
            return None, None
        if dy < -self.cell/2 or dy > 9 * self.cell + self.cell/2:
            return None, None
        board_x = round(dx / self.cell)
        board_y = round(dy / self.cell)
        if 0 <= board_x <= 8 and 0 <= board_y <= 9:
            if self.flipped:
                return 8 - board_x, 9 - board_y
            return board_x, board_y
        return None, None

    def select_piece(self, x, y):
        """
        Select a piece for moving.
        
        Args:
            x: Board x-coordinate
            y: Board y-coordinate
        """
        if (x, y) in self.pieces:
            piece = self.pieces[(x, y)]
            is_red = piece.isupper()
            if self.current_turn == 'w' and is_red:
                self.selected_piece = (x, y)
                self.highlight_square(x, y, self.colors['highlight'])
                self.generate_legal_moves(x, y)
            elif self.current_turn == 'b' and not is_red:
                self.selected_piece = (x, y)
                self.highlight_square(x, y, self.colors['highlight'])
                self.generate_legal_moves(x, y)

    def generate_move_notation(self, fx, fy, tx, ty):
        """
        Generate move notation in international Xiangqi format.
        
        Args:
            fx: From x-coordinate
            fy: From y-coordinate
            tx: To x-coordinate
            ty: To y-coordinate
            
        Returns:
            String with move notation
        """
        piece = self.pieces.get((fx, fy))
        if not piece:
            return "???"
        piece_char = self.piece_names_en.get(piece, '?')
        is_red = piece.isupper()
        if is_red:
            from_file = 9 - fx
            to_file = 9 - tx
            if ty < fy:
                direction = '+'
                steps = fy - ty
            elif ty > fy:
                direction = '-'
                steps = ty - fy
            else:
                direction = '='
                steps = abs(tx - fx)
            if direction == '=':
                return f"{piece_char}{from_file}{direction}{to_file}"
            else:
                return f"{piece_char}{from_file}{direction}{steps}"
        else:
            from_file = fx + 1
            to_file = tx + 1
            if ty > fy:
                direction = '+'
                steps = ty - fy
            elif ty < fy:
                direction = '-'
                steps = fy - ty
            else:
                direction = '='
                steps = abs(tx - fx)
            if direction == '=':
                return f"{piece_char}{from_file}{direction}{to_file}"
            else:
                return f"{piece_char}{from_file}{direction}{steps}"

    def undo_move(self):
        """
        Undo the last move.
        
        Returns:
            True if undo was successful, False otherwise
        """
        if len(self.move_from_to_history) == 0:
            return False
        from_x, from_y, to_x, to_y, captured_piece = self.move_from_to_history.pop()
        piece = self.pieces.pop((to_x, to_y))
        self.pieces[(from_x, from_y)] = piece
        if captured_piece:
            self.pieces[(to_x, to_y)] = captured_piece
        if self.move_history:
            self.move_history.pop()
        if len(self.position_history) > 1:
            self.position_history.pop()
        if self.current_turn == 'w':
            self.current_turn = 'b'
        else:
            self.current_turn = 'w'
        self.selected_piece = None
        self.legal_moves.clear()
        self.canvas.delete("highlight", "legal", "arrow")
        self.draw_pieces()
        self.highlight_check_and_mate()
        return True

    def is_square_attacked(self, x, y, attacking_color):
        """
        Check if a square is attacked by pieces of given color.
        
        Args:
            x: Board x-coordinate
            y: Board y-coordinate
            attacking_color: 'w' for red, 'b' for black
            
        Returns:
            True if square is attacked, False otherwise
        """
        for (fx, fy), piece in self.pieces.items():
            if (piece.isupper() and attacking_color == 'w') or (not piece.isupper() and attacking_color == 'b'):
                moves = self.generate_pseudo_legal_moves_for_piece(fx, fy, check_open_king=False)
                if (x, y) in moves:
                    return True
        return False

    def generate_pseudo_legal_moves_for_piece(self, x, y, check_open_king=True):
        """
        Generate pseudo-legal moves for a piece (without checking if they expose the king).
        
        Args:
            x: Board x-coordinate
            y: Board y-coordinate
            check_open_king: Whether to filter out moves that expose the king
            
        Returns:
            List of (x, y) tuples representing possible moves
        """
        piece = self.pieces.get((x, y))
        if not piece:
            return []
        piece_type = piece.lower()
        is_red = piece.isupper()
        moves = []
        if piece_type == 'r':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                while 0 <= nx <= 8 and 0 <= ny <= 9:
                    if (nx, ny) in self.pieces:
                        if self.pieces[(nx, ny)].isupper() != is_red:
                            moves.append((nx, ny))
                        break
                    moves.append((nx, ny))
                    nx += dx
                    ny += dy
        if piece_type == 'n':
            horse_moves = [
                (1, 2), (1, -2), (-1, 2), (-1, -2),
                (2, 1), (2, -1), (-2, 1), (-2, -1)
            ]
            block_dirs = {
                (1, 2): (0, 1), (1, -2): (0, -1),
                (-1, 2): (0, 1), (-1, -2): (0, -1),
                (2, 1): (1, 0), (2, -1): (1, 0),
                (-2, 1): (-1, 0), (-2, -1): (-1, 0)
            }
            for dx, dy in horse_moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx <= 8 and 0 <= ny <= 9:
                    bx, by = x + block_dirs[(dx, dy)][0], y + block_dirs[(dx, dy)][1]
                    if (bx, by) not in self.pieces:
                        if (nx, ny) not in self.pieces:
                            moves.append((nx, ny))
                        elif self.pieces[(nx, ny)].isupper() != is_red:
                            moves.append((nx, ny))
        if piece_type == 'b':
            elephant_moves = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
            for dx, dy in elephant_moves:
                nx, ny = x + dx, y + dy
                if nx < 0 or nx > 8 or ny < 0 or ny > 9:
                    continue
                if is_red:
                    if ny < 5: continue
                else:
                    if ny > 4: continue
                mx, my = x + dx//2, y + dy//2
                if (mx, my) not in self.pieces:
                    if (nx, ny) not in self.pieces:
                        moves.append((nx, ny))
                    elif self.pieces[(nx, ny)].isupper() != is_red:
                        moves.append((nx, ny))
        if piece_type == 'a':
            advisor_moves = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dx, dy in advisor_moves:
                nx, ny = x + dx, y + dy
                if nx < 0 or nx > 8 or ny < 0 or ny > 9:
                    continue
                if is_red:
                    if 3 <= nx <= 5 and 7 <= ny <= 9:
                        if (nx, ny) not in self.pieces:
                            moves.append((nx, ny))
                        elif self.pieces[(nx, ny)].isupper() != is_red:
                            moves.append((nx, ny))
                else:
                    if 3 <= nx <= 5 and 0 <= ny <= 2:
                        if (nx, ny) not in self.pieces:
                            moves.append((nx, ny))
                        elif self.pieces[(nx, ny)].isupper() != is_red:
                            moves.append((nx, ny))
        if piece_type == 'k':
            king_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dx, dy in king_moves:
                nx, ny = x + dx, y + dy
                if nx < 0 or nx > 8 or ny < 0 or ny > 9:
                    continue
                if is_red:
                    if 3 <= nx <= 5 and 7 <= ny <= 9:
                        if (nx, ny) not in self.pieces:
                            moves.append((nx, ny))
                        elif self.pieces[(nx, ny)].isupper() != is_red:
                            moves.append((nx, ny))
                else:
                    if 3 <= nx <= 5 and 0 <= ny <= 2:
                        if (nx, ny) not in self.pieces:
                            moves.append((nx, ny))
                        elif self.pieces[(nx, ny)].isupper() != is_red:
                            moves.append((nx, ny))
        if piece_type == 'c':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                jumped = False
                while 0 <= nx <= 8 and 0 <= ny <= 9:
                    if (nx, ny) in self.pieces:
                        if not jumped:
                            jumped = True
                        else:
                            if self.pieces[(nx, ny)].isupper() != is_red:
                                moves.append((nx, ny))
                            break
                    else:
                        if not jumped:
                            moves.append((nx, ny))
                    nx += dx
                    ny += dy
        if piece_type == 'p':
            if is_red:
                if y > 0:
                    nx, ny = x, y - 1
                    if (nx, ny) not in self.pieces:
                        moves.append((nx, ny))
                    elif self.pieces[(nx, ny)].isupper() != is_red:
                        moves.append((nx, ny))
                if y <= 4:
                    for nx in [x - 1, x + 1]:
                        if 0 <= nx <= 8:
                            ny = y
                            if (nx, ny) not in self.pieces:
                                moves.append((nx, ny))
                            elif self.pieces[(nx, ny)].isupper() != is_red:
                                moves.append((nx, ny))
            else:
                if y < 9:
                    nx, ny = x, y + 1
                    if (nx, ny) not in self.pieces:
                        moves.append((nx, ny))
                    elif self.pieces[(nx, ny)].isupper() != is_red:
                        moves.append((nx, ny))
                if y >= 5:
                    for nx in [x - 1, x + 1]:
                        if 0 <= nx <= 8:
                            ny = y
                            if (nx, ny) not in self.pieces:
                                moves.append((nx, ny))
                            elif self.pieces[(nx, ny)].isupper() != is_red:
                                moves.append((nx, ny))
        if check_open_king:
            filtered = []
            for tx, ty in moves:
                if not self.would_expose_king(x, y, tx, ty, is_red):
                    filtered.append((tx, ty))
            return filtered
        return moves

    def would_expose_king(self, fx, fy, tx, ty, is_red):
        """
        Check if moving a piece would expose the king to check.
        
        Args:
            fx: From x-coordinate
            fy: From y-coordinate
            tx: To x-coordinate
            ty: To y-coordinate
            is_red: True if moving piece is red
            
        Returns:
            True if move would expose king, False otherwise
        """
        captured = self.pieces.pop((tx, ty), None)
        moved_piece = self.pieces.pop((fx, fy))
        self.pieces[(tx, ty)] = moved_piece
        king_pos_red = None
        king_pos_black = None
        for (kx, ky), p in self.pieces.items():
            if p == 'K':
                king_pos_red = (kx, ky)
            elif p == 'k':
                king_pos_black = (kx, ky)
        illegal = False
        if king_pos_red and king_pos_black:
            rx, ry = king_pos_red
            bx, by = king_pos_black
            if rx == bx:
                y_min, y_max = min(ry, by), max(ry, by)
                block = False
                for yy in range(y_min + 1, y_max):
                    if (rx, yy) in self.pieces:
                        block = True
                        break
                if not block:
                    illegal = True
        if not illegal:
            if is_red:
                if king_pos_red and self.is_square_attacked(king_pos_red[0], king_pos_red[1], 'b'):
                    illegal = True
            else:
                if king_pos_black and self.is_square_attacked(king_pos_black[0], king_pos_black[1], 'w'):
                    illegal = True
        del self.pieces[(tx, ty)]
        self.pieces[(fx, fy)] = moved_piece
        if captured:
            self.pieces[(tx, ty)] = captured
        return illegal

    def generate_legal_moves(self, x, y):
        """
        Generate and highlight legal moves for a piece.
        
        Args:
            x: Board x-coordinate
            y: Board y-coordinate
        """
        self.legal_moves = self.generate_pseudo_legal_moves_for_piece(x, y, check_open_king=True)
        self.canvas.delete("legal")
        for mx, my in self.legal_moves:
            self.highlight_square(mx, my, self.colors['legal'], is_move=True)

    def is_in_check(self, color):
        """
        Check if the king of given color is in check.
        
        Args:
            color: 'w' for red, 'b' for black
            
        Returns:
            True if king is in check, False otherwise
        """
        king_pos = None
        for (x, y), piece in self.pieces.items():
            if (color == 'w' and piece == 'K') or (color == 'b' and piece == 'k'):
                king_pos = (x, y)
                break
        if not king_pos:
            return False
        attacking_color = 'b' if color == 'w' else 'w'
        return self.is_square_attacked(king_pos[0], king_pos[1], attacking_color)

    def is_in_checkmate(self, color):
        """
        Check if the king of given color is in checkmate.
        
        Args:
            color: 'w' for red, 'b' for black
            
        Returns:
            True if king is in checkmate, False otherwise
        """
        if not self.is_in_check(color):
            return False
        
        # Collect all pieces of the given color first to avoid dictionary changes during iteration
        pieces_of_color = []
        for (x, y), piece in list(self.pieces.items()):
            if (color == 'w' and piece.isupper()) or (color == 'b' and not piece.isupper()):
                pieces_of_color.append((x, y, piece))
        
        # Check each piece
        for x, y, piece in pieces_of_color:
            moves = self.generate_pseudo_legal_moves_for_piece(x, y, check_open_king=True)
            if moves:
                return False
        return True

    def highlight_check_and_mate(self):
        """Highlight kings that are in check or checkmate."""
        self.canvas.delete("check_mate")
        if self.is_in_check('w'):
            color = self.colors['checkmate'] if self.is_in_checkmate('w') else self.colors['check']
            self.highlight_king('w', color)
        if self.is_in_check('b'):
            color = self.colors['checkmate'] if self.is_in_checkmate('b') else self.colors['check']
            self.highlight_king('b', color)

    def highlight_king(self, color, outline_color):
        """
        Highlight the king of given color.
        
        Args:
            color: 'w' for red, 'b' for black
            outline_color: Color to use for highlighting
        """
        king_char = 'K' if color == 'w' else 'k'
        for (x, y), piece in self.pieces.items():
            if piece == king_char:
                if self.flipped:
                    draw_x = 8 - x
                    draw_y = 9 - y
                else:
                    draw_x = x
                    draw_y = y
                cx = self.x + draw_x * self.cell
                cy = self.y + draw_y * self.cell
                self.canvas.create_oval(
                    cx - 30, cy - 30, cx + 30, cy + 30,
                    outline=outline_color, width=6,
                    tags="check_mate"
                )
                break

    def try_move(self, to_x, to_y):
        """
        Attempt to move the selected piece to target square.
        
        Args:
            to_x: Target x-coordinate
            to_y: Target y-coordinate
        """
        if (to_x, to_y) in self.legal_moves:
            from_x, from_y = self.selected_piece
            captured = self.pieces.get((to_x, to_y))
            self.move_from_to_history.append((from_x, from_y, to_x, to_y, captured))
            self.position_history.append(self.fen())
            notation = self.generate_move_notation(from_x, from_y, to_x, to_y)
            self.move_history.append(notation)
            piece = self.pieces.pop((from_x, from_y))
            if (to_x, to_y) in self.pieces:
                self.pieces.pop((to_x, to_y))
            self.pieces[(to_x, to_y)] = piece
            self.current_turn = 'b' if self.current_turn == 'w' else 'w'
            self.draw_pieces()
            self.highlight_check_and_mate()
            self.canvas.delete("arrow")
            if hasattr(self, 'on_move_made'):
                self.on_move_made()
        self.selected_piece = None
        self.legal_moves.clear()
        self.canvas.delete("highlight", "legal")

    def highlight_square(self, x, y, color, is_move=False):
        """
        Highlight a square on the board.
        
        Args:
            x: Board x-coordinate
            y: Board y-coordinate
            color: Color to use for highlighting
            is_move: True if highlighting a legal move, False if highlighting selected piece
        """
        if self.flipped:
            draw_x = 8 - x
            draw_y = 9 - y
        else:
            draw_x = x
            draw_y = y
        cx = self.x + draw_x * self.cell
        cy = self.y + draw_y * self.cell
        tag = "legal" if is_move else "highlight"
        if is_move:
            self.canvas.create_oval(
                cx - 25, cy - 25, cx + 25, cy + 25,
                outline=color, width=4,
                tags=tag
            )
            self.canvas.create_oval(
                cx - 20, cy - 20, cx + 20, cy + 20,
                outline='#FFFFFF', width=2, dash=(3, 2),
                tags=tag
            )
        else:
            self.canvas.create_oval(
                cx - 30, cy - 30, cx + 30, cy + 30,
                outline=color, width=5,
                tags=tag
            )
            self.canvas.create_oval(
                cx - 25, cy - 25, cx + 25, cy + 25,
                outline='#FFA500', width=2,
                tags=tag
            )

    def convert_uci_to_move(self, uci_move):
        """
        Convert UCI move string to board coordinates.
        
        Args:
            uci_move: UCI move string (e.g., 'a2a4')
            
        Returns:
            Tuple (from_x, from_y, to_x, to_y) or None if invalid
        """
        if not uci_move or len(uci_move) < 4:
            return None
        try:
            from_file = uci_move[0]
            from_rank_str = ""
            to_file = uci_move[2] if len(uci_move) > 2 else ''
            to_rank_str = ""
            i = 1
            while i < len(uci_move) and uci_move[i].isdigit():
                from_rank_str += uci_move[i]
                i += 1
            if i < len(uci_move):
                to_file = uci_move[i]
                i += 1
            while i < len(uci_move) and uci_move[i].isdigit():
                to_rank_str += uci_move[i]
                i += 1
            from_file_idx = ord(from_file) - ord('a')
            from_rank = int(from_rank_str)
            to_file_idx = ord(to_file) - ord('a')
            to_rank = int(to_rank_str)
            from_y = 10 - from_rank
            to_y = 10 - to_rank
            if 0 <= from_file_idx <= 8 and 0 <= from_y <= 9 and \
               0 <= to_file_idx <= 8 and 0 <= to_y <= 9:
                return (from_file_idx, from_y, to_file_idx, to_y)
        except Exception as e:
            pass
        return None

    def draw_arrow(self, move):
        """
        Draw an arrow showing a move on the board.
        
        Args:
            move: UCI move string
        """
        self.canvas.delete("arrow")
        if not move or len(move) < 4:
            return
        coords = self.convert_uci_to_move(move)
        if not coords:
            return
        from_file, from_rank, to_file, to_rank = coords
        if (from_file, from_rank) not in self.pieces:
            return
        if self.flipped:
            from_file = 8 - from_file
            to_file = 8 - to_file
            from_rank = 9 - from_rank
            to_rank = 9 - to_rank
        x1 = self.x + from_file * self.cell
        y1 = self.y + from_rank * self.cell
        x2 = self.x + to_file * self.cell
        y2 = self.y + to_rank * self.cell
        self.canvas.create_line(
            x1, y1, x2, y2,
            width=6, fill=self.colors['arrow'],
            arrow='last', arrowshape=(18, 22, 10),
            capstyle=tk.ROUND, joinstyle=tk.ROUND,
            tags="arrow"
        )
        self.canvas.create_line(
            x1, y1, x2, y2,
            width=8, fill=self.colors['arrow_outline'],
            arrow='last', arrowshape=(20, 24, 12),
            capstyle=tk.ROUND, joinstyle=tk.ROUND,
            tags="arrow"
        )
        self.canvas.create_oval(
            x1 - 15, y1 - 15, x1 + 15, y1 + 15,
            outline=self.colors['arrow_outline'], width=4, tags="arrow"
        )
        self.canvas.create_oval(
            x1 - 12, y1 - 12, x1 + 12, y1 + 12,
            outline=self.colors['arrow'], width=3, tags="arrow"
        )
        self.canvas.create_oval(
            x2 - 18, y2 - 18, x2 + 18, y2 + 18,
            outline=self.colors['arrow_outline'], width=5, tags="arrow"
        )
        self.canvas.create_oval(
            x2 - 15, y2 - 15, x2 + 15, y2 + 15,
            outline=self.colors['arrow'], width=4, tags="arrow"
        )

    def flip(self):
        """Flip the board orientation."""
        self.flipped = not self.flipped
        self.selected_piece = None
        self.legal_moves.clear()
        self.canvas.delete("highlight", "legal", "arrow")
        self.draw_pieces()
        self.highlight_check_and_mate()

    def fen(self):
        """
        Generate FEN string for current position.
        
        Returns:
            FEN string
        """
        board = []
        for y in range(10):
            row = ""
            empty = 0
            for x in range(9):
                if (x, y) in self.pieces:
                    if empty > 0:
                        row += str(empty)
                        empty = 0
                    row += self.pieces[(x, y)]
                else:
                    empty += 1
            if empty > 0:
                row += str(empty)
            board.append(row)
        return f"{'/'.join(board)} {self.current_turn} - - 0 1"

    def reset_history(self):
        """Reset move history."""
        self.move_history = []
        self.position_history = [self.fen()]
        self.move_from_to_history = []

    def debug_palace(self):
        """Debug method for palace validation."""
        pass

    def is_within_palace(self, x, y, is_red):
        """
        Check if a square is within the palace for given color.
        
        Args:
            x: Board x-coordinate
            y: Board y-coordinate
            is_red: True for red palace, False for black palace
            
        Returns:
            True if square is within palace, False otherwise
        """
        if is_red:
            return 3 <= x <= 5 and 7 <= y <= 9
        else:
            return 3 <= x <= 5 and 0 <= y <= 2

    def count_pieces_of_type(self, piece_code):
        """
        Count pieces of a specific type on the board.
        
        Args:
            piece_code: Piece code (e.g., 'K', 'k', 'P', etc.)
            
        Returns:
            Number of pieces of that type
        """
        count = 0
        for piece in self.pieces.values():
            if piece == piece_code:
                count += 1
        return count

    def can_place_piece(self, x, y, piece_code):
        """
        Check if a piece can be placed at given square during setup.
        
        Args:
            x: Board x-coordinate
            y: Board y-coordinate
            piece_code: Piece code to place
            
        Returns:
            Tuple (success, message)
        """
        piece_type = piece_code.lower()
        is_red = piece_code.isupper()
        if piece_type in ['k', 'a']:
            if not self.is_within_palace(x, y, is_red):
                if piece_type == 'k':
                    return False, tr.get("king_outside_palace")
                else:
                    return False, tr.get("advisor_outside_palace")
        if piece_type == 'k':
            for (px, py), p in self.pieces.items():
                if p.lower() == 'k' and p.isupper() == is_red:
                    return False, tr.get("king_already_exists")
        max_allowed = self.max_pieces.get(piece_code, 0)
        current_count = self.count_pieces_of_type(piece_code)
        if current_count >= max_allowed:
            if piece_type == 'p':
                return False, tr.get("max_pawns_reached")
            elif piece_type == 'c':
                return False, tr.get("max_cannons_reached")
            elif piece_type in ['a', 'b', 'n', 'r']:
                return False, tr.get("max_pieces_reached")
        if (x, y) in self.pieces:
            return False, tr.get("square_occupied")
        return True, "OK"

    def remove_piece(self, x, y):
        """
        Remove a piece from the board during setup.
        
        Args:
            x: Board x-coordinate
            y: Board y-coordinate
            
        Returns:
            Tuple (success, message)
        """
        if (x, y) in self.pieces:
            piece = self.pieces[(x, y)]
            if piece.lower() == 'k':
                return False, tr.get("cannot_remove_king")
            del self.pieces[(x, y)]
            self.draw_pieces()
            return True, "OK"
        return False, tr.get("no_piece_on_square")

    def place_piece(self, x, y, piece_code):
        """
        Place a piece on the board during setup.
        
        Args:
            x: Board x-coordinate
            y: Board y-coordinate
            piece_code: Piece code to place
            
        Returns:
            Tuple (success, message)
        """
        can_place, message = self.can_place_piece(x, y, piece_code)
        if not can_place:
            return False, message
        self.pieces[(x, y)] = piece_code
        self.draw_pieces()
        return True, "OK"

    def is_position_valid(self):
        """
        Check if current position is valid (both kings present, piece counts correct, etc.).
        
        Returns:
            Tuple (valid, message)
        """
        has_red_king = False
        has_black_king = False
        for piece in self.pieces.values():
            if piece == 'K':
                has_red_king = True
            elif piece == 'k':
                has_black_king = True
        if not has_red_king or not has_black_king:
            return False, tr.get("both_kings_required")
        for piece_code, max_count in self.max_pieces.items():
            current_count = self.count_pieces_of_type(piece_code)
            if current_count > max_count:
                piece_type = piece_code.lower()
                if piece_type == 'p':
                    return False, tr.get("max_pawns_reached")
                elif piece_type == 'c':
                    return False, tr.get("max_cannons_reached")
                else:
                    return False, tr.get("max_pieces_reached")
        for (x, y), piece in self.pieces.items():
            piece_type = piece.lower()
            is_red = piece.isupper()
            if piece_type in ['k', 'a']:
                if not self.is_within_palace(x, y, is_red):
                    if piece_type == 'k':
                        return False, tr.get("king_outside_palace")
                    else:
                        return False, tr.get("advisor_outside_palace")
        return True, "OK"
