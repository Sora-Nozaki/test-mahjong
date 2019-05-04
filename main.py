# -*- coding: utf-8 -*-
from flask import Flask,render_template,request,url_for,redirect
from const import ALL_HAI
# from hand import Hand
import itertools
import random
import copy


app = Flask(__name__)

def syantenCheck(player_tehai):
    global tehai,kotsu,jantou
    global mentsu_p_max,mentsu_s_max,mentsu_m_max
    global tatsu_p_max,tatsu_s_max,tatsu_m_max,tatsu_z_max
    global toitsu_m,toitsu_p,toitsu_s,toitsu_check
    global ans #天鳳でシャンテン数を確認するよう(test)

    tehai = [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0]
    jantou = 0
    kotsu = 0
    mentsu_m_max,mentsu_p_max,mentsu_s_max = 0,0,0
    tatsu_p_max,tatsu_s_max,tatsu_m_max,tatsu_z_max = 0,0,0,0
    toitsu_m,toitsu_p,toitsu_s = 0,0,0
    toitsu_check = 0 #雀頭候補の有無
    syanten_num = 8

    #赤ドラを通常の牌として数える
    for value in player_tehai:
        tehai[value] += 1
    if tehai.pop(4)==1:
        tehai[4] +=1
    if tehai.pop(13)==1:
        tehai[13] +=1
    if tehai.pop(22)==1:
        tehai[22] +=1

    #test用
    ans = ""
    for index,i in enumerate(tehai):
        if index < 9:
            for j in range(i):
                l = index+1
                n = str(l)
                ans += n
            if index == 8:
                ans += "p"
        elif index < 18 and index >= 9:
            for j in range(i):
                l = index%9+1
                n = str(l)
                ans += n
            if index == 17:
                ans += "s"
        elif index < 27 and index >=18:
            for j in range(i):
                l = index%9+1
                n = str(l)
                ans += n
            if index == 26:
                ans += "m"
        else:
            for j in range(i):
                l = index%9+1
                n = str(l)
                ans += n
            if index == 33:
                ans += "z"

    #print("#########")
    #print("00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33")
    #print("1p","2p","3p","4p","5p","6p","7p","8p","9p","1s","2s","3s","4s","5s","6s","7s","8s","9s","1m","2m","3m","4m","5m","6m","7m","8m","9m",'東','南','西','北','白','発','中')
    #print(tehai)


    #チートイツのシャンテン数
    titoi_toitsu = 0
    haisyu_num = len(tehai) - tehai.count(0) #牌の種類数
    for i in tehai:
        if i >= 2:
            titoi_toitsu += 1
    syanten_titoi_temp = 6 - titoi_toitsu
    if haisyu_num <= 7:#手牌が7種類以下の場合
        syanten_titoi_temp += 7 - haisyu_num


    #国士無双のシャンテン数
    kokusi_num = 0
    kokusi_toitsu = 0
    tehai_cal = copy.deepcopy(tehai)
    for i in [0,8,9,17,18,26,27,28,29,30,31,32,33]:
        if tehai_cal[i] >= 2:
            kokusi_toitsu = 1
        if tehai_cal[i] >= 1:
            kokusi_num += 1
    syanten_kokusi_temp = 13 - kokusi_num
    if kokusi_toitsu:
        syanten_kokusi_temp -= 1
    # print(syanten_kokusi_temp,"国士無双")


    #一般形のシャンテン数
    #完全に孤立している牌の抜き取り
    kanzenKotsu_num = kanzenKotsu()
    kanzenShuntsu_num = kanzenShuntsu()
    kanzen_kotsu_mentsu_num = kanzenKotsu_num + kanzenShuntsu_num #完全シュンツ・コーツの合計
    kanzenKoritu_num = kanzenKoritsu()
    # print(tehai)

    #各種牌のそれぞれの合計を算出
    Check_m,Check_s,Check_p,Check_z = 0,0,0,0
    for i in range(0,34):
        if i <= 8:
            Check_p += tehai[i]
        elif i >= 9 and i <= 17:
            Check_s += tehai[i]
        elif i >= 18 and i <= 26:
            Check_m += tehai[i]
        else:
            Check_z += tehai[i]
    kanzenToitsu_exist = kanzenToitsu() #孤立したトイツの有無


    #コーツ→シュンツ→ターツ　最後に雀頭の有無でシャンテン計算
    if Check_p > 0: #ピンズがあれば実行
        mentsu_p_max=0
        tatsu_p_max=0
        mentsu_tatsu_p_num=MentsuTatsu_p(1,tehai)
        # print("pメンツターツ",mentsu_tatsu_p_num,mentsu_p_max)
    if Check_s > 0: #ソウズがあれば実行
        mentsu_s_max=0
        tatsu_s_max=0
        mentsu_tatsu_s_num=MentsuTatsu_s(1,tehai)
        # print("sメンツターツ",mentsu_tatsu_s_num)
    if Check_m > 0: #マンズがあれば実行
        mentsu_m_max=0
        tatsu_m_max=0
        mentsu_tatsu_m_num=MentsuTatsu_m(1,tehai)
        # print("mメンツターツ",mentsu_tatsu_m_num)
    if Check_z > 0: #字牌があれば実行
        tatsu_z_max = 0
        tatsu_z_num = Tatsu_z()
        # print("zターツ",tatsu_z_num)

    toitsu_num = toitsu_s + toitsu_p + toitsu_m + tatsu_z_max #トイツの合計
    syanten_temp = SyantenCal(toitsu_num,kanzen_kotsu_mentsu_num) #一般形のシャンテン数(仮)
    if syanten_temp < syanten_num :
        syanten_num = syanten_temp #最良形でのシャンテン数に変更


    #シュンツ→コーツ→ターツ　最後に雀頭の有無でシャンテン計算
    toitsu_check = 0
    if kotsu:
        if Check_p > 0:
            mentsu_p_max=0
            tatsu_p_max=0
            mentsu_tatsu_p_num=MentsuTatsu_p(2,tehai)
            # print("pメンツターツ",mentsu_tatsu_p_num,mentsu_p_max)
        if Check_s > 0:
            mentsu_s_max=0
            tatsu_s_max=0
            mentsu_tatsu_s_num=MentsuTatsu_s(2,tehai)
            # print("sメンツターツ",mentsu_tatsu_s_num)
        if Check_m > 0:
            mentsu_m_max=0
            tatsu_m_max=0
            mentsu_tatsu_m_num=MentsuTatsu_m(2,tehai)
            # print("mメンツターツ",mentsu_tatsu_m_num)
        if Check_z > 0:
            tatsu_z_max = 0
            tatsu_z_num = Tatsu_z()
            # print("zターツ",tatsu_z_num)

    toitsu_num = toitsu_s + toitsu_p + toitsu_m + tatsu_z_max
    syanten_temp = SyantenCal(toitsu_num,kanzen_kotsu_mentsu_num) #一般形のシャンテン数(仮)

    # print(syanten_titoi_temp,"チートイ")
    # print(syanten_kokusi_temp,"国士無双")
    # print(syanten_temp,"一般")

    if syanten_temp < syanten_num :
        syanten_num = syanten_temp
    if syanten_titoi_temp < syanten_num:
        syanten_num = syanten_titoi_temp
    if syanten_kokusi_temp < syanten_num:
        syanten_num = syanten_kokusi_temp
    # print("#########",syanten_num)

    if syanten_num == -1:
        return -1
    if not syanten_num:
        return 0
    return syanten_num


#字牌のターツ数のチェック
def Tatsu_z():
    global tehai,tatsu_z_max,toitsu_check
    tatsu_z_num = 0
    for i in range(27,34):
        if tehai[i] == 2:
            #tehai[i] -= 2
            tatsu_z_num += 1
            toitsu_check = 1
    tatsu_z_max = tatsu_z_num

    return tatsu_z_num


#ピンズの刻子数
def Kotsu_p(mode,tehai_cal):
    global kotsu
    kotsu_p_num = 0
    for i in range(9):
        if tehai_cal[i] >= 3:
            tehai_cal[i] -= 3
            kotsu_p_num += 1
            kotsu += 1
            # print("ピンズの刻子抜き取り",i,tehai_cal)
            if mode==1:
                return kotsu_p_num
    return kotsu_p_num,tehai_cal

#ピンズのメンツ・ターツ数
def MentsuTatsu_p(mode,tehai): #mode=1 :コーツ→シュンツ　　mode=2 :シュンツ→コーツ
    global mentsu_p_max,tatsu_p_max,toitsu_p,toitsu_check
    shuntsu_num = 0
    p_max = 0


    for i in range(8): #i シュンツの始まりを0から7番地まで順にずらして調べる
        mentsu_p = 0
        tatsu_p = 0
        toitsu_p=0
        # print("")
        # print(i)
        # print("tehai[",i,"]",tehai)
        tehai_cal = copy.deepcopy(tehai) #計算用に元データをコピー

        #コーツを先に抜き出す
        if mode==1:
            kotsu_data = Kotsu_p(0,tehai_cal)
            mentsu_p += kotsu_data[0]
            tehai_cal = kotsu_data[1]


        for j in range(7):
            while tehai_cal[i+j]>=1 and tehai_cal[i+j+1]>=1 and tehai_cal[i+j+2]>=1 and (i+j)<8:
                tehai_cal[i+j] -= 1
                tehai_cal[i+j+1] -= 1
                tehai_cal[i+j+2] -= 1
                mentsu_p += 1
                # print("ピンズの順子抜き取り",i,j,tehai_cal)

        if i > 3: #i > 3だと123のシュンツを無視してしまうので、再チェックも含めて以下の処理する
            for j in range(7):
                while tehai_cal[j]>=1 and tehai_cal[j+1]>=1 and tehai_cal[j+2]>=1 and j<8:
                    tehai_cal[j] -= 1
                    tehai_cal[j+1] -= 1
                    tehai_cal[j+2] -= 1
                    mentsu_p += 1
                    # print("ピンズの順子抜き取り",i,j,tehai_cal)

        #コーツを後で抜き出す
        if mode == 2:
            kotsu_data = Kotsu_p(0,tehai_cal)
            mentsu_p += kotsu_data[0]
            tehai_cal = kotsu_data[1]


        #ピンズターツの抜き取り
        for j in range(9):
            if tehai_cal[j] >= 2 and j < 27: #トイツの可能性を調べる
                toitsu_check = 1
                # print("頭チェック",i,j,tehai_cal)

        for j in range(9):
            if tehai_cal[j] >= 2 and j < 9: #トイツ抜き出し
                tehai_cal[j] -= 2
                tatsu_p += 1
                toitsu_p += 1
                # print("トイツ抜き出し",i,j,tehai_cal)

            if tehai_cal[j] and tehai_cal[j+1] and j < 8:
                tehai_cal[j] -= 1
                tehai_cal[j+1] -= 1
                tatsu_p += 1
                # print("リャンメン・ペンチャン抜き出し",i,j,tehai_cal)

            if tehai_cal[j] and not tehai_cal[j+1] and tehai_cal[j+2] and j < 7:
                tehai_cal[j] -= 1
                tehai_cal[j+2] -= 1
                tatsu_p += 1
                # print("カンチャン抜き出し",i,j,tehai_cal)

            mentsu_p_state = mentsu_p*10 + tatsu_p #メンツターツの点数付け

            if mentsu_p_state > p_max:
                p_max = mentsu_p_state
                mentsu_p_max = mentsu_p
                tatsu_p_max = tatsu_p
                shuntsu_num = mentsu_p*10 + tatsu_p
                # print("最良形の更新",p_max)

            #牌が残らなければ、そこで終了
            Check_p = 0
            for k in range(9):
                Check_p += tehai_cal[k]
            if not Check_p:
                # print("使い切った")
                return shuntsu_num

        Check_p = 0
        for j in range(9):
            Check_p += tehai_cal[j]
        if not Check_p: #全部使い切ったら、終了。
            # print("使い切った")
            return shuntsu_num
        if not mentsu_p:#メンツがない場合、終了。
            # print("メンツなし")
            return shuntsu_num

    return shuntsu_num


#ソウズの刻子数
def Kotsu_s(mode,tehai_cal):
    global kotsu
    kotsu_s_num = 0
    for i in range(9,18):
        if tehai_cal[i] >= 3:
            tehai_cal[i] -= 3
            kotsu_s_num += 1
            kotsu += 1
            # print("ソウズの刻子抜き取り",i,tehai_cal)
            if mode==1:
                return kotsu_s_num
    return kotsu_s_num,tehai_cal

#ソウズのメンツ・ターツ数
def MentsuTatsu_s(mode,tehai):
    global mentsu_s_max,tatsu_s_max,toitsu_s,toitsu_check
    shuntsu_num = 0
    s_max = 0

    for i in range(8):
        mentsu_s = 0
        tatsu_s = 0
        toitsu_s=0
        # print("")
        # print(i)
        # print("tehai[",i,"]",tehai)
        tehai_cal = copy.deepcopy(tehai)
        if mode==1:
            kotsu_data = Kotsu_s(0,tehai_cal)
            mentsu_s += kotsu_data[0]
            tehai_cal = kotsu_data[1]
        elif mode==3:
            kotsu_data = Kotsu_s(1,tehai_cal)
            mentsu_s += kotsu_data[0]
            tehai_cal = kotsu_data[1]
        for j in range(9,18):
            while tehai_cal[i+j]>=1 and tehai_cal[i+j+1]>=1 and tehai_cal[i+j+2]>=1 and (i+j)<16:
                tehai_cal[i+j] -= 1
                tehai_cal[i+j+1] -= 1
                tehai_cal[i+j+2] -= 1
                mentsu_s += 1
                # print("ソウズの順子抜き取り",i,j,tehai_cal)

        if i > 3:
            for j in range(9,18):
                while tehai_cal[j]>=1 and tehai_cal[j+1]>=1 and tehai_cal[j+2]>=1 and j<16:
                    tehai_cal[j] -= 1
                    tehai_cal[j+1] -= 1
                    tehai_cal[j+2] -= 1
                    mentsu_s += 1
                    # print("ソウズの順子抜き取り",i,j,tehai_cal)

        if mode == 2 or mode == 3:
            kotsu_data = Kotsu_s(0,tehai_cal)
            mentsu_s += kotsu_data[0]
            tehai_cal = kotsu_data[1]


        #ソウズターツの抜き取り
        for j in range(9,18):
            if tehai_cal[j] >= 2 and j < 27: #トイツ抜き出し
                toitsu_check = 1
                # print("頭チェック",i,j,tehai_cal)
        for j in range(9,18):
            if tehai_cal[j] >= 2 and j < 18: #トイツ抜き出し
                tehai_cal[j] -= 2
                tatsu_s += 1
                toitsu_s += 1
                # print("トイツ抜き出し",i,j,tehai_cal)

            if tehai_cal[j] and tehai_cal[j+1] and j < 17:
                tehai_cal[j] -= 1
                tehai_cal[j+1] -= 1
                tatsu_s += 1
                # print("リャンメン・ペンチャン抜き出し",i,j,tehai_cal)

            if tehai_cal[j] and not tehai_cal[j+1] and tehai_cal[j+2] and j < 16:#8→7に変更
                tehai_cal[j] -= 1
                tehai_cal[j+2] -= 1
                tatsu_s += 1
                # print("カンチャン抜き出し",i,j,tehai_cal)

            # print(j%9,"sメンツ,sターツ:",mentsu_s,tatsu_s)
            mentsu_s_state = mentsu_s*10 + tatsu_s
            if mentsu_s_state > s_max:
                s_max = mentsu_s_state
                mentsu_s_max = mentsu_s
                tatsu_s_max = tatsu_s
                shuntsu_num = mentsu_s*10 + tatsu_s
                # print("最良形の更新",s_max,shuntsu_num,id(tehai),id(tehai_cal))

            Check_s = 0
            for k in range(9,18):
                Check_s += tehai_cal[k]
            if not Check_s:
                # print("使い切った")
                return shuntsu_num


        Check_s = 0
        for j in range(9,18):
            Check_s += tehai_cal[j]
        if not Check_s: #全部使い切ったら、終了。
            # print("使い切った")
            return shuntsu_num
        if not mentsu_s:#メンツない場合、終了。？？
            # print("メンツなし")
            return shuntsu_num
    return shuntsu_num


#マンズの刻子数
def Kotsu_m(mode,tehai_cal):
    global kotsu
    kotsu_m_num = 0
    for i in range(18,27):
        if tehai_cal[i] >= 3:
            tehai_cal[i] -= 3
            kotsu_m_num += 1
            kotsu += 1
            # print("マンズの刻子抜き取り",i,tehai_cal)
            if mode==1:
                return kotsu_m_num
    return kotsu_m_num,tehai_cal

#マンズのメンツ・ターツ数
def MentsuTatsu_m(mode,tehai):
    global mentsu_m_max,tatsu_m_max,toitsu_m,toitsu_check
    shuntsu_num = 0
    m_max = 0

    for i in range(8):
        mentsu_m = 0
        tatsu_m = 0
        toitsu_m = 0

        # print("")
        # print(i)
        # print("tehai[",i+1,"m]",tehai)
        tehai_cal = copy.deepcopy(tehai)
        if mode==1:
            kotsu_data = Kotsu_m(0,tehai_cal)
            mentsu_m += kotsu_data[0]
            tehai_cal = kotsu_data[1]
        elif mode==3:
            kotsu_data = Kotsu_m(1,tehai_cal)
            mentsu_m += kotsu_data[0]
            tehai_cal = kotsu_data[1]
        for j in range(18,27):
            if i <= 6: #7以上だとtehai_calの要素数を超えてしまう
                while tehai_cal[i+j]>=1 and tehai_cal[i+j+1]>=1 and tehai_cal[i+j+2]>=1 and (i+j)<25:
                    tehai_cal[i+j] -= 1
                    tehai_cal[i+j+1] -= 1
                    tehai_cal[i+j+2] -= 1
                    mentsu_m += 1
                    # print("マンズの順子抜き取り",i,j,tehai_cal)

        if i > 3:
            for j in range(18,27):
                while tehai_cal[j]>=1 and tehai_cal[j+1]>=1 and tehai_cal[j+2]>=1 and j<25:
                    tehai_cal[j] -= 1
                    tehai_cal[j+1] -= 1
                    tehai_cal[j+2] -= 1
                    mentsu_m += 1
                    # print("マンズの順子抜き取り",i,j,tehai_cal)

        if mode == 2 or mode == 3:
            kotsu_data = Kotsu_m(0,tehai_cal)
            mentsu_m += kotsu_data[0]
            tehai_cal = kotsu_data[1]


        #マンズターツの抜き取り
        for j in range(18,27):
            if tehai_cal[j] >= 2 and j < 27: #トイツ抜き出し
                toitsu_check = 1
                # print("頭チェック",i,j,tehai_cal)
        for j in range(18,27):
            if tehai_cal[j] >= 2 and j < 27: #トイツ抜き出し
                tehai_cal[j] -= 2
                tatsu_m += 1
                toitsu_m += 1
                # print("トイツ抜き出し",i,j,tehai_cal)

            if tehai_cal[j] and tehai_cal[j+1] and j < 26:
                tehai_cal[j] -= 1
                tehai_cal[j+1] -= 1
                tatsu_m += 1
                # print("リャンメン・ペンチャン抜き出し",i,j,tehai_cal)

            if tehai_cal[j] and not tehai_cal[j+1] and tehai_cal[j+2] and j < 25:
                tehai_cal[j] -= 1
                tehai_cal[j+2] -= 1
                tatsu_m += 1
                # print("カンチャン抜き出し",i,j,tehai_cal)

            # print(j%9,"mメンツ,mターツ:",mentsu_m,tatsu_m)
            mentsu_m_state = mentsu_m*10 + tatsu_m
            if mentsu_m_state > m_max:
                m_max = mentsu_m_state
                mentsu_m_max = mentsu_m
                tatsu_m_max = tatsu_m
                shuntsu_num = mentsu_m*10 + tatsu_m
                # print("最良形の更新",m_max)

            Check_m = 0
            for k in range(18,27):
                Check_m += tehai_cal[k]
            if not Check_m:
                # print("使い切った")
                return shuntsu_num


        Check_m = 0
        for j in range(18,27):
            Check_m += tehai_cal[j]
        if not Check_m: #全部使い切ったら、終了。
            # print("使い切った")
            return shuntsu_num
        if not mentsu_m:#メンツない場合、終了。？？
            # print("メンツなし")
            return shuntsu_num
    return shuntsu_num


#シャンテンの計算
def SyantenCal(toitsu_num,kanzen_kotsu_mentsu_num):
    global mentsu_p_max,mentsu_s_max,mentsu_m_max
    global tatsu_p_max,tatsu_s_max,tatsu_m_max,tatsu_z_max
    global toitsu_check

    print("men_p,s,m,kanzen,tatsu_p,s,m,z,toitsu")
    print(mentsu_p_max,mentsu_s_max,mentsu_m_max,kanzen_kotsu_mentsu_num,tatsu_p_max,tatsu_s_max,tatsu_m_max,tatsu_z_max,toitsu_num)

    syanten_temp = 0
    block_num = 0
    block_num = (mentsu_p_max + mentsu_s_max + mentsu_m_max + kanzen_kotsu_mentsu_num) + (tatsu_p_max + tatsu_s_max + tatsu_m_max + tatsu_z_max)

    if block_num <= 4:
        syanten_temp = 8 - (mentsu_p_max + mentsu_s_max + mentsu_m_max + kanzen_kotsu_mentsu_num)*2 - (tatsu_p_max + tatsu_s_max + tatsu_m_max + tatsu_z_max)
        # print("４ターツ以下")
    else: #メンツ＋ターツが（頭含め）５以上なら、「メンツ＋ターツ＝５」として扱う
        syanten_temp = 8 - (5 + (mentsu_p_max + mentsu_s_max + mentsu_m_max + kanzen_kotsu_mentsu_num))
        # print(toitsu_check)
        if toitsu_num or toitsu_check: #5つ以上で雀頭、もしくはその候補がある場合は、そのまま
            # print("頭候補あり５ターツ以上")
            pass
        else:
            syanten_temp += 1
            # print("頭なし５ターツ以上")

    # print("block,syanten",block_num,syanten_temp)
    return syanten_temp



def kanzenKotsu():
    kanzenKotsu_num = 0

    for i in range(27,34):#字牌の完全刻子
        if tehai[i] >= 3:
            tehai[i] = 0
            kanzenKotsu_num += 1

    for i in range(0,19,9):
        #１(p,s,m)の完全刻子
        if tehai[i] >= 3 and not tehai[i+1] and not tehai[i+2]:
            tehai[i] = 0
            kanzenKotsu_num += 1
        #２の完全刻子
        if not tehai[i] and tehai[i+1] >= 3 and not tehai[i+2] and not tehai[i+3]:
            tehai[i+1] = 0
            kanzenKotsu_num += 1
        #３〜７の完全刻子
        for j in range(5):
            if not tehai[i+j] and not tehai[i+j+1] and tehai[i+j+2] >= 3 and not tehai[i+j+3] and not tehai[i+j+4]:
                tehai[i+j+2] = 0
                kanzenKotsu_num += 1
        #８の完全刻子
        if not tehai[i+5]  and not tehai[i+6] and tehai[i+7] >= 3 and not tehai[i+8]:
            tehai[i+7] = 0
            kanzenKotsu_num += 1
        #９の完全刻子
        if not tehai[i+6] and not tehai[i+7] and tehai[i+8] >= 3:
            tehai[i+8] = 0
            kanzenKotsu_num += 1
    return kanzenKotsu_num

def kanzenKoritsu():
    kanzenKoritu_num = 0

    for i in range(27,34):#字牌の完全孤立牌
        if tehai[i] == 1:
            tehai[i] = 0
            kanzenKoritu_num += 1
    for i in range(0,19,9):
        if tehai[i] == 1 and not tehai[i+1] and not tehai[i+2]:
            tehai[i] = 0
            kanzenKoritu_num += 1
        if not tehai[i] and tehai[i+1] == 1 and not tehai[i+2] and not tehai[i+3]:
            tehai[i+1] = 0
            kanzenKoritu_num += 1
        for j in range(5):
            if not tehai[i+j] and not tehai[i+j+1] and tehai[i+j+2] == 1 and not tehai[i+j+3] and not tehai[i+j+4]:
                tehai[i+j+2] = 0
                kanzenKoritu_num += 1
        if not tehai[i+5]  and not tehai[i+6] and tehai[i+7] == 1 and not tehai[i+8]:
            tehai[i+7] = 0
            kanzenKoritu_num += 1
        if not tehai[i+6] and not tehai[i+7] and tehai[i+8] == 1:
            tehai[i+8] = 0
            kanzenKoritu_num += 1
    return kanzenKoritu_num

def kanzenShuntsu():
    kanzenShuntsu_num = 0

    for x in [2,1]:
        for i in range(0,19,9):
            if tehai[i] == x and tehai[i+1] == x and tehai[i+2] == x  and not tehai[i+3] and not tehai[i+4]:
                tehai[i] = 0
                tehai[i+1] = 0
                tehai[i+2] = 0
                kanzenShuntsu_num += x
            if not tehai[i] and tehai[i+1] == x and tehai[i+2] == x and tehai[i+3] == x and not tehai[i+4] and not tehai[i+5]:
                tehai[i+1] = 0
                tehai[i+2] = 0
                tehai[i+3] = 0
                kanzenShuntsu_num += x
            for j in range(3):
                if not tehai[i+j] and not tehai[i+j+1] and tehai[i+j+2] == x and tehai[i+j+3] == x and tehai[i+j+4] == x and not tehai[i+j+5] and not tehai[i+j+6]:
                    tehai[i+j+2] = 0
                    tehai[i+j+3] = 0
                    tehai[i+j+4] = 0
                    kanzenShuntsu_num += x
            if not tehai[i+3]  and not tehai[i+4] and tehai[i+5] == x and tehai[i+6] == x and tehai[i+7] == x and not tehai[i+8]:
                tehai[i+5] = 0
                tehai[i+6] = 0
                tehai[i+7] = 0
                kanzenShuntsu_num += x
            if not tehai[i+4] and not tehai[i+5] and tehai[i+6] == x and tehai[i+7] == x and tehai[i+8] == x:
                tehai[i+6] = 0
                tehai[i+7] = 0
                tehai[i+8] = 0
                kanzenShuntsu_num += x
    return kanzenShuntsu_num

def kanzenToitsu():
    for i in range(27,34):#字牌の完全刻子
        if tehai[i] == 2:
            return 1

    for i in range(0,19,9):
        #１(p,s,m)の完全刻子
        if tehai[i] == 2 and not tehai[i+1]:
            return 1
        #２の完全刻子
        if not tehai[i] and tehai[i+1] == 2 and not tehai[i+2] and not tehai[i+3]:
            return 1
        #３〜７の完全刻子
        for j in range(5):
            if not tehai[i+j] and not tehai[i+j+1] and tehai[i+j+2] == 2 and not tehai[i+j+3] and not tehai[i+j+4]:
                return 1
        #８の完全刻子
        if not tehai[i+5]  and not tehai[i+6] and tehai[i+7] == 2 and not tehai[i+8]:
            return 1
        #９の完全刻子
        if not tehai[i+7] and tehai[i+8] == 2:
            return 1
    return 0








def initialize():
    global hai,players,dora
    hai = []
    for i in range(37): #全牌の生成 37
        if i==5 or i==15 or i==15:
            for n in range(3):
                hai.append(i)
        elif i==4 or i==14 or i==24:
            hai.append(i)
        else:
            for n in range(4):
                hai.append(i)

    players = [ [1,[],[],8,0],
                [2,[],[],8,0],
                [3,[],[],8,0],
                [4,[],[],8,0]
               ]
    #[user_id,{配牌},{捨て牌},[シャンテン計算用],"ツモ番"]
    dora = [[],[]] #[{表ドラ},{裏ドラ}]



def main():
    initialize()
    random.shuffle(players)
    dealer(players,hai)
    make_dora()
    for player in players:
        syanten_num = syantenCheck(player[1])
        player[3] = syanten_num

def display(players):
    data = []
    for index,player in enumerate(players):
        data.append([player[0],[ALL_HAI[hai] for hai in player[1]],[ALL_HAI[hai] for hai in player[2]],player[3],player[4]])
    return data

def dealer(players,hai):
    random.shuffle(hai)
    for player in players:
        for i in range(13):
            number = hai.pop()
            player[1].append(number)
        player[1].sort()

#テスト用(一人用)-ここから　　testに[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]を代入するとその状態を表示できる。使用しないときはtest = 0
         #"1p,2p,3p,4p,5p,6p,7p,8p,9p,1s,2s,3s,4s,5s,6s,7s,8s,9s,1m,2m,3m,4m,5m,6m,7m,8m,9m,東,南,西,北,白,発,中"
    test = 0
    if test:
        test_tehai = []
        for index,i in enumerate(test):
            if i:
                if index < 4:
                    for j in range(i):
                        test_tehai.append(index)
                elif index >= 4 and index < 13:
                    for j in range(i):
                        test_tehai.append(index+1)
                elif index >= 13 and index < 22:
                    for j in range(i):
                        test_tehai.append(index+2)
                elif index >= 22:
                    for j in range(i):
                        test_tehai.append(index+3)
        players[0][1] = test_tehai
        players[0][4] = 1
        print(players)
        syanten_num = syantenCheck(players[0][1])
        print(syanten_num)
        players[0][3] = syanten_num
    else:
##ここまで
        draw(0)

def draw(next):
    global ans
    number = hai.pop()
    players[next][1].append(number)
    players[next][4] = 1
    syanten_num = syantenCheck(players[next][1])
    print(syanten_num,"シャンテン")
    players[next][3] = syanten_num
    print(ans)
    # players[next][2] = Hand.complete(players[next])

def make_dora():
    for i in range(2):
        number = hai.pop()
        dora[i].append(number)



@app.route('/')
def hello():
    name = "Hello World"

    return render_template('./layout.html', title='flask test', name=name)

@app.route('/game')
def game():
    name = "GAME"
    hai_data = display(players)
    return render_template('./game.html', title='flask test', name=name, allhai=hai_data)

@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        main()
        return redirect(url_for('game'))
    elif request.method == 'POST':
        allhai_each_player = a
        res = request.form['post_value']

    return render_template('./hello.html', title='flask test',)


@app.route('/dispose', methods=['POST'])
def dispose():
    next = 0
    if request.method == 'POST':
        res = int(request.form['hai'])

        for player in players:
            if player[4] == 1:
                player[2].append(player[1].pop(res))
                player[4] = 0
                player[1].sort()
                order = players.index(player)
                if order == 3: #3
                    next = 0
                else:
                    next = order + 1
        draw(next)
    else:
        print("error")
    return redirect(url_for('game'))

## おまじない
if __name__ == "__main__":
    app.run(debug=True)

# keys = list(player[1])
        # kkk,kkk_pre,list_s,lll = [],[],[],[[],[],[]]
        # count_s = 0
        #
        # for index,data in enumerate(keys):
        #     keys[index] = divmod(data,4)
        # for data in keys:
        #     kkk.append(data[0])
        #
        # for i,data in enumerate(kkk): #シュンツになる全可能性の検索
        #     if (data >= 0 and data <= 6) or (data >= 9 and data <= 15) or (data >= 18 and data <= 24):
        #         plus1 = data + 1
        #         plus2 = data + 2
        #         if plus1 in kkk and plus2 in kkk:
        #             list_s.append([i,data]) #可能性のある要素番号(要素数にしたのはpop()だと重複も消えるから)
        # # print(list_s)
        # P_list_s = list(itertools.permutations(list_s))
        # # print(P_list_s)
        #
        # kkk_pre = kkk
        # for en in list(itertools.permutations(list_s)):
        #     kkk = kkk_pre
        #     i = 0
        #     # print(kkk,en)
        #     for d in en:
        #         # print("check==",d)
        #         if d[1] in kkk and (d[1]+1) in kkk and (d[1]+2) in kkk:
        #             plus1 = d[1] + 1
        #             plus2 = d[1] + 2
        #             # print(d[1],plus1,plus2)
        #
        #             # kkk.pop(d[0])
        #             # kkk.pop(kkk.index(plus1))
        #             # kkk.pop(kkk.index(plus2))
        #             kkk[d[0]] = -1
        #             kkk[kkk.index(plus1)] = -1
        #             kkk[kkk.index(plus2)] = -1
        #             # print("kkk##",kkk)
        #             count_s += 1
        #             i += 1
        #
        #     count_t,count_a = 0,0
        #     for data in kkk:
        #         if data >= 0:
        #             if kkk.count(data) == 2:
        #                 count_t += 1
        #
        #             elif kkk.count(data) == 3:
        #                 count_a += 1
        #             t = int(count_t / 2)
        #             a = int(count_a / 3)
        #     counter = [t,a,count_s]
        #     eval = counter[0]*0.8 + counter[1] + counter[2]
        #     lll[0].append(eval)
        #     lll[1].append(en)
        #     lll[2].append(counter)
        #
        # print(lll[0],max(lll[0]))
        #
        # counter = lll[2][lll[0].index(max(lll[0]))]
        #
        # # print(counter,"トイツ,アンコ,シュンツ")
        #
        # if (counter[0]==1 and counter[1] + counter[2] == 4) or (counter[0]==7):
        #     return "上がり"
        # elif counter[0]==6 or (counter[0]==0 and counter[1]+counter[2]==4) or (counter[0]==1 and counter[1]+counter[2]==3):
        #     return "テンパイ" #まだ甘い(シャン点数計算ができてない)
        # return "ノーテン"
        # def toitu_or_anko(self,kkk):
        #     count_t,count_a = 0,0
        #     for data in kkk:
        #         if kkk.count(data) == 2:
        #             count_t += 1
        #
        #         elif kkk.count(data) == 3:
        #             count_a += 1
        #         t = int(count_t / 2)
        #         a = int(count_a / 3)
        #     return [t, a]
