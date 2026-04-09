import math
import random
import time

import cv2
import numpy as np
import cvzoomwindow


class DLA:
    def __init__(self):

        # self.tune_blur = True
        self.tune_blur = False

        # desired_size = 20
        # desired_size = 28
        # desired_size = 30
        # desired_size = 35
        desired_size = 50
        # desired_size = 100
        # desired_size = 150
        # desired_size = 200
        # desired_size = 270
        # desired_size = 300

        # weird_scale = 8
        weird_scale = 3


        # self.num_layers = 80
        self.num_layers = 100//weird_scale

        # self.rescale_for_blur = 64
        self.rescale_for_blur = 100//weird_scale
        self.blur_val = 31
        self.blur_sigma = 0
        # self.thresh_val = 173
        self.thresh_val = 180

        self.spawn_radius_pad = 1
        self.despawn_radius_pad = 20

        self.max_num_movements = 10000

        self.h = desired_size + self.despawn_radius_pad * 3
        self.center = (self.h // 2, self.h // 2)

        self.pixels = np.zeros((self.h, self.h), dtype=np.uint8)
        self.pixels[self.center] = 255

        # could calc this after, so that the walking function can be parallel
        self.pixels_counters = np.zeros((self.h, self.h))

        self.layered_output_pixels = self.pixels.copy()

        self.blur_layers_res_multiplier = 4

        self.spawn_radius = self.spawn_radius_pad
        self.despawn_radius = self.despawn_radius_pad

        self.despawn_radius_start = self.despawn_radius

        self.furthest_frozen_point = self.center

        self.point_counter = 0

        self.layer_counter = 0
        random.seed(1)
        np.random.seed(1)

    def dist_to_center(self, point):
        return math.sqrt(
            (self.center[0] - point[0]) ** 2 + (self.center[1] - point[1]) ** 2
        )

    def get_point_on_spawn_radius(self):
        # circle_r = self.dist_to_center(self.furthest_frozen_point) + self.h * 0.1
        angle = 2 * math.pi * random.random()

        x = self.spawn_radius * np.cos(angle) + self.center[0]
        y = self.spawn_radius * np.sin(angle) + self.center[1]
        return (
            int(x),
            int(y)
        )

    def move_point(self, point):
        x_move = 0
        y_move = 0
        if np.random.rand() > 0.5:
            x_move = random.choice([1, -1])
        else:
            y_move = random.choice([1, -1])

        return (
            point[0] + x_move,
            point[1] + y_move
        )

    def point_has_frozen_neighbour(self, point):

        if self.pixels[point[0] + 1, point[1]] == 255:
            return True
        elif self.pixels[point[0] - 1, point[1]] == 255:
            return True
        elif self.pixels[point[0], point[1] + 1] == 255:
            return True
        elif self.pixels[point[0], point[1] - 1] == 255:
            return True
        return False

    def recalc_spawn_radius(self, point):

        if self.dist_to_center(point) > self.dist_to_center(self.furthest_frozen_point):
            self.furthest_frozen_point = point
            self.spawn_radius = self.dist_to_center(point) + self.spawn_radius_pad
            self.despawn_radius = self.dist_to_center(point) + self.despawn_radius_pad

    def random_walk_one_point(self):
        point = self.get_point_on_spawn_radius()

        for i in range(self.max_num_movements):

            point = self.move_point(point)

            if self.dist_to_center(point) >= self.despawn_radius - 1:
                return False

            if self.point_has_frozen_neighbour(point):
                self.pixels[point] = 255
                self.point_counter += 1
                self.pixels_counters[point] = self.point_counter
                self.recalc_spawn_radius(point)
                return True

        print("rand out of moves")
        return False

    def grow_tree(self):
        tree_done_growing = False
        while not tree_done_growing:
            self.random_walk_one_point()

            # print progress of tree
            if self.point_counter % 50 == 0:
                print(int(self.h // 2 - self.despawn_radius))

            if self.despawn_radius > (self.h / 2) - 10:
                tree_done_growing = True

        self.crop_pixels()
        self.save_pixels()

        if self.tune_blur:
            self.sliders_blur_layers()

        else:
            self.generate_layers(print_prog=True)

    def sliders_blur_layers(self):
        def nothing(x):
            pass

        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 900, 900)
        # cv2.moveWindow('image', 0, 0)

        zw = cvzoomwindow.CvZoomWindow("image")
        # zw.grid_disp_enabled = False
        zw.bright_disp_enabled = False

        cv2.namedWindow('sliders', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('sliders', 1000, 300)

        # create trackbars for color change

        cv2.createTrackbar("blur", 'sliders', (self.blur_val - 1)//2, 50, nothing)

        cv2.createTrackbar("blur_sigma", 'sliders', self.blur_sigma, 80, nothing)
        cv2.createTrackbar("threshold", 'sliders', self.thresh_val, 255, nothing)
        cv2.createTrackbar("num_layers", 'sliders', self.num_layers, 80, nothing)
        cv2.createTrackbar("res_scal", 'sliders', self.rescale_for_blur, 150, nothing)

        while True:
            if cv2.waitKey(1) == ord('q'):
                break

            self.blur_val = int(cv2.getTrackbarPos('blur', 'sliders')) * 2 + 1
            self.blur_sigma = cv2.getTrackbarPos('blur_sigma', 'sliders')
            self.thresh_val = cv2.getTrackbarPos('threshold', 'sliders')
            self.num_layers = cv2.getTrackbarPos('num_layers', 'sliders')
            self.rescale_for_blur = cv2.getTrackbarPos('res_scal', 'sliders')
            if self.rescale_for_blur == 0:
                self.rescale_for_blur = 1

            self.generate_layers()

            cv2.imshow('image', self.layered_output_pixels)
            # zw.imshow(self.layered_output_pixels)

        cv2.destroyAllWindows()

    def generate_layers(self, print_prog=False):

        layers = list()

        # includes all points even if last step is weird sized. (except for one point maybe)
        steps = np.linspace(0, self.point_counter, self.num_layers + 1, endpoint=True, dtype=int)
        for i in range(len(steps) - 1):
            if print_prog:
                print("creating layers " + str(self.num_layers - i))
            temp_layer = np.zeros(self.pixels.shape, dtype=np.uint8)

            # print(str(steps[i]) + " : " + str(steps[i + 1] - 1))

            mask_1 = self.pixels_counters >= steps[i]
            mask_2 = self.pixels_counters <= steps[i + 1] - 1
            mask = np.logical_and(mask_1, mask_2)

            temp_layer[mask] = self.pixels[mask]
            layers.append(temp_layer.copy())

        # print(self.point_counter)

        merged_layers = np.zeros(self.pixels.shape, np.uint8)
        shades = np.linspace(255, 1, self.num_layers)

        # self.rescale_for_blur = 16

        # self.blur_val = 21
        # self.threshval = 110

        merged_layers = cv2.resize(merged_layers, (merged_layers.shape[0] * self.rescale_for_blur, merged_layers.shape[1] * self.rescale_for_blur), interpolation=cv2.INTER_NEAREST)
        prev_merged_layers = merged_layers.copy()

        for i in range(len(layers)):
            if print_prog:
                print("merging layers " + str(self.num_layers - i))
                print("shape", prev_merged_layers.shape)
            prev_merged_layers[prev_merged_layers > 0] = 255

            # prev_merged_layers = cv2.GaussianBlur(prev_merged_layers, (self.blur_val, self.blur_val), 0)
            # prev_merged_layers = cv2.blur(prev_merged_layers, (self.blur_val, self.blur_val))

            # prev_merged_layers = cv2.medianBlur(prev_merged_layers, self.blur_val)
            # ret_val, prev_merged_layers = cv2.threshold(prev_merged_layers, self.thresh_val, 255, cv2.THRESH_BINARY)

            prev_merged_layers = cv2.GaussianBlur(
                prev_merged_layers,
                (self.blur_val, self.blur_val),
                self.blur_sigma)

            layer = layers[i]
            layer = cv2.resize(layer, (layer.shape[0] * self.rescale_for_blur, layer.shape[1] * self.rescale_for_blur), interpolation=cv2.INTER_NEAREST)

            mask = layer > 0
            prev_merged_layers[mask] = layer[mask]

            # prev_merged_layers = cv2.medianBlur(prev_merged_layers, self.blur_val)

            # prev_merged_layers = cv2.blur(prev_merged_layers, (self.blur_val, self.blur_val))

            ret_val, prev_merged_layers = cv2.threshold(
                prev_merged_layers,
                255 - self.thresh_val,
                255, cv2.THRESH_BINARY)

            cv2.imwrite("./png layers/" + str(i) + ".png", prev_merged_layers)


            mask = prev_merged_layers > 0
            prev_merged_layers[mask] = shades[i]

            mask = merged_layers == 0
            merged_layers[mask] = prev_merged_layers[mask]
            # cv2.imwrite("blurred_layers/layer_" + str(i) + ".png" , merged_layers)
            prev_merged_layers = merged_layers.copy()

        cv2.imwrite("blurred_out_BL.png", merged_layers)
        merged_layers = np.stack((merged_layers,) * 3, axis=-1)
        black_pixels = np.all(merged_layers == [0, 0, 0], axis=-1)
        merged_layers[black_pixels] = [255, 0, 0]
        self.layered_output_pixels = merged_layers

        cv2.imwrite("blurred_out.png", merged_layers)
        if print_prog:
            print()
            print("total points", self.point_counter)
            print("done")

    def crop_pixels(self):
        buffer = 1
        d = int(self.dist_to_center(self.furthest_frozen_point)) + buffer
        # d = int(d) * self.blur_layers_res_multiplier

        # c = self.h * self.blur_layers_res_multiplier // 2
        c = self.center[0]

        self.pixels = self.pixels[
                      c - d:
                      c + d,
                      c - d:
                      c + d
                      ].copy()
        self.pixels_counters = self.pixels_counters[
                               c - d:
                               c + d,
                               c - d:
                               c + d
                               ].copy()

        self.layered_output_pixels = self.pixels.copy()

    def save_pixels(self):
        cv2.imwrite("tree.png", self.pixels)

        # temp_layers = np.stack((self.layered_output_pixels,) * 3, axis=-1)
        #
        # d = self.dist_to_center(self.furthest_frozen_point)
        # d = int(d)
        #
        # temp_layers = temp_layers[
        #               self.center[0] - d:
        #               self.center[0] + d,
        #               self.center[1] - d:
        #               self.center[1] + d
        #               ]
        #
        # # self.layers_pixels[:,:] = self.layers_pixels[:,:,0]
        #
        # cv2.imwrite("../tree_layers.png", temp_layers)
        #
        # black_pixels = np.all(temp_layers == [0, 0, 0], axis=-1)
        #
        # temp_layers[black_pixels] = [255, 0, 0]
        # cv2.imwrite("../tree_layers_blue_1.png", temp_layers)
        #
        # print("total points", self.point_counter)


dla = DLA()
dla.grow_tree()
exit()

# Instance of CvZoomWindow class
zw = cvzoomwindow.CvZoomWindow(
    "Zoom Window",  # Name of the window
)

zw.grid_disp_enabled = False
zw.bright_disp_enabled = False
img = cv2.imread('tree.png')
s = img.shape
img = cv2.resize(img, (s[0] * 4, s[1] * 4), interpolation=cv2.INTER_NEAREST)

# cv2.imshow("show", img)
zw.imshow(img)
cv2.waitKey()

exit()
num_points = 686
num_layers = 40
points_per_layer = int(num_points / num_layers)
steps = np.arange(0, num_points, points_per_layer)
steps = steps.astype(int)
# steps = np.linspace(0,num_points - 1, num_layers, endpoint=False, dtype=int)
print(steps)
# exit()
for i in range(num_layers):
    print(steps[i], steps[i] + points_per_layer - 1)

print()
print()
num_points = 14
num_layers = 4
steps = np.linspace(0, num_points, num_layers + 1, endpoint=True, dtype=int)
for i in range(len(steps)):
    print(steps[i], steps[i + 1] - 1)

# shades = np.arange(0, 255, 80,)
# shades = np.linspace(0,255, 80)

# print(shades.astype(int))


# 629 : 645
# 646 : 662
# 663 : 679
# 686
