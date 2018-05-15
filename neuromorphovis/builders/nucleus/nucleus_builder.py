####################################################################################################
# Copyright (c) 2016 - 2018, EPFL / Blue Brain Project
#               Marwan Abdellah <marwan.abdellah@epfl.ch>
#
# This file is part of NeuroMorphoVis <https://github.com/BlueBrain/NeuroMorphoVis>
#
# This library is free software; you can redistribute it and/or modify it under the terms of the
# GNU Lesser General Public License version 3.0 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with this library;
# if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA.
####################################################################################################

__author__      = "Marwan Abdellah"
__copyright__   = "Copyright (c) 2016 - 2018, Blue Brain Project / EPFL"
__credits__     = ["Ahmet Bilgili", "Juan Hernando", "Stefan Eilemann"]
__version__     = "1.0.0"
__maintainer__  = "Marwan Abdellah"
__email__       = "marwan.abdellah@epfl.ch"
__status__      = "Production"

# System imports
import random

# Blender imports
from mathutils import Vector

import neuromorphovis as nmv
import neuromorphovis.consts
import neuromorphovis.shading
import neuromorphovis.scene
import neuromorphovis.utilities


####################################################################################################
# @RandomSpineBuilder
####################################################################################################
class NucleusBuilder:
    """Building and integrating nuclei inside the soma.
    """

    ################################################################################################
    # @__init__
    ################################################################################################
    def __init__(self,
                 morphology,
                 options):
        """Constructor

        :param morphology:
            A given morphology skeleton to create the mesh for.
        :param options:
            Loaded options from NeuroMorphoVis.
        """

        # Morphology
        self.morphology = morphology

        # Loaded options from NeuroMorphoVis
        self.options = options

        # A list of all the loaded nuclei
        self.nuclei_meshes = None

    ################################################################################################
    # @load_nuclei_meshes
    ################################################################################################
    def load_nuclei_meshes(self):
        """Loads all the nuclei meshes from the nuclei directory
        """

        # Load all the template spines and ignore the verbose messages of loading
        nmv.utilities.disable_std_output()
        self.nuclei_meshes = nmv.file.load_nuclei(nmv.consts.Paths.NUCLEI_MESHES_LQ_DIRECTORY)
        nmv.utilities.enable_std_output()

        # Create the material
        material = nmv.shading.create_material(
            name='%nuclei_material', color=self.options.mesh.nucleus_color,
            material_type=self.options.mesh.material)

        # Apply the shader
        for nucleus_object in self.nuclei_meshes:

            # Apply the shader to each spine mesh
            nmv.shading.set_material_to_object(nucleus_object, material)

    ################################################################################################
    # @add_nucleus_inside_soma
    ################################################################################################
    def add_nucleus_inside_soma(self):
        """Add a nucleus object randomly inside the soma of the morphology.

        :return:
            A reference to the added nucleus.
        """

        # Load all the template nuclei and ignore the verbose messages of loading
        self.load_nuclei_meshes()

        # Add the nucleus by selecting a random one from the loaded list
        nmv.logger.info('Integrating nucleus')

        # Select a random nucleus from the nuclei list
        nucleus_template = random.choice(self.nuclei_meshes)

        # Get a copy of the template and update it
        nucleus_object = nmv.scene.ops.duplicate_object(nucleus_template, id)

        # Rename the nucleus
        nucleus_object.name = '%s_nucleus' % self.options.morphology.label

        # Scale the nucleus
        nucleus_scale = random.uniform(0.5, 0.75) * self.morphology.soma.mean_radius
        nmv.scene.ops.scale_object_uniformly(nucleus_object, nucleus_scale)

        # Translate the spine to soma place in the soma
        nucleus_position = self.morphology.soma.centroid + Vector((random.uniform(-1.0, 1.0),
                                                                   random.uniform(-1.0, 1.0),
                                                                   random.uniform(-1.0, 1.0)))
        nmv.scene.ops.set_object_location(nucleus_object, nucleus_position)

        # Delete the template spines
        nmv.scene.ops.delete_list_objects(self.nuclei_meshes)

        # Return the spines objects list
        return nucleus_object
