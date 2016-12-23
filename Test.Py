import cProfile
import BWS

if __name__ == '__main__':
    P=cProfile.Profile()
    P.enable()
    T=BWS.BWS(dldir='E:/Coding/BWS-Downloads', gamedir='C:/Coding/Python workshop/BWS/BWS Game', start=0, end=-1)
    P.disable()
    P.print_stats()