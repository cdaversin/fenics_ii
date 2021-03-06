import xii.assembler.trace_assembly
import xii.assembler.average_assembly
import xii.assembler.restriction_assembly
from xii.linalg.matrix_utils import is_number
from xii.assembler.ufl_utils import form_arity
from xii.linalg.list_utils import shape_list, reshape_list, flatten_list

from block import block_vec, block_mat
from ufl.form import Form
import dolfin as df
import numpy as np


def assemble(form):
    '''Assemble multidimensional form'''
    # In the base case we want to fall trough the custom assemblers
    # for trace/average/restriction problems until something that 
    # dolfin can handle (hopefully)
    modules = (xii.assembler.trace_assembly,        # Codimension 1
               xii.assembler.average_assembly,      # Codimension 2
               xii.assembler.restriction_assembly)  # Codimension 0
    
    if isinstance(form, Form):
        arity = form_arity(form)
        # Try with our reduced assemblers
        for module in modules:
            tensor = module.assemble_form(form, arity)
            if tensor is not None:
                return tensor
        # Fallback
        return df.assemble(form)

    # We might get number
    if is_number(form): return form

    shape = shape_list(form)
    # Recurse
    blocks = reshape_list(map(assemble, flatten_list(form)), shape)
    
    return (block_vec if len(shape) == 1 else block_mat)(blocks)
