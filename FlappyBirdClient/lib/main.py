#coding: utf-8
import cocos
from cocos.actions import *
from cocos.director import *
from cocos.scene import *
from game_controller import *
import common

def main():
	director.init(width=common.visibleSize["width"], height=common.visibleSize["height"], caption="Flappy Bird")

	gameScene = Scene()
	game_start(gameScene)

	if director.scene:
		director.replace(gameScene)
	else:
		director.run(gameScene)