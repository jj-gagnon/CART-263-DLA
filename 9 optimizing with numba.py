import math
import random
import time

import cv2
import numpy as np
import cvzoomwindow

from numba import njit, prange


@njit(cache=True, fastmath=True)
def dist_to_center(point, center):
    return math.sqrt(
        (center[0] - point[0]) ** 2 + (center[1] - point[1]) ** 2
    )


@njit(cache=True, fastmath=True)
def get_point_on_spawn_radius(center, spawn_radius):
    # global center
    # global spawn_radius
    # angle = 2 * math.pi * random.random()
    # print(angle)
    angle = 2 * math.pi * np.random.rand()
    # print(angle)

    x = spawn_radius * np.cos(angle) + center[0]
    y = spawn_radius * np.sin(angle) + center[1]
    # print(x,y)
    # print()
    return (
        int(x),
        int(y)
    )


@njit(cache=True)
def move_point(point):

    x_move = 0
    y_move = 0
    if np.random.rand() > 0.5:
        if np.random.rand() > 0.5:
            x_move = 1
        else:
            x_move = -1
        # x_move = np.random.choice([1, -1])

    else:
        if np.random.rand() > 0.5:
            y_move = 1
        else:
            y_move = -1
        # y_move = np.random.choice([1, -1])

    return (
        point[0] + x_move,
        point[1] + y_move
    )


@njit(cache=True)
def grow_tree():
    # desired_size = 15
    # desired_size = 20
    # desired_size = 50
    # desired_size = 60
    desired_size = 80
    # desired_size = 120
    # desired_size = 150
    # desired_size = 200
    # desired_size = 270
    # desired_size = 300
    # desired_size = 1000

    # weird_scale = 8
    weird_scale = 3

    # num_layers = 80
    num_layers = 100 // weird_scale
    num_layers = 140

    # rescale_for_blur = 64
    rescale_for_blur = 100 // weird_scale
    rescale_for_blur = 140
    # blur_val = 21
    blur_val = 41
    blur_sigma = 0

    thresh_val = 150
    thresh_val = 185

    spawn_radius_pad = 1
    # despawn_radius_pad = 20
    # despawn_radius_pad = 40
    despawn_radius_pad = 80

    max_num_movements = 10000
    # max_num_movements = 400

    h = desired_size + despawn_radius_pad * 2
    center = (h // 2, h // 2)

    pixels = np.zeros((h, h), dtype=np.uint8)
    pixels[center] = 255

    # could calc this after, so that the walking function can be parallel
    pixels_counters = np.zeros((h, h))

    layered_output_pixels = pixels.copy()

    blur_layers_res_multiplier = 4

    spawn_radius = spawn_radius_pad
    despawn_radius = despawn_radius_pad

    despawn_radius_start = despawn_radius

    furthest_frozen_point = center

    point_counter = 0

    # 1, 8 is a nice even spread out
    # 3,9 a little wonky
    # 4 four points
    #19,22, 30, 32, 37
    np.random.seed(
        37

    )

    tree_done_growing = False
    while not tree_done_growing:

        point = get_point_on_spawn_radius(center, spawn_radius)

        # for i in range(max_num_movements):
        while True:
            # for i in range(max_num_movements):

            point = move_point(point)

            if dist_to_center(point, center) >= despawn_radius - 1:
                # print('broken')
                break

            # check if point has neighbour
            point_has_frozen_neighbour = False
            if pixels[point[0] + 1, point[1]] == 255:
                point_has_frozen_neighbour = True
            elif pixels[point[0] - 1, point[1]] == 255:
                point_has_frozen_neighbour = True
            elif pixels[point[0], point[1] + 1] == 255:
                point_has_frozen_neighbour = True
            elif pixels[point[0], point[1] - 1] == 255:
                point_has_frozen_neighbour = True

            if point_has_frozen_neighbour:
                pixels[point] = 255
                point_counter += 1
                pixels_counters[point] = point_counter

                # recalc spawn radisu
                if dist_to_center(point, center) > dist_to_center(furthest_frozen_point, center):
                    # print('s', despawn_radius)
                    furthest_frozen_point = point
                    spawn_radius = dist_to_center(point, center) + spawn_radius_pad
                    despawn_radius = dist_to_center(point, center) + despawn_radius_pad
                break

        # print progress of tree
        if point_counter % 20 == 0:
            print("progress", int(h // 2 - despawn_radius))

        if despawn_radius > (h / 2):
            tree_done_growing = True

    # crop_pixels(furthest_frozen_point, center)
    # save_pixels()
    # cv2.imwrite("cool error.png", pixels)

    # if tune_blur:
    #     sliders_blur_layers()
    # else:
    #     generate_layers(print_prog=True)



    # pixels = crop_pixels(pixels, furthest_frozen_point)
    # return pixels, None, None



    print("done, starting layers blur maerg")
    pixels = crop_pixels(pixels, furthest_frozen_point)
    pixels_counters = crop_pixels(pixels_counters, furthest_frozen_point)

    # png_layers, blurred_layers = generate_layers(point_counter, num_layers, pixels, rescale_for_blur, blur_val, thresh_val, pixels_counters)
    params = {
        "point_counter": point_counter,
        "num_layers": num_layers,
        "rescale_for_blur": rescale_for_blur,
        "blur_val": blur_val,
        "thresh_val": thresh_val,}
        # "pixels_counters": pixels_counters}

    # return pixels, params, png_layers, blurred_layers
    return pixels,pixels_counters, params

def sliders_blur_layers():
    def nothing(x):
        pass

    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', 900, 900)
    # cv2.moveWindow('image', 0, 0)

    zw = cvzoomwindow.CvZoomWindow("image")
    # zw.grid_disp_enabled = False
    zw.bright_disp_enabled = False

    cv2.namedWindow('sliders', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('sliders', 600, 200)

    # create trackbars for color change

    cv2.createTrackbar("blur", 'sliders', (blur_val - 1) // 2, 50, nothing)

    cv2.createTrackbar("blur_sigma", 'sliders', blur_sigma, 80, nothing)
    cv2.createTrackbar("threshold", 'sliders', thresh_val, 255, nothing)
    cv2.createTrackbar("num_layers", 'sliders', num_layers, 80, nothing)
    cv2.createTrackbar("res_scal", 'sliders', rescale_for_blur, 150, nothing)

    while True:
        if cv2.waitKey(1) == ord('q'):
            break

        blur_val = int(cv2.getTrackbarPos('blur', 'sliders')) * 2 + 1
        blur_sigma = cv2.getTrackbarPos('blur_sigma', 'sliders')
        thresh_val = cv2.getTrackbarPos('threshold', 'sliders')
        num_layers = cv2.getTrackbarPos('num_layers', 'sliders')
        rescale_for_blur = cv2.getTrackbarPos('res_scal', 'sliders')
        if rescale_for_blur == 0:
            rescale_for_blur = 1

        generate_layers()

        cv2.imshow('image', layered_output_pixels)
        # zw.imshow(layered_output_pixels)

    cv2.destroyAllWindows()


def generate_layers_numpy(pixels,pixels_counters, params):
    point_counter = params['point_counter']
    num_layers = params['num_layers']

    rescale_for_blur = params['rescale_for_blur']
    blur_val = params['blur_val']
    thresh_val = params['thresh_val']
    # pixels_counters = params['pixels_counters']

    layers = list()

    # includes all points even if last step is weird sized. (except for one point maybe)
    # steps = np.linspace(0, point_counter, num_layers + 1, endpoint=True)
    steps = np.linspace(0, point_counter, num_layers + 1)
    steps = steps.astype(np.int32)

    for i in range(len(steps) - 1):
        print("creating layers " + str(num_layers - i))
        # temp_layer = np.zeros(pixels.shape, dtype=np.uint8)
        temp_layer = np.zeros(pixels.shape)

        # print(str(steps[i]) + " : " + str(steps[i + 1] - 1))

        mask_1 = pixels_counters >= steps[i]
        mask_2 = pixels_counters <= steps[i + 1] - 1

        mask = np.logical_and(mask_1, mask_2)

        # print(temp_layer.dtype)
        # print(pixels.dtype)
        # s = temp_layer.shape
        #
        # temp_layer = temp_layer.flatten()
        # mask = mask.flatten()
        # pixels = pixels.flatten()

        temp_layer[mask] = pixels[mask]

        # temp_layer = temp_layer.reshape(s)
        # pixels = pixels.reshape(s)

        layers.append(temp_layer.copy())

    # print(point_counter)

    merged_layers = np.zeros(pixels.shape, np.uint8)
    shades = np.linspace(255, 1, num_layers)

    png_layers = list()

    # merged_layers = cv2.resize(merged_layers, (merged_layers.shape[0] * rescale_for_blur, merged_layers.shape[1] * rescale_for_blur), interpolation=cv2.INTER_NEAREST)
    # merged_layers = merged_layers.repeat(rescale_for_blur, axis=0).repeat(rescale_for_blur, axis=1)
    merged_layers = scale_pixels(merged_layers, rescale_for_blur)
    prev_merged_layers = merged_layers.copy()
    print("hey hey", prev_merged_layers.shape)
    for i in range(len(layers)):

        print("merging layers " + str(num_layers - i))

        # s = prev_merged_layers.shape
        # prev_merged_layers = prev_merged_layers.flatten()
        prev_merged_layers[prev_merged_layers > 0] = 255
        # prev_merged_layers = prev_merged_layers.reshape(s)

        prev_merged_layers = cv2.GaussianBlur(
            prev_merged_layers,
            (blur_val, blur_val), 0)


        layer = layers[i]
        layer = scale_pixels(layer, rescale_for_blur)

        mask = layer > 0

        # s = mask.shape
        # mask = mask.flatten()
        # layer = layer.flatten()
        # prev_merged_layers = prev_merged_layers.flatten()

        prev_merged_layers[mask] = layer[mask]

        # layer = layer.reshape(s)
        # prev_merged_layers = prev_merged_layers.reshape(s)

        # prev_merged_layers = cv2.medianBlur(prev_merged_layers, blur_val)
        # prev_merged_layers = cv2.GaussianBlur(
        #     prev_merged_layers,
        #     (blur_val, blur_val), 0)
        # prev_merged_layers = cv2.blur(prev_merged_layers, (blur_val, blur_val))

        # print(prev_merged_layers.shape)
        # print('numpy version')
        # ks = blur_val
        # sigma = 0.3 * ((ks - 1) * 0.5 - 1) + 0.8
        #
        # l = ks
        # ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
        # gauss = np.exp(-0.5 * np.square(ax) / np.square(sigma))
        # kernel = np.outer(gauss, gauss)
        # kernel = kernel / np.sum(kernel)

        # prev_merged_layers = np.pad(prev_merged_layers, (blur_val- 1) //2 )

        # s = prev_merged_layers.shape
        # pad_num = (blur_val - 1) // 2
        # padded = np.zeros((s[0] + 2 * pad_num, s[1] + 2 * pad_num))
        # for pad_i in range(s[0]):
        #     for pad_j in range(s[1]):
        #         padded[pad_i + pad_num, pad_j + pad_num] = prev_merged_layers[pad_i, pad_j]



        # prev_merged_layers = prev_merged_layers[blur_val-1:-blur_val-1, blur_val-1:-blur_val-1]
        print(prev_merged_layers.shape)

        # ret_val, prev_merged_layers = cv2.threshold(
        #     prev_merged_layers,
        #     255 - thresh_val,
        #     255, cv2.THRESH_BINARY)
        # s = prev_merged_layers.shape
        # prev_merged_layers = prev_merged_layers.flatten()
        prev_merged_layers[prev_merged_layers > 255 - thresh_val] = 255
        prev_merged_layers[prev_merged_layers <= 255 - thresh_val] = 0
        # prev_merged_layers = prev_merged_layers.reshape(s)

        # cv2.imwrite("./png layers/" + str(i) + ".png", prev_merged_layers)
        png_layers.append(prev_merged_layers.copy())

        mask = prev_merged_layers > 0
        # s = prev_merged_layers.shape
        # prev_merged_layers = prev_merged_layers.flatten()
        # mask = mask.flatten()
        # prev_merged_layers[mask] = shades[i]
        # prev_merged_layers[mask] = 1
        prev_merged_layers[mask] = shades[i]
        # prev_merged_layers = prev_merged_layers.reshape(s)

        mask = merged_layers == 0
        # s = mask.shape
        # mask = mask.flatten()
        # merged_layers = merged_layers.flatten()
        # prev_merged_layers = prev_merged_layers.flatten()
        merged_layers[mask] = prev_merged_layers[mask]
        # cv2.imwrite("blurred_layers/layer_" + str(i) + ".png" , merged_layers)
        prev_merged_layers = merged_layers.copy()
        # merged_layers = merged_layers.reshape(s)
        # prev_merged_layers = prev_merged_layers.reshape(s)
        # print('debug 3')
    # cv2.imwrite("blurred_out_BL.png", merged_layers)

    # merged_layers = np.stack((merged_layers) * 3, axis=-1)
    rgb = np.zeros((merged_layers.shape[0], merged_layers.shape[1], 3))
    rgb[:, :, 0] = merged_layers
    rgb[:, :, 1] = merged_layers
    rgb[:, :, 2] = merged_layers

    # print('debug 4')

    black_pixels = np.all(rgb == [0, 0, 0], axis=-1)
    rgb[black_pixels] = [255, 0, 0]

    # for blue_i in range(rgb.shape[0]):
    #     for blue_j in range(rgb.shape[1]):
    #         if rgb[blue_i, blue_j, 0] == 0:
    #             rgb[blue_i, blue_j] = np.array([0, 0, 255], dtype=np.uint8)

    # cv2.imwrite("1.png", merged_layers)

    print()
    print("total points", point_counter)
    print("done")

    return png_layers, rgb


@njit(cache=True)
def generate_layers(point_counter, num_layers, pixels, rescale_for_blur, blur_val, thresh_val, pixels_counters):
    layers = list()

    # includes all points even if last step is weird sized. (except for one point maybe)
    # steps = np.linspace(0, point_counter, num_layers + 1, endpoint=True)
    steps = np.linspace(0, point_counter, num_layers + 1)
    steps = steps.astype(np.int32)

    for i in range(len(steps) - 1):
        print("creating layers " + str(num_layers - i))
        # temp_layer = np.zeros(pixels.shape, dtype=np.uint8)
        temp_layer = np.zeros(pixels.shape)

        # print(str(steps[i]) + " : " + str(steps[i + 1] - 1))

        mask_1 = pixels_counters >= steps[i]
        mask_2 = pixels_counters <= steps[i + 1] - 1

        mask = np.logical_and(mask_1, mask_2)

        # print(temp_layer.dtype)
        # print(pixels.dtype)
        s = temp_layer.shape

        temp_layer = temp_layer.flatten()
        mask = mask.flatten()
        pixels = pixels.flatten()

        temp_layer[mask] = pixels[mask]

        temp_layer = temp_layer.reshape(s)
        pixels = pixels.reshape(s)

        layers.append(temp_layer.copy())

    # print(point_counter)

    merged_layers = np.zeros(pixels.shape, np.uint8)
    shades = np.linspace(255, 1, num_layers)

    png_layers = list()

    # merged_layers = cv2.resize(merged_layers, (merged_layers.shape[0] * rescale_for_blur, merged_layers.shape[1] * rescale_for_blur), interpolation=cv2.INTER_NEAREST)
    # merged_layers = merged_layers.repeat(rescale_for_blur, axis=0).repeat(rescale_for_blur, axis=1)
    merged_layers = scale_pixels(merged_layers, rescale_for_blur)
    prev_merged_layers = merged_layers.copy()
    print("hey hey", prev_merged_layers.shape)
    for i in range(len(layers)):

        print("merging layers " + str(num_layers - i))

        s = prev_merged_layers.shape
        prev_merged_layers = prev_merged_layers.flatten()
        prev_merged_layers[prev_merged_layers > 0] = 255
        # prev_merged_layers = prev_merged_layers.reshape(s)

        layer = layers[i]
        layer = scale_pixels(layer, rescale_for_blur)

        mask = layer > 0

        s = mask.shape
        mask = mask.flatten()
        layer = layer.flatten()
        # prev_merged_layers = prev_merged_layers.flatten()

        prev_merged_layers[mask] = layer[mask]

        # layer = layer.reshape(s)
        prev_merged_layers = prev_merged_layers.reshape(s)

        # prev_merged_layers = cv2.medianBlur(prev_merged_layers, blur_val)
        # prev_merged_layers = cv2.GaussianBlur(
        #     prev_merged_layers,
        #     (blur_val, blur_val), 0)
        # prev_merged_layers = cv2.blur(prev_merged_layers, (blur_val, blur_val))

        print(prev_merged_layers.shape)

        ks = blur_val
        sigma = 0.3 * ((ks - 1) * 0.5 - 1) + 0.8

        l = ks
        ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
        gauss = np.exp(-0.5 * np.square(ax) / np.square(sigma))
        kernel = np.outer(gauss, gauss)
        kernel = kernel / np.sum(kernel)

        # prev_merged_layers = np.pad(prev_merged_layers, (blur_val- 1) //2 )
        s = prev_merged_layers.shape
        pad_num = (blur_val - 1) // 2
        padded = np.zeros((s[0] + 2 * pad_num, s[1] + 2 * pad_num))
        for pad_i in range(s[0]):
            for pad_j in range(s[1]):
                padded[pad_i + pad_num, pad_j + pad_num] = prev_merged_layers[pad_i, pad_j]

        prev_merged_layers = conv2d_fast_nm(padded, kernel)


        # prev_merged_layers = prev_merged_layers[blur_val-1:-blur_val-1, blur_val-1:-blur_val-1]
        print(prev_merged_layers.shape)

        # ret_val, prev_merged_layers = cv2.threshold(
        #     prev_merged_layers,
        #     255 - thresh_val,
        #     255, cv2.THRESH_BINARY)
        s = prev_merged_layers.shape
        prev_merged_layers = prev_merged_layers.flatten()
        prev_merged_layers[prev_merged_layers > 255 - thresh_val] = 255
        prev_merged_layers[prev_merged_layers <= 255 - thresh_val] = 0
        prev_merged_layers = prev_merged_layers.reshape(s)

        # cv2.imwrite("./png layers/" + str(i) + ".png", prev_merged_layers)
        png_layers.append(prev_merged_layers.copy())

        mask = prev_merged_layers > 0
        s = prev_merged_layers.shape
        prev_merged_layers = prev_merged_layers.flatten()
        mask = mask.flatten()
        # prev_merged_layers[mask] = shades[i]
        # prev_merged_layers[mask] = 1
        prev_merged_layers[mask] = shades[i]
        # prev_merged_layers = prev_merged_layers.reshape(s)

        mask = merged_layers == 0
        s = mask.shape
        mask = mask.flatten()
        merged_layers = merged_layers.flatten()
        # prev_merged_layers = prev_merged_layers.flatten()
        merged_layers[mask] = prev_merged_layers[mask]
        # cv2.imwrite("blurred_layers/layer_" + str(i) + ".png" , merged_layers)
        prev_merged_layers = merged_layers.copy()
        merged_layers = merged_layers.reshape(s)
        prev_merged_layers = prev_merged_layers.reshape(s)
        # print('debug 3')
    # cv2.imwrite("blurred_out_BL.png", merged_layers)

    # merged_layers = np.stack((merged_layers) * 3, axis=-1)
    rgb = np.zeros((merged_layers.shape[0], merged_layers.shape[1], 3))
    rgb[:, :, 0] = merged_layers
    rgb[:, :, 1] = merged_layers
    rgb[:, :, 2] = merged_layers

    # print('debug 4')

    # black_pixels = np.all(rgb == [0, 0, 0], axis=-1)
    # rgb[black_pixels] = [255, 0, 0]

    for blue_i in range(rgb.shape[0]):
        for blue_j in range(rgb.shape[1]):
            if rgb[blue_i, blue_j, 0] == 0:
                rgb[blue_i, blue_j] = np.array([0, 0, 255], dtype=np.uint8)

    # cv2.imwrite("1.png", merged_layers)

    print()
    print("total points", point_counter)
    print("done")

    return png_layers, rgb


@njit(cache=True, parallel=True, fastmath=True)
def conv2d_fast_nm(img, krn):
    is0, is1, ks0, ks1 = *img.shape, *krn.shape
    rs0, rs1 = is0 - ks0 + 1, is1 - ks1 + 1
    res = np.zeros((rs0, rs1), dtype=krn.dtype)

    for k in range(ks0):
        for l in range(ks1):
            for i in range(rs0):
                for j in range(rs1):
                    res[i, j] += krn[k, l] * img[i + k, j + l]

    return res


# @njit()
def conv2d_fast_numba(img, krn, *, state={}):
    if 'f' not in state:
        import numpy as np

        def conv2d_fast_nm(img, krn):
            is0, is1, ks0, ks1 = *img.shape, *krn.shape
            rs0, rs1 = is0 - ks0 + 1, is1 - ks1 + 1
            res = np.zeros((rs0, rs1), dtype=krn.dtype)

            for k in range(ks0):
                for l in range(ks1):
                    for i in range(rs0):
                        for j in range(rs1):
                            res[i, j] += krn[k, l] * img[i + k, j + l]

            return res

        import numba
        state['f'] = numba.njit(cache=True, parallel=True, fastmath=True)(conv2d_fast_nm)

    return state['f'](img, krn)


@njit()
def crop_pixels(pixels, furthest_frozen_point):
    center = (pixels.shape[0] // 2, pixels.shape[1] // 2)
    buffer = 1
    d = int(dist_to_center(furthest_frozen_point, center)) + buffer
    # d = int(d) * blur_layers_res_multiplier

    # c = center[0]
    # global pixels
    # global pixels_counters

    pixels = pixels[
             center[0] - d:
             center[0] + d,
             center[1] - d:
             center[1] + d
             ].copy()
    # pixels_counters = pixels_counters[
    #                   c - d:
    #                   c + d,
    #                   c - d:
    #                   c + d
    #                   ].copy()

    return pixels


def save_pixels():
    cv2.imwrite("tree.png", pixels)


@njit()
def scale_pixels(pixels, scale):
    out_pixels = np.zeros((pixels.shape[0] * scale, pixels.shape[0] * scale), np.uint8)
    for i in range(out_pixels.shape[0]):
        for j in range(out_pixels.shape[1]):
            out_pixels[i, j] = pixels[i // scale, j // scale]
    return out_pixels




import time

t = time.perf_counter()

pixels,pixels_counters, params = grow_tree()

print(time.perf_counter() - t)

cv2.imwrite("tree.png", pixels)
# exit()

png_layers, blurred_layers = generate_layers_numpy(pixels, pixels_counters, params)

for i in range(len(png_layers)):
    print("saving layers ",  len(png_layers) - i)
    cv2.imwrite("./png layers/" + str(i) + ".png", png_layers[i])


cv2.imwrite("blurred_out.png", blurred_layers)
