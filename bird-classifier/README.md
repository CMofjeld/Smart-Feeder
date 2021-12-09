# Bird Classifier
## Summary
This directory contains the code used to train and evaluate the classification model that identifies bird species.

## Setup
1. Install [Nvidia TAO Toolkit](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html).
2. Download the [CUB200 dataset](http://www.vision.caltech.edu/visipedia/CUB-200-2011.html).
3. Organize the data into the [structure and format expected by the toolkit](https://docs.nvidia.com/tao/tao-toolkit/text/data_annotation_format.html). Skip step 2.A when running the notebook.

## Generating Deepstream compatible labels
To generate a label file that is compatible with Deepstream, run the provided python script:
```bash
python generate_ds_labelfile.py -c [path to classmap.json] -o [path to output generated label file at]
```

## Acknowledgements
The notebook used here is taken from the [Nvidia TAO CV Sample Workflows container](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/resources/cv_samples).