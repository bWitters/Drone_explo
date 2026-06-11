from multiprocessing import Process, Queue
import app
import Controleur
import tests.test_real_time_log

NUM_DRONES = 2
if __name__ == "__main__":
    queues_commande = []
    queues_etat_reel = []
    queues_position_simu = []
    for i in range(NUM_DRONES):
        queues_commande.append(Queue())
        queues_etat_reel.append(Queue())
        queues_position_simu.append(Queue())

    p1 = Process(target=app.go, args=(queues_commande,queues_etat_reel,queues_position_simu,))
    p2 = Process(target=Controleur.go, args=(queues_commande,queues_etat_reel,queues_position_simu,))
    
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("End of flight")