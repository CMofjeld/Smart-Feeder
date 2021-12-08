"""Generate a Deepstream compatible label file from TAO generated classmap.json"""
import json
import argparse

def main():
    # Parse args
    parser = argparse.ArgumentParser("generate a Deepstream compatible label file from TAO generated classmap.json")
    parser.add_argument("-c", "--classmap_path", type=str, help="path to classmap.json")
    parser.add_argument("-o", "--output_file", type=str, help="path to output file")
    args = parser.parse_args()

    # Load classmap JSON into memory and convert to dict
    with open(args.classmap_path, "r") as classmap_file:
        class_dict = json.load(classmap_file)

    # Get just the class labels
    labels = class_dict.keys()

    # Write to labelfile
    with open(args.output_file, "w") as labelfile:
        output_str = ";".join(labels) + "\n"
        labelfile.write(output_str)

if __name__ == "__main__":
    main()