# -*- coding: utf-8 -*-
from cocos.actions import *
from atlas import *
import common
import xlrd
from xlrd import open_workbook
from xlutils.copy import copy

spriteScores = {}
scoreLayer = None
finalScores = 0
#开始游戏后显示当前得分
def createScoreLayer(gameLayer):
    global scoreLayer
    scoreLayer = gameLayer
    setSpriteScores(0)

def setSpriteScores(score):
    global finalScores 
    finalScores = score
    if score != 0:
        print("Scores: %d" % (score))
        #记录当前分数
        import network
        network.send_data3(score)
        recordThisScores(score)
        pass
    global scoreLayer
    for k in spriteScores:
        try:
            scoreLayer.remove(spriteScores[k])
            spriteScores[k] = None
        except:
            pass

    scoreStr = str(score)
    i = 0
    for d in scoreStr:
        s = createAtlasSprite("number_score_0"+d)
        s.position = common.visibleSize["width"]/2 + 18 * i, common.visibleSize["height"]*4/5
        scoreLayer.add(s, z=50)
        spriteScores[i] = s
        i = i + 1

def showFinalScores():
    global finalScores
    print("FinalScores: %d" % (finalScores))
    import network
    network.send_data(finalScores)
    #记录本次游戏最后分数
    recordScores()

def recordScores():
    data = xlrd.open_workbook(r'record_table.xls')
    table = data.sheets()[0]
    wb=copy(data)
    sheet=wb.get_sheet(0)
    nrows=table.nrows
    ncols=table.ncols
    sheet.write(nrows - 1,2,finalScores)
    wb.save(r'record_table.xls')
    print("record scores succeed!")

def recordThisScores(score):
    data = xlrd.open_workbook(r'scores_table.xls')
    table = data.sheets()[0]
    wb=copy(data)
    sheet=wb.get_sheet(0)
    sheet.write(0,0,score)
    wb.save(r'scores_table.xls')
    print("record this scores succeed!")
