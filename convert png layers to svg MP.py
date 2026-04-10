import vtracer

from pathlib import Path
import svgutils

from svgpathtools import svg2paths2, wsvg
import multiprocessing




def scale_svg_centered(input_file, output_file, scale_factor):
    paths, attributes, svg_attributes = svg2paths2(input_file)

    paths: list = paths
    attributes: list = attributes

    paths.pop(0)
    attributes.pop(0)

    print(len(paths))
    print(len(attributes))
    print(len(svg_attributes))

    scaled_paths = []
    for i in range(len(paths)):

        if "transform" in attributes[i]:
            # print("transf")
            s: str = attributes[i]['transform']
            s = s.lstrip("translate")
            s = s.strip("()").split(',')
            x = int(s[0])
            y = int(s[1])
            # print(x, y)
            x = x * scale_factor
            y = y * scale_factor
            attributes[i]["transform"] = "translate(" + str(x) + "," + str(y) + ")"

        attributes[i]['fill'] = "white"
        attributes[i]['stroke'] = "red"
        attributes[i]['stroke-width'] = "4"
        p = paths[i].scaled(scale_factor)

        scaled_paths.append(p)

    if "width" in svg_attributes:
        svg_attributes["width"] = str(float(svg_attributes["width"]) * scale_factor)

    if "height" in svg_attributes:
        svg_attributes["height"] = str(float(svg_attributes["height"]) * scale_factor)

    if "viewBox" in svg_attributes:
        vb = list(map(float, svg_attributes["viewBox"].split()))
        vb = [v * scale_factor for v in vb]
        svg_attributes["viewBox"] = " ".join(map(str, vb))

    wsvg(
        scaled_paths,
        attributes=attributes,
        svg_attributes=svg_attributes,
        filename=output_file
    )

def worker_convert_to_svg(file_name):

    file_path = file_name
    if file_path.is_file():
        print(file_path.name)
        input_path = "./png layers/" + file_path.name
        output_path = "./svg layers/" + file_path.name + ".svg"
        vtracer.convert_image_to_svg_py(input_path, output_path, mode="polygon", length_threshold=0)

# if __name__ == '__main__':




    # directory_path = Path('./png layers')
    # file_names = directory_path.iterdir()
    # file_names = list(file_names)
    # p = multiprocessing.Pool(12)
    # p.map(worker_convert_to_svg, file_names)
    # exit()

# input_path = './png layers/9.png'
# output_path = './svg layers/9.png.svg'
# vtracer.convert_image_to_svg_py(input_path, output_path, mode="polygon")
input_path = './svg layers/9.png.svg'
output_path = './svg scaled and formatted/9.png.svg'
scale_svg_centered(input_path, output_path, scale_factor=0.0607422857)
exit()



# directory_path = Path('./svg layers')
# for file_path in directory_path.iterdir():
#     print(file_path)
#     # if file_path.is_file():
#     input_path = "./svg layers/" + file_path.name
#     output_path = "./svg scaled and formatted/" + file_path.name
#     scale_svg_centered(input_path, output_path, scale_factor=0.0607422857)
