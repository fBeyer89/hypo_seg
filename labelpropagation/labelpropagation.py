# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 11:55:10 2018

@author: fbeyer
"""
#import from nipype and other packages
import numpy as np
import pandas as pd
import os
import sys
from nipype.pipeline.engine import MapNode, Node, Workflow
import nipype.interfaces.io as nio
from nipype.interfaces.utility import Function
import nipype.interfaces.utility as util
import itertools

#import from functions (should be in the same folder as labelpropagation.py)
from quick_registration import create_quick_registration
from warp_transform_with_datagrabber import create_warp_transform
from ants_registration_wf_parallel import create_normalize_pipeline

###############################################################################
#THIS SCRIPT generates multilabel-atlas propagation to target images for hypothalamus segmentation


# Specify the location of the atlas data
data_dir="/path/to/atlas" #MODIFY
#Specify the working directory
working_dir="/path/to/wd/" #MODIFY

#path to template
ref="/some/path/to/T150template0.nii.gz" #MODIFY

#give here the list of the atlas images, and the images you'd like to segment
atlaslist="N44_atlas_images.txt"     #MODIFY                      
testlist="/path/to/your/targets.txt" #MODIFY


with open(atlaslist, 'r') as f:
    atlassubjects = [line.strip() for line in f]
with open(testlist, 'r') as f:
    targetsubjects = [line.strip() for line in f]

print atlassubjects


    
     
out_dir="/path/to/outputdir/"
 
#initialize labelpropagation workflow    
labelpropagation = Workflow(name='labelpropagation')   
labelpropagation.base_dir = working_dir + '/' 
labelpropagation.config['execution']['crashdump_dir'] = labelpropagation.base_dir + "/crash_files"


#first initialize registration of target to template  (the target should be a skull-stripped t1-weighted image) 
info = dict(
       target_native=[['path/to/','target_id','/','target_id','_skullstrippedt1.nii.gz']], #MODIFY
       )   

datasource_target = Node(
    interface=nio.DataGrabber(infields=['target_id'], outfields=['target_native']),
    name='datasource_t')
datasource_target.inputs.base_directory = data_dir
datasource_target.inputs.template = '%s%s%s%s%s' #MODIFY according to your datastructure.
datasource_target.inputs.template_args = info
datasource_target.inputs.sort_filelist = True   
datasource_target.iterables=[("target_id", targetsubjects)]
    
#full registration of test subject to template
normalize_to_template=create_normalize_pipeline()   
normalize_to_template.inputs.inputnode.standard=ref              


info = dict(
    atlas_native=[['path/to/atlas/T150template0','atlas_id','_MPRAGE_t1_reorient_16bit_acpc_noz0_skullstrippedRepaired.nii.gz']],
    atlas_warped=[['path/to/atlas/','atlas_id','_MPRAGE_t1_reorient_16bit_acpc_noz0_skullstripped_WarpedToTemplate.nii.gz']],
    atlas_aff2template=[['path/to/atlas','atlas_id','_MPRAGE_t1_reorient_16bit_acpc_noz0_skullstripped_Affine.txt']],
    atlas_warp2template=[['path/to/atlas','atlas_id','_MPRAGE_t1_reorient_16bit_acpc_noz0_skullstripped_Warp.nii.gz']],
    right_hyp=[['path/to/atlas','atlas_id','_hyp_re_swapped_RAS.nii.gz']],
    left_hyp=[['path/to/atlas','atlas_id','_hyp_li_swapped_RAS.nii.gz']]
    )


datasource = Node(
    interface=nio.DataGrabber(infields=['atlas_id'], outfields=['atlas_native','atlas_warped', 'atlas_aff2template','atlas_warp2template','right_hyp','left_hyp']),
    name='datasource')
datasource.inputs.base_directory = data_dir
datasource.inputs.template = '%s%s%s'
datasource.inputs.template_args = info
datasource.inputs.sort_filelist = True
datasource.iterables=[("atlas_id", atlassubjects)]


def repeat_elements(ref):
    import itertools
    ref_list = itertools.repeat(ref,3)
    #ref_list=np.repeat(ref,3)  
    return list(ref_list)
    
collect_inputs = Node(interface = util.Merge(3),name='collect_inputs')  
collect_ref = Node(Function(input_names=["ref"],
                           output_names=["ref_list"],
                           function=repeat_elements),name='collect_ref')  

        

 
##do quick registration between target image and atlas-transformed images             
quickreg=create_quick_registration()

#combine warps and propagate the labels from the atlas images to the target image
#The label propagation is then performed by using the composition of the stored forward transforms of each atlas image (Aaffi and Adefi)
#and the inverses of the correction transform for that atlas (Cdefi) and the inverse of the initial transforms for the subject image (Saff and Sdef),
warp=create_warp_transform() 


#sink the data
sink = Node(nio.DataSink(parameterization=True,
                         base_directory=out_dir, substitutions=[('_pair_', ''),
                                                                ('_apply_ants_reg2', 'Hyp_li'),
                                                                ('_apply_ants_reg1', 'Hyp_re'),
                                                                ('_apply_ants_reg0', 'anat'),
                                                                ('_atlas_id_', 'coreg_atlas_')]),
                                                                 name='sink')


labelpropagation.connect(
[
(datasource_target, normalize_to_template, [('target_native', 'inputnode.anat')]), 
(datasource, quickreg, [('atlas_warped', 'inputnode.anat')]),
(normalize_to_template, quickreg, [('outputnode.anat2std', 'inputnode.standard')]),
(datasource, collect_inputs, [('atlas_native', 'in1')]),
(datasource, collect_inputs, [('right_hyp', 'in2')]),
(datasource, collect_inputs, [('left_hyp', 'in3')]),
(datasource_target, collect_ref, [('target_native', 'ref')]),
(collect_ref, warp, [('ref_list', 'inputnode.ref')]),
(collect_inputs, warp, [('out', 'inputnode.input_image')]),
(datasource, warp, [('atlas_aff2template', 'inputnode.atlas_aff2template')]),
(datasource, warp, [('atlas_warp2template', 'inputnode.atlas_warp2template')]),
(normalize_to_template, warp, [('outputnode.inverse_composite', 'inputnode.template2target_inverse')]),
(quickreg, warp, [('outputnode.composite','inputnode.atlas2target_composite')]),
(quickreg, sink, [('outputnode.composite','atlas2target_warps.@composite')]), 
(quickreg,sink, [('outputnode.inverse_composite', 'atlas2target_warps.@inverse')]),
(normalize_to_template,sink, [('outputnode.inverse_composite', 'target2template_warps.@inverse')]),
(normalize_to_template,sink, [('outputnode.composite', 'target2template_warps.@composite')]),
(warp, sink, [('outputnode.ants_reg','@reg')])  
 ])
 
 
#run the workflow in MultiProc option
labelpropagation.write_graph(graph2use='flat')
labelpropagation.run(plugin='MultiProc') #)CondorDAGMan')#, plugin='MultiProc'





