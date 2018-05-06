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
import os, copy, math

# Internal import
import neuromorphovis as nmv
import neuromorphovis.consts
import neuromorphovis.geometry
import neuromorphovis.skeleton


####################################################################################################
# @resample_section
####################################################################################################
def resample_sections(section,
                      resampling_distance=2.5):
    """
    Resample a given section at a certain resampling distance.
    NOTE: Use a default value of 2.5 microns to resample the section.

    :param section:
        A given section to resample.
    :param resampling_distance:
        The distance, where a new sample will be added to the section.
    """

    # If the section has no samples, report this as an error and ignore this filter
    if len(section.samples) == 0:

        # Report the error
        nmv.logger.log('\t\t* ERROR: Section [%s: %d] has NO samples, cannot be re-sampled' %
              (section.get_type_string(), section.id))

        return

    # If the section has ONLY one sample, report this as an error and ignore this filter
    elif len(section.samples) == 1:

        # Report the error
        nmv.logger.log('\t\t* ERROR: Section [%s: %d] has only ONE sample, cannot be re-sampled' %
              (section.get_type_string(), section.id))

        return

    # If the section has ONLY two sample, report this as a warning
    elif len(section.samples) == 2:

        # Compute section length
        section_length = (section.samples[1].point - section.samples[0].point).length

        # Compute the combined diameters of the samples
        diameters = (section.samples[1].radius + section.samples[0].radius) * 2

        # Report the warning
        nmv.logger.log('\t\t* WARNING: Section [%s: %d] has only TWO samples: length [%f], diameters [%f]' %
              (section.get_type_string(), section.id, section_length, diameters))

        if section_length < diameters:
            nmv.logger.log('\t\t\t* BAD SECTION')

    # An index that will be used to keep track on the samples list
    i = 0
    while True:

        # Break at the last sample
        if i == len(section.samples) - 1:
            break

        # Compute the distance between the two samples
        distance = (section.samples[i + 1].point - section.samples[i].point).length

        # If the distance is greater than the DOUBLE of the resampling distance, then add the new
        # samples at the exact distance
        if distance > resampling_distance * 2:

            # Compute the direction
            direction = (section.samples[i + 1].point - section.samples[i].point).normalized()

            # Compute the auxiliary sample point, use epsilon for floating point comparison
            sample_point = \
                section.samples[i].point + (direction * resampling_distance * nmv.consts.Math.EPSILON)

            # Compute the auxiliary sample radius based on the previous and next samples
            sample_radius = (section.samples[i + 1].radius + section.samples[i].radius) * 0.5

            # Add the auxiliary sample, the id of the sample is set to -1 (auxiliary sample)
            auxiliary_sample = nmv.skeleton.Sample(
                point=sample_point, radius=sample_radius, id=-1, section=section)

            # Update the samples list
            section.samples.insert(i + 1, auxiliary_sample)

            # Reset the index to start from the beginning
            i = 0

        # If the distance is greater than the resampling distance, then add a new sample midway
        elif distance > resampling_distance and (distance < resampling_distance * 2):

            # Compute the direction
            direction = (section.samples[i + 1].point - section.samples[i].point).normalized()

            # Compute the auxiliary sample point at the middle between the two samples
            sample_point = section.samples[i].point + (direction * distance * 0.5)

            # Compute the auxiliary sample radius
            sample_radius = (section.samples[i + 1].radius + section.samples[i].radius) * 0.5

            # Add the auxiliary sample, the id of the sample is set to -1
            auxiliary_sample = nmv.skeleton.Sample(point=sample_point,
                radius=sample_radius, id=-1, section=section)

            # Update the samples list
            section.samples.insert(i + 1, auxiliary_sample)

            # Reset the index to start from the beginning
            i = 0

        else:

            # Increment the counter to proceed along the section
            i += 1

    # After resampling the section, update the logical indexes of the samples
    section.reorder_samples()


####################################################################################################
# @add_sample_at_section_center
####################################################################################################
def add_sample_at_section_center(section):
    """
    Adds an additional or auxiliary sample at the center of the section between the first and
    last samples to avoid any under-sampling artifacts.
    NOTE: This function is ONLY applied on sections that have two samples.

    :param section:
        A given section with two samples only.
    """

    # Verify that the section has only two samples
    if len(section.samples) == 2:

        # Compute the auxiliary sample position
        sample_position = (section.samples[0].point + section.samples[1].point) / 2.0

        # Compute the auxiliary sample radius
        sample_radius = (section.samples[0].radius + section.samples[1].radius) / 2.0

        # Build the extra samples, and use -1 for the ID to indicate that it is an auxiliary sample
        auxiliary_sample = nmv.skeleton.Sample(
            point=sample_position, radius=sample_radius, id=-1, morphology_id=-1, section=section)

        # Add the auxiliary sample to the section
        section.samples.insert(1, auxiliary_sample)

        # Reorder the samples and their IDs along the section
        section.reorder_samples()


####################################################################################################
# @remove_duplicate_samples
####################################################################################################
def remove_duplicate_samples(section,
                             threshold=1.0):
    """
    Remove duplicate samples along a given section.
    If the distance between the samples is less than the threshold, then remove the second sample.

    :param section:
        A given section to remove its duplicates.
    :param threshold:
        A threshold distance, by default 1.0 micron.
    """

    # Iterate over all the samples along the section
    for i, sample in enumerate(list(section.samples)):

        # Ensure that we don't exceed the section length
        if i == len(section.samples) - 2:
            break

        # Compute the distance between the two samples
        distance = (section.samples[i + 1].point - section.samples[i].point).length

        # If the distance is lower than the threshold
        if distance < threshold:

            # Then remove the duplicate sample
            section.samples.remove(section.samples[i + 1])

            # Repeat the process
            remove_duplicate_samples(section=section, threshold=threshold)

            # Due to the recursive call of the function, there are no more samples to process,
            break


####################################################################################################
# @remove_duplicate_samples
####################################################################################################
def remove_samples_inside_soma(section):
    """
    Remove the samples located inside the soma that result in intersecting the initial section of
    the branch with the soma. This function is ONLY applied to a root section that is connected
    directly to the soma. It compute the distance between the first sample and the origin
    and then, computes the distance between the rest of the samples and the origin. If the
    distance between the origin and any of the samples is SMALLER than that of the first sample,
    then remove the sample from the section.

    NOTE: Make sure that the section has at least two samples to avoid the meshing artifacts.
    NOTE: If the section has initially two samples and has internal sample, then flip the samples.

    :param section:
        A given section to remove its internal samples that are located inside the soma.
    """

    # If the section is not a root one, then ignore this filter and return
    if section.has_parent():

        # Not a root section, as it has a parent, then RETURN
        return

    # If the section has no samples, report this as an error and ignore this filter
    if len(section.samples) == 0:

        # Report the error
        nmv.logger.log('\t\t* ERROR: Section [%s: %d] has NO samples' %
              (section.get_type_string(), section.id))

        # Return
        return

    # If the section has ONLY one sample, report this as an error and ignore this filter
    elif len(section.samples) == 1:

        # Report the error
        nmv.logger.log('\t\t* ERROR: Section [%s: %d] has only ONE sample' %
              (section.get_type_string(), section.id))

        # Return
        return

    # Handle the case when the section has only two samples
    elif len(section.samples) == 2:

        # Make a copy of both samples along the section
        sample_0 = copy.copy(section.samples[0])
        sample_1 = copy.copy(section.samples[1])

        # Compare the distances between the two samples and the origin
        if sample_1.point.length < sample_0.point.length:

            # Report the repair
            nmv.logger.log('\t\t* REPAIRING: Removing internal sample, section [%s: %d]' %
                  (section.get_type_string(), section.id))

            # Flip the samples
            section.samples[0] = sample_1
            section.samples[1] = sample_0

    # The section has more than TWO samples
    else:

        # Compute the minimal distance at which the samples with smaller distances will be filtered
        minimal_distance = section.samples[0].point.length

        # Iterate over the next samples
        for i, sample in enumerate(list(section.samples)):

            # Ignore the first sample
            if i == 0:
                continue

            # Compare the distance between the sample and the origin to the minimal distance
            if sample.point.length < minimal_distance:

                # Remove the sample
                section.samples.remove(sample)

                # Report the repair
                nmv.logger.log('\t\t* REPAIRING: Removing internal sample, section [%s: %d]' %
                      (section.get_type_string(), section.id))

                # After removing this sample, the section might have two samples only, so we
                # recursively call this function and break afterwards.
                remove_samples_inside_soma(section=section)

                # Break
                break


####################################################################################################
# @remove_samples_within_extent
####################################################################################################
def remove_samples_within_extent(section,
                                 extent_center,
                                 extent_radius,
                                 ignore_first_sample=False):
    """
    Remove the samples located within a given extent (or sphere) from a section beginning.
    This function verifies whether the samples along the given sphere are located within its extent
    or not. If yes, the samples are removed, otherwise nothing happens.
    NOTE: The function returns the number of samples removed from the section, for verification.

    :param section:
        A sections to remove the samples from.
    :param extent_center:
        The center of the sphere extent.
    :param extent_radius:
        The radius of the sphere extent.
    :param ignore_first_sample:
        If this flag is set, the first sample is not removed.
    :return
        The number of samples removed during the application of this filter.
    """

    # If the section has LESS THAN two samples, the section cannot be handled.
    if len(section.samples) < 2:

        # Report the error
        nmv.logger.log('\t\t* ERROR: Section [%s: %d] has less than THREE samples, cannot be re-sampled' %
              (section.get_type_string(), section.id))

        # Return
        return 0

    # If the section has ONLY two samples, the section cannot be handled.
    if len(section.samples) == 2:

        # Report the error
        nmv.logger.log('\t\t* WARNING: Section [%s: %d] has only TWO samples, cannot be re-sampled' %
              (section.get_type_string(), section.id))

        # Return
        return 0

    # Count the number of removed samples from the section
    number_of_removed_samples = 0

    # Do it sample by sample (keep a COPY of the samples list via {list(section.samples)})
    for i, sample in enumerate(list(section.samples)):

        # Keep the first sample if requested
        if i == 0:

            # The @ignore_first_sample flag must be set to True
            if ignore_first_sample:

                # Skip the first sample
                continue

        # Check if the sample is located within the extent of the given sphere
        if nmv.geometry.ops.is_point_inside_sphere(extent_center, extent_radius, sample.point):

            # Remove the sample from the section
            section.samples.remove(sample)

            # Increment the counter of the removed samples
            number_of_removed_samples += 1

    # Return the number of removed samples
    return number_of_removed_samples



####################################################################################################
# @resample_section_front
####################################################################################################
def resample_section_front(section):
    """
    Re-samples the front side of a section.

    :param section:
        A section to be resampled at its front end.
    """

    # TODO: Report the resampling operation to identify any issues till further notice
    nmv.logger.log('\t\t* RESAMPLING: Section [%s] front' % (str(section.id)))

    # The re-sampling distance of the primary section is computed based on the section radius
    resampling_distance = section.samples[0].radius * math.sqrt(2)

    # To resample the front side of a primary section, we MUST remove all the samples located
    # within the range of the computed resampling distance. The center of this extent is the
    # considered the position of the first sample of the given section and the extent radius is
    # considered the re-sampling distance
    number_removed_sampled = remove_samples_within_extent(
        section=section, extent_center= section.samples[0].point,
        extent_radius=resampling_distance, ignore_first_sample=True)

    # Report the number of removed samples
    if number_removed_sampled > 0:
        nmv.logger.log('\t\t\t* Removing [%d] samples on the front side' % number_removed_sampled)

    # Compute the section direction after the re-sampling operation to add an auxiliary sample
    # after the first sample
    section_direction = (section.samples[1].point - section.samples[0].point).normalized()

    # Auxiliary sample position
    sample_position = section.samples[0].point + (section_direction * resampling_distance)

    # The auxiliary sample radius is the same as that of the first sample
    sample_radius = section.samples[1].radius

    # Build the extra samples, and use -1 for the ID to indicate that it is an auxiliary sample
    auxiliary_sample = nmv.skeleton.Sample(
        point=sample_position, radius=sample_radius, id=-1, section=section)

    # Insert the auxiliary sample just after the first sample
    section.samples.insert(1, auxiliary_sample)

    # Reorder the samples and their IDs along the section
    section.reorder_samples()


####################################################################################################
# @resample_section_rear
####################################################################################################
def resample_section_rear(section):
    """
    Re-samples the rear side of a section.

    :param section:
        A section to be resampled at its rear end.
    """

    # To make it easy to resample section from the rear end, reverse the samples, resample the
    # section and then reverse them back again
    # Reverse the sample list
    section.samples = list(reversed(section.samples))

    # TODO: Report the resampling operation to identify any issues till further notice
    nmv.logger.log('\t\t* RESAMPLING: Primary section [%s]' % (str(section.id)))

    # The re-sampling distance of the primary section is computed based on the section radius
    resampling_distance = section.samples[0].radius * math.sqrt(2)

    # To resample the front side of a primary section, we MUST remove all the samples located
    # within the range of the computed resampling distance. The center of this extent is the
    # considered the position of the first sample of the given section and the extent radius is
    # considered the re-sampling distance
    number_removed_sampled = remove_samples_within_extent(
        section=section, extent_center= section.samples[0].point,
        extent_radius=resampling_distance, ignore_first_sample=True)

    # Report the number of removed samples
    if number_removed_sampled > 0:
        nmv.logger.log('\t\t* Removing [%d] samples on the rear side' % number_removed_sampled)

    # Compute the section direction after the re-sampling operation to add an auxiliary sample
    # after the first sample
    section_direction = (section.samples[1].point - section.samples[0].point).normalized()

    # Auxiliary sample position
    sample_position = section.samples[0].point + (section_direction * resampling_distance)

    # The auxiliary sample radius is the same as that of the first sample
    sample_radius = section.samples[1].radius

    # Build the extra samples, and use -1 for the ID to indicate that it is an auxiliary sample
    auxiliary_sample = nmv.skeleton.Sample(
        point=sample_position, radius=sample_radius, id=-1, section=section)

    # Insert the auxiliary sample just after the first sample
    section.samples.insert(1, auxiliary_sample)

    # Reverse the sample list back to be in the right order
    section.samples = list(reversed(section.samples))

    # Reorder the samples and their IDs along the section
    section.reorder_samples()


####################################################################################################
# @resample_section_stem
####################################################################################################
def resample_section_stem(section):
    """
    Re-samples the stem of a section. This resampling preserves the first and last two
    samples along the section to preserve the resampling of the front and rear ends of the section.
    The resampling distance is computed based on the first and last samples of the section,
    where the diameter of the first sample will be used to resample the first half of the section,
    and that of the last sample will be used to resample the second half of the section.

    :param section:
        A section to be resampled at the stem, ignoring its front and rear ends.
    """

    # Compute the section length in advance
    section_length = nmv.skeleton.ops.compute_section_length(section)

    # The resampling distance that will be used to resample the front end of the section
    front_resampling_distance = section.samples[0].radius * 2

    # The resampling distance that will be used to resample the rear end of the section
    rear_resampling_distance = section.samples[-1].radius * 2

    # Epsilon, for avoiding floating point operations
    epsilon = 1e-5

    # An index that will be used to keep track on the samples list
    i = 1
    while True:

        # Compute the current length along the section
        current_length = nmv.skeleton.ops.compute_section_length_until_sample(section, i)

        # Compute the resampling distance
        resampling_distance = front_resampling_distance if current_length < 0.5 * section_length \
            else rear_resampling_distance

        # Break at the last two sample
        if i == len(section.samples) - 2:
            break

        # Compute the distance between the two samples
        distance = (section.samples[i + 1].point - section.samples[i].point).length

        # Compute distance ratio to overcome the 'epsilon' floating point comparison
        distance_ratio = float(distance) / float(resampling_distance)

        # If the distance is greater than the resampling distance, then add the new sample at the
        #  exact distance
        if distance_ratio > 1.001:

            # Compute the direction
            direction = (section.samples[i + 1].point - section.samples[i].point).normalized()

            # Compute the auxiliary sample point, use epsilon for floating point comparison
            sample_point = \
                section.samples[i].point + (direction * (resampling_distance + epsilon))

            # Compute the auxiliary sample radius based on the previous and next samples
            sample_radius = (section.samples[i + 1].radius + section.samples[i].radius) * 0.5

            # Add the auxiliary sample, the id of the sample is set to -1 (auxiliary sample)
            auxiliary_sample = nmv.skeleton.Sample(
                point=sample_point, radius=sample_radius, id=-1, section=section)

            # Update the samples list
            section.samples.insert(i + 1, auxiliary_sample)

            # Reset the index to start from the beginning (the second sample @samples[1])
            i = 1

        # If the distance is shorter than the resampling distance then remove the sample
        elif distance_ratio < 0.999:

            section.samples.remove(section.samples[i + 1])

            # Reset the index to start from the beginning (the second sample @samples[1])
            i = 1

        else:

            i += 1

    # After resampling the section, update the logical indexes of the samples
    section.reorder_samples()


####################################################################################################
# @resample_primary_section
####################################################################################################
def resample_section_components(section):
    """
    Re-samples a section along its front and rear ends in addition to its stem.
    The primary sections will be resampled in two steps. The first step will resample the edges
    of the section using the radii of the first and last samples of the section. The second step
    will resample the intermediate samples (or the samples that are located between the first and
    last samples) into equidistant samples using the diameter of the first sample, if possible.

    :param section:
        A given primary a section to be resampled.
    """

    # Ignore resampling the axon for the moment until tested
    if section.get_type_string() == 'AXON':
        return

    # Ignore resampling VERY short sections
    if section.is_short:
        return

    # Compute section length
    section_length = nmv.skeleton.ops.compute_section_length(section)

    # Compute the minimal section length that requires resampling
    minimal_section_length = (section.samples[0].radius + section.samples[-1].radius) * 2

    # If the section length is less than the minimal section length, the try to handle this
    # situation without resampling
    if section_length < minimal_section_length:

        # Report the issue
        nmv.logger.log('\t\t* RESAMPLING: Cannot resample the section [%s]' % section.id)
        return

    # Resample the primary sections
    if section.is_primary:

        if section.has_parent():

            # Resample the front side of the section
            resample_section_front(section=section)

        if section.has_children():

            # Resample the rear side of the section
            resample_section_rear(section=section)

        # Resample the stem only when the angle between the children is less than
        if len(section.children) == 2:
            vector_1 = (section.children[0].samples[1].point -
                        section.children[0].samples[0].point).normalized()
            vector_2 = (section.children[1].samples[1].point -
                        section.children[1].samples[0].point).normalized()
            angle = vector_1.angle(vector_2)

            #if angle < 15 or angle > 165:
            #    # Resample the stem of the section
            #    resample_section_stem(section=section)

    # Resample the secondary section, only at the rear
    else:

        if section.has_parent():

            # Resample the front side of the section
            resample_section_front(section=section)

        if section.has_children():

            # Resample the rear section of the secondary section only
            resample_section_rear(section=section)

    # Remove duplicate samples
    #remove_duplicate_samples(section=section)