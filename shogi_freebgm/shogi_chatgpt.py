import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import cshogi

# Pygameの初期化
pygame.mixer.init()

# BGMの読み込み
bgm = pygame.mixer.Sound("hanamatsuri.mp3")  # BGMのファイル名を指定

# BGMをループ再生
bgm.play(-1)  # -1は無限ループ

class ShogiGame:
    def __init__(self, master):
        self.master = master
        self.master.title("将棋")
        self.canvas = tk.Canvas(self.master, width=1000, height=440, bg="#F0DCBA")
        self.canvas.pack()

        # 棋譜エンジン初期化
        self.position = cshogi.Position()

        self.move_log = tk.Text(master, height=10, width=50)  # テキストボックスのサイズを調整
        self.move_log.pack()

        self.board = {}

        self.piece_count = {piece: 0 for piece in [
            '歩', '香', '桂', '銀', '金', '角', '飛', '王', '玉',
            '反歩', '反香', '反桂', '反銀', '反金', '反角', '反飛', '反王', '反玉']
        }

        self.update_piece_count_display()  # 初期の駒のカウント表示
        self.captured_pieces = []  # 取った駒を保存するリスト
        self.captured_canvas = tk.Canvas(self.master, width=80, height=440, bg="#D0B090")
        self.captured_canvas.place(x=700, y=10)  # 駒台の位置を設定

        self.load_images()
        self.create_board()
        self.place_pieces()

        self.selected_piece = None
        self.selection_rect = None  # 選択時の枠
        self.canvas.bind("<Button-1>", self.on_click)

        self.is_turn_red = True  # 赤のターンが最初
        self.turn_label = tk.Label(self.master, text="赤(上)のターン", font=("Arial", 16))
        self.turn_label.pack(side=tk.TOP, pady=10)  # 上部に配置

    def load_images(self):  # 画像の読み込み
        self.images = {piece: ImageTk.PhotoImage(
            Image.open(f"{piece.replace('反', '')}.png").resize((40, 40)).rotate(180 if '反' in piece else 0))
            for piece in ['歩', '香', '桂', '銀', '金', '角', '飛', '王', '玉',
                          '反歩', '反香', '反桂', '反銀', '反金', '反角', '反飛', '反王', '反玉']
        }

    def create_board(self):  # 盤面の作成
        [self.canvas.create_rectangle(i * 40 + 40, j * 40 + 40, i * 40 + 80, j * 40 + 80, outline="black")
         for i in range(9) for j in range(9)]
        kanji = ["一", "二", "三", "四", "五", "六", "七", "八", "九"]
        [self.canvas.create_text(420, i * 40 + 60, text=str(i + 1), font=("Arial", 12)) for i in range(9)]
        [self.canvas.create_text(i * 40 + 60, 20, text=kanji[i], font=("Arial", 12)) for i in range(9)]

    def place_pieces(self):  # 駒の配置
        initial_board = [
            ['香', '桂', '銀', '金', '王', '金', '銀', '桂', '香'],
            ['　', '飛', '　', '　', '　', '　', '　', '角', '　'],
            ['歩', '歩', '歩', '歩', '歩', '歩', '歩', '歩', '歩'],
            ['　', '　', '　', '　', '　', '　', '　', '　', '　'],
            ['　', '　', '　', '　', '　', '　', '　', '　', '　'],
            ['　', '　', '　', '　', '　', '　', '　', '　', '　'],
            ['反歩', '反歩', '反歩', '反歩', '反歩', '反歩', '反歩', '反歩', '反歩'],
            ['　', '反角', '　', '　', '　', '　', '　', '反飛', '　'],
            ['反香', '反桂', '反銀', '反金', '反玉', '反金', '反銀', '反桂', '反香']
        ]

        self.board = {(i, j): self.canvas.create_image(
            j * 40 + 60, i * 40 + 60, image=self.images[piece], tags=piece)
            for i, row in enumerate(initial_board) for j, piece in enumerate(row) if piece != '　'}
        for row in initial_board:
            for piece in row:
                if piece != '　':
                    self.piece_count[piece] += 1

    def on_click(self, event):  # クリック時の処理
        col, row = (event.x - 40) // 40, (event.y - 40) // 40
        if 0 <= row < 9 and 0 <= col < 9:
            self.move_piece(row, col) if self.selected_piece else self.select_piece(row, col)

    def select_piece(self, row, col):
        piece = self.board.get((row, col))
        if piece:
            self.selected_piece = (row, col)
            x, y = col * 40 + 60, row * 40 + 60
            self.selection_rect = self.canvas.create_rectangle(x - 20, y - 20, x + 20, y + 20, outline="red", width=2)

    def move_piece(self, row, col):
        if (row, col) != self.selected_piece:
            old_row, old_col = self.selected_piece
            piece = self.board.get((old_row, old_col))

            # 移動先の駒を確認
            target_piece = self.board.get((row, col))
            if target_piece:
                self.display_captured_piece(self.canvas.gettags(target_piece)[0])
                self.canvas.delete(target_piece)
                self.board.pop((row, col))

            self.board[(row, col)] = piece
            x, y = col * 40 + 60, row * 40 + 60
            self.canvas.coords(piece, x, y)

            self.board.pop((old_row, old_col))
            self.canvas.delete(self.selection_rect)
            self.selected_piece = None

            # ターンを交代
            self.is_turn_red = not self.is_turn_red
            self.update_turn_display()
            self.update_piece_count_display()

    def display_captured_piece(self, piece):
        self.captured_pieces.append(piece)
        self.update_captured_display()

    def update_captured_display(self):
        self.captured_canvas.delete("all")
        [self.captured_canvas.create_image(40, 20 + index * 40, image=self.images[piece])
         for index, piece in enumerate(self.captured_pieces)]

    def update_piece_count_display(self):
        self.piece_count_display = tk.Label(self.master, text=self.get_piece_count_text(), font=("Arial", 8))
        self.piece_count_display.place(x=450, y=20)
        self.piece_count_display.config(text=self.get_piece_count_text())

    def get_piece_count_text(self):
        return "\n".join([f"{piece}: {count}" for piece, count in self.piece_count.items()])

    def update_turn_display(self):
        self.turn_label.config(text="赤(上)のターン" if self.is_turn_red else "黒(下)のターン")

if __name__ == "__main__":
    root = tk.Tk()
    game = ShogiGame(root)
    root.mainloop()
