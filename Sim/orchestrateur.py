from multiprocessing import Process, Queue
import app
import test_commande_gen
import controleur_rust
import real_time_log
import os
import sys

NUM_DRONES = 2

if __name__ == "__main__":
    queues_commande = []
    queues_commande_for_display = []
    queues_etat_reel = []
    queues_lidar = []
    for i in range(NUM_DRONES):
        queues_commande.append(Queue())
        queues_etat_reel.append(Queue())
        queues_commande_for_display.append(Queue())
        queues_lidar.append(Queue())

    p1 = Process(target=app.go, args=(queues_commande,queues_etat_reel,queues_commande_for_display,queues_lidar,))
    p2 = Process(target=controleur_rust.wrapper_sync, args=(queues_commande,queues_etat_reel,queues_lidar,))
    p3 = Process(target=real_time_log.go, args=(queues_commande_for_display[0],))
    
    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()

    print("End of flight")