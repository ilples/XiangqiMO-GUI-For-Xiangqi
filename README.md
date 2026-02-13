# XiangqiMO

XiangqiMO is a graphical interface program for analyzing Chinese chess (Xiangqi). It features an interactive board with full Xiangqi rules, position analysis using the Fairy-Stockfish engine, and a manual piece setup mode. The interface supports multiple languages including English, Russian, Chinese, Vietnamese, and Malay.

## Features

- **Interactive Xiangqi Board** — Full implementation of Xiangqi rules with legal move validation
- **Engine Analysis** — Integration with Fairy-Stockfish engine (included) showing two best moves with evaluation
- **Position Setup** — Manual piece placement mode for creating custom positions
- **Move History** — Complete move log with international notation
- **Check/Checkmate Highlighting** — Visual indicators when kings are in danger
- **Multi-language Support** — English, Russian, Chinese, Vietnamese, Malay
- **Board Flipping** — Toggle board orientation for either player's perspective
- **Undo/Reset** — Easy move management


<img width="1493" height="1010" alt="2026-02-13_23-12-51" src="https://github.com/user-attachments/assets/f2865b55-ba33-4ba6-8294-1d994772a50b" />


<img width="1491" height="1007" alt="2026-02-13_23-15-50" src="https://github.com/user-attachments/assets/2fb21138-9c50-4dc8-9faa-a680a5a00336" />




## Installation

### Method 1: Terminal / Command Line

```
# Clone the repository
git clone https://github.com/yourusername/XiangqiMO.git
cd XiangqiMO

# Run the application
python main.py
```

### Method 2: Graphical (No Git Required)

1. **Download the program**
   - Go to the GitHub repository page
   - Click the green "Code" button
   - Select "Download ZIP"
   - Extract the ZIP file to a folder of your choice

2. **Install Python** (if not already installed)
   - Visit [python.org](https://www.python.org/downloads/)
   - Download Python 3.7 or higher
   - During installation, check "Add Python to PATH"

3. **Run the application**
   - Open the folder where you extracted the files
   - Double-click on ```main.py``` or run in terminal:

   ```
     python main.py
   
   ```
## Requirements

- Python 3.7 or higher
- Fairy-Stockfish engine (included in the package)

## Usage

1. **Play** — Simply click on pieces and make moves
2. **Analyze** — Press the ANALYZE button to get engine suggestions
3. **Flip Board** — Toggle perspective with the FLIP BOARD button
4. **Setup Mode** — Click SETUP to manually arrange pieces
5. **Undo** — Press UNDO to revert the last move

______________________________________________________________________________________________________________________________________________________
## Terms of Use

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Credits

- [Fairy-Stockfish](https://github.com/ianfab/fairy-stockfish) — Xiangqi engine (GPL-3.0)
