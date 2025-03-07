import argparse
import os
import sys
from speech_bubble import run_command


def create_1920x1080_image(icon_file, icon_x, icon_y, speech_bubble_dir, speech_bubble_x, speech_bubble_y, output_dir):
    if not speech_bubble_dir or not os.path.isdir(speech_bubble_dir):
        print(f"Does not exist directory. : {speech_bubble_dir}")
        sys.exit(1)

    if not output_dir or not os.path.isdir(output_dir):
        print(f"Does not exist directory. : {output_dir}")
        sys.exit(1)

    for root, _, files in os.walk(speech_bubble_dir):
        files = sorted(files)
        for file in files:
            if file.endswith(".png"):
                filepath = os.path.join(root, file)
                output_filepath = os.path.join(output_dir, f"output_{file}")
                cmd = [
                    "convert", "-size", "1920x1080", "xc:none",
                    f"{icon_file}", "-gravity", "southwest", "-geometry", f"+{icon_x}+{icon_y}", "-composite",
                    f"{filepath}", "-gravity", "southwest", "-geometry", f"+{speech_bubble_x}+{speech_bubble_y}", "-composite",
                    f"{output_filepath}"
                ]
                run_command(cmd)


def main():
    # コマンドライン引数のパーサーを設定
    parser = argparse.ArgumentParser(description="Process speech bubble image to 1920x1080 image.")
    parser.add_argument("icon_file", type=str, help="icon image file")
    parser.add_argument("icon_x", type=int, help="icon x position")
    parser.add_argument("icon_y", type=int, help="icon y position")
    parser.add_argument("speech_bubble_dir", type=str, help="sppech bubble image directory")
    parser.add_argument("speech_bubble_x", type=int, help="speech bubble x position")
    parser.add_argument("speech_bubble_y", type=int, help="speech bubble y position")
    parser.add_argument("output_dir", type=str, help="output directory")
    args = parser.parse_args()

    create_1920x1080_image(args.icon_file, args.icon_x, args.icon_y, args.speech_bubble_dir, args.speech_bubble_x, args.speech_bubble_y, args.output_dir)


if __name__ == "__main__":
    main()