# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:27:06 2015

@author: fbeyer
"""
'''
Workflow to run staple algorithm
'''
import sys
import os
from nipype.pipeline.engine import MapNode, Node, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.fsl as fsl
import nipype.interfaces.ants as ants
import nipype.interfaces.utility as util
from nipype.interfaces import niftyseg
import nipype.interfaces.io as nio

##Here, you need to append the path to the "seg-apps"-folder from niftyseg (https://github.com/KCL-BMEIS/NiftySeg)
#This folder contains the function seg_LabFusion which is
#wrapped by the nipype package: https://nipype.readthedocs.io/en/latest/interfaces/generated/interfaces.niftyseg/label_fusion.html#labelfusion
sys.path.append('/path/to/niftyseg/seg-apps')

data_dir = '/'
working_dir = '/some/wd/folder/staple/'
out_dir = '/some/results/folder/staple/'


staple_wf = Workflow(name='staple_wf')
staple_wf.base_dir=working_dir
staple_wf.config['execution']['crashdump_dir'] = staple_wf.base_dir + "/crash_files"


##selecting target subjects for which the hypothalami should be fusioned
all_subjects="/path/to/targets"
#

with open(all_subjects, 'r') as f:
    allsubjects = [line.strip() for line in f]

info = dict(
    atlas_input=[['/path/to/merged/','target_id','','/merged/anat.nii.gz']],
    hyp_input=[['/path/to/merged/','hyp_','hemi','_swapped_RAS_trans_bin.nii.gz']],
    orig=[['/path/to/originalt1/','_t1.nii.gz']]   
    )

datasource = Node(
    interface=nio.DataGrabber(infields=['target_id', 'hemi'], outfields=['atlas_input','hyp_input','orig']), #,'c1'
    name='datasource')
datasource.inputs.base_directory = data_dir
datasource.iterables=[('hemi',['re','li']), ('target_id', allsubjects)]
datasource.inputs.template = '%s%s%s%s%s%s'
datasource.inputs.template_args = info
datasource.inputs.sort_filelist = True  


staple = MapNode(niftyseg.LabelFusion(),name = 'staple', iterfield=['classifier_type'])
staple.inputs.classifier_type=['STEPS'] 
staple.inputs.prob_flag=False
staple.inputs.unc=True
staple.inputs.kernel_size=3
staple.inputs.template_num=44
staple.inputs.sm_ranking='LNCC' 



	
sink = Node(nio.DataSink(parameterization=True,
base_directory=out_dir,substitutions=[('_staple0', 'steps'),('_staple1','staple'), \
('lh_merged_maths_maths_steps','lh_hyp_steps'), \
('rh_merged_maths_maths_steps','rh_hyp_steps'), \
('lh_merged_maths_maths_staple','lh_hyp_staple'), \
('rh_merged_maths_maths_staple','rh_hyp_staple'), \
('_template_num_10','atlas_n10'),\
('_template_num_43','atlas_n43'),\
('_hemi_lh_','lh_'),\
('_hemi_rh_','rh_')]),
name='sink')

staple_wf.connect([
(datasource, staple, [('hyp_input', 'in_file')]),
(datasource, staple, [('orig','file_to_seg')]),
(datasource, staple, [('atlas_input','template_file')]),
(staple, sink, [('out_file', 'staple.out_label')])
])

staple_wf.run(plugin='MultiProc')#plugin='CondorDAGMan')#plugin='MultiProc') #)#)#
