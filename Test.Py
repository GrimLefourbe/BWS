import cProfile
import BWS
import Weidu
import ModInfo
import BWS_GUI
from PyQt5 import QtWidgets
import sys

if __name__ == '__main__':
    P=cProfile.Profile()
    #P.enable()
    app = QtWidgets.QApplication(sys.argv)
    T = BWS_GUI.BWS_GUI(app=app)
    #T = BWS.BWS(no_gui=False)
    W = Weidu.Weidu_Handler(weidupath="C:/Coding/Python workshop/BWS/Game/weidu.exe", gamepath="C:/Coding/Python workshop/BWS/Game")

    #P.disable()
    #P.print_stats()