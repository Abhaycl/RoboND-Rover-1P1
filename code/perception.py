import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
#def color_thresh(img, rgb_thresh=(160, 160, 160)):
def color_thresh(img, min_path=np.array([159, 159, 159]), max_path=np.array([255, 255, 255]),
                      min_rock=np.array([93, 173, 131]), max_rock=np.array([98, 255, 182]),
                      min_obst=np.array([0, 0, 0]), max_obst=np.array([140, 140, 140])):
    # Create an array of zeros same xy size as img, but single channel
    #color_select = np.zeros_like(img[:,:,0])
    color_select_path = np.zeros_like(img[:,:,0])
    color_select_rock = np.zeros_like(img[:,:,0])
    color_select_obst = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    # Threshold for navigable path
    above_thresh = ((img[:, :, 0] > min_path[0]) & (img[:, :, 0] <= max_path[0])) \
                 & ((img[:, :, 1] > min_path[1]) & (img[:, :, 1] <= max_path[1])) \
                 & ((img[:, :, 2] > min_path[2]) & (img[:, :, 2] <= max_path[2]))
    # Threshold for rocks
    # Convert BGR to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image to get only yellow colors
    between_thresh = ((hsv[:, :, 0] > min_rock[0]) & (hsv[:, :, 0] <= max_rock[0])) \
                   & ((hsv[:, :, 1] > min_rock[1]) & (hsv[:, :, 1] <= max_rock[1])) \
                   & ((hsv[:, :, 2] > min_rock[2]) & (hsv[:, :, 2] <= max_rock[2]))
    # Threshold for obstacles
    below_thresh = ((img[:, :, 0] > min_obst[0]) & (img[:, :, 0] <= max_obst[0])) \
                 & ((img[:, :, 1] > min_obst[1]) & (img[:, :, 1] <= max_obst[1])) \
                 & ((img[:, :, 2] > min_obst[2]) & (img[:, :, 2] <= max_obst[2]))
    # Index the array of zeros with the boolean array and set to 1
    #color_select[above_thresh] = 1
    color_select_path[above_thresh] = 1
    color_select_rock[between_thresh] = 1
    color_select_obst[below_thresh] = 1
    # Return the binary images for each objects
    #return color_select
    return color_select_path, color_select_rock, color_select_obst


# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles


# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated


def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world


# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    mask = cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1], img.shape[0]))
    #return warped
    return warped, mask


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    # Define calibration box in source (actual) and destination (desired) coordinates
    # These source and destination points are defined to warp the image
    # to a grid where each 10x10 pixel square represents 1 square meter
    # The destination box will be 2*distance_size on each side
    distance_size = 5
    scale = 2 * distance_size
    # Set a bottom offset to account for the fact that the bottom of the image 
    # is not the position of the rover but a bit in front of it
    # this is just a rough guess, feel free to change it!
    image = Rover.img
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140], [200, 96], [118, 96]])
    destination = np.float32([[image.shape[1]/2 - distance_size, image.shape[0] - bottom_offset],
                              [image.shape[1]/2 + distance_size, image.shape[0] - bottom_offset],
                              [image.shape[1]/2 + distance_size, image.shape[0] - scale - bottom_offset], 
                              [image.shape[1]/2 - distance_size, image.shape[0] - scale - bottom_offset],])
    # 2) Apply perspective transform
    warped, mask = perspect_transform(Rover.img, source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    threshed_path, threshed_rock, threshed_obst = color_thresh(warped)
    obst_map = np.absolute(np.float32(threshed_obst)) * mask
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
    Rover.vision_image[:,:,0] = obst_map * 255
    Rover.vision_image[:,:,1] = threshed_rock * 255
    Rover.vision_image[:,:,2] = threshed_path * 255
    # 5) Convert map image pixel values to rover-centric coords
    obst_xpix, obst_ypix = rover_coords(obst_map)
    rock_xpix, rock_ypix = rover_coords(threshed_rock)
    path_xpix, path_ypix = rover_coords(threshed_path)
    # 6) Convert rover-centric pixel values to world coordinates
    world_size = Rover.worldmap.shape[0]
    obst_xworld, obst_yworld = pix_to_world(obst_xpix, obst_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size, Rover.scale)
    rock_xworld, rock_yworld = pix_to_world(rock_xpix, rock_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size, Rover.scale)
    path_xworld, path_yworld = pix_to_world(path_xpix, path_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size, Rover.scale)
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    # Don't corrupt perspective and thus map fidelity.
    if (Rover.roll < 1.0 or Rover.roll < 359.0) and (Rover.pitch < 1.0 or Rover.pitch < 359.0):
        Rover.worldmap[obst_yworld, obst_xworld, 0] = 255
        Rover.worldmap[rock_yworld, rock_xworld, 1] = 255
        Rover.worldmap[path_yworld, path_xworld, 2] = 255
    # 8) Convert rover-centric pixel positions to polar coordinates
    obst_dist, obst_angles = to_polar_coords(obst_xpix, obst_ypix)
    rock_dist, rock_angles = to_polar_coords(rock_xpix, rock_ypix)
    path_dist, path_angles = to_polar_coords(path_xpix, path_ypix)
    rover_dist, rover_angles = to_polar_coords(Rover.pos[0], Rover.pos[1])
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    Rover.obst_dists = obst_dist
    Rover.obst_angles = obst_angles
    Rover.rock_dists = rock_dist
    Rover.rock_angles = rock_angles
    Rover.nav_dists = path_dist
    Rover.nav_angles = path_angles
    Rover.rover_dists = rover_dist
    Rover.rover_angles = rover_angles
    
    # Keep the initial position
    if Rover.pos_ini:
        Rover.pos_ini = False
        Rover.home_dists = rover_dist
        Rover.home_angles = rover_angles
    
    return Rover