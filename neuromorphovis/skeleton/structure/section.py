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


####################################################################################################
# Section
####################################################################################################
class Section:
    """ A morphological section represents a series of morphological samples. """

    ################################################################################################
    # @__init__
    ################################################################################################
    def __init__(self,
                 id,
                 parent_id,
                 children_ids,
                 samples,
                 type):
        """Constructor

        :param id:
            Section index.
        :param parent_id:
            The index of the parent section.
        :param children_ids:
            A list of the indexes of the children sections.
        :param samples:
            A list of samples that compose this section.
        :param type:
            Section type, can be AXON, DENDRITE, APICAL_DENDRITE, or NONE.
        """

        # Section index
        self.id = id

        # The index of the parent section
        self.parent_id = parent_id

        # A list of the indexes of the children sections
        self.children_ids = children_ids

        # Segments samples (points along the section)
        self.samples = samples

        # Add a reference to the section as a member variable of the sample, for accessibility !
        for sample in self.samples:
            sample.section = self

        # Section type: AXON (2), DENDRITE (3), APICAL_DENDRITE (4), or NONE
        self.type = type

        # A reference to the section parent, if it exists
        self.parent = None

        # A list of the children
        self.children = []

        # Is the 'root' section of any branch connected to the soma or not ?!
        # NOTE: By default for all the sections, this options is set to False, however,
        # for the root sections, the branch is checked if it is connected to the soma or not. If
        # True, then we keep a reference to the face that will be used to extrude or connect that
        # branch to the soma.
        self.connected_to_soma = False

        # A reference to the reconstructed mesh that represents the section.
        # NOTE: This reference will be used to link the mesh to the soma if the arbor is connected
        # to the soma relying on the value of the connected_to_soma variable.
        self.mesh = None

        # The index of the face that is supposed to connect the soma with the root section of a
        # branch.
        # NOTE: This variable is only set to the root sections.
        self.soma_face_index = None

        self.soma_face_centroid = None

        # This parameters defines whether this section is a continuation for a parent section or
        # not. By default it is set to False, however, during the morphology pre-processing, it must
        # be updated if the section is determined to be a continuous one.
        self.is_primary = False

        # The branching order of this section
        self.branching_order = 0

    ################################################################################################
    # @get_type_string
    ################################################################################################
    def get_type_string(self):
        """Return a string that reflects the type of the arbor, AXON, APICAL or BASAL.

        :return:
            String that reflects the type of the arbor, AXON, APICAL or BASAL
        """

        if str(self.type) == '2':
            return 'AXON'
        elif str(self.type) == '3':
            return 'BASAL_DENDRITE'
        elif str(self.type) == '4':
            return 'APICAL_DENDRITE'
        else:
            return 'UNKNOWN_BRANCH_TYPE'

    ################################################################################################
    # @is_axon
    ################################################################################################
    def is_axon(self):
        """Check if this section belongs to the axon or not.

        :return:
            True if the section belongs to the axon.
        """
        if str(self.type) == '2':
            return True
        return False

    ################################################################################################
    # @is_basal_dendrite
    ################################################################################################
    def is_basal_dendrite(self):
        """Check if this section belongs to a basal dendrite or not.

        :return:
            True if the section belongs to a basal dendrite.
        """
        if str(self.type) == '3':
            return True
        return False

    ################################################################################################
    # @is_basal_dendrite
    ################################################################################################
    def is_apical_dendrite(self):
        """Check if this section belongs to an apical dendrite or not.

        :return:
            True if the section belongs to an apical dendrite.
        """
        if str(self.type) == '4':
            return True
        return False

    ################################################################################################
    # @is_root
    ################################################################################################
    def is_root(self):
        """Check if the section is root or not.

        :return:
            True if the section is root, and False otherwise.
        """
        if self.parent is None:
            return True
        return False

    ################################################################################################
    # @has_children
    ################################################################################################
    def has_children(self):
        """Check if the section has children sections or not.

        :return:
            True or False.
        """

        if len(self.children_ids) > 0 or len(self.children) > 0:
            return True

        return False

    ################################################################################################
    # @has_parent
    ################################################################################################
    def has_parent(self):
        """Check if the section has a parent section or not.

        :return:
            True of False.
        """

        if self.parent_id is None or self.parent is None:
            return False

        return True

    ################################################################################################
    # @reorder_samples
    ################################################################################################
    def reorder_samples(self):
        """After the insertion of new samples into the section, their order is changed. Therefore,
        we must re-order them to be able to link them with their logical order.
        """

        # Update the indexes of the samples based on their order along the section
        for i, section_sample in enumerate(self.samples):

            # Set the sample index according to its order along the section in the samples list
            section_sample.id = i
