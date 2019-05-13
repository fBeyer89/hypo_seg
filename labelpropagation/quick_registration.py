# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 11:12:11 2015

@author: fbeyer
"""

from nipype.pipeline.engine import Node, MapNode, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.ants as ants
'''
Workflow for performing quick registration of target image in template space &
atlas images in template space.

A QUICK REGISTRATION performs a deformable registration using the same parameters as the 
full registration, and was only performed at the first three levels, excluding the full resolution level.
'''
def create_quick_registration(name='quickreg'):
    # workflow
    quickreg=Workflow(name='quickreg')
    # inputnode
    inputnode=Node(util.IdentityInterface(fields=['anat', 'standard']),    name='inputnode')
    #MapNode(util.IdentityInterface(fields=['anat', 'standard']),    name='inputnode', iterfield=['anat'])
    # outputnode
    outputnode=Node(util.IdentityInterface(fields=['anat2std_transforms', 'composite', 'anat2std', 'std2anat_transforms', 'std2anat', 'inverse_composite']),
    name='outputnode')

    antsreg= Node(ants.Registration(dimension=3,
    transforms=['SyN'],
    metric=['CC'],
    metric_weight=[1],
    number_of_iterations=[[70,50,30]],
    convergence_threshold=[1e-6],
    convergence_window_size=[10],
    shrink_factors=[[8,4,2]],
    smoothing_sigmas=[[3,2,1]],
    sigma_units=['vox'],
    initial_moving_transform_com=1,
    transform_parameters=[(0.1,3.0,0.0)],
    sampling_strategy=['None'],
    sampling_percentage=[1],
    radius_or_number_of_bins=[4],
    num_threads=1,
    interpolation='Linear',
    winsorize_lower_quantile=0.005,
    winsorize_upper_quantile=0.995,
    collapse_output_transforms=True,
    output_warped_image=True,
    write_composite_transform=True,
    #output_inverse_warped_image=True,
    #output_warped_image=True,
    use_histogram_matching=True,
    ),
    name='antsreg')
    # connections
    quickreg.connect([
    (inputnode, antsreg, 
    [('anat', 'moving_image'), 
     ('standard', 'fixed_image')]),
    (antsreg, outputnode, 
    [('forward_transforms', 'anat2std_transforms'),
    ('reverse_transforms', 'std2anat_transforms'),
    ('inverse_composite_transform', 'inverse_composite'),
    ('warped_image', 'anat2std'),
    ('composite_transform', 'composite'),
    ('inverse_warped_image', 'std2anat')])
    ])
    
    return quickreg