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
[image8]: ./misc/.png ""
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
Run the simulator Roversim_x86_64.exe.

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

### 1. We execute the functions that have been provided in the notebook, first with the test data provided, then with the data that I have recorded from the simulator. Add/modify functions to allow color selection of obstacles and rock samples.

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

### 2. I complete the process_image() function with the appropriate analysis steps for mapping pixels by identifying navigable terrain, obstacles and rock samples on a world map. I run process_image() with the test data using the provided movie functions to create a video output as a result.

I have made some modifications to different functions. All details are shown in the jupyter notebook'Rover_Project_Test_Notebook.ipynb'.

- Output Image results with test_dataset provided

![alt text][image6]

- Output Image results with my recorded test data

![alt text][image7]

### Autonomous Navigation and Mapping

#### Fill in the perception_step() (at the bottom of the perception.py script) and decision_step() (in decision.py) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

- A. perception.py modifications:

These color_thresh function modifications make it so that it outputs all 3 thresholds, one for navigable path, rock samples, and rock samples; respectively. Thought, red and green thresholds higher than 100 and blue threshold lower than 50 do to recognize the yellow pixels from the rock samples.

```python
def color_thresh(img, rgb_thresh=(160, 160, 160, 100, 100, 50)):
    # Create an array of zeros same xy size as img, but single channel
    #color_select = np.zeros_like(img[:,:,0])
    color_select_path = np.zeros_like(img[:,:,0])
    color_select_rock = np.zeros_like(img[:,:,0])
    color_select_obst = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
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
    # Index the array of zeros with the boolean array and set to 1
    #color_select[above_thresh] = 1
    color_select_path[above_thresh] = 1
    color_select_rock[between_thresh] = 1
    color_select_obst[below_thresh] = 1
    # Return the binary image
    #return color_select
    return color_select_path, color_select_rock, color_select_obst
```


## The Simulator
The first step is to download the simulator build that's appropriate for your operating system.  Here are the links for [Linux](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Linux_Roversim.zip), [Mac](	https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Mac_Roversim.zip), or [Windows](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Windows_Roversim.zip).  

You can test out the simulator by opening it up and choosing "Training Mode".  Use the mouse or keyboard to navigate around the environment and see how it looks.

## Dependencies
You'll need Python 3 and Jupyter Notebooks installed to do this project.  The best way to get setup with these if you are not already is to use Anaconda following along with the [RoboND-Python-Starterkit](https://github.com/ryan-keenan/RoboND-Python-Starterkit). 


Here is a great link for learning more about [Anaconda and Jupyter Notebooks](https://classroom.udacity.com/courses/ud1111)

## Recording Data
I've saved some test data for you in the folder called `test_dataset`.  In that folder you'll find a csv file with the output data for steering, throttle position etc. and the pathnames to the images recorded in each run.  I've also saved a few images in the folder called `calibration_images` to do some of the initial calibration steps with.  

The first step of this project is to record data on your own.  To do this, you should first create a new folder to store the image data in.  Then launch the simulator and choose "Training Mode" then hit "r".  Navigate to the directory you want to store data in, select it, and then drive around collecting data.  Hit "r" again to stop data collection.

## Data Analysis
Included in the IPython notebook called `Rover_Project_Test_Notebook.ipynb` are the functions from the lesson for performing the various steps of this project.  The notebook should function as is without need for modification at this point.  To see what's in the notebook and execute the code there, start the jupyter notebook server at the command line like this:

```sh
jupyter notebook
```

This command will bring up a browser window in the current directory where you can navigate to wherever `Rover_Project_Test_Notebook.ipynb` is and select it.  Run the cells in the notebook from top to bottom to see the various data analysis steps.  

The last two cells in the notebook are for running the analysis on a folder of test images to create a map of the simulator environment and write the output to a video.  These cells should run as-is and save a video called `test_mapping.mp4` to the `output` folder.  This should give you an idea of how to go about modifying the `process_image()` function to perform mapping on your data.  

## Navigating Autonomously
The file called `drive_rover.py` is what you will use to navigate the environment in autonomous mode.  This script calls functions from within `perception.py` and `decision.py`.  The functions defined in the IPython notebook are all included in`perception.py` and it's your job to fill in the function called `perception_step()` with the appropriate processing steps and update the rover map. `decision.py` includes another function called `decision_step()`, which includes an example of a conditional statement you could use to navigate autonomously.  Here you should implement other conditionals to make driving decisions based on the rover's state and the results of the `perception_step()` analysis.

`drive_rover.py` should work as is if you have all the required Python packages installed. Call it at the command line like this: 

```sh
python drive_rover.py
```  

Then launch the simulator and choose "Autonomous Mode".  The rover should drive itself now!  It doesn't drive that well yet, but it's your job to make it better!  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results!  Make a note of your simulator settings in your writeup when you submit the project.**

### Project Walkthrough
If you're struggling to get started on this project, or just want some help getting your code up to the minimum standards for a passing submission, we've recorded a walkthrough of the basic implementation for you but **spoiler alert: this [Project Walkthrough Video](https://www.youtube.com/watch?v=oJA6QHDPdQw) contains a basic solution to the project!**.


