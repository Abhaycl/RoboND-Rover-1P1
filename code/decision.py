import numpy as np


# Check that the rover is at the proper angle to accelerate or continue turning within the defined areas
def turn(Rover, yaw_angle):
    # The rover will turn to a suitable navigable position
    if Rover.yaw <= yaw_angle + 9 and Rover.yaw >= yaw_angle - 9:
        # When the rover does not rotate, it will accelerate
        throttle = True
    else:
        # When the rover rotates, it will not accelerate
        throttle = False
        # Turn range is 15 degrees, when stopped the next line will induce 4-wheel turning
        Rover.steer = 15
    
    return throttle


# The rover can get stuck with some object, it will decelerate while it turns
def stuck(Rover, mode, throttle):
    # In large areas the rover seldom makes circles, with this we deflect it
    if (Rover.vel >= Rover.max_vel and Rover.steer == 15) or (Rover.vel >= Rover.max_vel and Rover.steer == -15):
        Rover.steer = 0
    
    # If the rover gets stuck with an object
    if(Rover.vel > 0.05 and Rover.mode != mode):
        Rover.stuck_time = 0
    elif (Rover.total_time > 1 and Rover.vel == 0.0):
        if Rover.stuck_time == 0:
            Rover.stuck_time = Rover.total_time
        elif (Rover.total_time - Rover.stuck_time) > 1:
            # The rover's going backwards
            Rover.throttle = throttle
            # If there are valid values from the navigation path
            if (np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)) >= 0 or (np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15) < 0):
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            else:
                Rover.steer = 15


# This is where you can build a decision tree for determining throttle, brake and steer
# commands based on the output of the perception_step() function
def decision_step(Rover):
    
    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!
    
    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # The rover has located a sample of rock
        if len(Rover.rock_angles) != 0:
            # Set steering to average angle clipped to the range +/- 15
            Rover.steer = np.clip(np.mean(Rover.rock_angles * 180 / np.pi), -15, 15)
            if len(Rover.rock_angles) >= 20:
                if Rover.vel < 1:
                    # Set throttle value to throttle setting
                    Rover.throttle = 0.35
                    Rover.brake = 0
                elif Rover.vel >= 1:
                    Rover.brake = 5
                    Rover.throttle = 0
                else:
                    Rover.throttle = 0
                    Rover.brake = 0
                
                #stuck(Rover, mode = 'picking up', throttle = -0.5)
            
            elif len(Rover.rock_angles) < 20:
                # Set mode to "stop" and hit the brakes
                if Rover.vel < 0.7:
                # Set throttle value to throttle setting
                    Rover.throttle = 0.1
                    Rover.brake = 0
                elif Rover.vel >= 0.7:
                    Rover.throttle = 0
                    Rover.brake = 5
                else:
                    Rover.throttle = 0
                # Set brake to stored brake value
                if Rover.near_sample:
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    # If the rover is near the sample, it will proceed to collect the rock
                    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
                        Rover.send_pickup = True
        
        # If there is a suitable navigable road, check for Rover.mode status
        elif Rover.mode == 'forward' and len(Rover.rock_angles) == 0 and Rover.near_sample == 0:
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:
                # If mode is forward, navigable terrain looks good
                # and velocity is below max, then throttle
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                #tmp = np.clip(np.mean(Rover.nav_angles * 180 / np.pi), -15, 15)
                #Rover.steer = np.clip(tmp - 3 if tmp <= 0 else tmp + 3, -8, 8)
                
                # If the rover gets stuck, it will decelerate by rotating
                stuck(Rover, mode = 'forward', throttle = -1)
            
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                # Set mode to "stop" and hit the brakes!
                Rover.throttle = 0
                # Set brake to stored brake value
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop' and len(Rover.rock_angles) == 0:
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15
                # If we're stopped but see sufficient navigable terrain in front then go!
                elif len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    if Rover.samples_to_find == Rover.samples_collected:
                        # Indicates maximum separation from the starting point
                        Rover.dist_fin = abs(Rover.rover_dists - Rover.home_dists)
                        Rover.mode = 'return'
                    else:
                        Rover.mode = 'forward'
        
        # If we have collected all the samples, return home
        elif Rover.mode == 'return':
            # Distance from origin to rover
            dist_ent = abs(Rover.rover_dists - Rover.home_dists)
            
            # If the rover is in an area near the origin it will stop after it has collected all the rocks
            if (Rover.rover_dists < Rover.home_dists + 4) and (Rover.rover_dists > Rover.home_dists - 4):
                # Set mode to "stop" and hit the brakes!
                Rover.mode = 'STOP HOME'
                Rover.throttle = 0
                Rover.steer = 0
                # Set brake to stored brake value
                Rover.brake = Rover.brake_set
            
            elif dist_ent < Rover.dist_fin:
                # Indicates maximum separation from the starting point
                Rover.dist_fin = abs(Rover.rover_dists - Rover.home_dists)
                
                # Check the extent of navigable terrain
                if len(Rover.nav_angles) >= Rover.stop_forward:
                # If mode is forward, navigable terrain looks good
                # and velocity is below max, then throttle
                    if Rover.vel < Rover.max_vel:
                        # Set throttle value to throttle setting
                        Rover.throttle = Rover.throttle_set
                    else: # Else coast
                        Rover.throttle = 0
                    Rover.brake = 0
                    # Distance from origin to rover
                    dist_ent = abs(Rover.rover_dists - Rover.home_dists)
                    # Set steering to average angle clipped to the range +/- 15
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    
                    # If the rover gets stuck, it will decelerate by rotating
                    stuck(Rover, mode = 'return', throttle = -1)
                
                # If there's a lack of navigable terrain pixels then go to 'stop' mode
                elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    # If we're in stop mode but still moving keep braking
                    if Rover.vel > 0.2:
                        Rover.throttle = 0
                        Rover.brake = Rover.brake_set
                        Rover.steer = 0
                        # If we're not moving (vel < 0.2) then do something else
                    elif Rover.vel <= 0.2:
                        # Now we're stopped and we have vision data to see if there's a path forward
                        if len(Rover.nav_angles) < Rover.go_forward:
                            Rover.throttle = 0
                            # Release the brake to allow turning
                            Rover.brake = 0
                            # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                            Rover.steer = -15
                        # If we're stopped but see sufficient navigable terrain in front then go!
                        elif len(Rover.nav_angles) >= Rover.go_forward:
                            # Set throttle back to stored value
                            Rover.throttle = Rover.throttle_set
                            # Release the brake
                            Rover.brake = 0
                            # Distance from origin to rover
                            dist_ent = abs(Rover.rover_dists - Rover.home_dists)
                            # Set steer to mean angle
                            Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            
            else:
                # Stops the rover to rotate
                if Rover.vel > 0:
                    Rover.brake = Rover.brake_set
                
                Rover.throttle = 0
                Rover.brake = 0
                throttle = False
                
                # Delimitation of the navigable area for rover orientation
                if (Rover.pos[0] > 54) and (Rover.pos[0] < 63) and (Rover.pos[1] > 96) and (Rover.pos[1] < 107):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 263)
                elif (Rover.pos[0] > 12) and (Rover.pos[0] <= 63) and (Rover.pos[1] > 91) and (Rover.pos[1] < 104):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 350)
                elif (Rover.pos[0] > 73) and (Rover.pos[0] < 86) and (Rover.pos[1] > 69) and (Rover.pos[1] < 79):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 52)
                elif (Rover.pos[0] >= 63) and (Rover.pos[0] < 88) and (Rover.pos[1] > 76) and (Rover.pos[1] < 94):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 334)
                
                # Delimitation of the navigable area for rover orientation
                if (Rover.pos[0] > 114) and (Rover.pos[0] < 123) and (Rover.pos[1] > 45) and (Rover.pos[1] < 52):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 189)
                elif (Rover.pos[0] > 101) and (Rover.pos[0] < 119) and (Rover.pos[1] > 7) and (Rover.pos[1] < 73):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 98)
                
                # Delimitation of the navigable area for rover orientation
                if (Rover.pos[0] > 99) and (Rover.pos[0] < 107) and (Rover.pos[1] > 180) and (Rover.pos[1] < 193):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 272)
                elif (Rover.pos[0] > 100) and (Rover.pos[0] < 134) and (Rover.pos[1] > 115) and (Rover.pos[1] < 180):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 289)
                
                # Delimitation of the navigable area for rover orientation
                if (Rover.pos[0] >= 88) and (Rover.pos[0] < 99) and (Rover.pos[1] > 73) and (Rover.pos[1] < 90):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 78)
                
                # Delimitation of the navigable area for rover orientation
                if (Rover.pos[0] > 104) and (Rover.pos[0] < 108) and (Rover.pos[1] > 80) and (Rover.pos[1] < 85):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 190)
                elif (Rover.pos[0] > 135) and (Rover.pos[0] < 147) and (Rover.pos[1] > 90) and (Rover.pos[1] < 100):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 120)
                elif (Rover.pos[0] > 146) and (Rover.pos[0] < 151) and (Rover.pos[1] > 108) and (Rover.pos[1] < 111):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 142)
                elif (Rover.pos[0] >= 99) and (Rover.pos[0] < 148) and (Rover.pos[1] > 73) and (Rover.pos[1] < 115):
                    # The rover will turn to a suitable navigable position
                    throttle = turn(Rover, 198)
                
                if throttle:
                    # The rover will move
                    Rover.steer = 0
                    Rover.throttle = Rover.throttle_set
                    # Distance from origin to rover
                    dist_ent = abs(Rover.rover_dists - Rover.home_dists)
                else:
                    # Indicates maximum separation from the starting point
                    Rover.dist_fin = abs(Rover.rover_dists - Rover.home_dists)
            
            #print(Rover.mode)
            #print("POSICION INTERMEDIA:", dist_ent)
            #print("PUNTO FINAL: ", Rover.dist_fin)
            #print("DISTANCIA ROVER: ", Rover.rover_dists)
            #print("ANGULO ROVER: ", Rover.rover_angles)
            #print("DISTANCIA HOME: ", Rover.home_dists)
            #print("ANGULO HOME: ", Rover.home_angles)
            #print("NAV ANGLES: ", Rover.nav_angles)
            #print("ACELERACION: ", Rover.throttle)
            #print("FRENO: ", Rover.brake)
            #print("GIRO: ", Rover.steer)
    
    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
    
    #if Rover.samples_collected >= 1 and Rover.pos_fin == True:
    #    Rover.pos_fin = False
    #    Rover.dist_fin = abs(Rover.rover_dists - Rover.home_dists)
    #    Rover.mode = 'return'
    
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
    
    return Rover