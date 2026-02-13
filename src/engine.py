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
        
        # Determine base path and find engine
        self.engine_path = self.find_engine(engine_path)

    def get_base_path(self):
        """
        Determine the base path for the application.
        Works both for script and for frozen executable.
        
        Returns:
            Base path as string
        """
        if getattr(sys, 'frozen', False):
            # If the application is frozen (compiled to exe)
            return os.path.dirname(sys.executable)
        else:
            # If running as script, get the directory containing this file
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
        project_root = os.path.dirname(base_path)  # Go up one level from src/
        
        # List of possible engine locations
        possible_paths = [
            # Absolute path from constructor
            default_path if os.path.isabs(default_path) else None,
            
            # In the same directory as this script (src folder)
            os.path.join(base_path, "fairy-stockfish.exe"),
            os.path.join(base_path, "fairy-stockfish"),
            os.path.join(base_path, "stockfish.exe"),
            os.path.join(base_path, "stockfish"),
            
            # In the project root (one level up)
            os.path.join(project_root, "fairy-stockfish.exe"),
            os.path.join(project_root, "fairy-stockfish"),
            os.path.join(project_root, "stockfish.exe"),
            os.path.join(project_root, "stockfish"),
            
            # In an engine folder in project root
            os.path.join(project_root, "engine", "fairy-stockfish.exe"),
            os.path.join(project_root, "engine", "fairy-stockfish"),
            
            # In an engine folder in src
            os.path.join(base_path, "engine", "fairy-stockfish.exe"),
            os.path.join(base_path, "engine", "fairy-stockfish"),
            
            # In current working directory
            os.path.join(os.getcwd(), "fairy-stockfish.exe"),
            os.path.join(os.getcwd(), "fairy-stockfish"),
        ]
        
        # Remove None values
        possible_paths = [p for p in possible_paths if p is not None]
        
        # Try each path
        for path in possible_paths:
            if os.path.exists(path):
                if self.debug:
                    print(f"Found engine at: {path}")
                return path
        
        # If not found, return default path and hope for the best
        if self.debug:
            print(f"Engine not found, using default: {default_path}")
        return default_path

    def log(self, msg):
        """Log message (disabled by default)."""
        pass

    def start(self):
        """
        Start the engine process and initialize UCI with MultiPV=2.
        
        Returns:
            True if engine started successfully, False otherwise
        """
        try:
            if not os.path.exists(self.engine_path):
                if self.debug:
                    print(f"Engine not found at: {self.engine_path}")
                return False
            
            if self.debug:
                print(f"Starting engine: {self.engine_path}")
                
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
                        if self.debug:
                            print("Engine ready")
                        return True
                except queue.Empty:
                    continue
            
            return False
            
        except Exception as e:
            if self.debug:
                print(f"Error starting engine: {e}")
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
                if self.debug:
                    print(f"Send: {command}")
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
            except Exception as e:
                if self.debug:
                    print(f"Error sending command: {e}")

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
            if self.debug:
                print("Engine not ready")
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
                            
                            pv_match = re.search(r'pv\s+([a-z][0-9][a-z][0-9])', output)
                            if not pv_match:
                                pv_match = re.search(r'pv\s+([a-z][0-9]{2}[a-z][0-9]{2})', output)
                            if not pv_match:
                                pv_match = re.search(r'pv\s+([a-z0-9]{4,5})', output)
                            
                            if pv_match:
                                move = pv_match.group(1)
                                
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
                            time.sleep(0.5)
                            break
                            
                except queue.Empty:
                    continue
            
            for i in range(1, multipv+1):
                if i in mpv_results:
                    results.append(mpv_results[i])
                elif i == 1 and bestmove:
                    results.append((bestmove, "0.00"))
                else:
                    results.append((None, None))
            
            while len(results) < multipv:
                results.append((None, None))
            
            return results[:multipv]
            
        except Exception as e:
            if self.debug:
                print(f"Error in analyze_multi: {e}")
            return [(None, None)] * multipv

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
            if self.debug:
                print(f"Error in analyze: {e}")
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
            if self.debug:
                print("Engine closed")