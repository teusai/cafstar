## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

"""
functions for setting up the RealSense depth camera, acquiring images, and detecting circles

To run stand alone test:
python camera.py

"""

import pyrealsense2 as rs
import numpy as np
import cv2

def setConfig(depth, color):                          # Configure depth and color streams
   pipeline = rs.pipeline()
   config = rs.config()

   # Get device product line for setting a supporting resolution
   pipeline_wrapper = rs.pipeline_wrapper(pipeline)
   pipeline_profile = config.resolve(pipeline_wrapper)
   device = pipeline_profile.get_device()
   device_product_line = str(device.get_info(rs.camera_info.product_line))

   found_rgb = False
   for s in device.sensors:
       if s.get_info(rs.camera_info.name) == 'RGB Camera':
           found_rgb = True
           break
   if not found_rgb:
       print("The demo requires Depth camera with Color sensor")
       exit(0)

   if depth == True:
      if device_product_line == 'L500':
         config.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)
      else:
         config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
   if color == True:
      if device_product_line == 'L500':
          config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
      else:
          config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

   return config, pipeline

def startStream(config, pipeline):       # Start streaming
   pipeline.start(config)

def getFrames(pipeline, depth, color):
   depth_image = 0
   color_image = 0
   got_frame = False

   frames = pipeline.poll_for_frames()
   if frames.is_frame():
      got_frame = True
      if depth == True:
         depth_frame = frames.get_depth_frame()
         depth_image = np.asanyarray(depth_frame.get_data())
         depth_image[depth_image > 3800] = 0
         depth_image[depth_image < 3200] = 0
         depth_image = depth_image[230:525, 470:1000]
         depth_image = cv2.resize(depth_image, (1280, 720))
         depth_image = np.flipud(depth_image)
         
      if color == True:
         color_frame = frames.get_color_frame()
         color_image = np.asanyarray(color_frame.get_data())
         color_image = np.flipud(color_image)

   return got_frame, depth_image, color_image

def stopStreaming(pipeline):
   pipeline.stop()

def getCircles(depth_image, minDist, p1, p2, Rmin, Rmax):
   circleL = []

   # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
   depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=1), cv2.COLORMAP_BONE)

   grayImg = cv2.cvtColor(depth_colormap, cv2.COLOR_BGR2GRAY)
   grayImg = cv2.blur(grayImg, (3,3)) # probably won't need this

   # depth_colormap = grayImg
   dp = 1.		# ratio of input image to accumulator
   #minDist = 200	# between detected circles
   #p1 = 102		# currently 102, increasing detects fewer circles
   #p2 = 12		# currently 12, reducing detects more circles
   #Rmin = 15		# 15 for 14'
   #Rmax = 50		# 50 for 14'
   circles = cv2.HoughCircles(grayImg, cv2.HOUGH_GRADIENT, dp, minDist, param1=p1, param2=p2, minRadius=Rmin, maxRadius=Rmax)
        
   if circles is not None:
        #print(circles)
        circleL = circles[0]			# returns a list containing 1 list
   return circleL, depth_colormap

if __name__ == "__main__":
   depth = True
   color = False
   config, pipeline = setConfig(depth, color)
   startStream(config, pipeline)

   depth_Image = 0
   color_image = 0

   cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)

   for i in range(5000):
        got_frame, depth_image, color_image = getFrames(pipeline, depth, color)   # returns numpy arrays
        
        if got_frame == True:
         depth_image = np.fliplr(depth_image)
                  
         depth_image[depth_image > 3900] = 0    	# 14' ceiling = 4,267 mm from floor.  Clear pixels > 3,300 mm from camera
         depth_image[depth_image < 3200] = 0	# clear pixels < 2,200 from camera
         depth_image = 2 * depth_image    # if the environment is clean and there are no false positives then scale up the depth image so the data in range has higher contrast.  This improves circle detection.

         cL, depth_colormap = getCircles(depth_image, 200, 102, 16, 15, 50)

         for xyr in cL:
            #print(xyr[0], xyr[1], xyr[2])
            center = (int(xyr[0]), int(xyr[1]))
            radius = int(xyr[2])
            cv2.circle(depth_colormap, center, radius, (0,255,255), 30)    # draw the outer circle
            if center[0] < 1280 and center[1] < 720:
               print(center, radius, depth_image[center[1], center[0]])

         if depth and color:
            depth_colormap_dim = depth_colormap.shape
            color_colormap_dim = color_image.shape

            # If depth and color resolutions are different, resize color image to match depth image for display
            if depth_colormap_dim != color_colormap_dim:
                  resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
                  images = np.hstack((depth_colormap, resized_color_image))
            else:
                  images = np.hstack((depth_colormap, color_image))
         elif depth:
               images = depth_colormap
         elif color:
               images = color_image

         # Show images
         cv2.imshow('RealSense', images)
        cv2.waitKey(1)

   stopStreaming(pipeline)