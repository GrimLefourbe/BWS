import cProfile
import BWS
import Weidu

if __name__ == '__main__':
    P=cProfile.Profile()
    #P.enable()
    T=BWS.BWS(start=0, end=10)
    W = Weidu.Weidu_Handler(weidupath="C:/Coding/Python workshop/BWS/Game/weidu.exe", gamepath="C:/Coding/Python workshop/BWS/Game")
    #P.disable()
    #P.print_stats()