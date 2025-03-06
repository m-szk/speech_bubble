import argparse
import math
import os
import subprocess
from PIL import Image  # Pillowライブラリをインポート

TEMP_TEXT_PNG = ".temp.text.png"
TEMP_OUTLINE_TEXT_PNG = ".temp.outline.png"
OUTLINE_PERCENTAGE = 0.07


def _get_temp_image_name(nine_slice_image):
    return f".temp.{os.path.basename(nine_slice_image)}"


def get_image_size(image_path):
    with Image.open(image_path) as img:
        return img.size


def _print_cmd(cmd):
    output_cmd = []
    for c in cmd:
        if c == "(" or c == ")":
            output_cmd.append(f"\\{c}")
        else:
            output_cmd.append(c)
    print(" ".join(output_cmd))


def run_command(cmd):
    _print_cmd(cmd)
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _create_outline_text_image(
    width,
    height,
    text,
    font_name,
    font_size,
    font_color,
    outline_percentage,
    outline_color,
    output_image,
    blur=0,
):
    # fmt: off
    outline_size = max(1, math.ceil(float(font_size) * outline_percentage))
    cmd = []
    cmd_1 = [
        "magick", "-size", f"{width}x{height}", "xc:none",
        "-font", f"{font_name}", "-background", "None", "-pointsize", f"{font_size}",
        "-fill", f"{outline_color}", "-stroke", f"{outline_color}", "-strokewidth", f"{outline_size}", "-gravity", "West",
        "-annotate", "0", f"{text}",
    ]
    cmd_blur = [
        "-gaussian-blur", f"0x{blur}",
    ]
    cmd_2 = [
        "-fill", f"{font_color}", "-stroke", "none",
        "-annotate", "0", f"{text}", f"{output_image}"
    ]
    # fmt: on
    cmd.extend(cmd_1)
    if blur is not None and blur > 0:
        cmd.extend(cmd_blur)
    cmd.extend(cmd_2)
    run_command(cmd)


def _create_text_image(text, font_name, font_size, output_image):
    # fmt: off
    cmd = [
        "magick", "-font", f"{font_name}",
        "-background", "None", "-pointsize", f"{font_size}",
        f"label:{text}", "-gravity", "West", f"{output_image}"
    ]
    # fmt: on
    run_command(cmd)


def _create_background_image(
    width, height, nine_slice_image, nine_slice_color, left, top, right, bottom, output_image, 
):
    img_width, img_height = get_image_size(nine_slice_image)
    print(f"{nine_slice_image} image size: {img_width}x{img_height}")

    # fmt: off
    cmd = []
    cmd_1 = [
        "magick", nine_slice_image, "-write", "mpr:org", "+delete",
        "(", "mpr:org", "-crop", f"{left}x{top}+0+0", "+repage", ")",
        "(", "mpr:org", "-crop", f"{right - left}x{top}+{left}+0", "-resize", f"{width}x{top}!", ")",
        "(", "mpr:org", "-crop", f"{img_width - right}x{top}+{right}+0", "+repage", ")",
        "+append", "-write", "mpr:top", "+delete",
        "(", "mpr:org", "-crop", f"{left}x{bottom - top}+0+{top}", "-resize", f"{left}x{height}!", ")",
        "(", "mpr:org", "-crop", f"{right - left}x{bottom - top}+{left}+{top}", "-resize", f"{width}x{height}!", ")",
        "(", "mpr:org", "-crop", f"{img_width - right}x{bottom - top}+{right}+{top}", "-resize", f"{img_width - right}x{height}!", ")",
        "+append", "-write", "mpr:middle", "+delete",
        "(", "mpr:org", "-crop", f"{left}x{img_height - bottom}+0+{bottom}", "+repage", ")",
        "(", "mpr:org", "-crop", f"{right - left}x{img_height - bottom}+{left}+{bottom}", "-resize", f"{width}x{img_height - bottom}!", ")",
        "(", "mpr:org", "-crop", f"{img_width - right}x{img_height - bottom}+{right}+{bottom}", "+repage", ")",
        "+append", "-write", "mpr:bottom", "+delete",
        "mpr:top", "mpr:middle", "mpr:bottom", "-append",
    ]
    cmd_nine_slice_color = [
        "-fill", f"{nine_slice_color}", "-colorize", "100%",
    ] 
    cmd_2 = [
        f"PNG00:{output_image}"
    ]
    # fmt: on
    cmd.extend(cmd_1)
    if nine_slice_color:
        cmd.extend(cmd_nine_slice_color)
    cmd.extend(cmd_2)
    run_command(cmd)


def _create_speech_bubble_image(text_image, background_image, output_image):
    # fmt: off
    cmd = [
        "composite", "-gravity", "center",
        f"{text_image}", f"{background_image}",
        f"{output_image}"
    ]
    # fmt: on
    run_command(cmd)


def speech_bubble(
    output_image,
    text,
    font_name,
    font_size,
    font_color,
    outline_percentage,
    outline_color,
    nine_slice_image,
    left,
    top,
    right,
    bottom,
    blur = 0,
    nine_slice_color = None,
):
    # fmt: off
    _create_text_image(text, font_name, font_size, TEMP_TEXT_PNG)
    text_img_width, text_img_height = get_image_size(TEMP_TEXT_PNG)
    text_img_width += font_size * outline_percentage
    text_img_height += font_size * outline_percentage

    _create_outline_text_image(text_img_width, text_img_height, text, font_name, font_size, font_color, outline_percentage, outline_color, TEMP_OUTLINE_TEXT_PNG, blur)

    temp_image_name = _get_temp_image_name(nine_slice_image)
    _create_background_image(
        text_img_width, text_img_height,
        nine_slice_image, nine_slice_color, left, top, right, bottom,
        temp_image_name
    )
    # fmt: on

    _create_speech_bubble_image(TEMP_OUTLINE_TEXT_PNG, temp_image_name, output_image)


def main():
    # fmt: off
    parser = argparse.ArgumentParser(description="Process text and 9slice image to speech bubble image.")
    parser.add_argument("text", type=str, help="speech bubble text")
    parser.add_argument("font_name", type=str, help="font name")
    parser.add_argument("font_size", type=int, help="font size")
    parser.add_argument("font_color", type=str, help="font color")
    parser.add_argument("outline_percentage", type=float, help="1.0 = 100%")
    parser.add_argument("outline_color", type=str, help="outline color")
    parser.add_argument("nine_slice_image", type=str, help="speech bubble image")
    parser.add_argument("left", type=int, help="9slice left position")
    parser.add_argument("top", type=int, help="9slice top position")
    parser.add_argument("right", type=int, help="9slice right position")
    parser.add_argument("bottom", type=int, help="9slice bottom position")
    parser.add_argument("output_image", type=str, help="output image file")
    parser.add_argument('-b', '--blur', type=int, help='blur power')
    parser.add_argument('-c', '--color', type=str, help='9slice color')
    args = parser.parse_args()
    # fmt: on

    speech_bubble(
        args.output_image,
        args.text,
        args.font_name,
        args.font_size,
        args.font_color,
        args.outline_percentage,
        args.outline_color,
        args.nine_slice_image,
        args.left,
        args.top,
        args.right,
        args.bottom,
        args.blur,
        args.color
    )


if __name__ == "__main__":
    main()
