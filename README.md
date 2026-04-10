# Step 7: Optimizing with Numba

![image](./readme_images/1.png)

## Description
- used numba to dramitcally increase the speed of the actual DLA simulation to get the initial discrete brownian tree. 
	- Sadly this required leaving the OOP approach i using before. 
- tried using numba to optimize the stacking, blurring, and layering process. After much hard work and problem solving I finally got numba working on the required fucntions only to find that it was much slower than just using numpy. One of the main reasons is that Numba does not allow multidimensional indexing. So all the image arrays had to be flattened first and then reshaped over and over again. The learning lesson here is the Numba works really really well for when you have are writing nested for loops in python. But if you are already using a library that is optimized and whose backend is c/c++/rust then using numba probably wont be much faster. 
- With numba i could make much larger brownian trees. 

## Interesting error
- Forgot to stop a particle from continuing once it has been frozen to the tree. So particles would keep drawing and make a sort of fractal and noisy path. 

![image](./readme_images/2.gif)


Open image in a new tab to zoom in on the detail:

![image](./readme_images/3.png)