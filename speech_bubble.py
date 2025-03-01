import argparse
import os
import subprocess
from PIL import Image  # Pillowライブラリをインポート

TEMP_TEXT_PNG = ".temp.text.png"


def get_temp_image_name(nine_slice_image):
    return f".temp.{os.path.basename(nine_slice_image)}"


def get_image_size(image_path):
    with Image.open(image_path) as img:
        return img.size


def print_cmd(cmd):
    output_cmd = []
    for c in cmd:
        if c == "(" or c == ")":
            output_cmd.append(f"\\{c}")
        else:
            output_cmd.append(c)
    print(" ".join(output_cmd))


def run_command(cmd):
    print_cmd(cmd)
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def create_text_image(text, font_name, font_size, output_image):
    # fmt: off
    cmd = [
        "magick", "-font", f"{font_name}",
        "-background", "None", "-pointsize", f"{font_size}",
        f"label:{text}", f"{output_image}"
    ]
    # fmt: on
    run_command(cmd)


def create_background_image(
    width, height, nine_slice_image, left, top, right, bottom, output_image
):
    img_width, img_height = get_image_size(nine_slice_image)
    print(f"{nine_slice_image} image size: {img_width}x{img_height}")

    # fmt: off
    cmd = [
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
        f"{output_image}"
    ]
    # fmt: on
    run_command(cmd)


def create_speech_bubble_image(background_image, output_image):
    # fmt: off
    cmd = [
        "composite", "-gravity", "center",
        f"{TEMP_TEXT_PNG}", f"{background_image}",
        f"{output_image}"
    ]
    # fmt: on
    run_command(cmd)


def main():
    # fmt: off
    parser = argparse.ArgumentParser(description="Process text and 9slice image to speech bubble image.")
    parser.add_argument("text", type=str, help="speech bubble text")
    parser.add_argument("font_name", type=str, help="font name")
    parser.add_argument("font_size", type=str, help="font size")
    parser.add_argument("nine_slice_image", type=str, help="speech bubble image")
    parser.add_argument("left", type=int, help="9slice left position")
    parser.add_argument("top", type=int, help="9slice top position")
    parser.add_argument("right", type=int, help="9slice right position")
    parser.add_argument("bottom", type=int, help="9slice bottom position")
    parser.add_argument("output_image", type=str, help="output image file")
    args = parser.parse_args()

    create_text_image(args.text, args.font_name, args.font_size, TEMP_TEXT_PNG)
    text_img_width, text_img_height = get_image_size(TEMP_TEXT_PNG)

    temp_image_name = get_temp_image_name(args.nine_slice_image)
    create_background_image(
        text_img_width, text_img_height,
        args.nine_slice_image, args.left, args.top, args.right, args.bottom,
        temp_image_name
    )
    # fmt: on

    create_speech_bubble_image(temp_image_name, args.output_image)


if __name__ == "__main__":
    main()
