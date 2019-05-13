# hypo_seg: automated segmentation of hypothalamus with multi-atlas based label fusion

##This repository contains scripts for multi-atlas based hypothalamus segmentation. 
Input is an anatomical T1-weighted image (ideally 1 mm isotropic, acquired with the ADNI-protocol).
Output will be binary left and right hypothalamus segmentations.

for details please see: 
Thomas, K., Beyer, F., Witte, A.V.: "Altered hypothalamic microstructure in human obesity"
https://www.biorxiv.org/content/10.1101/593004v1

Steps in the algorithm: 
1.non-linear registration of the T1-weighted image to an intermediate template
2.non-linear registration of atlas images to target image in template space
3.propagation of hypothalamic segmentations from the atlas images (N=44 in total) to the target space
4.merging hypothalamic segmentations and label fusion

To perform the steps described in **Algorithm**:
Step 1, 2, 3: 
**labelpropagation/labelpropagation.py**
- TO DO: adapt paths to atlas files/target files/list of atlas and target SICs/ working directory/ output directory
- helper functions (don't modify anything here) are
	warp_transform_with_datagrabber.py
	quick_registration.py
	ants_registration_wf_parallel.py

Step 4.: 
**/fusion/merge_results.sh**
- bash-script to merge and binarize hypothalamic segmentations that were propagated from atlas images to target space
- TO DO: adapt paths to results from labelpropagation.

**/fusion/runstaple.py**
- TO DO: adapt paths to results from merge_results.
- merges binarized hypothalamic segmentations from all atlas images with the STEPS algorithm implemented in NiftySeg (https://github.com/KCL-BMEIS/NiftySeg/tree/master/seg-apps), wrapped in nipype (https://nipype.readthedocs.io/en/latest/interfaces/generated/interfaces.niftyseg/label_fusion.html#labelfusion)


For template and atlas images from the LIFE-Adult study, please visit: https://edmond.mpdl.mpg.de/imeji/collection/QEBGeGdvAXHCaS8m

#Atlas images
N44_atlas_images.txt: SIC (subject identification codes) of 44 atlas subjects.
atlasimages.tar.gz: contains folders of atlas subjects with the following files:

XXX_MPRAGE_t1_reorient_16bit_acpc_noz0_skullstrippedRepaired.nii.gz: original T1 image
XXX_hyp_re_swapped_RAS.nii.gz: semi-automatically, manually segmented right hypothalamus
XXX_hyp_li_swapped_RAS.nii.gz: semi-automatically, manually segmented right hypothalamus
XXX_MPRAGE_t1_reorient_16bit_acpc_noz0_skullstripped_WarpedToTemplate.nii.gz: T1 warped to intermediate template
XXX_MPRAGE_t1_reorient_16bit_acpc_noz0_skullstripped_Warp.nii.gz: warpfield from T1 to intermediate template
XXX_MPRAGE_t1_reorient_16bit_acpc_noz0_skullstripped_InverseWarp.nii.gz: inverse warpfield from T1 to intermediate template
XXX_MPRAGE_t1_reorient_16bit_acpc_noz0_skullstripped_Affine.txt: affine transform from T1 to intermediate template

#Template
T150template0.nii.gz: template originating from N=150 participants of the LIFE-Adult Study
