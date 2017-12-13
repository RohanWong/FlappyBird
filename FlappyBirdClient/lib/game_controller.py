# -*- coding: utf-8 -*-
import cocos
from cocos.scene import *
from cocos.actions import *
from cocos.layer import *  
from cocos.text  import *
from cocos.menu import *
import random
from atlas import *
from land import *
from bird import *
from score import *
from pipe import *
from collision import *
from network import *
import common
##
import time
import xlwt
import xlrd
import sys
from xlrd import open_workbook
from xlutils.copy import copy


gameLayer = None
gameScene = None
spriteBird = None
land_1 = None
land_2 = None
startLayer = None
pipes = None
score = 0
listener = None
account = None
password = None
ipTextField = None
errorLabel = None
isGamseStart = False

##
difficulty = 0
re = False
name = None
pwd = None
sign = None

def get_difficulty():
    return difficulty

def initGameLayer():
    global spriteBird, gameLayer, land_1, land_2
    # gameLayer: 游戏场景所在的layer
    gameLayer = Layer()
    bg = createAtlasSprite("bg_day")
    bg.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    gameLayer.add(bg, z=0)
    # add moving bird
    spriteBird = creatBird()
    gameLayer.add(spriteBird, z=20)
    # add moving land
    land_1, land_2 = createLand()
    gameLayer.add(land_1, z=10)
    gameLayer.add(land_2, z=10)
    # add gameLayer to gameScene
    gameScene.add(gameLayer)

def game_start(_gameScene):
    global gameScene
    # 给gameScene赋值
    gameScene = _gameScene
    initGameLayer()
    log_botton = LogOrSignMenu()
    gameLayer.add(log_botton, z=20, name='log_button')
    # start_botton = SingleGameStartMenu()
    # gameLayer.add(start_botton, z=20, name="start_button")
    connect(gameScene)

def createLabel(value, x, y):
    label=Label(value,  
        font_name='Times New Roman',  
        font_size=15, 
        color = (0,0,0,255), 
        width = common.visibleSize["width"] - 20,
        multiline = True,
        anchor_x='center',anchor_y='center')
    label.position = (x, y)
    return label

# single game start button的回调函数
def singleGameReady():
    removeContent()
    ready = createAtlasSprite("text_ready")
    ready.position = (common.visibleSize["width"]/2, common.visibleSize["height"] * 3/4)

    tutorial = createAtlasSprite("tutorial")
    tutorial.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    
    spriteBird.position = (common.visibleSize["width"]/3, spriteBird.position[1])

    #handling touch events
    class ReadyTouchHandler(cocos.layer.Layer):
        is_event_handler = True     #: enable director.window events

        def __init__(self):
            super( ReadyTouchHandler, self).__init__()

        def on_mouse_press (self, x, y, buttons, modifiers):
            """This function is called when any mouse button is pressed

            (x, y) are the physical coordinates of the mouse
            'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
            'modifiers' is a bitwise or of pyglet.window.key modifier constants
               (values like 'SHIFT', 'OPTION', 'ALT')
            """
            self.singleGameStart(buttons, x, y)

        # ready layer的回调函数
        def singleGameStart(self, eventType, x, y):
            isGamseStart = True
        
            spriteBird.gravity = gravity #gravity is from bird.py
            # handling bird touch events
            addTouchHandler(gameScene, isGamseStart, spriteBird)
            score = 0   #分数，飞过一个管子得到一分
            # add moving pipes
            pipes = createPipes(gameLayer, gameScene, spriteBird, score)
            # 小鸟AI初始化
            # initAI(gameLayer)
            # add score
            createScoreLayer(gameLayer)
            # add collision detect
            addCollision(gameScene, gameLayer, spriteBird, pipes, land_1, land_2)
            # remove startLayer
            gameScene.remove(readyLayer)

    readyLayer = ReadyTouchHandler()
    readyLayer.add(ready)
    readyLayer.add(tutorial)
    gameScene.add(readyLayer, z=10)

def backToMainMenu():
    global re
    re = True
    restartButton = RestartMenu()
    gameLayer.add(restartButton, z=50, name="restart_button")


def showContent(content):
    removeContent()
    notice = createLabel(content, common.visibleSize["width"]/2+5, common.visibleSize["height"] * 9/10)
    gameLayer.add(notice, z=70, name="content")

def removeContent():
    try:
        gameLayer.remove("content")
    except Exception, e:
        pass


def chooseLevel():
    if re:
        gameLayer.remove("restart_button")
    else:
        gameLayer.remove("start_button")
    difficulty_botton = DifficultyMenu()
    gameLayer.add(difficulty_botton, z=20, name="difficulty_button")



def showNotice():
    connected = connect(gameScene) # connect is from network.py
    if not connected:
        content = "Cannot connect to server"
        showContent(content)
    else:
        request_notice() # request_notice is from network.py



def log_out():
    global name, pwd
    (name, pwd) = (None, None)
    if re:
        gameLayer.remove("restart_button")
    else:
        gameLayer.remove("start_button")
    log_botton = LogOrSignMenu()
    gameLayer.add(log_botton, z=20, name='log_button')



def log_in():
    global sign
    sign = False
    gameLayer.remove("log_button")
    inputBotton = InputMenu()
    gameLayer.add(inputBotton, z=50, name="input_button")
    # if re:
    #     restartBotton = RestartMenu()
    #     gameLayer.add(restartBotton, z=50, name="restart_button")
    # else:
    #     start_botton = SingleGameStartMenu()
    #     gameLayer.add(start_botton, z=20, name="start_button")

def sign_up():
    global sign
    sign = True
    gameLayer.remove("log_button")
    inputBotton = InputMenu()
    gameLayer.add(inputBotton, z=50, name="input_button")

def process_name(value):
    global name
    if value == '':
        print "no character"
        pass
    else:
        name = value

def process_pwd(value):
    global pwd
    if value == '':
        print "no character"
        pass
    else:       
        pwd = value

def process_input():
    global name, pwd
    if sign:
        result = check_sign_up(name, pwd)
    else:
        result = check_log_in(name, pwd)

    gameLayer.remove("input_button")
    if result and sign:
        content = "Sign up successfully."
        showContent(content)
    elif result and not sign:
        content = "Log in successfully."
        showContent(content)
    elif not result and sign:
        content = "Sign up failed."
        showContent(content)
    elif not result and not sign:
        content = "Log in failed."
        showContent(content)
    time.sleep(1)
    if result:
        if re:
            restartBotton = RestartMenu()
            gameLayer.add(restartBotton, z=50, name="restart_button")
        else:
            start_botton = SingleGameStartMenu()
            gameLayer.add(start_botton, z=20, name="start_button")
    else:
        log_botton = LogOrSignMenu()
        gameLayer.add(log_botton, z=20, name='log_button')




def check_sign_up(name,pwd):
    if name == "" or pwd == "": return False
    sign_up_able=True
    book = xlrd.open_workbook(r'register_table.xls',formatting_info=True)
    b=book.sheets()[0]
    wb=copy(book)
    sheet=wb.get_sheet(0)
    nrows=b.nrows
    ncols=b.ncols
    count=nrows
    for i in range(nrows):
        cty=b.cell(i,0).ctype
        n=b.cell(i,0).value
        if cty==2:
            n=str(int(n))
        if name == n :
            sign_up_able=False
    
    if sign_up_able==True:
        sheet.write(count,0,name)
        sheet.write(count,1,pwd)
        count=count+1
        print('sign up success')
        wb.save(r'register_table.xls')
        return True
    else:
        print('sign up fail')
        return False
  

def check_log_in(name,pwd):
    if name == "" or pwd == "": return False
    book = xlrd.open_workbook(r'register_table.xls')
    table=book.sheets()[0]
    nrows=table.nrows
    ncols=table.ncols
    log_in_able=False
    for i in range(nrows):
        ctype_1 = table.cell(i,0).ctype
        no_1 = table.cell(i,0).value
        if ctype_1 ==2:       
            no_1 = str(int(no_1))
        if name == no_1:
            log_in_able=True
            ctype = table.cell(i,1).ctype
            no = table.cell(i,1).value
            if ctype==2:
                no = str(int(no))
            if no==pwd:
                print('log in success') 
                return True
            else:
                print('log in fail')
                return False
    if log_in_able==False:
        print('log in fail')
        return False  


class DifficultyMenu(Menu):
    def __init__(self):  
        super(DifficultyMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_easy.png"), self.back0)),
                (ImageMenuItem(common.load_image("button_normal.png"), self.back1)),
                (ImageMenuItem(common.load_image("button_hard.png"), self.back2)),
                ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def back(self):
        global difficulty
        difficulty = self.difficulty
        gameLayer.remove("difficulty_button")
        if re:
            restartButton = RestartMenu()
            gameLayer.add(restartButton, z=50, name="restart_button")
        else:
            start_botton = SingleGameStartMenu()
            gameLayer.add(start_botton, z=50, name="start_button")

    def back0(self):
        self.difficulty = 0
        self.back()

    def back1(self):
        self.difficulty = 1
        self.back()

    def back2(self):
        self.difficulty = 2
        self.back()

class RestartMenu(Menu):
    def __init__(self):  
        super(RestartMenu, self).__init__()
        self.menu_valign = CENTER  
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_restart.png"), self.initMainMenu)),
                (ImageMenuItem(common.load_image("button_notice.png"), showNotice)),
                (ImageMenuItem(common.load_image("button_difficulty.png"), chooseLevel)),
                (ImageMenuItem(common.load_image("button_logout.png"), log_out)),
                ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def initMainMenu(self):
        gameScene.remove(gameLayer)
        initGameLayer()
        isGamseStart = False
        singleGameReady()

class LogOrSignMenu(Menu):
    def __init__(self):  
        super(LogOrSignMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_login.png"), log_in)),
                (ImageMenuItem(common.load_image("button_signup.png"), sign_up)),
                ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

class InputMenu(Menu):
    def __init__(self):  
        super(InputMenu, self).__init__()
        global name, pwd
        (name, pwd) = (None, None)
        self.menu_valign = CENTER
        self.menu_halign = LEFT
        items = [
                (EntryMenuItem('id:', process_name, '', 10)),
                (EntryMenuItem('pwd:', process_pwd, '', 10)),
                (ImageMenuItem(common.load_image("button_ok.png"), process_input)),
                ]  
        self.create_menu(items,selected_effect=shake(),unselected_effect=shake_back())



class SingleGameStartMenu(Menu):
    def __init__(self):  
        super(SingleGameStartMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_start.png"), self.gameStart)),
                (ImageMenuItem(common.load_image("button_notice.png"), showNotice)),
                (ImageMenuItem(common.load_image("button_difficulty.png"), chooseLevel)),
                (ImageMenuItem(common.load_image("button_logout.png"), log_out)),
                ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def gameStart(self):
        global re
        re = False
        gameLayer.remove("start_button")
        singleGameReady() 