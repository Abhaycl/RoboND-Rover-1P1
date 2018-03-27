# Search and Sample Return Project Starter Code

The goal of this project is it will give you first hand experience with the three essential elements of robotics, which are perception, decision making and actuation.  You will carry out this project in a simulator environment built with the Unity game engine.
<!--more-->

[//]: # (Image References)

[image0]: ./misc/rover_image.jpg "Rover"
[image1]: ./misc/data_test.jpg "Data Test"
[image2]: ./misc/pictures_for_calibration.jpg "Pictures For Calibration"
[image3]: ./misc/perspective_transform.jpg "Perspective Transform"
[image4]: ./misc/color_thresholding.jpg "Color Thresholding"
[image5]: ./misc/coordinate_transformations.jpg "Coordinate Transformations"
[image6]: ./misc/test_dataset_video.jpg "Test Dataset Video"
[image7]: ./misc/test_data_video.jpg "Test Data Video"
[image8]: ./misc/simulator.jpg "Simulator Parameters"
[image9]: ./misc/.png ""

![alt text][image0]

#### How to run the jupyter test program

```bash
1.  cd code
2.  jupyter notebook Rover_Project_Test_Notebook.ipynb
```

#### How to run the program with the simulator

```bash
1.  cd code
2.  python drive_rover.py
```
Run the simulator Roversim_x86_64.exe

---

The summary of the files and folders int repo is provided in the table below:

| File/Folder                     | Definition                                                                                            |
| :------------------------------ | :---------------------------------------------------------------------------------------------------- |
| calibration_images/*            | Folder that contains the images to calibrate the camera.                                              |
| code/*                          | Folder that contains the source files of the project.                                                 |
| misc/*                          | Folder that contains third-person image of the rover.                                                 |
| output/*                        | It contains the video .mp4 with the test images of the rover on the ground.                           |
| test_dataset/*                  | It contains everything related to the Waypoint updater node.                                          |
|                                 |                                                                                                       |
| README.md                       | Contains the project documentation.                                                                   |

---

### The goals / steps of this project are the following:

- Training / Calibration:
  - Download the simulator and take data in "Training Mode"
  - Test out the functions in the Jupyter Notebook provided
  - Add functions to detect obstacles and samples of interest (golden rocks)
  - Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map. The `output_image` you create in this step should demonstrate that your mapping pipeline works.
  - Use `moviepy` to process the images in your saved dataset with the `process_image()` function. Include the video you produce as part of your submission.

- Autonomous Navigation / Mapping
  - Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook).
  - Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands.
  - Iterate on your perception and decision function until your rover does a reasonable job of navigating and mapping. (Mapping 40% of the map, at 60% Fidelity, and locate at least 1 rock sample).

#### We execute the functions that have been provided in the notebook, first with the test data provided, then with the data that I have recorded from the simulator. Add/modify functions to allow color selection of obstacles and rock samples.

- Collection of test data

![alt text][image1]

- Images for the calibration

![alt text][image2]

- Perspective Transform

![alt text][image3]

- Color Thresholding

![alt text][image4]

- Coordinate Transformations

![alt text][image5]

#### I complete the process_image() function with the appropriate analysis steps for mapping pixels by identifying navigable terrain, obstacles and rock samples on a world map. I run process_image() with the test data using the provided movie functions to create a video output as a result.

I have made some modifications to different functions. All details are shown in the jupyter notebook 'Rover_Project_Test_Notebook.ipynb'.

- Output Image results with test_dataset provided

![alt text][image6]

- Output Image results with my recorded test data

![alt text][image7]

### Autonomous Navigation and Mapping

#### Fill in the perception_step() (at the bottom of the perception.py script) and decision_step() (in decision.py) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

- A. perception.py modifications:

###### 1. These color_thresh function modifications make it so that it outputs all 3 thresholds, one for navigable path, rock samples, and rock samples; respectively. Thought, red and green thresholds higher than 100 and blue threshold lower than 50 do to recognize the yellow pixels from the rock samples.

Thresholds are defined and used to identify the objects, such as the path, obstacles and rocks to be collected.
```python
def color_thresh(img, rgb_thresh=(160, 160, 160, 100, 100, 50)):
```

Create an array of zeros same xy size as img, but single channel.
```python
    color_select_path = np.zeros_like(img[:,:,0])
    color_select_rock = np.zeros_like(img[:,:,0])
    color_select_obst = np.zeros_like(img[:,:,0])
```

Require that each pixel be above all three threshold values in RGB above_thresh will now contain a boolean array with "True" where threshold was met.
```python
    # Threshold for navigable path
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                 & (img[:,:,1] > rgb_thresh[1]) \
                 & (img[:,:,2] > rgb_thresh[2])
    # Threshold for rocks
    between_thresh = (img[:,:,0] > rgb_thresh[3]) \
                   & (img[:,:,1] > rgb_thresh[4]) \
                   & (img[:,:,2] < rgb_thresh[5])
    # Threshold for obstacles
    below_thresh = (img[:,:,0] < rgb_thresh[0]) \
                 & (img[:,:,1] < rgb_thresh[1]) \
                 & (img[:,:,2] < rgb_thresh[2])
```

Index the array of zeros with the boolean array and set to 1.
```python
    color_select_path[above_thresh] = 1
    color_select_rock[between_thresh] = 1
    color_select_obst[below_thresh] = 1
```

Return the binary images
```python
    return color_select_path, color_select_rock, color_select_obst
```

2. Changes to the perspect_transform function generate a second output to consider the outside field of view, which would otherwise be considered part of the obstacles without this method. Also, a mask is obtained to further narrow the field of view

```python
def perspect_transform(img, src, dst):
    M = cv2.getPerspectiveTransform(src, dst)
	# Warped image
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))
	# Mask
    mask = cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1], img.shape[0]))

    # Return warped
    return warped, mask
```

3. Changes to the perception_step() or process_image() function have been made to apply all the functions previously stated to provide a complete computer vision image that can be used to tell the rover where it can travel and where it can't, as well as adding the ability to detect rock samples. I also applied the to_polar_coords() function to the rock 'x' and 'y' pixels to provide the rover distance and direction to where the rock samples are, for steering guidance.

Perform perception steps to update Rover
```python
def perception_step(Rover):
    # Get the images from the rover's camera
    image = Rover.img
```
	
Define source and destination points for perspective transform, define calibration box in source (actual) and destination (desired) coordinates these source and destination points are defined to warp the image to a grid where each 10x10 pixel square represents 1 square meter.
```python
    # The destination box will be 2*distance_size on each side
    distance_size = 5
```

A bottom offset is set to account for the fact that the bottom of the image is not the position of the rover but a bit in front of it this is just a rough guess.
```python
    bottom_offset = 6
    scale = 2 * distance_size
    source = np.float32([[14, 140], [301 ,140], [200, 96], [118, 96]])
    destination = np.float32([[image.shape[1]/2 - distance_size, image.shape[0] - bottom_offset],
                              [image.shape[1]/2 + distance_size, image.shape[0] - bottom_offset],
                              [image.shape[1]/2 + distance_size, image.shape[0] - scale - bottom_offset], 
                              [image.shape[1]/2 - distance_size, image.shape[0] - scale - bottom_offset],])
```

Apply perspective transform to obtain the warped image and .
```python
    warped, mask = perspect_transform(Rover.img, source, destination)
```

Apply color threshold to identify navigable terrain/obstacles/rock samples.
```python
    threshed_path, threshed_rock, threshed_obst = color_thresh(warped)
    obst_map = np.absolute(np.float32(threshed_obst)) * mask
```

Update Rover vision image (this will be displayed on left side of screen).
```python
    Rover.vision_image[:,:,0] = obst_map * 255
    Rover.vision_image[:,:,1] = threshed_rock * 255
    Rover.vision_image[:,:,2] = threshed_path * 255
```

Convert map image pixel values to rover-centric coords.
```python
    obst_xpix, obst_ypix = rover_coords(obst_map)
    rock_xpix, rock_ypix = rover_coords(threshed_rock)
    path_xpix, path_ypix = rover_coords(threshed_path)
```

Convert rover-centric pixel values to world coordinates.
```python
    world_size = Rover.worldmap.shape[0]
    obst_xworld, obst_yworld = pix_to_world(obst_xpix, obst_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size, scale)
    rock_xworld, rock_yworld = pix_to_world(rock_xpix, rock_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size, scale)
    path_xworld, path_yworld = pix_to_world(path_xpix, path_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size, scale)
```

Update Rover worldmap (to be displayed on right side of screen).
```python
    Rover.worldmap[obst_yworld, obst_xworld, 0] += 255
    Rover.worldmap[rock_yworld, rock_xworld, 1] += 255
    Rover.worldmap[path_yworld, path_xworld, 2] += 255
```

Convert rover-centric pixel positions to polar coordinates.
```python
    obst_dist, obst_angles = to_polar_coords(obst_xpix, obst_ypix)
    rock_dist, rock_angles = to_polar_coords(rock_xpix, rock_ypix)
    path_dist, path_angles = to_polar_coords(path_xpix, path_ypix)
```

Update Rover pixel distances and angles.
```python
    Rover.obst_dists = obst_dist
    Rover.rock_dists = rock_dist
    Rover.nav_dists = path_dist
    Rover.obst_angles = obst_angles
    Rover.rock_angles = rock_angles
    Rover.nav_angles = path_angles
```

If you have found and collected all the rocks the initial starting value is set.
```python
    if Rover.mode == 'home':
        Rover.home_dists, Rover.home_angles = to_polar_coords(Rover.start_pos[0], Rover.start_pos[1])
	
	#The values of the rover are returned
    return Rover
```

- B. decision.py modifications:

1. Made these changes to the decision_step() function to provide the extra capability to locate and steer towards rock samples when found, stop when near a sample, and pickup sample when it has stopped in front of the rock sample.

```python
def decision_step(Rover):
    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!
    
    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        #if Rover.mode == 'forward':
        if len(Rover.rock_angles) != 0:
            Rover.sample_pos_found = Rover.rock_angles
            Rover.steer = np.clip(np.mean(Rover.rock_angles * 180 / np.pi), -15, 15)
            if len(Rover.rock_angles) >= 20:
                Rover.sample_pos_found = Rover.rock_dists
                if Rover.vel < 1:
                # Set throttle value to throttle setting
                    Rover.throttle = 0.1
                    Rover.brake = 0
                elif Rover.vel >= 1:
                    Rover.brake = 5
                    Rover.throttle = 0
                else:
                    Rover.throttle = 0
                Rover.brake = 0
            elif len(Rover.rock_angles) <= 20:
                Rover.sample_pos_found = len(Rover.rock_angles)
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
                    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
                        Rover.send_pickup = True
        elif Rover.mode == 'forward' and len(Rover.rock_angles) == 0 and Rover.near_sample == 0: 
            Rover.sample_pos_found = len(Rover.rock_angles)
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
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
        
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
    
    return Rover
```

- C. drive_rover.py modifications:

1. Made these changes to the init() function to provide the extra variables to the rover for storing rock sample distance and angles, along with a string variable that's used to prompt in different situations for testing and debugging purposes.

```python
    def __init__(self):
        self.start_time = None # To record the start time of navigation
        self.total_time = None # To record total duration of naviagation
        self.img = None # Current camera image
        self.pos = None # Current position (x, y)
        self.yaw = None # Current yaw angle
        self.pitch = None # Current pitch angle
        self.roll = None # Current roll angle
        self.vel = None # Current velocity
        self.steer = 0 # Current steering angle
        self.throttle = 0 # Current throttle value
        self.brake = 0 # Current brake value
        self.nav_angles = None # Angles of navigable terrain pixels
        self.nav_dists = None # Distances of navigable terrain pixels
        self.ground_truth = ground_truth_3d # Ground truth worldmap
        self.mode = 'forward' # Current mode (can be forward or stop)
        #self.throttle_set = 0.2 # Throttle setting when accelerating
        self.throttle_set = 0.6 # Throttle setting when accelerating
        self.brake_set = 10 # Brake setting when braking
        # The stop_forward and go_forward fields below represent total count
        # of navigable terrain pixels.  This is a very crude form of knowing
        # when you can keep going and when you should stop.  Feel free to
        # get creative in adding new fields or modifying these!
        #self.stop_forward = 50 # Threshold to initiate stopping
        self.stop_forward = 100 # Threshold to initiate stopping
        #self.go_forward = 500 # Threshold to go forward again
        self.go_forward = 1000 # Threshold to go forward again
        self.max_vel = 2 # Maximum velocity (meters/second)
        # Image output from perception step
        # Update this image to display your intermediate analysis steps
        # on screen in autonomous mode
        self.vision_image = np.zeros((160, 320, 3), dtype=np.float) 
        # Worldmap
        # Update this image with the positions of navigable terrain
        # obstacles and rock samples
        self.worldmap = np.zeros((200, 200, 3), dtype=np.float) 
        self.samples_pos = None # To store the actual sample positions
        self.samples_to_find = 0 # To store the initial count of samples
        self.samples_located = 0 # To store number of samples located on map
        self.samples_collected = 0 # To count the number of samples collected
        self.near_sample = 0 # Will be set to telemetry value data["near_sample"]
        self.picking_up = 0 # Will be set to telemetry value data["picking_up"]
        self.send_pickup = False # Set to True to trigger rock pickup
        self.rock_dists = 0 # rock distances by perception_step
        self.rock_angles = 0 # rock angles by perception_step
        self.sample_pos_found = None # to print string of sample position situation
```

#### Launching in autonomous mode your rover can navigate and map autonomously. Explain your results and how you might improve them in your writeup.

In autonomous mode, I managed to map at least 40% with at least 60% fidelity. Also, some capability to detect, navigate towards rock samples, and pick them up was added. There are instances where it would crash against the rocks in the middle of the map, sometimes getting stuck. Also, sometimes it stays in a loop going to the same places over and over, or just stays around in circles looking for a greater navigable path.

Would further optimization be pursued, it would be in the better obstacle detection area (specially rocks in the middle of the map, not big enough to be perceived as obstacle), along with better decision making after it notices it stayed in a loop, and running in circles.

#### Running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines! Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by drive_rover.py) in your writeup when you submit the project so your reviewer can reproduce your results.

![alt text][image8]

### Observations, possible improvements, things used

I applied the perception step functions to provide computer vision leveraging the Rover data set up in the drive_rover.py; from color_thresh() to pix_to_world(). Modified slightly the color_thresh() function to output the 3 threshold required to detect obstacles, path, and rock samples. Furthermore, added directional data to Rover for rock samples by applying to_polar_coords() to rock pixels.

Also, in the decision_step() function, I added simple if and elif chain events to trigger stopping and slower speeds upon detecting rock samples, with some steering towards the rock pixel angles provided by the perception step, the movements are a little abrupt. Occasionally, it stops on top of the rock samples and gets stuck. The rover sometimes, stays running around in circles, not sure if this is due to the frames per seconds (FPS) or if it's perception_step() that could be improved.

I would improve time optimization to have the rover run and stop more efficiently. Furthermore, make the rover go back to where it started; this might be tight together with position awareness that would also prevent the rover from running around in circles.