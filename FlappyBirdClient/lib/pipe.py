# -*- coding: utf-8 -*-
from cocos.actions import *
from cocos.cocosnode import *
from cocos.collision_model import *
import random
from atlas import *
from bird import *
from score import *
from game_controller import *
import game_controller
import common

# constants
pipeCount = 2
pipeHeight = 320
pipeWidth = 52
pipeDistance = [100, 100]    #上下管道间的距离
pipeInterval = 180    #两根管道的水平距离
waitDistance = 100    #开始时第一根管道距离屏幕最右侧的距离
heightOffset = 25     #管道的高度偏移值
#mine
speed = 60
position_diff = 10
# vars
PIPE_NEW = 0
PIPE_PASS = 1
pipes = {}    #contains nodes of pipes
pipeState = {}    #PIPE_NEW or PIPE_PASS
downPipeYPosition = {}    #朝下pipe的最下侧的y坐标
upPipeYPosition = {}  #朝上pipe的最上侧的y坐标
pipeIndex = 0

def createPipes(layer, gameScene, spriteBird, score):
    global g_score, movePipeFunc, calScoreFunc, speed
    def initPipe():
        global speed, pipeDistance, position_diff
        difficulty = game_controller.get_difficulty()
        if difficulty == 0:
            speed = 60
            position_diff = 100
        elif difficulty == 1:
            speed = 45
            position_diff = 160
        elif difficulty == 2:
            speed = 40
            position_diff = 200
        for i in range(0, pipeCount):
            #把downPipe和upPipe组合为singlePipe
            downPipe = CollidableRectSprite("pipe_down", 0, (pipeHeight + pipeDistance[i]), pipeWidth/2, pipeHeight/2) #朝下的pipe而非在下方的pipe
            upPipe = CollidableRectSprite("pipe_up", 0, 0, pipeWidth/2, pipeHeight/2)  #朝上的pipe而非在上方的pipe
            singlePipe = CocosNode()
            singlePipe.add(downPipe, name="downPipe")
            singlePipe.add(upPipe, name="upPipe")
            
            #设置管道高度和位置
            singlePipe.position=(common.visibleSize["width"] + i*pipeInterval + waitDistance, heightOffset)
            if i == 1: randPipe(singlePipe, i, True)
            layer.add(singlePipe, z=10)
            pipes[i] = singlePipe
            pipeState[i] = PIPE_NEW
            upPipeYPosition[i] = heightOffset + pipeHeight/2
            downPipeYPosition[i] = heightOffset + pipeHeight/2 + pipeDistance[i]


    def randPipe(pipeNode, i, init):
        global pipeDistance, pipeDistance, position_diff
        difficulty = game_controller.get_difficulty()
        pipeDistance[i] = 100 - 10 * difficulty + random.randint(0, 20)
        center = random.randint(256 - position_diff/2, 256 + position_diff/2)
        pipeNode.get('downPipe').position = (0, pipeDistance[i] + pipeHeight)
        pipeNode.get('downPipe').cshape.center = (0, pipeDistance[i] + pipeHeight) 
        pipeNode.position = (common.visibleSize["width"] + i*pipeInterval + waitDistance, center - pipeHeight/2 - pipeDistance[i]/2)
        upPipeYPosition[i] = center - pipeDistance[i]/2
        downPipeYPosition[i] = center + pipeDistance[i]/2

        if not init:
            _next = i - 1
            if _next < 0: _next = pipeCount - 1
            pipeNode.position = (pipes[_next].position[0] + pipeInterval, center - pipeHeight/2 - pipeDistance[i]/2)
    
    def movePipe(dt):
        global position_diff, pipeDistance, upPipeYPosition, downPipeYPosition
        moveDistance = common.visibleSize["width"]/(2*speed)   # 移动速度和land一致
        for i in range(0, pipeCount):
            
            pipes[i].position = (pipes[i].position[0]-moveDistance, pipes[i].position[1])
            if pipes[i].position[0] < -pipeWidth/2:
                pipeNode = pipes[i]
                pipeState[i] = PIPE_NEW
                randPipe(pipeNode, i, False)
                break    

    def calScore(dt):
        global g_score
        birdXPosition = spriteBird.position[0]
        for i in range(0, pipeCount):
            if pipeState[i] == PIPE_NEW and pipes[i].position[0]< birdXPosition:
                pipeState[i] = PIPE_PASS
                g_score = g_score + 1
                setSpriteScores(g_score) #show score on top of screen

    g_score = score
    initPipe()
    movePipeFunc = movePipe
    calScoreFunc = calScore
    gameScene.schedule(movePipe)
    gameScene.schedule(calScore)
    return pipes



def removeMovePipeFunc(gameScene):
    global movePipeFunc
    if movePipeFunc != None:
        gameScene.unschedule(movePipeFunc)

def removeCalScoreFunc(gameScene):
    global calScoreFunc
    if calScoreFunc != None:
        gameScene.unschedule(calScoreFunc)

def getPipes():
    return pipes

def getUpPipeYPosition():
    return upPipeYPosition

def getDownPipeYPosition():
    return downPipeYPosition

def getPipeCount():
    return pipeCount

def getPipeWidth():
    return pipeWidth

def getPipeDistance():
    return pipeDistance

