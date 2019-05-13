# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 11:12:11 2015

@author: fbeyer
"""

from nipype.pipeline.engine import MapNode,Node, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.ants as ants
'''
Workflow for normalization of the target image to the template using ANTs
'''
def create_normalize_pipeline(name='normalize'):
    # workflow
    normalize=Workflow(name='normalize')
    # inputnode
    inputnode=Node(util.IdentityInterface(fields=['anat', 'standard']),    name='inputnode')
    # outputnode
    outputnode=Node(util.IdentityInterface(fields=['anat2std_transforms', 'composite', 'inverse_composite', 'anat2std', 'std2anat_transforms', 'std2anat']),
    name='outputnode')
    # normalization with ants
    antsreg= Node(ants.Registration(dimension=3,
    transforms=['Rigid','Affine','SyN'],
    metric=['MI','MI','CC'],
    metric_weight=[1,1,1],
    number_of_iterations=[[1000,500,250,100],[1000,500,250,100],[100,70,50,20]],
    convergence_threshold=[1e-6,1e-6,1e-6],
    convergence_window_size=[10,10,10],
    shrink_factors=[[8,4,2,1],[8,4,2,1],[8,4,2,1]],
    smoothing_sigmas=[[3,2,1,0],[3,2,1,0],[3,2,1,0]],
    sigma_units=['vox','vox','vox'],
    initial_moving_transform_com=1,
    transform_parameters=[(0.1,),(0.1,),(0.1,3.0,0.0)],
    sampling_strategy=['Regular', 'Regular', 'None'],
    sampling_percentage=[0.25,0.25,1],
    radius_or_number_of_bins=[32,32,4],
    num_threads=1,
    interpolation='Linear',
    winsorize_lower_quantile=0.005,
    winsorize_upper_quantile=0.995,
    collapse_output_transforms=True,
    output_warped_image=True,
    write_composite_transform=True,
    output_inverse_warped_image=True,
    #output_warped_image=True,
    use_histogram_matching=True,
    ),
    name='antsreg')
    # connections
    normalize.connect([
    (inputnode, antsreg, 
    [('anat', 'moving_image'), 
     ('standard', 'fixed_image')]),
    (antsreg, outputnode, 
    [('forward_transforms', 'anat2std_transforms'),
     ('composite_transform','composite'),
     ('inverse_composite_transform', 'inverse_composite'),
    ('reverse_transforms', 'std2anat_transforms'),
    ('warped_image', 'anat2std'),
    ('inverse_warped_image', 'std2anat')])
    ])
    
    return normalize