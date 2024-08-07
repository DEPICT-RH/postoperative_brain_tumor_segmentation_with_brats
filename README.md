# postoperative_brain_tumor_segmentation_with_brats

convert_brats2021_to_twolabel.py
converts BraTS2021 segmentation files to a two-label format provided HD-GLIO segmentation files.

# Prerequisites:
    The python script requires the packages:
      argparse, numpy, nibabel and scipy.
    
# Usage:
    python convert_brats2021_to_twolabel.py <brats_file> <hdglio_file> <output_file> [--cluster_size_threshold 50] [--at_fill True]

# Arguments:
    brats_file: Path to the original BraTS2021 segmentation NIfTI file.
    hdglio_file: Path to the HD-GLIO segmentation NIfTI file.
    output_file: Path to save the converted NIfTI file.
    --cluster_size_threshold: Minimum cluster size threshold (voxels) (default: 50).
    --at_fill: Fill completely AT enclosed necrosis (default: True).

# Example:
    python convert_brats2021_to_twolabel.py ./data/brats2021_seg.nii.gz ./data/hdglio_seg.nii.gz ./output/output_twolabel_seg.nii.gz
