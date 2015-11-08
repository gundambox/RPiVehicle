# RPiVehicle #

這是由Raspberry Pi所控制的自走車主程式

# 實作架構 #

器材

1. 藍芽耳麥
2. 藍芽接收器
3. Raspberry Pi 2 Model B
4. 三輪自走車
5. L298N 馬達驅動板

# 藍芽接收器與raspberry pi的連接 #

Raspberry Pi 2的OS採用官方的OS：Raspbian

將從藍芽傳來的指令經由錄音串流到語音辨識進行處理。

# 語音辨識簡介與流程 #

## 簡介 ##

CMU Sphinx是一個開放原始碼的語音辨識系統

架構上使用隱馬可夫模型(HMM)作為語音辨認的核心

利用n-gram構成的語言模型(LM)限制辦認的可能詞彙

以及所有詞彙所對應發音的字典檔。

本程式的語言模型限制只辨認前進、左轉、右轉、後退及停止等五個指令。

## 控制說明 ##

```python
Motor1A = 16
Motor1B = 18

Motor2A = 23
Motor2B = 21
```

以上是指定控制腳位，對應到下圖的16、18、21及23

![腳位圖1](http://gundambox.github.io/img/%E5%88%9D%E8%A9%A6%E8%AA%9E%E9%9F%B3%E8%BE%A8%E8%AD%98-%E8%81%B2%E9%9F%B3%E9%81%99%E6%8E%A7%E8%BB%8A/%E5%88%9D%E8%A9%A6%E8%AA%9E%E9%9F%B3%E8%BE%A8%E8%AD%98-%E8%81%B2%E9%9F%B3%E9%81%99%E6%8E%A7%E8%BB%8A-1.png)

16、18、21及23腳位請參考下面兩張圖

![腳位圖2](http://gundambox.github.io/img/%E5%88%9D%E8%A9%A6%E8%AA%9E%E9%9F%B3%E8%BE%A8%E8%AD%98-%E8%81%B2%E9%9F%B3%E9%81%99%E6%8E%A7%E8%BB%8A/%E5%88%9D%E8%A9%A6%E8%AA%9E%E9%9F%B3%E8%BE%A8%E8%AD%98-%E8%81%B2%E9%9F%B3%E9%81%99%E6%8E%A7%E8%BB%8A-2.png)

![腳位圖3](http://gundambox.github.io/img/%E5%88%9D%E8%A9%A6%E8%AA%9E%E9%9F%B3%E8%BE%A8%E8%AD%98-%E8%81%B2%E9%9F%B3%E9%81%99%E6%8E%A7%E8%BB%8A/%E5%88%9D%E8%A9%A6%E8%AA%9E%E9%9F%B3%E8%BE%A8%E8%AD%98-%E8%81%B2%E9%9F%B3%E9%81%99%E6%8E%A7%E8%BB%8A-3.png)

以下為IC說明圖

![IC說明圖](http://gundambox.github.io/img/%E5%88%9D%E8%A9%A6%E8%AA%9E%E9%9F%B3%E8%BE%A8%E8%AD%98-%E8%81%B2%E9%9F%B3%E9%81%99%E6%8E%A7%E8%BB%8A/%E5%88%9D%E8%A9%A6%E8%AA%9E%E9%9F%B3%E8%BE%A8%E8%AD%98-%E8%81%B2%E9%9F%B3%E9%81%99%E6%8E%A7%E8%BB%8A-4.png)

下表是腳位電壓與動作說明

| In1(In3) 	| In2(In4) 	| Out1(out3)	| out2(out4)	| 馬達狀態	|
|-----------	|-----------	|---------------	|---------------	|-----------	|
| 0			| 0			|				|				| 停止		|
| 0			| 1			| 0				| 1				| 前進		|
| 1			| 0			| 1				| 0				| 後退		|
| 1			| 1			|				|				| 停止		|

若以上面圖的自走車圖片而言

黑線為OUT1對應到pin 16(motor1A)、紅線為pin 18(motor1B)

motor2黑線為OUT4(IN4)為pin 23(motor2A)、紅線為pin 21(motor2B)

當右轉時，motor1為前進、motor2為後退，所以程式碼為

```python
elif cmd == '右轉':
    print '右轉'
    GPIO.output(Motor1A,GPIO.LOW)
    GPIO.output(Motor1B,GPIO.HIGH)
    
    GPIO.output(Motor2A,GPIO.LOW)
    GPIO.output(Motor2B,GPIO.HIGH)
```

# demo影片 #

[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/ZJntNTvb_g8/0.jpg)](http://www.youtube.com/watch?v=ZJntNTvb_g8)

# 參考 #

1. [Detect & Record Audio in Python](http://stackoverflow.com/questions/892199/detect-record-audio-in-python)
2. [Controlling DC Motors Using Python With a Raspberry Pi](http://computers.tutsplus.com/tutorials/controlling-dc-motors-using-python-with-a-raspberry-pi--cms-20051)
3. [Basic concepts of speech](http://cmusphinx.sourceforge.net/wiki/tutorialconcepts)
4. [语音识别的基础知识与CMUsphinx介绍](http://blog.csdn.net/zouxy09/article/details/7941585)
5. [Bluetooth manager window won't open](http://unix.stackexchange.com/questions/161820/bluetooth-manager-window-wont-open)
4.	[Raspberry pi 記錄2-設定wifi、藍芽](http://www.dotblogs.com.tw/bowwowxx/archive/2014/04/17/144774.aspx)
5.	[AUDIO CONFIGURATION](https://www.raspberrypi.org/documentation/configuration/audio-config.md)
6.	[L298N 馬達驅動板接線說明與正反轉程式測試](http://ruten-proteus.blogspot.tw/2014/02/L298NGuide.html)
7.	[Controlling DC Motors Using Python With a Raspberry Pi](http://computers.tutsplus.com/tutorials/controlling-dc-motors-using-python-with-a-raspberry-pi--cms-20051)
8.	[PocketSphinx語音辨識系統的編譯、安裝和使用](http://blog.csdn.net/zouxy09/article/details/7942784)
9.	[PocketSphinx語音辨識系統語言模型的訓練和聲學模型的改進](http://blog.csdn.net/zouxy09/article/details/7949126)
10.	[PocketSphinx語音辨識系統聲學模型的訓練與使用](http://blog.csdn.net/zouxy09/article/details/7962382)
11.	[HDMI轉VGA](https://sites.google.com/site/raspberypishare0918/home/di-yi-ci-qi-dong/1-7-hdmi-zhuan-vga)
12.	[OS(NOOBS)下載](https://www.raspberrypi.org/downloads/)
