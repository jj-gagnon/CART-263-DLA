import math
import random
import time

import cv2
import numpy as np


class DLA:
    def __init__(self):
        desired_size = 75
        # desired_size = 100
        # desired_size = 120
        # desired_size = 140

        # desired_size = 175
        # desired_size = 300
        # desired_size = 300

        self.spawn_radius_pad = 1
        self.despawn_radius_pad = 20

        self.h = desired_size + self.despawn_radius_pad * 2
        self.center = (self.h // 2, self.h // 2)


        self.pixels = np.zeros((self.h, self.h), dtype=np.uint8)
        self.pixels[self.center] = 255

        self.pixels_counters = np.zeros((self.h, self.h))

        # self.layers_pixels = np.zeros((self.h, self.h), dtype=np.uint8)
        # self.layers_pixels_for_blur = np.zeros((1080, 1080), dtype=np.uint8)
        self.layers_pixels = self.pixels.copy()

        self.blur_layers_res_multiplier = 4
        self.layers_pixels_for_blur = cv2.resize(self.pixels,
                                                 (self.h * self.blur_layers_res_multiplier,
                                                  self.h * self.blur_layers_res_multiplier), interpolation=cv2.INTER_NEAREST)

        # cv2.namedWindow("animation", cv2.WINDOW_NORMAL)
        # cv2.resizeWindow("animation", 600, 600)

        # self.spawn_radius = self.h * 0.02
        self.spawn_radius = self.spawn_radius_pad
        self.despawn_radius = self.despawn_radius_pad

        self.despawn_radius_start = self.despawn_radius

        self.furthest_frozen_point = self.center

        self.max_num_movements = 10000

        self.point_counter = 0

        self.layer_counter = 0

        # self.draw_spawn_and_despawn_radius()

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

            # self.draw_spawn_and_despawn_radius()

    def random_walk_one_point(self):
        point = self.get_point_on_spawn_radius()
        # print(point)
        # max_num_moves = 10000
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
            # self.random_walk_one_point_animated()
            self.random_walk_one_point()

            # print progress of tree
            if self.point_counter % 50 == 0:
                print(int(self.h // 2 - self.despawn_radius))

            if self.despawn_radius > (self.h / 2) - 10:
                tree_done_growing = True
        self.generate_layers()
        self.save_pixels()

    def generate_layers(self):
        num_layers = 80
        scale = 16

        blur = 41
        thresh = 80


        points_per_layer = int(self.point_counter / num_layers)

        steps = np.arange(0, self.point_counter, points_per_layer)
        steps = steps.astype(int)

        layers = list()

        for i in range(num_layers):
            print("creating layers " + str(num_layers - i))
            temp_layer = np.zeros(self.pixels.shape, dtype=np.uint8)
            print("from " + str(steps[i]))
            print("to " + str(steps[i] + points_per_layer - 1))
            mask_1 = self.pixels_counters >= steps[i]
            mask_2 = self.pixels_counters <= steps[i] + points_per_layer - 1
            mask = np.logical_and(mask_1, mask_2)

            # mask = mask_2

            temp_layer[mask] = self.pixels[mask]
            layers.append(temp_layer.copy())
            cv2.imwrite("layers/layer_" + str(i) + ".png", temp_layer)

        merged_layers = np.zeros(self.pixels.shape, np.uint8)
        prev_merged_layers = merged_layers.copy()

        shades = np.linspace(255, 1, num_layers)



        merged_layers = cv2.resize(merged_layers, (merged_layers.shape[0] * scale, merged_layers.shape[1] * scale), interpolation=cv2.INTER_NEAREST)
        prev_merged_layers = merged_layers.copy()

        for i in range(len(layers)):
            print("merging layers " + str(num_layers - i))
            prev_merged_layers[prev_merged_layers > 0] = 255

            prev_merged_layers = cv2.GaussianBlur(prev_merged_layers, (blur, blur), 0)
            ret_val, prev_merged_layers = cv2.threshold(prev_merged_layers, thresh, 255, cv2.THRESH_BINARY)

            layer = layers[i]
            layer = cv2.resize(layer, (layer.shape[0] * scale, layer.shape[1] * scale), interpolation=cv2.INTER_NEAREST)
            mask = layer > 0

            prev_merged_layers[mask] = layer[mask]

            mask = prev_merged_layers > 0
            prev_merged_layers[mask] = shades[i]

            mask = merged_layers == 0
            merged_layers[mask] = prev_merged_layers[mask]

            temp_save = np.stack((merged_layers,) * 3, axis=-1)
            black_pixels = np.all(temp_save == [0, 0, 0], axis=-1)
            temp_save[black_pixels] = [255, 0, 0]

            cv2.imwrite("blurred_layers/layer_" + str(i) + ".png" , temp_save)
            prev_merged_layers = merged_layers.copy()

        merged_layers = np.stack((merged_layers,) * 3, axis=-1)
        black_pixels = np.all(merged_layers == [0, 0, 0], axis=-1)
        merged_layers[black_pixels] = [255, 0, 0]

        cv2.imwrite("blurred_out.png", merged_layers)

    def accumulate_layers_no_blur(self):
        temp_pixels = self.pixels.copy()
        mask = temp_pixels > 0

        r = np.interp(self.despawn_radius, [self.despawn_radius_start, self.h // 2], [0, 255])

        temp_pixels[mask] = temp_pixels[mask] - int(r)

        mask = self.layers_pixels == 0

        self.layers_pixels[mask] = temp_pixels[mask]

    def accumulate_layers_blur_thresh(self):
        temp_pixels = self.pixels.copy()
        temp_pixels = cv2.resize(temp_pixels, (1080, 1080), interpolation=cv2.INTER_NEAREST)

        temp_pixels = cv2.GaussianBlur(temp_pixels, (21, 21), 0)
        # temp_pixels = cv2.GaussianBlur(temp_pixels, (41, 41), 0)
        ret, temp_pixels = cv2.threshold(temp_pixels, 90, 255, cv2.THRESH_BINARY)

        mask = temp_pixels > 0

        r = np.interp(self.despawn_radius, [self.despawn_radius_start, self.h // 2], [0, 255])

        temp_pixels[mask] = temp_pixels[mask] - int(r)

        mask = self.layers_pixels_for_blur == 0

        self.layers_pixels_for_blur[mask] = temp_pixels[mask]

    def accumulate_layers_blur_thresh_increasing(self):

        temp_layer_pixels = self.layers_pixels_for_blur.copy()

        blur = 5
        thresh = 40

        blur = 9
        thresh = 80

        blur = 17
        thresh = 70

        blur = 81
        thresh = 220

        temp_layer_pixels = cv2.GaussianBlur(temp_layer_pixels, (blur, blur), 0)
        ret, temp_layer_pixels = cv2.threshold(temp_layer_pixels, thresh, 255, cv2.THRESH_BINARY)

        temp_pixels = self.pixels.copy()
        temp_pixels = cv2.resize(
            temp_pixels, (
                self.h * self.blur_layers_res_multiplier,
                self.h * self.blur_layers_res_multiplier),
            interpolation=cv2.INTER_NEAREST)

        # temp_pixels = cv2.GaussianBlur(temp_pixels, (7, 7), 0)
        # ret, temp_pixels = cv2.threshold(temp_pixels, 120, 255, cv2.THRESH_BINARY)

        shade_for_layer = int(
            np.interp(self.despawn_radius, [self.despawn_radius_start, self.h // 2], [255, 1])
            # np.interp(self.despawn_radius, [self.despawn_radius_start, self.h // 2], [0,255])
        )

        # mask = temp_layer_pixels > 0
        # temp_pixels[mask] = temp_layer_pixels[mask]

        mask = temp_pixels == 0
        temp_pixels[mask] = temp_layer_pixels[mask]

        mask = temp_pixels > 0
        temp_pixels[mask] = 255 - self.layer_counter * 15

        mask = self.layers_pixels_for_blur > 0
        temp_pixels[mask] = self.layers_pixels_for_blur[mask]

        self.layers_pixels_for_blur = temp_pixels

    def grow_tree_accumulate_layers(self):

        num_layers = 10
        layer_step = (self.h / 2 - self.despawn_radius) / num_layers

        tree_done_growing = False
        while not tree_done_growing:

            point_added = self.random_walk_one_point()
            if point_added:
                self.point_counter += 1

            if (self.h / 2 - self.despawn_radius) % layer_step < 0.5:
                print(self.h / 2 - self.despawn_radius)

            if self.point_counter % 150 == 0:
                # if self.point_counter % 150 == 0:

                # print(int(self.h // 2 - self.despawn_radius))
                # self.accumulate_layers_blur_thresh()
                self.accumulate_layers_blur_thresh_increasing()
                self.layer_counter += 1

            if self.despawn_radius >= (self.h // 2):
                tree_done_growing = True

        self.save_pixels_with_blur()

    def save_pixels_with_blur(self):
        cv2.imwrite("../tree.png", self.pixels)

        temp_layers = np.stack((self.layers_pixels_for_blur,) * 3, axis=-1)

        d = self.dist_to_center(self.furthest_frozen_point)
        d = int(d) * self.blur_layers_res_multiplier

        c = self.h * self.blur_layers_res_multiplier // 2
        temp_layers = temp_layers[
                      c - d:
                      c + d,
                      c - d:
                      c + d
                      ]

        # self.layers_pixels[:,:] = self.layers_pixels[:,:,0]

        cv2.imwrite("../tree_layers.png", temp_layers)

        black_pixels = np.all(temp_layers == [0, 0, 0], axis=-1)

        temp_layers[black_pixels] = [255, 0, 0]
        cv2.imwrite("../tree_layers_blue.png", temp_layers)

        print("total points", self.point_counter)

    def save_pixels(self):
        cv2.imwrite("tree.png", self.pixels)

        temp_layers = np.stack((self.layers_pixels,) * 3, axis=-1)

        d = self.dist_to_center(self.furthest_frozen_point)
        d = int(d)

        temp_layers = temp_layers[
                      self.center[0] - d:
                      self.center[0] + d,
                      self.center[1] - d:
                      self.center[1] + d
                      ]

        # self.layers_pixels[:,:] = self.layers_pixels[:,:,0]

        cv2.imwrite("../tree_layers.png", temp_layers)

        black_pixels = np.all(temp_layers == [0, 0, 0], axis=-1)

        temp_layers[black_pixels] = [255, 0, 0]
        cv2.imwrite("../tree_layers_blue.png", temp_layers)

        print("total points", self.point_counter)

    def grow_tree_animated(self):
        cv2.namedWindow("animation", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("animation", 1000, 1000)
        fps = 60
        fps = 1000

        tree_done_growing = False
        while not tree_done_growing:
            t = time.perf_counter()
            self.random_walk_one_point()

            if self.despawn_radius > (self.h / 2) - 10:
                tree_done_growing = True

            cv2.imshow("animation", self.pixels)
            if cv2.waitKey(1) == ord('q'):
                # press q to terminate the loop
                cv2.destroyAllWindows()
                exit()

            time_elapsed = time.perf_counter() - t

            if time_elapsed < 1 / fps:
                time.sleep(1 / fps - time_elapsed)

    def random_walk_one_point_animated(self):

        cv2.namedWindow("animation", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("animation", 600, 600)
        fps = 60
        fps = 1000

        point = self.get_point_on_spawn_radius()
        # print(point)
        num_moves = 1000
        for i in range(num_moves):
            t = time.perf_counter()
            self.pixels[point] = 0

            point = self.move_point(point)

            if self.point_has_frozen_neighbour(point):
                self.pixels[point] = 255
                self.recalc_spawn_radius(point)
                return

            if self.dist_to_center(point) > self.despawn_radius:
                return

            self.pixels[point] = 255
            cv2.imshow("animation", self.pixels)
            if cv2.waitKey(1) == ord('q'):
                # press q to terminate the loop
                cv2.destroyAllWindows()
                exit()

            time_elapsed = time.perf_counter() - t

            if time_elapsed < 1 / fps:
                time.sleep(1 / fps - time_elapsed)

        self.pixels[point] = 0
        return


dla = DLA()
dla.grow_tree()
exit()
#
# img = cv2.imread('cool error.png')
# s = img.shape
# img = cv2.resize(img, (s[0] * 4, s[1] * 4),interpolation=cv2.INTER_NEAREST)
#
# cv2.imshow("show", img)
# cv2.waitKey()

# num_points = 1002
# num_layers = 20
# points_per_layer = int(num_points / num_layers)
# steps = np.arange(0, num_points, points_per_layer)
# steps = steps.astype(int)
# # steps = np.linspace(0,num_points - 1, num_layers, endpoint=False, dtype=int)
# print(steps)
# # exit()
# for i in range(num_layers):
#     print(steps[i], steps[i] + points_per_layer - 1)


# shades = np.arange(0, 255, 80,)
# shades = np.linspace(0,255, 80)

# print(shades.astype(int))
