import subprocess
import time
import os
import threading
import queue
import re
import sys

class StockfishEngine:
    """
    Wrapper class for Fairy-Stockfish chess engine.
    Handles engine communication and analysis with MultiPV support.
    """
    def __init__(self, engine_path="fairy-stockfish.exe"):
        """
        Initialize the engine wrapper.
        
        Args:
            engine_path: Path to the Fairy-Stockfish executable
        """
        self.process = None
        self.ready = False
        self.output_queue = queue.Queue()
        self.reader_thread = None
        self.debug = False
        
        self.engine_path = self.find_engine(engine_path)

    def get_base_path(self):
        """
        Determine the base path for the application.
        Works both for script and for frozen executable.
        
        Returns:
            Base path as string
        """
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def find_engine(self, default_path):
        """
        Find the Fairy-Stockfish engine in various possible locations.
        
        Args:
            default_path: Default engine path from constructor
            
        Returns:
            Path to engine executable or default path if not found
        """
        base_path = self.get_base_path()
        project_root = os.path.dirname(base_path)
        
        engine_variants = [
            "fairy-stockfish.exe",
            "fairy-stockfish",
            "stockfish.exe",
            "stockfish",
            "fairy-stockfish_x86-64.exe",
            "fairy-stockfish-largeboard_x86-64.exe"
        ]
        
        for variant in engine_variants:
            test_path = os.path.join(project_root, "engine", variant)
            if os.path.exists(test_path):
                return test_path
        
        for variant in engine_variants:
            test_path = os.path.join(project_root, variant)
            if os.path.exists(test_path):
                return test_path
        
        for variant in engine_variants:
            test_path = os.path.join(base_path, variant)
            if os.path.exists(test_path):
                return test_path
        
        for variant in engine_variants:
            test_path = os.path.join(os.getcwd(), "engine", variant)
            if os.path.exists(test_path):
                return test_path
        
        for variant in engine_variants:
            test_path = os.path.join(os.getcwd(), variant)
            if os.path.exists(test_path):
                return test_path
        
        return default_path

    def log(self, msg):
        pass

    def start(self):
        """
        Start the engine process and initialize UCI with MultiPV=2.
        
        Returns:
            True if engine started successfully, False otherwise
        """
        try:
            if not os.path.exists(self.engine_path):
                alt_paths = ["fairy-stockfish.exe", "fairy-stockfish", "stockfish.exe", "stockfish"]
                for p in alt_paths:
                    if os.path.exists(p):
                        self.engine_path = p
                        break
                else:
                    return False
            
            self.process = subprocess.Popen(
                self.engine_path,
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.reader_thread = threading.Thread(target=self._reader, daemon=True)
            self.reader_thread.start()
            
            self._send("uci")
            time.sleep(0.5)
            
            while not self.output_queue.empty():
                self.output_queue.get()
            
            self._send("setoption name UCI_Variant value xiangqi")
            time.sleep(0.2)
            self._send("setoption name FairyBoard value xiangqi")
            time.sleep(0.1)
            self._send("setoption name MultiPV value 2")
            time.sleep(0.1)
            self._send("setoption name Threads value 2")
            self._send("setoption name Hash value 128")
            self._send("ucinewgame")
            self._send("isready")
            
            timeout = time.time() + 8
            while time.time() < timeout:
                try:
                    output = self.output_queue.get(timeout=0.2)
                    if "readyok" in output:
                        self.ready = True
                        return True
                except queue.Empty:
                    continue
            
            return False
            
        except Exception as e:
            return False

    def _reader(self):
        """
        Reader thread function that reads engine output and puts it in the queue.
        """
        while self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        self.output_queue.put(line)
            except:
                break

    def _send(self, command):
        """
        Send a command to the engine.
        
        Args:
            command: Command string to send
        """
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
            except Exception as e:
                pass

    def analyze_multi(self, fen, depth=18, multipv=2):
        """
        Analyze position and return multiple best moves with MultiPV.
        
        Args:
            fen: FEN string of the position
            depth: Search depth
            multipv: Number of best moves to return
            
        Returns:
            List of tuples (move, score) for each MultiPV line
        """
        if not self.ready:
            return [(None, None)] * multipv
        
        results = []
        try:
            if not fen or fen == "":
                fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
            
            self._send(f"position fen {fen}")
            time.sleep(0.2)
            
            while not self.output_queue.empty():
                self.output_queue.get()
            
            self._send(f"go depth {depth}")
            
            mpv_results = {}
            bestmove = None
            
            timeout = time.time() + 30
            while time.time() < timeout:
                try:
                    output = self.output_queue.get(timeout=0.5)
                    
                    if "info" in output and "multipv" in output and "pv" in output:
                        mpv_match = re.search(r'multipv\s+(\d+)', output)
                        if mpv_match:
                            mpv = int(mpv_match.group(1))
                            
                            # Try multiple regex patterns for UCI moves
                            move = None
                            
                            # Pattern 1: Standard UCI (e.g., a2a4)
                            pv_match = re.search(r'pv\s+([a-i][0-9][a-i][0-9])', output)
                            if pv_match:
                                move = pv_match.group(1)
                            
                            # Pattern 2: With double digits (e.g., a10a9 for Xiangqi)
                            if not move:
                                pv_match = re.search(r'pv\s+([a-i][0-9]{2}[a-i][0-9]{2})', output)
                                if pv_match:
                                    move = pv_match.group(1)
                            
                            # Pattern 3: Any 4-5 character alphanumeric
                            if not move:
                                pv_match = re.search(r'pv\s+([a-z0-9]{4,5})', output)
                                if pv_match:
                                    move = pv_match.group(1)
                            
                            if move:
                                # Validate move format for Xiangqi
                                if self.is_valid_uci_move(move):
                                    score = "0.00"
                                    cp_match = re.search(r'score cp\s+(-?\d+)', output)
                                    if cp_match:
                                        cp = int(cp_match.group(1))
                                        score = f"{cp/100:.2f}"
                                    else:
                                        mate_match = re.search(r'score mate\s+(-?\d+)', output)
                                        if mate_match:
                                            mate = mate_match.group(1)
                                            score = f"mate {mate}"
                                    
                                    mpv_results[mpv] = (move, score)
                    
                    if "bestmove" in output:
                        parts = output.split()
                        if len(parts) >= 2:
                            bestmove = parts[1]
                            if bestmove == "(none)":
                                bestmove = None
                            time.sleep(0.5)
                            break
                            
                except queue.Empty:
                    continue
            
            # Compile results
            for i in range(1, multipv+1):
                if i in mpv_results:
                    results.append(mpv_results[i])
                elif i == 1 and bestmove and self.is_valid_uci_move(bestmove):
                    results.append((bestmove, "0.00"))
                else:
                    results.append((None, None))
            
            while len(results) < multipv:
                results.append((None, None))
            
            return results[:multipv]
            
        except Exception as e:
            return [(None, None)] * multipv

    def is_valid_uci_move(self, move):
        """
        Validate if a UCI move string is valid for Xiangqi.
        
        Args:
            move: UCI move string
            
        Returns:
            True if valid, False otherwise
        """
        if not move or len(move) < 4:
            return False
        
        try:
            # Extract from and to squares
            if len(move) == 4:
                # Format: a2a4
                from_file = move[0]
                from_rank = move[1]
                to_file = move[2]
                to_rank = move[3]
            elif len(move) == 5:
                # Format: a10a9 (Xiangqi has ranks 1-10)
                from_file = move[0]
                from_rank = move[1:3]
                to_file = move[3]
                to_rank = move[4:6] if len(move) > 5 else move[4]
            else:
                return False
            
            # Check if files are a-i (Xiangqi has 9 files)
            if from_file not in 'abcdefghi' or to_file not in 'abcdefghi':
                return False
            
            # Check if ranks are 1-10
            try:
                from_rank_int = int(from_rank)
                to_rank_int = int(to_rank)
                if from_rank_int < 1 or from_rank_int > 10 or to_rank_int < 1 or to_rank_int > 10:
                    return False
            except ValueError:
                return False
            
            return True
        except:
            return False

    def analyze(self, fen, depth=18):
        """
        Legacy method for single-move analysis.
        
        Args:
            fen: FEN string of the position
            depth: Search depth
            
        Returns:
            Tuple (best_move, score)
        """
        if not self.ready:
            return None, None
        
        try:
            if not fen or fen == "":
                fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
            
            self._send(f"position fen {fen}")
            time.sleep(0.2)
            
            while not self.output_queue.empty():
                self.output_queue.get()
            
            self._send(f"go depth {depth}")
            
            best_move = None
            score = "0.00"
            
            timeout = time.time() + 20
            while time.time() < timeout:
                try:
                    output = self.output_queue.get(timeout=0.5)
                    
                    if "bestmove" in output:
                        parts = output.split()
                        if len(parts) >= 2:
                            best_move = parts[1]
                            if best_move == "(none)":
                                best_move = None
                            break
                    
                    if "score cp" in output:
                        try:
                            cp = output.split("score cp")[1].split()[0]
                            score = str(int(cp) / 100)
                        except:
                            pass
                            
                except queue.Empty:
                    continue
            
            return best_move, score
            
        except Exception as e:
            return None, None

    def close(self):
        """Close the engine process."""
        if self.process:
            try:
                self._send("quit")
                time.sleep(0.5)
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                self.process.kill()
            self.process = None
            self.ready = False
