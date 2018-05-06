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
import sys, os, subprocess, time

# Add other modules
sys.path.append("%s/../file" % os.path.dirname(os.path.realpath(__file__)))
sys.path.append("%s/../interface" % os.path.dirname(os.path.realpath(__file__)))
sys.path.append("%s/../shared" % os.path.dirname(os.path.realpath(__file__)))

# Internal modules
import arguments_parser
import file_ops
import slurm_configuration

import neuromorphovis.consts


####################################################################################################
# @squeue
####################################################################################################
def squeue():
    """
    Returns a list of all the current jobs on the cluster.

    :return: A list of all the current jobs on the cluster.
    """

    # Get the current processes running on the cluster
    #value = subprocess.Popen('squeue', stdout=subprocess.PIPE, shell=True)
    #(output, err) = value.communicate()
    #output = value.communicate()[0]
    #print(output)

    result = subprocess.check_output(['squeue'])
    result = str(result)
    return result.split("\\n")


####################################################################################################
# @get_current_number_jobs_for_user
####################################################################################################
def get_current_number_jobs_for_user(user_name):
    """
    Get the current number of jobs running on the cluster for a specific user identified by his
    user name.

    :param user_name: The user name of the user.
    :return: The current number of jobs running on the cluster for a specific user identified by his
    user name.
    """

    number_jobs = 0
    jobs = squeue()
    for job in jobs:
        if user_name in job:
            number_jobs += 1
    return number_jobs


####################################################################################################
# @create_batch_job_config_string
####################################################################################################
def create_batch_job_config_string(slurm_config):
    """
    Creates a string header for the batch job.

    :param slurm_config : SLURM configuration parameters.
    :rtype Batch configuration string.
    """

    # This is for compactness !
    sl = "\n"  # single new line
    dl = "\n\n"  # double new line

    # Magic number
    b = "#!/bin/bash%s" % sl

    """ Auto-generated header """
    b += "######################################################%s" % sl
    b += "# WARNING - AUTO GENERATED FILE%s" % sl
    b += "# Please don't modify that file manually%s" % sl
    b += "######################################################%s" % sl

    """ Node configuration """
    # Job name
    b += "#SBATCH --job-name=\"%s%s\"%s" % (slurm_config.job_name, str(slurm_config.job_number), sl)

    # Number of nodes required to execute the job
    b += "#SBATCH --nodes=%s%s" % (slurm_config.num_nodes, sl)

    # Number of cpus per tasks
    b += "#SBATCH --cpus-per-task=%s%s" % (slurm_config.num_cpus_per_task, sl)

    # Number of tasks
    b += "#SBATCH --ntasks=%s%s" % (slurm_config.num_tasks_per_node, sl)

    # Memory required per task in MBytes
    b += "#SBATCH --mem=%s%s" % (slurm_config.memory_mb, sl)

    # slurm session time
    b += "#SBATCH --time=%s%s" % (slurm_config.session_time, sl)

    # Job partition
    b += "#SBATCH --partition=%s%s" % (slurm_config.partition, sl)

    # Job account
    b += "#SBATCH --account=%s%s" % ("proj3", sl)

    """ Logs """
    std_out = "%s/slurm-stdout_%s.log" % (slurm_config.logs_directory, str(slurm_config.job_number))
    std_err = "%s/slurm-stderr_%s.log" % (slurm_config.logs_directory, str(slurm_config.job_number))
    b += "#SBATCH --output=%s%s" % (std_out, sl)
    b += "#SBATCH --error=%s%s" % (std_err, dl)

    # Load the modules
    b += '# Loading modules %s' % sl
    for module in slurm_config.modules:
        b+= 'module load %s \n' % module

    """ System variables """
    #  slurm profile
    b += "%s%s%s" % (sl, slurm_config.profile, dl)

    # Job home
    b += "#JOB_HOME=\"%s\"%s" % (slurm_config.execution_directory, sl)

    # Kerberos renewal
    b += "# Renewal of KERBEROS periodically for the length of the job%s" % sl
    b += "krenew -b -K 30%s" % dl

    # Node list
    b += "echo \"On which node your job has been scheduled :\"%s" % sl
    b += "echo $SLURM_JOB_NODELIST%s" % dl

    # Shell limits
    b += "echo \"Print current shell limits :\"%s" % sl
    b += "ulimit -a%s" % dl

    # Running the serial tasks.
    b += "echo \"Running ...\"%s" % sl
    b += "cd %s%s" % (slurm_config.execution_directory, dl)
    ####################################################################

    return b


####################################################################################################
# @create_batch_job_script_for_gid
####################################################################################################
def create_batch_job_script_for_gid(arguments,
                                    gid):
    """
    Creates a batch job file for a neuron with specific GID.

    :param arguments: Command line arguments.
    :param gid: Neuron GID.
    """

    # Create slurm configuration
    slurm_config = slurm_configuration.SlurmConfiguration()

    # Update slurm configuration data
    # Job number should match the gid
    slurm_config.job_number = int(gid)

    # Execution directory, same as output directory
    slurm_config.execution_directory = '%s' % arguments.output_directory

    # Log directory
    slurm_config.logs_directory = '%s/%s' % \
                                  (arguments.output_directory, nmv.consts.Paths.SLURM_LOGS_FOLDER)

    # Generate the batch job configuration string
    batch_job_config_string = create_batch_job_config_string(slurm_config)

    # Setup the shell command
    shell_command = arguments_parser.create_executable_for_single_gid(arguments, gid)

    # Add the command to the batch job config string
    batch_job_config_string += shell_command

    # Write the batch job script to file in the slurm jobs directory
    slurm_jobs_directory = '%s/%s' % (arguments.output_directory, nmv.consts.Paths.SLURM_JOBS_FOLDER)
    file_ops.write_batch_job_string_to_file(slurm_jobs_directory, gid, batch_job_config_string)


####################################################################################################
# @create_batch_job_script_for_multiple_gids
####################################################################################################
def create_batch_job_script_for_multiple_gids(arguments,
                                              gids,
                                              script_id):
    """
    Creates a batch job file for different neurons with specific gids for the meshing.

    :param arguments: Command line arguments.
    :param gids: A list of GIDs.
    :param script_id: Script ID.
    """

    # Create slurm configuration
    slurm_config = slurm_configuration.SlurmConfiguration()

    # Update slurm configuration data
    # Job number should match the gid
    slurm_config.job_number = script_id

    # Execution directory, same as output directory
    slurm_config.execution_directory = '%s' % arguments.output_directory

    # Log directory
    slurm_config.logs_directory = '%s/%s' % \
                                  (arguments.output_directory, nmv.consts.Paths.SLURM_LOGS_FOLDER)

    # Generate the batch job configuration string
    batch_job_config_string = create_batch_job_config_string(slurm_config)

    # Add the shell command to run blender
    # Setup the shell command
    shell_command = ""
    for gid in gids:
        shell_command += arguments_parser.create_executable_for_single_gid(arguments, gid) + '\n'

    # Add the command to the batch job config string
    batch_job_config_string += shell_command

    # Write the batch job script to file in the slurm jobs directory
    slurm_jobs_directory = '%s/%s' % (arguments.output_directory, nmv.consts.Paths.SLURM_JOBS_FOLDER)
    file_ops.write_batch_job_string_to_file(slurm_jobs_directory, script_id, batch_job_config_string)


####################################################################################################
# @create_batch_job_script_for_gid
####################################################################################################
def create_batch_job_script_for_morphology_file(arguments,
                                                morphology_file):
    """
    Creates a batch job file for a morphology file.

    :param arguments: Command line arguments.
    :param morphology_file: Neuron morphology_file.
    """

    # Create slurm configuration
    slurm_config = slurm_configuration.SlurmConfiguration()

    # Update slurm configuration data
    # Job number should match the gid
    slurm_config.job_number = 0

    # Execution directory, same as output directory
    slurm_config.execution_directory = '%s' % arguments.output_directory

    # Log directory
    slurm_config.logs_directory = '%s/%s' % \
                                  (arguments.output_directory, nmv.consts.Paths.SLURM_LOGS_FOLDER)

    # Generate the batch job configuration string
    batch_job_config_string = create_batch_job_config_string(slurm_config)

    # Setup the shell command
    shell_command = arguments_parser.create_executable_for_single_morphology_file(
        arguments, morphology_file)

    # Add the command to the batch job config string
    batch_job_config_string += shell_command

    # Write the batch job script to file in the slurm jobs directory
    slurm_jobs_directory = '%s/%s' % (arguments.output_directory, nmv.consts.Paths.SLURM_JOBS_FOLDER)
    file_ops.write_batch_job_string_to_file(
        slurm_jobs_directory, morphology_file, batch_job_config_string)


####################################################################################################
# @submit_batch_jobs
####################################################################################################
def submit_batch_jobs(user_name,
                      slurm_jobs_directory):
    """
    Submits all the batch jobs found in the jobs directory.
    This function takes into account the maximum limit imposed by the cluster (500 jobs per user).

    :param user_name: The user name of the current user.
    :param slurm_jobs_directory: The directory where the batch jobs are created. .
    """

    # Get all the scripts in the slurm jobs directory to submit them
    scripts = file_ops.get_files_in_directory(slurm_jobs_directory, file_extension='.sh')

    # Use an index to keep track on the number of jobs submitted to the cluster.
    script_index = 0

    # Submit the jobs taking into account the maximum number of jobs dedicated per user
    while True:

        # Just sleep for a second
        time.sleep(1)

        # Get the number of jobs active for that user
        number_active_jobs = get_current_number_jobs_for_user(user_name=user_name)

        # If the number of jobs is greater than 500, then wait a second and try again
        if number_active_jobs >= 500:
            nmv.logger.log('Waiting for resources')
            continue

        # Otherwise, you can submit some jobs
        else:

            # Get the number of jobs that are available to submit
            number_available_jobs = 500 - number_active_jobs

            # Submit as many jobs as you can
            for i in range(number_available_jobs):

                # Make sure that we still have some jobs to submit, otherwise break
                if script_index >= len(scripts):
                    return

                # Get the script full path
                script_full_path = '%s/%s' % (slurm_jobs_directory, scripts[script_index])

                # 'chmod' the script to be able to execute it
                shell_command = 'chmod +x %s' % script_full_path

                # Execute the command
                subprocess.call(shell_command, shell=True)

                # Format the shell command
                shell_command = 'sbatch %s' % script_full_path

                # Execute the command
                nmv.logger.log('Submitting [%s]' % shell_command)
                subprocess.call(shell_command, shell=True)

                # Increment the script index
                script_index += 1


####################################################################################################
# @run_gid_jobs_on_cluster
####################################################################################################
def run_gid_jobs_on_cluster(arguments,
                            gids):
    """
    Runs the batch jobs on the cluster.

    :param arguments: Input arguments.
    :param gids: GID list for all the neurons.
    """

    for gid in gids:

        # Create the batch jobs for the all the GIDs in the target
        create_batch_job_script_for_gid(arguments=arguments, gid=gid)

    # Submit the jobs
    # TODO: Add an option for the user
    slurm_jobs_directory = '%s/%s' % (arguments.output_directory, nmv.consts.Paths.SLURM_JOBS_FOLDER)
    submit_batch_jobs(user_name='abdellah', slurm_jobs_directory=slurm_jobs_directory)


####################################################################################################
# @run_morphology_files_jobs_on_cluster
####################################################################################################
def run_morphology_files_jobs_on_cluster(arguments,
                                         morphology_files):
    """
    Runs the batch jobs on the cluster.

    :param arguments: Input arguments.
    :param morphology_files: A list of morphology files.
    """

    for morphology_file in morphology_files:

        # Create the batch jobs for the all the GIDs in the target
        create_batch_job_script_for_morphology_file(
            arguments=arguments, morphology_file=morphology_file)

    # Submit the jobs
    # TODO: Add an option for the user
    slurm_jobs_directory = '%s/%s' % (arguments.output_directory, nmv.consts.Paths.SLURM_JOBS_FOLDER)
    submit_batch_jobs(user_name='abdellah', slurm_jobs_directory=slurm_jobs_directory)

