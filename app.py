import tkinter as tk
import time
import threading

from recognition import recognize

root = tk.Tk()
root.title("タイトル")
root.resizable(True, True)
root.geometry("1200x400")

dictionary = [
    set(['おはよう', 'おはようございます']),
    set(['こんにちは', '今日は']),
    set(['今晩は', 'こんばんは']),
    set(['じゃあね', 'さようなら']),
    set(['あなたの名前は何ですか', 'あなの名前を教えて', '名前を教えて', '名前教えて'])
]

messages = [
    'おはよう',
    'こんにちは!',
    'こんばんは！',
    'じゃあね〜',
    '秘密♡',
    "すみません、よく聞こえませんでした"
]

def get_message(text):
    '''
    認識したテキストに対する応答メッセージを取得
    '''
    for m, s in zip(messages, dictionary):
        if text in s:
            return m
    
    return messages[-1]

def is_unknown(message):
    '''
    未対応のメッセージかどうか
    '''
    return message == messages[-1]

def get_text_from_speech(event):
    '''
    音声認識を起動して認識したテキストを取得する
    '''
    time.sleep(0.3)
    recognized_text = recognize()
    message = get_message(recognized_text)
    progress = []
    wait_counts = 4
    for i in range(1, wait_counts+1):
        if i == wait_counts:
            progress += "❓" if is_unknown(message) else "❗"
        else:
            progress += "."
        labels[0]['text'] = " ".join(progress)
        time.sleep(0.8)
        
    if is_unknown(message):
        labels[0]['text']  = recognized_text + "...❓❓❓"
    else:
        labels[0]['text'] = message
    
    return

def callback(event):
    '''
    別スレッドで計算するためのラッパー
    '''
    # 別スレッドで実行
    labels[0]['text'] = "話しかけてください"
    th = threading.Thread(target=get_text_from_speech, args=(event,))
    th.start()


labels = []
label = tk.Label(root, text="", font=("System", 60)); labels.append(label)
labels[0]['text'] = ""
    

# クリック時音声認識を開始するボタン
button = tk.Button(root, text="話す", font=("System", 16))
button.bind("<ButtonPress>", callback)
for label in labels:
    label.pack(expand = True)

button.pack(expand = True)

# run app
root.mainloop()