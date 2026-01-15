import math
import numpy as np

def normalize_angle(angle, zero_2_2pi=False):
    """
      Angle modulo operation
      Default angle modulo range is [-pi, pi)

      Parameters
      ----------
      angle : float or array_like
          A angle or an array of angles. This array is flattened for
          the calculation. When an angle is provided, a float angle is
          returned.
      zero_2_2pi : bool, optional
          Change angle modulo range to [0, 2pi)
          Default is False.

      Returns
      -------
      ret : float or ndarray
          an angle or an array of modulated angle.

      Examples
      --------
      >>> normalize_angle(-4.0)
      2.28318531

      >>> normalize_angle([-4.0])
      np.array(2.28318531)

      """
    if isinstance(angle, float):
        is_float = True
    else:
        is_float = False

    angle = np.asarray(angle).flatten()

    if zero_2_2pi:
        mod_angle = angle % (2 * np.pi)
    else:
        mod_angle = (angle + np.pi) % (2 * np.pi) - np.pi

    if is_float:
        return mod_angle.item()
    else:
        return mod_angle
    
def FromRayToAngle(ray, sensor_angle, mirror = False):
    if mirror:
        return(sensor_angle[ray - 1] + 2*math.pi)
    else:
        return(sensor_angle[ray - 1])
    
class SensorsAnalyzer():
    def __init__(self,
                 ):
        self.distance_treshold = 1.2
        self.analyzed_data = {
        "positive gap number": None,
        "positive gap index ray": [],
        "positive gap detection memory": [],
        "positive gap index ray": [],
        "positive gap angle ray": [],
        "positive gap direction": []
        }


    def analyze(self, lidar_data, lidar_ray_angles):
        self.analyzed_data["positive gap index ray"] = self.PositiveGapDetector(lidar_data, self.distance_treshold)
        self.UpdateGapDetection(self.analyzed_data["positive gap index ray"])
        self.analyzed_data["positive gap number"] = len(self.analyzed_data["positive gap detection memory"])
        self.analyzed_data["positive gap angle ray"], self.analyzed_data["positive gap direction"] = self.ComputePositiveGap(self.analyzed_data["positive gap detection memory"],lidar_ray_angles)[:2]
        print("### Analyse ###")
        print("\n\n")
        print("Positive gap index ray :")
        print(self.analyzed_data["positive gap index ray"])
        print("\n\n")
        print("Gap number")
        print(self.analyzed_data["positive gap number"])
        print("\n\n")
        print("Gap angle ray")
        print(self.analyzed_data["positive gap angle ray"])
        print("\n\n")
        print("Gap direction")
        print(self.analyzed_data["positive gap direction"])


    # Detection des gap poisitifs
    def PositiveGapDetector(self, lidar_data, distance_threshold):
        GAP_index_ray = []
        start_ray = None
        end_ray = None

        #On récupère l'indice de la raie qui débute le gap et l'indice de la raie qui termine le gap
        for i, dist in enumerate(lidar_data):
            if dist > distance_threshold:
                if start_ray == None:
                    start_ray = i + 1
                
            if dist < distance_threshold:
                if start_ray != None: 
                    end_ray = i
                    GAP_index_ray.append([start_ray, end_ray])
                    start_ray = None

            if i == len(lidar_data) - 1 and lidar_data[-1] > distance_threshold:
                end_ray = len(lidar_data)
                GAP_index_ray.append([start_ray, end_ray])

        #On retire les gaps trop petit
        for i in range(len(GAP_index_ray) - 1, -1, -1):
            if i == 0 or i == len(GAP_index_ray) - 1: 
                if GAP_index_ray[0][0] == 1 and GAP_index_ray[-1][1] == 181:
                    if abs(GAP_index_ray[0][0] - GAP_index_ray[0][1]) + abs(GAP_index_ray[-1][0] - GAP_index_ray[-1][1]) < 17:
                        del GAP_index_ray[i]
                elif abs(GAP_index_ray[i][0] - GAP_index_ray[i][1]) < 17:
                    del (GAP_index_ray[i])

            elif abs(GAP_index_ray[i][0] - GAP_index_ray[i][1]) < 17:
                del (GAP_index_ray[i])

        #On concatène les gaps qui termine et commence un tour complet
        if len(GAP_index_ray) > 1:
            if GAP_index_ray[-1][-1] == 181 and GAP_index_ray[0][0] == 1:
                GAP_index_ray[0][0] = GAP_index_ray[-1][0]
                del(GAP_index_ray[-1])
        return GAP_index_ray

    def ComputePositiveGap(self, detection_memorie, ray_angles):
        #On calcul l'angle des raies dans le repère du drone
        GAP_size = []
        GAP_angle = []
        GAP_direction = []

        for index in detection_memorie:

            if index[1] > index[2]:
                start_angle = FromRayToAngle(index[1], ray_angles, False)
                end_angle = FromRayToAngle(index[2], ray_angles, False)

                GAP_angle.append([start_angle, end_angle])
                GAP_size.append(abs(start_angle - end_angle))
                GAP_direction.append(normalize_angle((start_angle + end_angle)/2))

            else:
                start_angle = FromRayToAngle(index[1], ray_angles, False)
                end_angle = FromRayToAngle(index[2], ray_angles, False)

                GAP_angle.append([start_angle, end_angle])
                GAP_size.append(abs(start_angle - end_angle))
                GAP_direction.append(normalize_angle((start_angle + end_angle)/2))
        
        Inter_pos_size = []

        for i, angle in enumerate(GAP_direction):
            if i < len(GAP_direction) - 1:
                diff_angle = abs(normalize_angle(GAP_direction[i] - GAP_direction[i+1]))
            else:
                diff_angle = abs(normalize_angle(GAP_direction[i] - GAP_direction[0]))
            Inter_pos_size.append(diff_angle)

        return (GAP_angle, GAP_direction, GAP_size, Inter_pos_size)

    #Modification de liste d'etat self.detectionMemorie en fonction des nouveaux gaps detectes 
    def UpdateGapDetection(self, GAP_index_ray):
        counter_match_memorie_gap = 0
        unmatch_memorie_gap = [gap[0] for gap in self.analyzed_data["positive gap detection memory"]]

        for i, indexs in enumerate(GAP_index_ray):

            counter_match_actual_gap = 0
            unmatch_actual_gap = None

            for k, gap in enumerate(self.analyzed_data["positive gap detection memory"]):
                if len(self.analyzed_data["positive gap detection memory"]) != 0:
                    if gap[1] > gap[2]:
                        #print("a")
                        if indexs[0] > indexs[1]:
                            if indexs[0] <= gap[2] + 181 and indexs[1] + 181 >= gap[1]:
                                if counter_match_actual_gap == 0:
                                    gap[1:3] = indexs
                                    counter_match_actual_gap += 1 
                                    counter_match_memorie_gap += 1
                                    unmatch_memorie_gap.remove(k)
                        if indexs[1] < 90:
                            if indexs[0] + 181 <= gap[2] + 181 and indexs[1] + 181 >= gap[1]:
                                if counter_match_actual_gap == 0:
                                    gap[1:3] = indexs
                                    counter_match_actual_gap += 1 
                                    counter_match_memorie_gap += 1
                                    unmatch_memorie_gap.remove(k)
                        if indexs[0] > 90:
                            if indexs[0] <= gap[2] + 181 and indexs[1] >= gap[1]:
                                if counter_match_actual_gap == 0:
                                    gap[1:3] = indexs
                                    counter_match_actual_gap += 1 
                                    counter_match_memorie_gap += 1
                                    unmatch_memorie_gap.remove(k)

                    if indexs[0] > indexs[1]:
                        #print("a")
                        if gap[1]> gap[2]:
                            if gap[1] <= indexs[1] + 181 and gap[2] + 181 >= indexs[0]:
                                if counter_match_actual_gap == 0:
                                    gap[1:3] = indexs
                                    counter_match_actual_gap += 1 
                                    counter_match_memorie_gap += 1
                                    unmatch_memorie_gap.remove(k)
                        if gap[2] < 90:
                            if gap[1] + 181 <= indexs[1] + 181 and gap[2] + 181 >= indexs[0]:
                                if counter_match_actual_gap == 0:
                                    gap[1:3] = indexs
                                    counter_match_actual_gap += 1 
                                    counter_match_memorie_gap += 1
                                    unmatch_memorie_gap.remove(k)
                        if gap[1] > 90:
                            if gap[1] <= indexs[1] + 181 and gap[2] >= indexs[0]:
                                if counter_match_actual_gap == 0:
                                    gap[1:3] = indexs
                                    counter_match_actual_gap += 1 
                                    counter_match_memorie_gap += 1
                                    unmatch_memorie_gap.remove(k)

                    else:
                        #print("b")
                        if indexs[0] <= gap[2] and indexs[1] >= gap[1]:
                            if counter_match_actual_gap == 0:
                                gap[1:3] = indexs
                                counter_match_actual_gap += 1 
                                counter_match_memorie_gap += 1
                                unmatch_memorie_gap.remove(k)
            #On ajoute les nouveau gap qui n'ont pas match
            if counter_match_actual_gap == 0:
                unmatch_actual_gap = indexs
                num = i
                unmatch_actual_gap.insert(0,i)
                self.analyzed_data["positive gap detection memory"].insert(num, unmatch_actual_gap)
                self.namearrangement(self.analyzed_data["positive gap detection memory"], num)
                unmatch_memorie_gap = [m + 1 if i <= m else m for m in unmatch_memorie_gap]
        #On supprime les anciens gap qui n'ont pas match 
        if counter_match_memorie_gap != len(self.analyzed_data["positive gap detection memory"]):
            for m in reversed(unmatch_memorie_gap):
                del (self.analyzed_data["positive gap detection memory"][m])
                self.namearrangement(self.analyzed_data["positive gap detection memory"], m - 1)
    
    def namearrangement(self, detection_state, name):
        if len(detection_state) == 1:
            detection_state[name][0] = 0
            return(detection_state)
        if name < len(detection_state) - 1:
            if name == -1:
                name = 0
                detection_state[name][0] = 0
                return(self.namearrangement(detection_state,name))
            if detection_state[name+1][0] != detection_state[name][0] + 1:
                detection_state[name+1][0] += -(detection_state[name+1][0] - (detection_state[name][0] + 1))
                return(self.namearrangement(detection_state, name + 1))
            else:
                return(self.namearrangement(detection_state, name + 1))

