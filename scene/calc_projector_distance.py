"""
We've been using 14' as the height (distance from projector lens to floor)
recent area of projection estimate came back smaller than expected
using 11'1" (3.35m) as the width of the screen
this calculates a new height of 12' 4" (3.77m)
"""

# %%
import math

# Projector specifications
throw_ratio = 1.8
aspect_ratio = 1920 / 1200

# Calculate FOV
horizontal_fov = 2 * math.atan((aspect_ratio) / (2 * throw_ratio))
vertical_fov = 2 * math.atan(1 / (2 * throw_ratio))

# Convert from radians to degrees
horizontal_fov_degrees = math.degrees(horizontal_fov)
vertical_fov_degrees = math.degrees(vertical_fov)

horizontal_fov_degrees, vertical_fov_degrees

# %%
# (47.92497794915637, 31.048221993508516)

# %%
# distance of projector from screen when screen is 3.35 m wide
# 3.35 m / 2 = 1.675 m
distance = 1.675 / math.tan(horizontal_fov / 2)
distance 

# %%
# 3.77 m = 12.35 feet ~ 12' 4" <-- lens height from floor