import math
import random
import time

import cv2
import numpy as np


class DLA:
    def __init__(self):
        desired_size = 250
        self.h = desired_size + 20
        self.pixels = np.zeros((self.h, self.h), dtype=np.uint8)
        self.center = (self.h // 2, self.h // 2)
        self.pixels[self.center] = 255

        # cv2.namedWindow("animation", cv2.WINDOW_NORMAL)
        # cv2.resizeWindow("animation", 600, 600)

        self.spawn_radius_pad = 1
        self.despawn_radius_pad = 50

        # self.spawn_radius = self.h * 0.02
        self.spawn_radius = 5
        self.despawn_radius = 10

        self.furthest_frozen_point = self.center

        self.max_num_movements = 1000

        self.draw_spawn_and_despawn_radius()

    def dist_to_center(self, point):
        return math.sqrt(
            (self.center[0] - point[0]) ** 2 + (self.center[1] - point[1]) ** 2
        )

    # def draw_spawn_and_despawn_radius(self):
    #     num_points_to_draw = 50
    #     # angles = 2 * math.pi * np.random.random(num_points_to_draw)
    #     angles = 2 * math.pi * np.linspace(0,1, num_points_to_draw, False)
    #
    #     x = self.spawn_radius * np.cos(angles) + self.center[0]
    #     y = self.spawn_radius * np.sin(angles) + self.center[1]
    #
    #     self.pixels[x.astype(int),y.astype(int)] = 100
    #
    #     x = self.despawn_radius * np.cos(angles) + self.center[0]
    #     y = self.despawn_radius * np.sin(angles) + self.center[1]
    #
    #     self.pixels[x.astype(int), y.astype(int)] = 100

    def draw_spawn_and_despawn_radius(self):
        cv2.circle(self.pixels, self.center, int(self.spawn_radius), 70)
        cv2.circle(self.pixels, self.center, int(self.despawn_radius), 150)

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

            self.draw_spawn_and_despawn_radius()

    def random_walk_one_point(self):
        point = self.get_point_on_spawn_radius()
        # print(point)
        max_num_moves = 800
        for i in range(max_num_moves):

            point = self.move_point(point)

            if self.point_has_frozen_neighbour(point):
                self.pixels[point] = 255
                self.recalc_spawn_radius(point)
                return

            if self.dist_to_center(point) > self.despawn_radius:
                return

        return

    def grow_tree(self):
        tree_done_growing = False
        while not tree_done_growing:
            self.random_walk_one_point_animated()

            if self.despawn_radius > (self.h / 2) - 10:
                tree_done_growing = True

    def grow_tree_animated(self):
        cv2.namedWindow("animation", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("animation", 1000, 1000)
        fps = 60
        fps = 1000

        counter = 0

        tree_done_growing = False
        while not tree_done_growing:
            t = time.perf_counter()
            self.random_walk_one_point()

            if self.despawn_radius > (self.h / 2) - 10:
                tree_done_growing = True


            cv2.imshow("animation", self.pixels)
            cv2.imwrite("./out/" + str(counter) + ".jpg", self.pixels)

            counter += 1

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


# def try_freezing_one_point():
#     pass
# time.sleep(-1)
# exit()

dla = DLA()
# dla.grow_tree()
dla.grow_tree_animated()
# dla.
