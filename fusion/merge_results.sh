#!/bin/bash


for subj in XXX #loop through targets

##result directory for merged file of all hypothalami
res_dir="/data/pt_life/data_fbeyer/hypothalamus_atlas/multiatlas/newsegmentation_for_N236/merging/${subj}/merged/"
mkdir -p $res_dir

do
echo "running $subj"

#merging all atlas-based, warped anatomical images for the target.
if [ ! -f  $res_dir/anat.nii.gz ];
then
fslmerge -t  $res_dir/anat.nii.gz /path/to/results/_target_id_${subj}/coreg_atlas_*/anat/T150template0*_MPRAGE_t1_reorient_16bit_acpc_noz0_skullstrippedRepaired_trans.nii.gz

fslmaths $res_dir/anat.nii.gz -bin $res_dir/anat_bin.nii.gz

else
echo "merging anat done"
fi


#merging all atlas-based, warped hypothalami for the target.
for side in re li
do

echo "merging $side"

##Option to visualize result
#slicesdir /data/pt_life/data_fbeyer/hypothalamus_atlas/multiatlas/validate_intermediate_template_approach/results/${subj}/coreg_atlas_*/Hyp_${side}/*_hyp_${side}_swapped_RAS_trans.nii.gz
#mv slicesdir slicesdir_${side}

if [ ! -f $res_dir/hyp_${side}_swapped_RAS_trans.nii.gz ];
then
fslmerge -t $res_dir/hyp_${side}_swapped_RAS_trans.nii.gz /path/to/results/_target_id_${subj}/coreg_atlas_*/Hyp_${side}/*_hyp_${side}_swapped_RAS_trans.nii.gz

fslmaths $res_dir/hyp_${side}_swapped_RAS_trans.nii.gz -bin $res_dir/hyp_${side}_swapped_RAS_trans_bin.nii.gz

else 
echo "merging side $side done"
fi

done
done
