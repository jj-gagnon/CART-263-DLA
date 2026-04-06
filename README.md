# Step 3: Spawn new particles only on bounding circle

![gif](./gif.gif)

![image](./image.jpg)

# Description
- Animation no longer shows the random motion of the particles. Only the tree as more particles stick to it. 
- Spawn new particles randomly along a circle that is just bigger than the tree structure and gets larger as the tree grows. Which is colored in dark grey in the gif above. 
- There is now a despawn radius which if a particle wanders past it will be deleted. This is colored in light grey in the gif above. 
- These optimizations made a big difference. 
