# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 14:00:12 2015
This script will create a workflow to collect and apply multiple warps
@author: fbeyer
"""
from nipype.pipeline.engine import MapNode, Node, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.fsl as fsl
import nipype.interfaces.ants as ants


def create_warp_transform(name='warpmultitransform'):
        # set fsl output type
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # initiate workflow
    warp = Workflow(name='warp')
    # inputnode
    inputnode=MapNode(util.IdentityInterface(fields=['input_image',
    'atlas_aff2template',
    'atlas_warp2template',
    'atlas2target_composite',
    'template2target_inverse',
    'ref'
    ]),
    name='inputnode',iterfield=['input_image', 'ref'])
    # outputnode
    outputnode=Node(util.IdentityInterface(fields=['ants_reg',
    ]),
    name='outputnode')

   
    collect_transforms = Node(interface = util.Merge(4),name='collect_transforms')    
        
    ants_reg = MapNode(ants.ApplyTransforms(input_image_type = 3, dimension = 3, interpolation = 'Linear'), name='apply_ants_reg', iterfield=['input_image', 'reference_image'])
    ants_reg.inputs.invert_transform_flags=[False,False,False,False]
    
    
    
    
    warp.connect([
                          (inputnode, ants_reg, [('input_image', 'input_image')]),
                          (inputnode, ants_reg, [('ref', 'reference_image')]),
                          (inputnode, collect_transforms, [('atlas_aff2template', 'in4')]),
                          (inputnode, collect_transforms, [('atlas_warp2template', 'in3')]),
                          (inputnode, collect_transforms, [('atlas2target_composite', 'in2')]),
                          (inputnode, collect_transforms, [('template2target_inverse', 'in1')]),                             
                          (collect_transforms, ants_reg,  [('out', 'transforms')]),#for WarpImageMultiTransform:transformation_series
                          (ants_reg, outputnode, [('output_image', 'ants_reg')])
                          ])
    
                          
    return warp