"""
author: 茉sinn
date: 2024Y4Q-2025Y1Q
demo video 链接: https://pan.baidu.com/s/1SLbR0QGNQ83aFf0wrb5hnw 提取码: fnzc

introduction:
本项目基于tkinter及pygame构建PC端下落式音游MumoMusic ，
共包含三个曲目*三种难度，并可进行延时校正的设置。
游戏通过在正确时间点按下对应位置键盘获得游戏得分，
其中包含六个打击位置pos、tap-touch-hold三种按键note，
并在界面上提醒玩家曲目及难度信息、perfect/good打击特效、连击数、目前得分及进度条，
一曲结束会进行得分结算并评级，用于丰富游戏玩法。

"""

# 导入库
import time
import tkinter as tk
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.font import Font
import pygame
from mutagen.mp3 import *
import sys
import os

# 全局变量--用于参数传递
stts=None
shiftTF=None
fpath="C:/Users/30208/AppData/Local/Programs/Python/Python310/MUMOmusic/"

# SettingPage: 延时校正界面
class SettingPage:
    # 读谱
    def loadrhythm(rhythm):
        with open(rhythm, 'r') as file:
            lines = [line.rstrip('\n').split('\t') for line in file.readlines()]
        for i in range(0, len(lines)):
            lines[i] = [element for element in lines[i] if element]
            lines[i] = [int(item) for item in lines[i]]

        # 5*6个时间序列
        taptime = [lines[0], lines[1], lines[2], lines[3], lines[4], lines[5]]
        return taptime

    # 谱面判定之tap
    def tapcheck(i, tapindex, thistime, tapstate, frame, tapmissTF, pglist):
        if frame in range(thistime-15,thistime-10):
            tapindex+=1
            tapmissTF=False
            tapstate='bad'
        elif frame in range(thistime-10,thistime-5):
            tapindex+=1
            tapmissTF=False
            tapstate='early'
            pglist.append((i, 'g', frame))
        elif frame in range(thistime-5, thistime+5):
            tapindex += 1
            tapmissTF = False
            tapstate='perfect'
            pglist.append((i,'p',frame))
        elif frame in range(thistime+5, thistime+10):
            tapindex += 1
            tapmissTF = False
            tapstate='late'
            pglist.append((i, 'g', frame))
        elif frame >= thistime+10:
            tapindex+=1
            tapstate='miss'
        else:
            tapstate='NA'
            tapmissTF=False
        return tapstate, tapmissTF, tapindex

    # 谱面绘制
    def showrhythm(note,notes,notetime,frame,allframes,x):
        if not notes:
            for t in range(0,len(notetime)):
                time=notetime[t]
                noterect=note.get_rect()
                noterect.x = x
                noterect.y = -20
                notes.append((noterect,time))

    # 谱面动画
    def moverhythm(note,notes,notetime,frame,speed):
        for i,(noterect,starttime) in enumerate(notes):
            if len(notetime)>i and frame-starttime>=-(800/speed):
                noterect.y+=speed
                if noterect.y>800:
                    notes.pop(i)
                    break

    # 全部重置
    def reset(songtimetostart):
        pygame.mixer.music.stop()

        # notes队列--用于showrhythm()
        taps1 = []
        taps2 = []
        taps3 = []
        taps4 = []
        taps5 = []
        taps6 = []

        # int型变量初始化：frame、特效队列pglist
        frame = 0
        tapindex = [0, 0, 0, 0, 0, 0]
        taplastframe = [0, 0, 0, 0, 0, 0]
        pglist = []

        # boolean型变量初始化：missTF
        tapmissTF = [False, False, False, False, False, False]

        # 音符note判定状态state初始化
        tapstate = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA']

        pygame.mixer.music.play(-1, 1.5+songtimetostart / 1000)
        return taps1, taps2, taps3, taps4, taps5, taps6, frame, tapindex, taplastframe, pglist, tapmissTF, tapstate

    #  SettingPage主方法
    def set(songtimetostart,startattention):
        pygame.init()
        setpage = pygame.display.set_mode((1600, 900))

        # 背景图片1background_image1、音符tap、谱面流速speed
        song=fpath+"song/shadowgraph.mp3"
        rhythm=fpath+"rhythm/0.txt"
        background_image1 = pygame.image.load(fpath+"image/SetPage.png").convert_alpha()
        board = pygame.image.load(fpath+"image/board.png").convert_alpha()
        tap = pygame.image.load(fpath+"image/tap.png").convert_alpha()
        speed = 5

        # perfect/good队列pglist贴图
        p=[]
        g=[]
        for i in range (0,30):
            ap=pygame.image.load(fpath+"image/p/"+str(i)+".png").convert_alpha()
            ag=pygame.image.load(fpath+"image/g/"+str(i)+".png").convert_alpha()
            p.append(ap)
            g.append(ag)

        # notes队列--用于showrhythm()
        taps1 = []
        taps2 = []
        taps3 = []
        taps4 = []
        taps5 = []
        taps6 = []
        taptime = SettingPage.loadrhythm(rhythm)

        # int型变量初始化：frame、特效队列pglist
        frame=0
        tapindex = [0, 0, 0, 0, 0, 0]
        taplastframe = [0, 0, 0, 0, 0, 0]
        pglist=[]

        # boolean型变量初始化：missTF
        tapmissTF = [False, False, False, False, False, False]

        # 音符note判定状态state初始化
        tapstate = ['NA','NA','NA','NA','NA','NA']

	    # 需要考虑将SettingPage中的songtimetostart返回至ShowPage，并通过button传入PlayPage
        pygame.mixer.music.load(song)
        clock = pygame.time.Clock()
        pygame.mixer.music.play(-1,1.5+songtimetostart/1000)
        allframes = int(MP3(song).info.length * 60)
        print(allframes)
        tmp=songtimetostart

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if 0 <= x <= 50 and 0 <= y <= 50:
                        print("Stop and Quit.")
                        running=False

                    # 修改延时
                    if 295<=x<=495 and 280<=y<=480:
                        songtimetostart=tmp
                        taps1, taps2, taps3, taps4, taps5, taps6, frame, tapindex, \
                        taplastframe, pglist, tapmissTF, tapstate=SettingPage.reset(songtimetostart)
                    if -1000<=tmp<=1000:
                        if 520 <= x < 585 and 300 <= y <= 360:
                            tmp += 5
                        if 585 <= x < 650 and 300 <= y <= 360:
                            tmp += 20
                        if 650 <= x < 715 and 300 <= y <= 360:
                            tmp += 100
                        if 520 <= x < 585 and 420 <= y <= 480:
                            tmp -= 5
                        if 585 <= x < 650 and 420 <= y <= 480:
                            tmp -= 20
                        if 650 <= x < 715 and 420 <= y <= 480:
                            tmp -= 100
                if event.type == pygame.QUIT:
                    running = False
            if frame==allframes:
                taps1, taps2, taps3, taps4, taps5, taps6, frame, tapindex, \
                taplastframe, pglist, tapmissTF, tapstate=SettingPage.reset(songtimetostart)
            keys_pressed = pygame.key.get_pressed()

            # 开始游戏按shift
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                startattention = False

            #按键判定
            if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_d] or keys_pressed[pygame.K_f] or\
                    keys_pressed[pygame.K_j] or keys_pressed[pygame.K_k] or keys_pressed[pygame.K_l]:
                if frame > taplastframe[4] + 1:
                    tapmissTF[4] = True
                else:
                    tapmissTF[4] = False
                taplastframe[4] = frame

            # tap判定
            for i in range(0,6):
                if tapindex[i]<len(taptime[i]):
                    if tapmissTF[i]:
                        tapstate[i],tapmissTF[i], tapindex[i] = SettingPage.tapcheck(i,tapindex[i],taptime[i][tapindex[i]],tapstate[i],frame, tapmissTF[i], pglist)
                    else:
                        if frame>taptime[i][tapindex[i]]+10:
                            tapindex[i]+=1
                            print(str(i) + " tap miss ")

            # 界面图片更新
            setpage.blit(background_image1, (0, 0))

            # 音符note下落动画
            for i in range(1,7):
                note=eval('tap')
                notes=eval('taps'+str(i))
                notetime=eval('taptime')[i-1]
                SettingPage.showrhythm(note, notes, notetime, frame, allframes, 200*i)
                SettingPage.moverhythm(note, notes, notetime, frame, speed)
                for j, (noterect, starttime) in enumerate(notes):
                    setpage.blit(note,noterect)

            # perfect及good特效动画
            if len(pglist) > 0:
                for i, (pos, porg, arrtime) in enumerate(pglist):
                    if frame - arrtime >= 29:
                        pglist.pop(i)
                    setpage.blit(eval(porg)[frame - arrtime], (150 + pos * 200, 500))

            # 界面文字delaynum
            text_delaynum = pygame.font.SysFont('twcen', 60).render(str(tmp), True, (253, 217, 136))
            text_delaynum_rect = text_delaynum.get_rect(center=(390, 380))
            setpage.blit(text_delaynum, text_delaynum_rect)

            # 判定线贴图
            setpage.blit(board, (0, 0))

            # 游戏开始按shift键，保证按键的识别
            text_startattention = pygame.font.SysFont('twcen', 54).render('Please press SHIFT to start!', True,(253, 217, 136))
            text_startattention_rect = text_startattention.get_rect(center=(800, 400))
            if startattention:
                setpage.blit(text_startattention, text_startattention_rect)

            pygame.display.flip()
            frame+=1
            clock.tick(60)

        pygame.quit()
        global stts
        stts=songtimetostart
        global shiftTF
        shiftTF=startattention
        return songtimetostart,startattention

# PlayPage: 游戏界面
class PlayPage:
    # 选择对应的歌曲库&谱面库
    def whichmusic(music):
        if music == "music1EZ":
            # 对应的歌曲mp3
            song=fpath+"song/INFINITY.mp3"
            # 对应的谱面txt
            rhythm=fpath+"rhythm/1.txt"
            # 对应的谱面流速
            speed=15 # EZ为15，HD为20，IN为25
            songname='Infinity'
            songrank='EZ'
        elif music == "music1HD":
            # 对应的歌曲mp3
            song=fpath+"song/INFINITY.mp3"
            # 对应的谱面txt
            rhythm=fpath+"rhythm/1.txt"
            # 对应的谱面流速
            speed=20 # EZ为15，HD为20，IN为25
            songname='Infinity'
            songrank='HD'
        elif music == "music1IN":
            # 对应的歌曲mp3
            song=fpath+"song/INFINITY.mp3"
            # 对应的谱面txt
            rhythm=fpath+"rhythm/1.txt"
            # 对应的谱面流速
            speed=25 # EZ为15，HD为20，IN为25
            songname='Infinity'
            songrank='IN'
        elif music == "music2EZ":
            # 对应的歌曲mp3
            song=fpath+"song/LEYI.mp3"
            # 对应的谱面txt
            rhythm=fpath+"rhythm/2.txt"
            # 对应的谱面流速
            speed=15 # EZ为15，HD为20，IN为25
            songname='LeYi'
            songrank='EZ'
        elif music == "music2HD":
            # 对应的歌曲mp3
            song=fpath+"song/LEYI.mp3"
            # 对应的谱面txt
            rhythm=fpath+"rhythm/2.txt"
            # 对应的谱面流速
            speed=20 # EZ为15，HD为20，IN为25
            songname='LeYi'
            songrank='HD'
        elif music == "music2IN":
            # 对应的歌曲mp3
            song=fpath+"song/LEYI.mp3"
            # 对应的谱面txt
            rhythm=fpath+"rhythm/2.txt"
            # 对应的谱面流速
            speed=25 # EZ为15，HD为20，IN为25
            songname='LeYi'
            songrank='IN'
        elif music == "music3EZ":
            # 对应的歌曲mp3
            song=fpath+"song/MONSTER.mp3"
            # 对应的谱面txt
            rhythm=fpath+"rhythm/3.txt"
            # 对应的谱面流速
            speed=15 # EZ为15，HD为20，IN为25
            songname='Monster'
            songrank='EZ'
        elif music == "music3HD":
            # 对应的歌曲mp3
            song=fpath+"song/MONSTER.mp3"
            # 对应的谱面txt
            rhythm=fpath+"rhythm/3.txt"
            # 对应的谱面流速
            speed=20 # EZ为15，HD为20，IN为25
            songname='Monster'
            songrank='HD'
        else:
            # 对应的歌曲mp3
            song=fpath+"song/MONSTER.mp3"
            # 对应的谱面txt
            rhythm=fpath+"rhythm/3.txt"
            # 对应的谱面流速
            speed=25 # EZ为15，HD为20，IN为25
            songname='Monster'
            songrank='IN'
        return song,rhythm,speed,songname,songrank

    # 谱面读取
    def loadrhythm(rhythm,speed):
        with open(rhythm, 'r') as file:
            lines = [line.rstrip('\n').split('\t') for line in file.readlines()]
        for i in range(0, len(lines)):
            lines[i] = [element for element in lines[i] if element]
            lines[i] = [int(item) for item in lines[i]]

        # 5*6个时间序列
        taptime = [lines[0], lines[1], lines[2], lines[3], lines[4], lines[5]]
        touchtime = [lines[6], lines[7], lines[8], lines[9], lines[10], lines[11]]
        holdstarttime = [lines[12], lines[13], lines[14], lines[15], lines[16], lines[17]]
        holdendtime = [lines[18], lines[19], lines[20], lines[21], lines[22], lines[23]]
        holdtime=[0,0,0,0,0,0]
        for i in range(0,6):
            holdtime[i]=[]
            for j in range(0,len(holdstarttime[i])):
                for k in range(holdstarttime[i][j],holdendtime[i][j],300//speed):
                    holdtime[i].append(k)
        return taptime,touchtime,holdtime,holdstarttime,holdendtime

    # 谱面判定之tap
    def tapcheck(i, tapindex, thistime, tapstate, frame,\
             badcore, earlycore, perfectcore, latecore, misscore,\
             combo, allcombo, tapmissTF, pglist):
        if frame in range(thistime-15,thistime-10):
            allcombo.append(combo)
            combo=0
            badcore+=1
            tapindex+=1
            tapmissTF=False
            tapstate='bad'
            print(str(tapindex)+" tap bad "+str(badcore))
        elif frame in range(thistime-10,thistime-5):
            combo+=1
            earlycore+=1
            tapindex+=1
            tapmissTF=False
            tapstate='early'
            pglist.append((i, 'g', frame))
            print(str(tapindex)+" tap early "+str(earlycore))
        elif frame in range(thistime-5, thistime+5):
            combo += 1
            perfectcore += 1
            tapindex += 1
            tapmissTF = False
            tapstate='perfect'
            pglist.append((i,'p',frame))
            print(str(tapindex)+" tap perfect "+str(perfectcore))
        elif frame in range(thistime+5, thistime+10):
            combo += 1
            latecore += 1
            tapindex += 1
            tapmissTF = False
            tapstate='late'
            pglist.append((i, 'g', frame))
            print(str(tapindex)+" tap late "+str(latecore))
        elif frame >= thistime+10:
            allcombo.append(combo)
            combo=0
            misscore+=1
            tapindex+=1
            tapstate='miss'
            print(str(tapindex)+" tap miss "+str(misscore))
        else:
            tapstate='NA'
            tapmissTF=False
        return combo, badcore, earlycore, perfectcore, latecore, misscore, tapstate, tapmissTF, tapindex

    # 谱面判定之touch
    def touchcheck(i, touchindex, thistime, touchstate, frame, \
                 badcore, earlycore, perfectcore, latecore, misscore, \
                 combo, allcombo, touchmissTF, pglist):
        if frame in range(thistime - 5, thistime + 5):
            combo += 1
            perfectcore += 1
            touchindex += 1
            touchmissTF = False
            touchstate='perfect'
            pglist.append((i, 'p', frame))
            print(str(touchindex) + " touch perfect "+str(perfectcore))
        elif frame >= thistime + 5:
            allcombo.append(combo)
            combo = 0
            misscore += 1
            touchindex += 1
            touchstate='miss'
            print(str(touchindex) + " touch miss"+str(misscore))
        else:
            touchstate='NA'
            touchmissTF = False
        return combo, badcore, earlycore, perfectcore, latecore, misscore, touchstate, touchmissTF, touchindex

    # 谱面判定之hold
    def holdcheck(i,holdindex, lastholdindex, starttime, endtime, holdstate, frame, lastframe,\
             badcore, earlycore, perfectcore, latecore, misscore,\
             combo, allcombo, holdmissTF,holdstartTF, pglist):
        holdmissTF = False
        if not holdstartTF:
            lastframe=frame
            lastholdindex=holdindex
            if frame in range(starttime-15,starttime-10):
                allcombo.append(combo)
                combo=0
                badcore+=1
                holdindex+=1
                holdstate = 'NA'
                print(str(holdindex) + " hold bad " +str(badcore))
            elif frame in range(starttime-10,starttime-5):
                holdstartTF = True
                holdstate='early'
                pglist.append((i, 'g', frame))
            elif frame in range(starttime-5, starttime+5):
                holdstartTF = True
                holdstate = 'perfect'
                pglist.append((i, 'p', frame))
            elif frame in range(starttime+5, starttime+10):
                holdstartTF = True
                holdstate = 'late'
                pglist.append((i, 'g', frame))
            elif frame >= starttime+10:
                allcombo.append(combo)
                combo=0
                misscore+=1
                holdindex+=1
                holdstate = 'NA'
                print(str(holdindex) + " hold miss(too late press) "+str(misscore))
            else:
                holdmissTF=False
        else:
            if (frame!=lastframe+1)and(frame<=endtime):
                allcombo.append(combo)
                combo = 0
                misscore += 1
                holdindex += 1
                holdstate = 'NA'
                print(str(holdindex) + " hold miss(not continue to press)"+str(misscore))
            elif (frame==lastframe+1)and(frame<endtime):
                lastframe=frame
                lastholdindex=holdindex
            elif (frame==lastframe+1)and(frame==endtime):
                if holdstate=='early':
                    combo+=1
                    earlycore+=1
                    holdindex+=1
                    holdstartTF=False
                    holdstate='NA'
                    print(str(holdindex) + " hold early"+str(earlycore))
                elif holdstate=='perfect':
                    combo+=1
                    perfectcore += 1
                    holdindex += 1
                    holdstartTF = False
                    holdstate = 'NA'
                    print(str(holdindex) + " hold perfect"+str(perfectcore))
                elif holdstate=='late':
                    combo+=1
                    latecore += 1
                    holdindex += 1
                    holdstartTF = False
                    holdstate = 'NA'
                    print(str(holdindex) + " hold late"+str(latecore))
                else:
                    holdmissTF=False
        return combo, badcore, earlycore, perfectcore, latecore, misscore, holdstate, holdmissTF, holdstartTF, holdindex, lastframe, lastholdindex

    # 分数计算score
    def Score(badcore, earlycore, perfectcore, latecore, misscore, H, T):
        score=int((1/(H+T)*perfectcore+((1/(H+T))-(1/(4*H)))*(earlycore+latecore))*1000000)
        if perfectcore==H+T:
            score=1000000
            rank='MM'
        elif score in range(950000,1000000):
            rank='M'
        elif score in range(900000, 950000):
            rank = 'S'
        elif score in range(850000, 900000):
            rank = 'A'
        elif score in range(800000, 850000):
            rank = 'B'
        elif score in range(750000, 800000):
            rank = 'C'
        else:
            rank = 'F'
        return score,rank

    # 谱面绘制
    def showrhythm(note,notes,notetime,frame,x,y):
        if not notes:
            for time in notetime:
                noterect=note.get_rect()
                noterect.x = x
                noterect.y = y
                notes.append((noterect,time))

    # 谱面动画
    def moverhythm(note,notes,notetime,frame,speed):
        for i,(noterect,starttime) in enumerate(notes):
            if len(notetime)>i and frame-starttime>=-(800/speed):
                noterect.y+=speed
                if noterect.y>800:
                    notes.pop(i)
                    break

    # PlayPage主方法
    def play(music,songtimetostartt,startattention):
        pygame.init()
        playpage = pygame.display.set_mode((1600, 900))
        pygame.display.set_caption(music)

        # 背景图片1background_image1、进度条progressbar、得分条scorebar、音符taptouchhold、结算页面songscore、backgroundscore、等级MM-F、歌曲名song、谱面rhythm、谱面流速speed
        songtimetostart=songtimetostartt
        song, rhythm, speed, songname, songrank = PlayPage.whichmusic(music)
        background_image1 = pygame.image.load(fpath+"image/PlayPage.png").convert_alpha()
        progressbar = pygame.image.load(fpath+"image/progressbar.png").convert_alpha()
        scorebar = pygame.image.load(fpath+"image/scorebar.png").convert_alpha()
        board = pygame.image.load(fpath+"image/board.png").convert_alpha()
        tap = pygame.image.load(fpath+"image/tap.png").convert_alpha()
        touch = pygame.image.load(fpath+"image/touch.png").convert_alpha()
        hold = pygame.image.load(fpath+"image/hold.png").convert_alpha()
        songscore = pygame.image.load(fpath+"image/"+str(songname)+"Score.png").convert_alpha()
        backgroundscore = pygame.image.load(fpath+"image/backgroundscore.png").convert_alpha()
        MM = pygame.image.load(fpath+"image/MM.png").convert_alpha()
        M = pygame.image.load(fpath+"image/M.png").convert_alpha()
        S = pygame.image.load(fpath+"image/S.png").convert_alpha()
        A = pygame.image.load(fpath+"image/A.png").convert_alpha()
        B = pygame.image.load(fpath+"image/B.png").convert_alpha()
        C = pygame.image.load(fpath+"image/C.png").convert_alpha()
        F = pygame.image.load(fpath+"image/F.png").convert_alpha()

        # perfect/good队列pglist贴图
        p=[]
        g=[]
        for i in range (0,30):
            ap=pygame.image.load(fpath+"image/p/"+str(i)+".png").convert_alpha()
            ag=pygame.image.load(fpath+"image/g/"+str(i)+".png").convert_alpha()
            p.append(ap)
            g.append(ag)

        # notes队列--用于showrhythm()
        taps1 = []
        taps2 = []
        taps3 = []
        taps4 = []
        taps5 = []
        taps6 = []
        touchs1 = []
        touchs2 = []
        touchs3 = []
        touchs4 = []
        touchs5 = []
        touchs6 = []
        holds1=[]
        holds2=[]
        holds3=[]
        holds4=[]
        holds5=[]
        holds6=[]

        # 音符的5*6个时间序列
        taptime, touchtime, holdtime, holdstarttime, holdendtime = PlayPage.loadrhythm(rhythm,speed)

        # 音符总数：H=tap+hold-12 T=touch-6
        H=T=0
        for i in range(0,6):
            H+=len(taptime[i])
            H+=len(holdstarttime[i])
            T+=len(touchtime[i])
        H-=12
        T-=6

        # int型变量初始化：frame、lastframe、taplastframe、score、badcore、earlycore、perfectcore、latecore、misscore、combo、allcombo、特效队列pglist
        frame=score=badcore=earlycore=perfectcore=latecore=misscore=combo=0
        tapindex = [0, 0, 0, 0, 0, 0]
        touchindex = [0, 0, 0, 0, 0, 0]
        holdindex = [0, 0, 0, 0, 0, 0]
        lastholdindex = [0, 0, 0, 0, 0, 0]
        lastframe = [0, 0, 0, 0, 0, 0]
        taplastframe = [0, 0, 0, 0, 0, 0]
        allcombo=[]
        pglist=[]

        # boolean型变量初始化：missTF
        tapmissTF = [False, False, False, False, False, False]
        touchmissTF = [False, False, False, False, False, False]
        holdmissTF = [False, False, False, False, False, False]
        holdstartTF = [False, False, False, False, False, False]

        # 音符note判定状态state初始化
        tapstate = ['NA','NA','NA','NA','NA','NA']
        touchstate = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA']
        holdstate = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA']

        # 游戏结果等级
        rank = 'NA'

        pygame.mixer.music.load(song)
        clock = pygame.time.Clock()
        pygame.mixer.music.play(0,1.5+songtimetostart/1000)
        allframes = int(MP3(song).info.length * 60)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if 0 <= x <= 50 and 0 <= y <= 50:
                        print("Stop and Quit.")
                        running=False
                if event.type == pygame.QUIT:
                    running = False
            if pygame.mixer.music.get_busy() is False:
                print("Finished!!!")
                running=False

            keys_pressed = pygame.key.get_pressed()

            # 开始游戏按shift
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                startattention = False

            # 按键判定
            if keys_pressed[pygame.K_s]:
                if frame>taplastframe[0]+1:
                    tapmissTF[0] = True
                else:
                    tapmissTF[0] = False
                taplastframe[0]=frame
                touchmissTF[0] = True
                holdmissTF[0] = True
            if keys_pressed[pygame.K_d]:
                if frame > taplastframe[1] + 1:
                    tapmissTF[1] = True
                else:
                    tapmissTF[1] = False
                taplastframe[1] = frame
                touchmissTF[1] = True
                holdmissTF[1] = True
            if keys_pressed[pygame.K_f]:
                if frame>taplastframe[2]+1:
                    tapmissTF[2] = True
                else:
                    tapmissTF[2] = False
                taplastframe[2]=frame
                touchmissTF[2] = True
                holdmissTF[2] = True
            if keys_pressed[pygame.K_j]:
                if frame > taplastframe[3] + 1:
                    tapmissTF[3] = True
                else:
                    tapmissTF[3] = False
                taplastframe[3] = frame
                touchmissTF[3] = True
                holdmissTF[3] = True
            if keys_pressed[pygame.K_k]:
                if frame > taplastframe[4] + 1:
                    tapmissTF[4] = True
                else:
                    tapmissTF[4] = False
                taplastframe[4] = frame
                touchmissTF[4] = True
                holdmissTF[4] = True
            if keys_pressed[pygame.K_l]:
                if frame > taplastframe[5] + 1:
                    tapmissTF[5] = True
                else:
                    tapmissTF[5] = False
                taplastframe[5] = frame
                touchmissTF[5] = True
                holdmissTF[5] = True

            # notes判定
            for i in range(0,6):
                if tapindex[i]<len(taptime[i]):
                    if tapmissTF[i]:
                        combo, badcore, earlycore, perfectcore, latecore, misscore, tapstate[i],\
                        tapmissTF[i], tapindex[i] = PlayPage.tapcheck(i,tapindex[i],taptime[i][tapindex[i]],tapstate[i],frame,\
                                 badcore,earlycore,perfectcore,latecore,misscore,\
                                 combo,allcombo,tapmissTF[i], pglist)
                    else:
                        if frame>taptime[i][tapindex[i]]+10:
                            misscore+=1
                            tapindex[i]+=1
                            allcombo.append(combo)
                            combo=0
                            print(str(tapindex[i]) + " tap miss " + str(misscore))
                if touchindex[i]<len(touchtime[i]):
                    if touchmissTF[i]:
                        combo, badcore, earlycore, perfectcore, latecore, misscore, touchstate[i],\
                        touchmissTF[i], touchindex[i] = PlayPage.touchcheck(i,touchindex[i],touchtime[i][touchindex[i]],touchstate[i],frame,\
                                 badcore,earlycore,perfectcore,latecore,misscore,\
                                 combo,allcombo,touchmissTF[i], pglist)
                    else:
                        if frame>touchtime[i][touchindex[i]]+5:
                            misscore+=1
                            touchindex[i]+=1
                            allcombo.append(combo)
                            combo=0
                            print(str(touchindex[i]) + " touch miss " + str(misscore))
                if holdindex[i]<len(holdstarttime[i]):
                    if holdmissTF[i]:
                        combo, badcore, earlycore, perfectcore, latecore, misscore, holdstate[i], holdmissTF[i], holdstartTF[i], holdindex[i],\
                        lastframe[i], lastholdindex[i] = PlayPage.holdcheck(i,holdindex[i],lastholdindex[i],holdstarttime[i][holdindex[i]], holdendtime[i][holdindex[i]], holdstate[i], frame, lastframe[i],\
                                 badcore,earlycore,perfectcore,latecore,misscore,\
                                 combo,allcombo,holdmissTF[i],holdstartTF[i], pglist)
                    else:
                        if (frame>holdstarttime[i][holdindex[i]]+10 and holdstate[i]=='NA') or \
                                (frame<holdendtime[i][holdindex[i]] and (holdstate[i]=='early' or holdstate[i]=='perfect' or holdstate[i]=='late')):
                            holdstartTF[i]=False
                            holdstate[i] = 'NA'
                            misscore+=1
                            holdindex[i]+=1
                            allcombo.append(combo)
                            combo=0
                            print(str(holdindex[i]) + " hold miss " + str(misscore))

            # 加入游戏结束时的combo数
            if frame==allframes-1320:
                allcombo.append(combo)
            score,rank=PlayPage.Score(badcore, earlycore, perfectcore, latecore, misscore, H, T)
            rankimage = eval(rank)

            # score值显示为7位数
            if score!=1000000:
                str_score='0'*(7-len(str(score)))+str(score)
            else:
                str_score=str(score)

            # 界面图片更新
            playpage.blit(background_image1, (0, 0))

            # 音符note下落动画
            for notename in ['tap','touch','hold']:
                if notename=='tap'or'touch':
                    initialy=-20
                if notename=='hold':
                    initialy=-300
                for i in range(1,7):
                    note=eval(notename)
                    notes=eval(notename+'s'+str(i))
                    notetime=eval(notename+'time')[i-1]
                    PlayPage.showrhythm(note, notes, notetime, frame, 200*i,initialy)
                    PlayPage.moverhythm(note, notes, notetime, frame, speed)
                    for j, (noterect, starttime) in enumerate(notes):
                        playpage.blit(note,noterect)

            # 进度条progressbar、得分条scorebar动画
            playpage.blit(scorebar, (1400,int(900-900*score/1000000)))
            if frame>=180:
                progressbar_x=1400
                progressbar_y=int(900-((frame-180)/(allframes-180-1320))*900)
                playpage.blit(progressbar, (progressbar_x, progressbar_y))

            # perfect及good特效动画
            if len(pglist) > 0:
                for i, (pos, porg, arrtime) in enumerate(pglist):
                    if frame - arrtime <= 29:
                        playpage.blit(eval(porg)[frame - arrtime], (150 + pos * 200, 500))
                    if frame - arrtime >= 29:
                        pglist.pop(i)

            # 判定线贴图
            playpage.blit(board, (0, 0))

            # 界面文字combo、combonum、scorenum、songname、songrank
            text_combo = pygame.font.SysFont('twcen', 36).render('Combo', True, (253, 217, 136))
            text_combo_rect = text_combo.get_rect(center=(800, 20))
            text_combonum = pygame.font.SysFont('twcen', 54).render(str(combo), True, (253, 217, 136))
            text_combonum_rect = text_combonum.get_rect(center=(800, 60))
            if combo>=3:
                playpage.blit(text_combo, text_combo_rect)
                playpage.blit(text_combonum, text_combonum_rect)
            text_scorenum = pygame.font.SysFont('twcen', 46).render(str_score, True, (253, 217, 136))
            text_scorenum_rect = text_scorenum.get_rect(center=(1500, 40))
            playpage.blit(text_scorenum, text_scorenum_rect)
            text_songname = pygame.font.SysFont('twcen', 54).render(songname, True, (253, 217, 136))
            text_songname_rect = text_songname.get_rect(center=(300, 40))
            playpage.blit(text_songname, text_songname_rect)
            text_songrank = pygame.font.SysFont('twcen', 54).render(songrank, True, (253, 217, 136))
            text_songrank_rect = text_songrank.get_rect(center=(1350, 40))
            playpage.blit(text_songrank, text_songrank_rect)
            # 游戏开始按shift键，保证按键的识别
            text_startattention = pygame.font.SysFont('twcen', 54).render('Please press SHIFT to start!', True,(253, 217, 136))
            text_startattention_rect = text_startattention.get_rect(center=(800, 400))
            if startattention:
                playpage.blit(text_startattention, text_startattention_rect)

            # 结算动画：backgroundscore、songscore、rankimage、‘score’、scorenum、’maxcombo‘、maxcombonum，perfect、miss、bad、good、early、late
            if frame >= allframes-1320 and frame < allframes:
                songscore_x = 1600-(frame-allframes+1200)*30
                if songscore_x<-100:
                    songscore_x=-100
                backgroundscore_x=1600
            if frame >= allframes-94 and frame < allframes-90:
                backgroundscore_x = 1600-(frame-allframes+94)*60
            if frame >= allframes-90:
                songscore_x=(allframes-frame-90)*60
                backgroundscore_x=songscore_x+1460
                if backgroundscore_x<=0:
                    backgroundscore_x=0
                if songscore_x<=-1800:
                    songscore_x=-1800
            if frame >= allframes - 1320:
                if rankimage==MM or M:
                    rankimage_x=songscore_x+1160
                else:
                    rankimage_x = songscore_x+1180
                t_score_x=songscore_x+1305
                n_score_x=songscore_x+1385
                t_maxcombo_x=songscore_x+1330
                n_maxcombo_x=songscore_x+1410
                pg_x=songscore_x+1305
                be_x=songscore_x+1293
                ml_x=songscore_x+1281
                playpage.blit(backgroundscore, (backgroundscore_x, 0))
                playpage.blit(songscore, (songscore_x, 0))
                playpage.blit(rankimage, (rankimage_x, 0))
                t_score = pygame.font.SysFont('twcen', 54).render('Score', True, (68, 25, 21))
                t_score_rect = t_score.get_rect(center=(t_score_x, 420))
                playpage.blit(t_score, t_score_rect)
                n_score = pygame.font.SysFont('twcen', 60).render(str_score, True, (114, 10, 0))
                n_score_rect = n_score.get_rect(center=(n_score_x, 470))
                playpage.blit(n_score, n_score_rect)
                t_maxcombo = pygame.font.SysFont('twcen', 54).render('maxCombo', True, (68, 25, 21))
                t_maxcombo_rect = t_maxcombo.get_rect(center=(t_maxcombo_x, 550))
                playpage.blit(t_maxcombo, t_maxcombo_rect)
                n_maxcombo = pygame.font.SysFont('twcen', 60).render(str(max(allcombo)), True, (114, 10, 0))
                n_maxcombo_rect = n_maxcombo.get_rect(center=(n_maxcombo_x, 600))
                playpage.blit(n_maxcombo, n_maxcombo_rect)
                pg = pygame.font.SysFont('twcen', 28).render('Perfect '+str(perfectcore)+' / Good '+str(earlycore+latecore), True, (68, 25, 21))
                pg_rect = pg.get_rect(center=(pg_x, 700))
                playpage.blit(pg, pg_rect)
                be = pygame.font.SysFont('twcen', 28).render('Bad ' + str(badcore) + ' / Early ' + str(earlycore), True, (68, 25, 21))
                be_rect = be.get_rect(center=(be_x, 754))
                playpage.blit(be, be_rect)
                ml = pygame.font.SysFont('twcen', 28).render('Miss ' + str(misscore) + ' / Late ' + str(latecore), True, (68, 25, 21))
                ml_rect = ml.get_rect(center=(ml_x, 808))
                playpage.blit(ml, ml_rect)

            pygame.display.flip()
            frame+=1
            clock.tick(60)

        pygame.quit()
        global shiftTF
        shiftTF=startattention
        return startattention

# ShowPage: 开始点歌界面
class ShowPage:
    # 全局参数传递
    def argpassing():
        global stts
        if stts is not None:
            songtimetostart = stts
        else:
            songtimetostart = 0
        global shiftTF
        if shiftTF is not None:
            startattention = shiftTF
        else:
            startattention = True
        return songtimetostart,startattention

    # 进入游戏界面
    def button1():
        print("music1;levelEZ")
        # 跳转至playpage界面
        show = ShowPage.show
        show.withdraw()
        music = "music1EZ"
        songtimetostart, startattention=ShowPage.argpassing()
        startattention=PlayPage.play(music, songtimetostart,startattention)
        show.deiconify()

    def button2():
        print("music1;levelHD")
        show = ShowPage.show
        show.withdraw()
        music = "music1HD"
        songtimetostart, startattention=ShowPage.argpassing()
        startattention=PlayPage.play(music, songtimetostart,startattention)
        show.deiconify()

    def button3():
        print("music1;levelIN")
        show = ShowPage.show
        show.withdraw()
        music = "music1IN"
        songtimetostart, startattention=ShowPage.argpassing()
        startattention=PlayPage.play(music, songtimetostart,startattention)
        show.deiconify()

    def button4():
        print("music2;levelEZ")
        show = ShowPage.show
        show.withdraw()
        music = "music2EZ"
        songtimetostart, startattention=ShowPage.argpassing()
        startattention=PlayPage.play(music, songtimetostart,startattention)
        show.deiconify()

    def button5():
        print("music2;levelHD")
        show = ShowPage.show
        show.withdraw()
        music = "music2HD"
        songtimetostart, startattention=ShowPage.argpassing()
        startattention=PlayPage.play(music, songtimetostart,startattention)
        show.deiconify()

    def button6():
        print("music2;levelIN")
        show = ShowPage.show
        show.withdraw()
        music = "music2IN"
        songtimetostart, startattention=ShowPage.argpassing()
        startattention=PlayPage.play(music, songtimetostart,startattention)
        show.deiconify()

    def button7():
        print("music3;levelEZ")
        show = ShowPage.show
        show.withdraw()
        music = "music3EZ"
        songtimetostart, startattention=ShowPage.argpassing()
        startattention=PlayPage.play(music, songtimetostart,startattention)
        show.deiconify()

    def button8():
        print("music3;levelHD")
        show = ShowPage.show
        show.withdraw()
        music = "music3HD"
        songtimetostart, startattention=ShowPage.argpassing()
        startattention=PlayPage.play(music, songtimetostart,startattention)
        show.deiconify()

    def button9():
        print("music3;levelIN")
        show = ShowPage.show
        show.withdraw()
        music = "music3IN"
        songtimetostart, startattention=ShowPage.argpassing()
        startattention=PlayPage.play(music,songtimetostart,startattention)
        show.deiconify()

    # 进入设置界面
    def button10():
        print("SETTING")
        show = ShowPage.show
        show.withdraw()
        songtimetostart, startattention=ShowPage.argpassing()
        songtimetostart,startattention=SettingPage.set(songtimetostart,startattention)
        show.deiconify()

    # 关闭窗口
    def close_window():
        show = ShowPage.show
        show.destroy()

    # 创建窗口show（主界面）
    show = ttk.Window(
        title='Mumo music',
        themename='litera',
        size=(1600, 900),
        minsize=(0, 0),
        maxsize=(1600, 900)
    )
    songtimetostart = 0

    # ShowPage主方法
    def main():
        show=ShowPage.show
        show.geometry(f"+150+50")
        show.resizable(False,False)

        #添加背景图片
        background_image1 = ImageTk.PhotoImage(file=fpath+"image/ShowPage.png")
        background_label1 = tk.Label(show, image=background_image1)
        background_label1.place(x=0, y=0, relwidth=1, relheight=1)

        #添加按钮：EZ HD IN
        b1=ttk.Button(show, text="EZ", bootstyle=(SUCCESS, OUTLINE),command=ShowPage.button1)
        b2=ttk.Button(show, text="HD", bootstyle=(WARNING, OUTLINE),command=ShowPage.button2)
        b3=ttk.Button(show, text="IN", bootstyle=(DANGER, OUTLINE),command=ShowPage.button3)
        b1.place(x=295,y=520,width=60,height=60)
        b2.place(x=355, y=520, width=60, height=60)
        b3.place(x=415, y=520, width=60, height=60)
        b4 = ttk.Button(show, text="EZ", bootstyle=(SUCCESS, OUTLINE), command=ShowPage.button4)
        b5 = ttk.Button(show, text="HD", bootstyle=(WARNING, OUTLINE), command=ShowPage.button5)
        b6 = ttk.Button(show, text="IN", bootstyle=(DANGER, OUTLINE), command=ShowPage.button6)
        b4.place(x=820, y=520, width=60, height=60)
        b5.place(x=880, y=520, width=60, height=60)
        b6.place(x=940, y=520, width=60, height=60)
        b7 = ttk.Button(show, text="EZ", bootstyle=(SUCCESS, OUTLINE), command=ShowPage.button7)
        b8 = ttk.Button(show, text="HD", bootstyle=(WARNING, OUTLINE), command=ShowPage.button8)
        b9 = ttk.Button(show, text="IN", bootstyle=(DANGER, OUTLINE), command=ShowPage.button9)
        b7.place(x=1345, y=520, width=60, height=60)
        b8.place(x=1405, y=520, width=60, height=60)
        b9.place(x=1465, y=520, width=60, height=60)

        #添加标签，歌曲名及歌曲图
        afont=Font(family="Microsoft YaHei", size=14,slant="italic")
        l1=ttk.Label(show,text="  music1 Infinity",font=afont,bootstyle="inverse-dark")
        l1.place(x=75,y=520,width=220,height=60)
        image_music1 = ImageTk.PhotoImage(file=fpath+"image/INFINITY.png")
        l2 = tk.Label(show, image=image_music1)
        l2.place(x=75, y=100, width=400, height=400)
        l3 = ttk.Label(show, text="  music2 乐意效劳", font=afont, bootstyle="inverse-dark")
        l3.place(x=600, y=520, width=220, height=60)
        image_music2 = ImageTk.PhotoImage(file=fpath+"image/LEYI.png")
        l4 = tk.Label(show, image=image_music2)
        l4.place(x=600, y=100, width=400, height=400)
        l5 = ttk.Label(show, text="  music3 Monster", font=afont, bootstyle="inverse-dark")
        l5.place(x=1125, y=520, width=220, height=60)
        image_music3 = ImageTk.PhotoImage(file=fpath+"image/MONSTER.png")
        l6 = tk.Label(show, image=image_music3)
        l6.place(x=1125, y=100, width=400, height=400)

        # 添加按钮：SETTING EXIT
        b10 = ttk.Button(show, text="SETTING", bootstyle=(DARK, OUTLINE), command=ShowPage.button10)
        b11 = ttk.Button(show, text="EXIT", bootstyle=(DARK, OUTLINE), command=ShowPage.close_window)
        b10.place(x=75, y=765, width=180, height=60)
        b11.place(x=1345, y=765, width=180, height=60)

        show.mainloop()

ShowPage.main()
