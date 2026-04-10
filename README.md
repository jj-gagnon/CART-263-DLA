# Step 9: Finalizing the design



## Description
- I had all the pieces and ideas that I needed so I tried tuning parameters to try and nail in a final design. 
- I was able to apply a seed for all the randomness in the program so that I could find a tree shape that I liked. 
- I tried many seeds and many settings and was converging on a look that I was happy with. 
- Then I realized that some of the raster images were not being properly converted to SVG. This was the start of a very long and frustrating path trying to figure out the error. There were 140 layers and all but only 1 or 2 work perfectly. There was no error thrown. The erroneous output would just be a slightly off-black image that was way smaller than it should be. 
- Anyway after much much trial and error I gave up. The best guess I had was that there are certain configurations of pixels that break the library I was using, which was vtracer. 
- I tried another path tracing library and it worked, although at the cost of taking about an hour to convert all the raster layers to SVG images, even when using multiprocessing. 
- Thankfully I only had to make changes once or twice though before nailing in my final design. 
- Sadly the second library I used change the pattern of the location of the dots to be a bit more random. 


(This image is large. open image in new tab to zoom in on detail)
![image](./readme_images/1.png)

![image](./readme_images/2.png)

![image](./readme_images/3.png)

![image](./readme_images/4.png)

![image](./readme_images/5.png)
