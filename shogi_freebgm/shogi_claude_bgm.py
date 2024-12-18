import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

import pygame

# Pygameの初期化
pygame.mixer.init()

# BGMの読み込み
bgm = pygame.mixer.Sound("hanamatsuri.mp3")  # BGMのファイル名を指定

# BGMをループ再生
bgm.play(-1)  # -1は無限ループ




class ShogiGame:
    def __init__(self, master)
        self.master = master
        self.master.title("将棋")
        self.canvas = tk.Canvas(self.master, width=1000, height=440, bg="#F0DCBA")  # ウィンドウ幅を1500に拡大
        self.canvas.pack()

         # move_logを初期化
        self.move_log = tk.Text(master, height=10, width=50)  # テキストボックスのサイズを調整
        self.move_log.pack()

        self.board = {}

        self.piece_count = {  # 駒のカウント用の辞書
            '歩': 0,
            '香': 0,
            '桂': 0,
            '銀': 0,
            '金': 0,
            '角': 0,
            '飛': 0,
            '王': 0,
            '玉': 0,
            '反歩': 0,
            '反香': 0,
            '反桂': 0,
            '反銀': 0,
            '反金': 0,
            '反角': 0,
            '反飛': 0,
            '反王': 0,
            '反玉': 0,
        }
        self.update_piece_count_display()  # 初期の駒のカウント表示


        self.captured_pieces = []  # 取った駒を保存するリスト
        self.captured_canvas = tk.Canvas(self.master, width=80, height=440, bg="#D0B090")
        self.captured_canvas.place(x=700, y=10)  # 駒台の位置を設定
            # 駒台の描画（左はそのまま、右を調整）
        self.canvas.create_rectangle(5, 10, 35, 430, fill="#D0B090", outline="black")  # 左の駒台
        self.canvas.create_rectangle(430, 10, 440, 430, fill="#D0B090", outline="black")  # 右の駒台


        self.load_images()
        self.create_board()
        self.place_pieces()

        

        self.selected_piece = None
        self.selection_rect = None  # 選択時の枠
        self.canvas.bind("<Button-1>", self.on_click)

        self.is_turn_red = True  # 赤のターンが最初
        self.turn_label = tk.Label(self.master, text="赤(上)のターン", font=("Arial", 16))
        self.turn_label.pack(side=tk.TOP, pady=10)  # 上部に配置

    def can_select_piece(self, piece): #ターンによって選択できる駒を制限
        if self.is_turn_red and "反" not in self.canvas.gettags(piece)[0]:
            return True
        elif not self.is_turn_red and "反" in self.canvas.gettags(piece)[0]:
            return True
        return False

    def update_turn_display(self):
        if self.is_turn_red:
            self.turn_label.config(text="赤(上)のターン")  # 赤のターン
        else:
            self.turn_label.config(text="黒(下)のターン")  # 黒のターン


    def load_images(self): #画像の読み込み
        self.images = {}
        pieces = ['歩', '香', '桂', '銀', '金', '角', '飛', '王', '玉']
        for piece in pieces:
            self.images[piece] = ImageTk.PhotoImage(Image.open(f"{piece}.png").resize((40, 40)))
            self.images[f"反{piece}"] = ImageTk.PhotoImage(Image.open(f"{piece}.png").resize((40, 40)).rotate(180))

    def create_board(self): #盤面の作成

        for i in range(9):
            for j in range(9):
                x, y = i * 40 + 40, j * 40 + 40
                self.canvas.create_rectangle(x, y, x + 40, y + 40, outline="black")

        # 符号を描画
        for i in range(9):
            # 縦の符号（1〜9）
            self.canvas.create_text(420, (i ) * 40 + 60, text=str(i + 1), font=("Arial", 12))
            # 横の符号（一〜九）
            kanji = ["一", "二", "三", "四", "五", "六", "七", "八", "九"]
            self.canvas.create_text( i * 40 + 60, 20, text=kanji[i], font=("Arial", 12))  # 漢字を配列で指定

    def place_pieces(self): #駒の配置
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

        self.board = {}
        for i, row in enumerate(initial_board):
            for j, piece in enumerate(row):
                if piece != '　':

                     # 駒のカウントを更新
                    self.piece_count[piece] += 1

                    x, y = j * 40 + 40, i * 40 + 40  # 盤のマスの中央に駒を配置
                    self.board[(i, j)] = self.canvas.create_image(x + 20, y + 20, image=self.images[piece], tags=piece)
                                       
    def on_click(self, event): #クリック時の処理
        col = (event.x - 40) // 40
        row = (event.y - 40) // 40

        if 0 <= row < 9 and 0 <= col < 9:
            if self.selected_piece:
                self.move_piece(row, col)
            else:
                self.select_piece(row, col)

#先手、後手　#駒の選択
    def select_piece(self, row, col): 
        piece = self.board.get((row, col))
        if piece:
            if self.can_select_piece(piece):  # 駒を選べるかチェック
                self.selected_piece = (row, col)
                x, y = col * 40 + 60, row * 40 + 60
                self.selection_rect = self.canvas.create_rectangle(x - 20, y - 20, x + 20, y + 20, outline="red", width=2)
            else:
                messagebox.showwarning("無効な選択", "その駒は選択できません。")

#駒の移動が有効かどうか
    def is_valid_move(self, piece, old_pos, new_pos): 
        old_row, old_col = old_pos
        new_row, new_col = new_pos

        if piece in ['歩', '反歩']:  # 歩
            if piece == '歩':
                return new_row == old_row + 1 and new_col == old_col  # 前に1マス
            else:
                return new_row == old_row - 1 and new_col == old_col  # 反歩は後ろに1マス
        elif piece in ['香', '反香']:  # 香車
            return old_col == new_col and new_row > old_row  # 縦に何マスでも
        elif piece in ['桂', '反桂']:  # 桂馬
            return (abs(new_row - old_row), abs(new_col - old_col)) == (2, 1) or (abs(new_row - old_row), abs(new_col - old_col)) == (1, 2)
        elif piece in ['銀', '反銀']:  # 銀
            return (abs(new_row - old_row) == 1 and abs(new_col - old_col) <= 1)  # 1マス斜めまたは前に
        elif piece in ['金', '反金']:  # 金
            return (abs(new_row - old_row) <= 1 and abs(new_col - old_col) <= 1)  # 1マス周囲
        elif piece in ['角', '反角']:  # 角
            return abs(new_row - old_row) == abs(new_col - old_col)  # 斜めに
        elif piece in ['飛', '反飛']:  # 飛車
            return old_row == new_row or old_col == new_col  # 縦か横に
        elif piece in ['王', '反玉']:  # 王将または玉
            return abs(new_row - old_row) <= 1 and abs(new_col - old_col) <= 1  # 1マス周囲

        return False  # 有効な移動でない場合


# 取った駒を表示   
    def display_captured_piece(self, piece): 
        self.captured_pieces.append(piece)  # 取った駒をリストに追加
        self.update_captured_display()  # 駒台を更新
# 駒台の更新    
    def update_captured_display(self): 

        self.captured_canvas.delete("all")  # 既存の駒台をクリア
        for index, piece in enumerate(self.captured_pieces):
            self.captured_canvas.create_image(40, 20 + index * 40, image=self.images[piece])  # 駒を表示


 # 駒のカウント表示を更新
    def update_piece_count_display(self):
        self.piece_count_display = tk.Label(self.master, text=self.get_piece_count_text(), font=("Arial", 8))
        self.piece_count_display.place(x=450,y=20)  # 右側に配置
        self.piece_count_display.config(text=self.get_piece_count_text())  # 直接テキストを設定

 # 駒のカウントをテキストで取得
    def get_piece_count_text(self):
            
        count_text = "駒台:\n"  # 初めのテキストを設定し、改行を追加
        for piece, count in self.piece_count.items():
            count_text += f"{piece}: {count}\n"  # 駒ごとに改行を追加
        return count_text

# 棋譜を記録
    def record_move(self, old_row, old_col, new_row, new_col):
            # 棋譜の更新
        piece_name = self.canvas.gettags(self.board.get((new_row, new_col)))[0] if (new_row, new_col) in self.board else '空白'
        move = f"{piece_name}({old_col+1},{old_row+1})→({new_col+1},{new_row+1})"
        self.move_log.insert(tk.END, move + "\n")  # テキストボックスに追加


# 棋譜を表示
    def update_move_list_display(self):
        self.move_list_display.delete(1.0, tk.END)  # テキストボックスをクリア
        indented_moves = '\n'.join(f"  {move}" for move in self.moves)  # インデントを追加
        self.move_list_display.insert(tk.END, indented_moves)  # 棋譜を表示


    def move_piece(self, row, col): # 駒の移動
            
           
        if (row, col) != self.selected_piece:
            old_row, old_col = self.selected_piece
            piece = self.board.get((old_row, old_col))

            # 移動が有効かチェック
            if not self.is_valid_move(self.canvas.gettags(piece)[0], (old_row, old_col), (row, col)):
                messagebox.showwarning("無効な移動", "その駒はそのようには移動できません。")
                return

            # 移動先の駒を確認
            target_piece = self.board.get((row, col))

            if target_piece:
                # 移動先に駒があれば、その駒を駒台に移動
                captured_piece_name = self.canvas.gettags(target_piece)[0]

                # 取られた駒のカウントを減少させる
                if captured_piece_name in self.piece_count:
                    self.piece_count[captured_piece_name] -= 1  # 駒のカウントを減らす

                self.display_captured_piece(captured_piece_name)  # 取った駒を表示

                # 駒を削除（表示も含めて）
                self.canvas.delete(target_piece)  
                self.board.pop((row, col))  # ボードから削除

            # 駒を移動元から移動先へ移動
            self.board[(row, col)] = piece  # 移動先に駒を追加
            x, y = col * 40 + 60, row * 40 + 60  # 新しい座標
            self.canvas.coords(piece, x, y)

            if self.is_king_captured():
                if self.end_game():
                # BGMを止めたり、ゲーム終了の処理
                    return    

            # 移動元の位置を空にする
            self.board.pop((old_row, old_col))

            # 選択時の枠を削除
            self.canvas.delete(self.selection_rect)  
            self.selected_piece = None

            # ターンを交代
            self.is_turn_red = not self.is_turn_red  
            self.update_turn_display()  
            self.update_piece_count_display()  

            # 棋譜を更新
            self.record_move(old_row, old_col, row, col)  # 移動を記録
   
        

    
     # 王または玉が取られたかどうか
    def is_king_captured(self):
                
        if self.piece_count['王'] == 0 or self.piece_count['反玉'] == 0:
            bgm.stop()  # BGMを停止
            return True
        return False

    

    def end_game(self): # ゲーム終了
        self.canvas.unbind("<Button-1>")  # クリックでの駒移動を無効化
        messagebox.showinfo("ゲーム終了", "王が取られました。ゲーム終了です。")
        self.master.quit()  # ウィンドウを閉じる場合

    

if __name__ == "__main__": # メイン関数
    root = tk.Tk()
    game = ShogiGame(root)
    root.mainloop()
   
