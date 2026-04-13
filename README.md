# Step 4: Making the tree structure's branches have more width


![image](./readme_images/1.png)
![image](./readme_images/2.png)

## Description
- The idea here is that tree is broken up into layers, where each layer represents the tree at a certain stage of growth. By blurring and image then applying a threshold operation, you can make a shape bigger. This is what I do here. The trick is that each new particle (pixel) added to the tree gets blurred increasingly after it is added. 
- That was the goal but in this implementation there was some kind of 8 bit overflow error when trying to make larger images. The error looks cool though so I put them in here:
- Had to increase the resolution of the images to allow to blur to act more smoothly. 
- You can get very different results by change the blur amount, the threshold, and amount that the image size is upscaled. The two images above are examples of the different looks that can be acheived. 

## Interesting error 1
This one was due to an 8 bit overflow
![image](./readme_images/3.gif)
![image](./readme_images/4.jpg)


## Interesting error 2
This one occured when I messed up the order of operations for the blurring and stacking of layers
![image](./readme_images/5.png)
![image](./readme_images/6.png)





## Next Step
[Step 5: Correct blurring and stacking](https://github.com/jj-gagnon/CART-263-DLA/tree/step-5-correct-blur-and-stacking)


## Table of Contents
[Step 1: Simple and slow](https://github.com/jj-gagnon/CART-263-DLA/tree/step-1-simple-and-slow)

[Step 2: Failed optimization](https://github.com/jj-gagnon/CART-263-DLA/tree/step-2-failed-optimization)

[Step 3: Spawn new particles only on bounding circle](https://github.com/jj-gagnon/CART-263-DLA/tree/step-3-spawn-points-on-circle)

[Step 4: Making the tree structure's branches have more width](https://github.com/jj-gagnon/CART-263-DLA/tree/step-4-accumulative-blurring-and-threshold)

[Step 5: Correct blurring and stacking](https://github.com/jj-gagnon/CART-263-DLA/tree/step-5-correct-blur-and-stacking)

[Step 6: Creating image layers and converting to SVG](https://github.com/jj-gagnon/CART-263-DLA/tree/step-6-converting-to-image-layers-and-svg)

[Step 7: Optimizing with Numba](https://github.com/jj-gagnon/CART-263-DLA/tree/step-7-optimizing-with-numba)

[Step 8: First and second laser cut tests](https://github.com/jj-gagnon/CART-263-DLA/tree/step-8-first-and-second-test-laser-cut)

[Step 9: Finalizing the design](https://github.com/jj-gagnon/CART-263-DLA/tree/step-9-first-attempt-at-finalizing-the-design)

[Step 10: Preparing files for laser cutter](https://github.com/jj-gagnon/CART-263-DLA/tree/step-10-preparing-files)

[Step 11: Assembly](https://github.com/jj-gagnon/CART-263-DLA/tree/step-11-assembly)

[Step 12: Finished](https://github.com/jj-gagnon/CART-263-DLA/tree/step-12-finished)
