import cProfile
import BWS
import Weidu
import ModInfo
import BWS_GUI
from PyQt5 import QtWidgets
import sys
import logging

if __name__ == '__main__':
    P=cProfile.Profile()
    #P.enable()
    try:
        app = QtWidgets.QApplication(sys.argv)
        T = BWS_GUI.BWS_GUI(app=app)
    #T = BWS.BWS(no_gui=False)
        W = Weidu.Weidu_Handler(weidupath="C:/Coding/Python workshop/BWS/Game/weidu.exe", gamepath="C:/Coding/Python workshop/BWS/Game")
    except:
        logging.exception("!")
    #P.disable()
    #P.print_stats()