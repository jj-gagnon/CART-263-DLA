import random
import time
import cv2
import numpy as np


def check_for_neighbour(point, pixels):
    point = list(point)
    if pixels[point[0] + 1, point[1]] == 255:
        return True
    elif pixels[point[0] - 1, point[1]] == 255:
        return True
    elif pixels[point[0], point[1] + 1] == 255:
        return True
    elif pixels[point[0], point[1] - 1] == 255:
        return True
    return False


# def check_for_neighbour_distance(point, pixels, distance):
def check_for_neighbour_distance(point, pixels, distance):
    x, y = point
    # points = list()
    counter = 0
    for i in range(x - distance, x + distance + 1):
        for j in range(y - distance, y + distance + 1):
            if pixels[i, j] == 255:
                counter += 1
            # points.append((x,y))

    if counter > 0:
        return True
    else:
        return False


h = 100
w = 100
pixels = np.zeros((h, w), dtype=np.uint8)
center = (h // 2, w // 2)
pixels[center] = 255

# print(center)
# pixels[99,99] = 255
# pixels[98,98] = 255
# pixels[97,97] = 255
# pixels[96,96] = 255
#
# check_for_neighbour_distance(center,pixels, 2)
# exit()


win_name = "animation"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
# 2. Set the window size (width, height)
cv2.resizeWindow(win_name, 600, 600)
# new_points = [center]

new_points = list()

num_points = 2000

new_points_x = np.random.randint(4, w - 4, num_points)
new_points_y = np.random.randint(4, h - 4, num_points)
new_points = np.column_stack([new_points_y, new_points_x])

new_points = list(new_points)
for i in range(num_points):
    new_points[i] = tuple(new_points[i])

# fps = 30
fps = 30
# fps = 1000

num_move_steps = 20000

new_points = list(new_points)
for i in range(num_points):
    new_points[i] = tuple(new_points[i])

# for point in new_points:
#     if check_for_neighbour_distance(point, pixels, 3):
#         new_points.remove(point)

# print(new_points)
# print(tuple(new_points[0]))
# exit()

# center = (center[0] + 1, center[1])
# center = (0,98)

for num_move_steps_i in range(num_move_steps):
    # continue
    t = time.perf_counter()

    # for point in new_points:
    #     pixels[point] = 0

    # check which points have stuck to structure
    # points_to_del = list()
    break_outer = False
    for point in new_points:

        # print(pixels[new_points[num_points_i]])

        # if point[0] == 0 or point[0] == h - 1 or point[1] == 0 or point[1] == w - 1:
        if point[0] < 4 or point[0] > w - 4 or point[1] < 4 or point[1] > h - 4:
            new_points.remove(point)
            # print("on the edge")
        elif pixels[point] == 255:
            new_points.remove(point)
            # print("on top of")

            # if point[0] > max_h:
            #     max_h = point[0]
            # if point[0] < min_h:
            #     min_h = point[0]
            # if point[1] > max_w:
            #     max_w = point[1]
            # if point[1] < min_w:
            #     min_w = point[1]


        elif check_for_neighbour(point, pixels):

            pixels[point] = 255


            if point[0] < 4 or point[0] > w - 4 or point[1] < 4 or point[1] > h - 4:
                break_outer = True

            new_points.remove(point)


    if break_outer:
        break
    # print("new points", new_points)

    # delete points that have been stuck to structure
    # for point in points_to_del:
    #     del new_points[point]

    for point_i in range(len(new_points)):
        x_move = 0
        y_move = 0
        if np.random.rand() > 0.5:
            x_move = random.choice([1, -1])
        else:
            y_move = random.choice([1, -1])

        new_points[point_i] = (
            new_points[point_i][0] + x_move,
            new_points[point_i][1] + y_move
        )





    for point in new_points:

        pixels[point] = 255

    cv2.imshow(win_name, pixels)
    cv2.imwrite("./out/" + str(num_move_steps_i) + ".jpg", pixels)

    for point in new_points:
        pixels[point] = 0

    if cv2.waitKey(1) == ord('q'):
        # press q to terminate the loop
        cv2.destroyAllWindows()
        break

    time_elapsed = time.perf_counter() - t

    if time_elapsed < 1 / fps:
        time.sleep(1 / fps - time_elapsed)

for point in new_points:
    pixels[point] = 0

cv2.imwrite("../out.png", pixels)
#
# # img = cv2.imread('shinchan.jpg')
#
# height, width = pixels.shape
#
# i = 0
#
#
# fps = 30
# while True:
#     t = time.perf_counter()
#
#     i += 1
#
#     # divided the image into left and right part
#     # like list concatenation we concatenated
#     # right and left together
#     l = pixels[:, :(i % width)]
#     r = pixels[:, (i % width):]
#
#     img1 = np.hstack((r, l))
#
#     # this function will concatenate
#     # the two matrices
#     cv2.imshow('animation', img1)
#
#     if cv2.waitKey(1) == ord('q'):
#         # press q to terminate the loop
#         cv2.destroyAllWindows()
#         break
#
#     time_elapsed = time.perf_counter() - t
#
#     if time_elapsed < 1 / fps:
#         time.sleep(1 / fps - time_elapsed)
