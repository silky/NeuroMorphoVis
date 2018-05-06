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
# @Meshing
####################################################################################################
class Meshing:
    """Meshing enumerators
    """

    ############################################################################################
    # @__init__
    ############################################################################################
    def __init__(self):
        pass

    ################################################################################################
    # @Technique
    ################################################################################################
    class Technique:
        """Meshing techniques
        """

        # Piecewise watertight meshing
        PIECEWISE_WATERTIGHT = 'MESHING_TECHNIQUE_PIECEWISE_WATERTIGHT'

        # Bridging meshing
        BRIDGING = 'MESHING_TECHNIQUE_BRIDGING'

        # Union meshing
        UNION = 'MESHING_TECHNIQUE_UNION'

        ############################################################################################
        # @__init__
        ############################################################################################
        def __init__(self):
            pass

        ############################################################################################
        # @get_enum
        ############################################################################################
        @staticmethod
        def get_enum(argument):

            # Piecewise-watertight
            if argument == 'piecewise-watertight':
                return Meshing.Technique.PIECEWISE_WATERTIGHT

            # Union
            elif argument == 'union':
                return Meshing.Technique.UNION

            # Bridging
            elif argument == 'bridging':
                return Meshing.Technique.BRIDGING

            # By default use piecewise-watertight
            else:
                return Meshing.Technique.PIECEWISE_WATERTIGHT

    ################################################################################################
    # @Technique
    ################################################################################################
    class SomaConnection:
        """Soma connection to the arbors
        """

        # Connected
        CONNECTED = 'SOMA_CONNECTED_TO_ARBORS'

        # Disconnected
        DISCONNECTED = 'SOMA_DISCONNECTED_FROM_ARBORS'

        ############################################################################################
        # @__init__
        ############################################################################################
        def __init__(self):
            pass

        ############################################################################################
        # @get_enum
        ############################################################################################
        @staticmethod
        def get_enum(argument):

            # Soma is connected to the arbors
            if argument == 'connected':
                return Meshing.SomaConnection.CONNECTED

            # Soma is disconnected from the arbors
            elif argument == 'disconnected':
                return Meshing.SomaConnection.DISCONNECTED

            # By default use the soma disconnected mode
            else:
                return Meshing.SomaConnection.DISCONNECTED

    ################################################################################################
    # @ArborsConnection
    ################################################################################################
    class ObjectsConnection:
        """Objects connected to each others via joint operation
        """

        # Connected
        CONNECTED = 'CONNECTED_OBJECTS'

        # Disconnected
        DISCONNECTED = 'DISCONNECTED_OBJECTS'

        ############################################################################################
        # @__init__
        ############################################################################################
        def __init__(self):
            pass

        ############################################################################################
        # @get_enum
        ############################################################################################
        @staticmethod
        def get_enum(argument):

            # All the objects are connected to a single mesh object
            if argument == 'connected':
                return Meshing.ObjectsConnection.CONNECTED

            # The objects are disconnected from each others
            elif argument == 'disconnected':
                return Meshing.ObjectsConnection.DISCONNECTED

            # By default use the mesh objects are disconnected
            else:
                return Meshing.ObjectsConnection.DISCONNECTED

    ################################################################################################
    # @Edges
    ################################################################################################
    class Edges:
        """Arbors edges
        """

        # Smooth edges
        SMOOTH = 'ARBORS_SMOOTH_EDGES'

        # Hard edges
        HARD = 'ARBORS_HARD_EDGES'

        ############################################################################################
        # @__init__
        ############################################################################################
        def __init__(self):
            pass

        ############################################################################################
        # @get_enum
        ############################################################################################
        @staticmethod
        def get_enum(argument):

            # Use smooth edges
            if argument == 'smooth':
                return Meshing.Edges.SMOOTH

            # Use hard edges
            elif argument == 'hard':
                return Meshing.Edges.HARD

            # By default use hard edges
            else:
                return Meshing.Edges.HARD

    ################################################################################################
    # @Branching
    ################################################################################################
    class Branching:
        """Branching method
        """

        # Make the branching based on the angles between the branches
        ANGLES = 'ANGLE_BASED_BRANCHING'

        # Make the branching based in the radii between the branches
        RADII = 'RADII_BASED_BRANCHING'

        ############################################################################################
        # @__init__
        ############################################################################################
        def __init__(self):
            pass

        ############################################################################################
        # @get_enum
        ############################################################################################
        @staticmethod
        def get_enum(argument):

            # Angle
            if argument == 'angles':
                return Meshing.Branching.ANGLES

            # Radii
            elif argument == 'radii':
                return Meshing.Branching.RADII

            # By default return angles
            else:
                return Meshing.Branching.ANGLES

    ################################################################################################
    # @Model
    ################################################################################################
    class Surface:
        """Reconstructed model quality, is it realistic quality or beauty
        """

        # Smooth surface
        SMOOTH = 'SURFACE_ROUGH'

        # Add noise to the surface to make it rough
        ROUGH = 'SURFACE_SMOOTH'

        ############################################################################################
        # @__init__
        ############################################################################################
        def __init__(self):
            pass

        ############################################################################################
        # @get_enum
        ############################################################################################
        @staticmethod
        def get_enum(argument):

            # Rough surface
            if argument == 'rough':
                return Meshing.Surface.ROUGH

            # Smooth surface
            elif argument == 'smooth':
                return Meshing.Surface.SMOOTH

            # By default construct a smooth surface
            else:
                return Meshing.Surface.SMOOTH

    ################################################################################################
    # @Rendering
    ################################################################################################
    class Rendering:
        """Rendering options
        """

        ############################################################################################
        # @__init__
        ############################################################################################
        def __init__(self):
            pass

        ########################################################################################
        # @View
        ########################################################################################
        class View:
            """Rendering view options
            """

            # Close up view
            CLOSE_UP_VIEW = 'RENDERING_MESH_CLOSE_UP_VIEW'

            # Full morphology view
            MID_SHOT_VIEW = 'RENDERING_MESH_MID_SHORT_VIEW'

            # Full morphology view
            WIDE_SHOT_VIEW = 'RENDERING_MESH_WIDE_SHOT_VIEW'

            ####################################################################################
            # @__init__
            ####################################################################################
            def __init__(self):
                pass

            ####################################################################################
            # @get_enum
            ####################################################################################
            @staticmethod
            def get_enum(argument):

                # Close up view
                if argument == 'close-up':
                    return Meshing.Rendering.View.CLOSE_UP_VIEW

                # Mid-shot view
                elif argument == 'mid-shot':
                    return Meshing.Rendering.View.MID_SHOT_VIEW

                # Wide-shot view
                elif argument == 'wide-shot':
                    return Meshing.Rendering.View.WIDE_SHOT_VIEW

                # By default use the mid-shot view
                else:
                    return Meshing.Rendering.View.MID_SHOT_VIEW

        ########################################################################################
        # @Resolution
        ########################################################################################
        class Resolution:
            """Rendering resolution options
            """

            # Rendering to scale (for figures)
            TO_SCALE = 'RENDER_MESH_TO_SCALE'

            # Rendering based on a user defined resolution
            FIXED_RESOLUTION = 'RENDER_MESH_FIXED_RESOLUTION'

            ########################################################################################
            # @__init__
            ########################################################################################
            def __init__(self):
                pass

            ########################################################################################
            # @get_enum
            ########################################################################################
            @staticmethod
            def get_enum(argument):

                # To scale
                if argument == 'to-scale':
                    return Meshing.Rendering.Resolution.TO_SCALE

                # Fixed resolution
                elif argument == 'fixed':
                    return Meshing.Rendering.Resolution.FIXED_RESOLUTION

                # By default render at the specified resolution
                else:
                    return Meshing.Rendering.Resolution.FIXED_RESOLUTION

    ################################################################################################
    # @UnionMeshing
    ################################################################################################
    class UnionMeshing:
        """Union meshing technique options
        """

        # Quad skeleton
        QUAD_SKELETON = 'UNION_QUAD_SKELETON'

        # Circular skeleton
        CIRCULAR_SKELETON = 'UNION_CIRCULAR_SKELETON'

        ############################################################################################
        # @__init__
        ############################################################################################
        def __init__(self):
            pass

