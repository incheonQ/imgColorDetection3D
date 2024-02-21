from PIL import Image, ImageTk
import tkinter as tk
import tkinter.ttk
from tkinter import filedialog
import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import threading

def clearFrame(frame): # https://stackoverflow.com/questions/15781802/python-tkinter-clearing-a-frame
    for widget in frame.winfo_children():
        widget.destroy()

def rgb_to_hex(rgb):
    r, g, b = rgb
    r, g, b = int(r), int(g), int(b)
    return '#' + hex(r)[2:].zfill(2) + hex(g)[2:].zfill(2) + hex(b)[2:].zfill(2)

def CompressImage(img, q):
    updateSys(f"[System] 이미지가 너무 커서 압축할게요!")
    width, height = img.size
    new_size = (width//q, height//q)
    img = img.resize(new_size)
    updateSys(f"[System] 원본 이미지 : {(width, height)} \t압축된 이미지 : {new_size}")
    return img

def CheckImage(img):         ########################### 작동 안함 ❗❗❗ ###########################
    # 이미지를 화면에 표시
    pass 

def ImageUpload():
    global img
    
    btn_ImageUpload.config(bg='#DAA520')
    
    # 이미지 업로드
    img_path = filedialog.askopenfilenames(initialdir='./', title='파일을 선택해주세요.', filetypes=[("png", "*.png *.jpeg *.jpg")])
    img = Image.open(img_path[0])
    
    # 너무 큰 이미지 사이즈 줄이기
    if img.height * img.width > 100000:
        q = round(max(img.height, img.width) / 1000)
        if q > 1:
            img = CompressImage(img, q)
    
    # 이미지 RGB 값만 남기기
    img = img.convert('RGB')
    
    # 이미지 확인
    CheckImage(img)
    
    btn_ImageUpload.config(bg='#32CD32')
    
def updateProgress(i, n):
    currProgress.set( (i+1) / n * 100)
    progressbar.update()
    
# def updateSystem(txt): ######### 미사용 ❗❗❗ #########
#     curr = currSystem.get() + f'\n{txt}'
#     currSystem.set(curr)
#     lbl_System.update()
    
def updateSys(txt):
    txt_System.config(state=tk.NORMAL)
    txt_System.insert(tk.END, txt+'\n')
    txt_System.update()
    txt_System.config(state=tk.DISABLED)

def KMeansTheBestNumberofClusters(df, cluster_min=2, cluster_max=7, random_state=27):
    score_dict = {}
    for i, k in enumerate(range(cluster_min, cluster_max+1)):
        kmeans = KMeans(n_clusters=k, random_state=random_state).fit(df)
        try:
            silhouette_avg = silhouette_score(df, kmeans.labels_)
            score_dict[k] = silhouette_avg
        except:
            break
        updateSys(f'[System] # of cluster : {k} \tSilhouette index {silhouette_avg}') 
        
        # updateProgress(i, cluster_max+1 - cluster_min) ######### 미사용 ❗❗❗ #########
    
    the_best_number_of_clusters = [k for k, v in score_dict.items() if v == max(score_dict.values())][0]
    
    return the_best_number_of_clusters

def colorExpression(color_list):
    for i, color in enumerate(color_list):
        globals()[f'lbl_{i}'] = tk.Label(frame_result, text=color, bg=color, width=10, height=3)
        globals()[f'lbl_{i}'].pack()

def ExtractRepresentativeColors():
    clearFrame(frame_result)
    btn_ExtractRepresentativeColors.config(bg="#DAA520")
    
    img_arr = np.array(img)
    
    # 고유값 추출
    updateSys('[System] 고유값 추출중...') 
    uniq = np.unique(img_arr.reshape(img_arr.shape[0]*img_arr.shape[1], 3), axis=0) # [:,:,0:-1]
    updateSys(f'[System] {uniq.shape[0]}개 고유값 추출 완료!') 
    
    df = pd.DataFrame(uniq, columns=['R', 'G', 'B'])
    
    # KMeans Clustering으로 비슷한 색끼리 군집화
    if combobox.get() == '최적화':
        updateSys("[System] 최적의 군집 갯수 구하는 중...") 
        n_clusters = KMeansTheBestNumberofClusters(df)
        updateSys(f"[System] 최적의 군집 갯수는 {n_clusters}개입니다!") 
        
    else:
        n_clusters = int(combobox.get())
    updateSys(f"[System] {n_clusters}개의 군집 생성 중...") 
    kmeans = KMeans(n_clusters=n_clusters, random_state=27).fit(df)
    df['label'] = kmeans.labels_
    
    label_RGB = df.groupby('label').mean()
    label_RGB = label_RGB.apply(round)
    
    hexx_list = [rgb_to_hex(label_RGB.iloc[i].tolist()) for i in label_RGB.index]
    updateSys(f"[System] 입력하신 이미지의 대표색은 다음과 같습니다!") 
    
    colorExpression(hexx_list)
    btn_ExtractRepresentativeColors.config(bg="#32CD32")

win = tk.Tk()
win.geometry("600x800")
win.title("Extract Representative Colors from Image")

# currProgress = tk.DoubleVar()
# progressbar=tkinter.ttk.Progressbar(win, maximum=100, mode="determinate", variable=currProgress)
# progressbar.pack()

frame_top = tk.Frame(win)
frame_top.pack(side='top', anchor='w')

frame_control = tk.Frame(win, relief='solid', bd=2)
frame_control.pack(side='top', anchor='e')

frame_system = tk.Frame(win, relief='solid', bd=2)
frame_system.pack(side='top')

frame_result = tk.Frame(win, relief='solid', bd=2)
frame_result.pack(side='bottom', anchor='e')

logo = tk.PhotoImage(file="./img/logo2.png", master=frame_top)
lbl_logo = tk.Label(frame_top, image=logo)
lbl_logo.pack(side='left')

btn_ImageUpload = tk.Button(frame_control, text="이미지 선택", command=ImageUpload)
btn_ImageUpload.pack(side='left')

values=['최적화', 2, 3, 4, 5, 6, 7, 8, 9, 10] 
combobox=tkinter.ttk.Combobox(frame_control, width=5, values=values)
combobox.set("최적화")
combobox.pack(side='left')

btn_ExtractRepresentativeColors = tk.Button(frame_control, text="대표색 추출", command=ExtractRepresentativeColors)
btn_ExtractRepresentativeColors.pack(side='left')

# currSystem = tk.StringVar() ######### 미사용 ❗❗❗ #########
# currSystem.set('[System] 안녕하세요!')
# lbl_System = tk.Label(frame_system, textvariable=currSystem)
# lbl_System.pack()

lbl_image = tk.Label(text='image')
lbl_image.pack(side='left')

scrollbar=tk.Scrollbar(frame_system)
scrollbar.pack(side="right", fill="y")

txt_System = tk.Text(frame_system, width=100, height=10, yscrollcommand=scrollbar.set)
scrollbar["command"]=txt_System.yview
txt_System.insert(tk.CURRENT, '[System] 안녕하세요!\n')
txt_System.config(state=tk.DISABLED)
txt_System.pack()

win.mainloop()
