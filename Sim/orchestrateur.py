from multiprocessing import Process, Queue
import app
import Controleur

if __name__ == "__main__":
    queue = Queue()
    p1 = Process(target=app.run(), args=(queue,))
    p2 = Process(target=Controleur.run(), args=(queue,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("End of flight")