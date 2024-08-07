"""
convert_brats2021_to_twolabel.py

This script converts BraTS2021 segmentation files to a two-label format provided HD-GLIO segmentation files.

Usage:
    python convert_brats2021_to_twolabel.py <brats_file> <hdglio_file> <output_file> [--cluster_size_threshold 50] [--at_fill True]

Arguments:
    brats_file: Path to the original BraTS2021 segmentation NIfTI file.
    hdglio_file: Path to the HD-GLIO segmentation NIfTI file.
    output_file: Path to save the converted NIfTI file.
    --cluster_size_threshold: Minimum cluster size threshold (voxels) (default: 50).
    --at_fill: Fill completely AT enclosed necrosis (default: True).

Example:
    python convert_brats2021_to_twolabel.py ./data/brats2021_seg.nii.gz ./data/hdglio_seg.nii.gz ./output/output_twolabel_seg.nii.gz

License:
    Copyright 2024 Peter Jagd Sørensen
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Citation:
    If you use this script in your research, please cite the following article:

    [Full Citation]
    DOI: [DOI link]
"""

import argparse
import numpy as np
import nibabel as nib
from scipy import ndimage as ndi

def read_nifti(nifti, dtype=None):
    image_in = nib.load(f'{nifti}')
    volume = image_in.get_fdata()

    if dtype:
        image_in.header.set_data_dtype(dtype)
        volume = volume.astype(dtype)

    return volume, image_in


def write_nifti(template_image, data, nifti_out, dtype=None):

    if dtype:
        template_image.header.set_data_dtype(dtype)
        data = data.astype(dtype)

    image_out = nib.Nifti1Image(data, template_image.affine, template_image.header)
    nib.save(image_out, f'{nifti_out}')


def convert_data_brats2021_to_twolabel(d_brats, d_hdglio, cluster_size_threshold=50, at_fill=True):
    # Prerequisite conversion step 1: Obtain tumour segmentation using HD-GLIO.
    # This step must be conducted independently with HD-GLIO and be provided with argument d_hdglio.
    # https://github.com/CCI-Bonn/HD-GLIO (accessed August 7, 2024)
    
    # Conversion step 2 and 3: Filter BraTS NCR/NET to inside HD-GLIO WT and combine with ED (essentially removing NCR)
    NE = np.where(((d_hdglio != 0) & (d_brats == 1)) | (d_brats == 2), 1, 0)

    # Conversion step 4: Remove completely AT enclosed necrosis
    if at_fill:
        AT = np.where(d_brats == 4, 1, 0)
        filled_AT = ndi.binary_fill_holes(AT)
        enclosed_NCR = np.where((filled_AT == 1) & (AT == 0), 1, 0)
        NE = np.where(enclosed_NCR == 1, 0, NE)

    # Conversion step 5 and 6: Remove from NE isolated clusters smaller than threshold (voxels)
    threshold = cluster_size_threshold  # set cluster minimum size threshold (voxels)
    labelled_NE, nlabels = ndi.label(NE) # label clusters of NCR/NET
    lbls, n = np.unique(labelled_NE, return_counts=True)  # count the number of voxels n in each cluster labelled lbls
    lbls_above_thr = lbls[(n > threshold) & (lbls > 0)]  # Threshold. Nb 0 is background and should be removed always    
    # Update NE with clusters > 50 surviving, and always ED (no matter cluster size)
    NE_out = np.where(np.isin(labelled_NE, lbls_above_thr) | (d_brats == 2), 1, 0)  # update NE
    
    # Conversion step 7: Transfer AT to CE
    d_out = np.where(d_brats == 4, 2, NE_out)  # insert CE

    return d_out


def convert_file_brats2021_to_twolabel(brats_file, hdglio_file, output_file, cluster_size_threshold=50, at_fill=True):
    
    dtype=np.uint8  # desired data type - uint8 suffice and keeps file size small
    # Read files
    d_brats, brats_image = read_nifti(brats_file, dtype=dtype)  # Original BraTS 2021 three-label (1 [NCR/NET], 2 [ED] and 4 [AT]) segmentation
    d_hdglio, hdglio_image = read_nifti(hdglio_file, dtype=dtype)  # HD-GLIO two-label segmentation
    
    # Convert
    d_converted = convert_data_brats2021_to_twolabel(d_brats, d_hdglio, cluster_size_threshold=cluster_size_threshold, at_fill=True)
    
    # Save to file
    write_nifti(brats_image, d_converted, output_file, dtype=np.uint8)
    

def main():
    parser = argparse.ArgumentParser(description='Convert BraTS2021 segmentation to two-label format using HD-GLIO segmentation.')
    parser.add_argument('brats_file', type=str, help='Path to the original BraTS2021 segmentation NIfTI file.')
    parser.add_argument('hdglio_file', type=str, help='Path to the HD-GLIO segmentation NIfTI file.')
    parser.add_argument('output_file', type=str, help='Path to save the converted NIfTI file.')
    parser.add_argument('--cluster_size_threshold', type=int, default=50, help='Minimum cluster size threshold (voxels) (default: 50).')
    parser.add_argument('--at_fill', type=bool, default=True, help='Fill completely AT enclosed necrosis (default: True).')

    args = parser.parse_args()

    convert_file_brats2021_to_twolabel(
        args.brats_file, 
        args.hdglio_file, 
        args.output_file, 
        cluster_size_threshold=args.cluster_size_threshold, 
        at_fill=args.at_fill
    )


if __name__ == '__main__':
    main()
