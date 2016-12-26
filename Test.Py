import cProfile
import BWS

if __name__ == '__main__':
    P=cProfile.Profile()
    P.enable()
    T=BWS.BWS(start=0, end=5)
    P.disable()
    P.print_stats()