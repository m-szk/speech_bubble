import argparse
import os
import pysrt
import sys
from speech_bubble import speech_bubble


def get_text_list(srt_file):
    subs = pysrt.open(srt_file, encoding="utf-8")
    return [sub.text for sub in subs]


def main():
    # fmt: off
    parser = argparse.ArgumentParser(description="Process srt to speech bubble image.")
    parser.add_argument("srt_file", type=str, help="srt file")
    parser.add_argument("font_name", type=str, help="font name")
    parser.add_argument("font_size", type=str, help="font size")
    parser.add_argument("outline_percentage", type=float, help="1.0 = 100%")
    parser.add_argument("nine_slice_image", type=str, help="speech bubble image")
    parser.add_argument("left", type=int, help="9slice left position")
    parser.add_argument("top", type=int, help="9slice top position")
    parser.add_argument("right", type=int, help="9slice right position")
    parser.add_argument("bottom", type=int, help="9slice bottom position")
    parser.add_argument("output_dir", type=str, help="output image directory")
    parser.add_argument('-b', '--blur', type=int, help='blur power')
    args = parser.parse_args()
    # fmt: on

    if not args.output_dir or not os.path.isdir(args.output_dir):
        print(f"Does not exist directory. : {args.output_dir}")
        sys.exit(1)

    for index, text in enumerate(get_text_list(args.srt_file)):
        output_image = os.path.join(args.output_dir, f"{index:03}.png")
        speech_bubble(
            text,
            args.font_name,
            args.font_size,
            args.outline_percentage,
            args.nine_slice_image,
            args.left,
            args.top,
            args.right,
            args.bottom,
            output_image,
            args.blur,
        )


if __name__ == "__main__":
    main()
