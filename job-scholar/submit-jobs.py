#!/usr/bin/env python

"""Job Scholar highest level submission script.
"""

# ========================================================================
#
# Imports
#
# ========================================================================
import os
import yaml
import argparse
import datetime
import stat
import subprocess
import shutil


# ========================================================================
#
# Classes
#
# ========================================================================


class Job:

    def __init__(self,
                 name,
                 queue,
                 cpu_type,
                 compiler,
                 executable,
                 input_file,
                 files_to_copy,
                 nodes,
                 minutes,
                 pre_args,
                 post_args,
                 walltime,
                 ranks_per_node,
                 cores_per_node,
                 hyperthreads,
                 knl_core_specialization,
                 cpu_bind,
                 total_ranks,
                 cores_per_rank,
                 hypercores_per_thread,
                 threads_per_rank,
                 total_threads,
                 path,
                 script):

        self.name = name
        self.queue = queue
        self.cpu_type = cpu_type
        self.compiler = compiler
        self.executable = executable
        self.input_file = input_file
        self.files_to_copy = files_to_copy
        self.nodes = nodes
        self.minutes = minutes
        self.pre_args = pre_args
        self.post_args = post_args
        self.walltime = walltime
        self.ranks_per_node = ranks_per_node
        self.cores_per_node = cores_per_node
        self.hyperthreads = hyperthreads
        self.knl_core_specialization = knl_core_specialization
        self.cpu_bind = cpu_bind
        self.total_ranks = total_ranks
        self.cores_per_rank = cores_per_rank
        self.hypercores_per_thread = hypercores_per_thread
        self.threads_per_rank = threads_per_rank
        self.total_threads = total_threads
        self.path = path
        self.script = script


class JobSet:

    def __init__(self,
                 name,
                 test_run,
                 email,
                 mail_type,
                 project_allocation,
                 notes,
                 path):

        self.name = name
        self.email = email
        self.mail_type = mail_type
        self.project_allocation = project_allocation
        self.test_run = test_run
        self.notes = notes
        self.path = path


# ========================================================================
#
# Function for finding machine name
#
# ========================================================================


def find_machine_name():
    if os.getenv('NREL_CLUSTER') == 'peregrine':
        return 'peregrine'
    elif os.getenv('NERSC_HOST') == 'cori':
        return 'cori'
    else:
        print("Cannot determine host")
        exit(-1)


# ========================================================================
#
# Function for creating directory to contain this set of job results
#
# ========================================================================


def create_job_set_directory(job_set_name):
    now = datetime.datetime.now()
    path = '%s-%s' % (job_set_name, now.strftime("%Y-%m-%d-%H-%M"))
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the job set directory %s failed" % path)
    else:
        print("Successfully created the job set directory %s " % path)
    return path


# ========================================================================
#
# Function for creating directory to contain a single job's results
#
# ========================================================================


def create_job_directory(job_set_path, job_name):
    path = os.path.join(job_set_path, job_name)
    try:
        os.mkdir(path)
    except OSError:
        print("   Creation of the job directory %s failed" % path)
    else:
        print("   Directory: %s " % path)
    return path


# ========================================================================
#
# Function for checking file existence before job submission
#
# ========================================================================


def check_file_existence(job_executable, job_input_file, job_files_to_copy):
    if os.path.isfile(job_executable) is False:
        print("   Executable does not exist: %s" % job_executable)
        exit(-1)
    elif os.path.isfile(job_input_file) is False:
        print("   Input file does not exist: %s" % job_input_file)
        exit(-1)

    for myfile in job_files_to_copy:
        if os.path.isfile(myfile) is False:
            print("   Necessary file does not exist: %s" % myfile)
            exit(-1)


# ========================================================================
#
# Function for writing single job script
#
# ========================================================================


def write_job_script(machine, job, job_set):
    print("   Writing job script...")

    job.script = "#!/bin/bash -l\n\n"
    job.script += "# Notes: " + job_set.notes + "\n\n"

    if machine == 'peregrine':
        job.script += "#PBS -N " + job.name + "\n"
        job.script += ("#PBS -l nodes=" + str(job.nodes)
                       + ":ppn=" + str(job.cores_per_node)
                       + ",walltime=" + str(job.walltime) + "\n")
        job.script += "#PBS -A " + job_set.project_allocation + "\n"
        job.script += "#PBS -q " + job.queue + "\n"
        job.script += "#PBS -j oe\n"
        job.script += "#PBS -W umask=002\n"
        job.script += "#PBS -m " + job_set.mail_type + "\n"
        job.script += "#PBS -M " + job_set.email + "\n"
    elif machine == 'cori':
        job.script += "#SBATCH -J " + job.name + "\n"
        job.script += "#SBATCH -o %x.o%j\n"
        job.script += "#SBATCH -C " + job.cpu_type + "\n"
        job.script += "#SBATCH -L SCRATCH\n"
        job.script += "#SBATCH -A " + job_set.project_allocation + "\n"
        job.script += "#SBATCH -t " + str(job.walltime) + "\n"
        job.script += "#SBATCH -q " + job.queue + "\n"
        job.script += "#SBATCH -N " + str(job.nodes) + "\n"
        job.script += "#SBATCH --mail-user=" + job_set.email + "\n"
        job.script += "#SBATCH --mail-type=" + job_set.mail_type + "\n"
        if job.knl_core_specialization != '':
            job.script += ("#SBATCH -S "
                           + str(job.knl_core_specialization) + "\n")

    job.script += r"""
set -e

cmd() {
  echo "+ $@"
  eval "$@"
}

"""
    job.script += ("echo \"Running with " + str(job.ranks_per_node)
                   + " ranks per node and " + str(job.threads_per_rank)
                   + " threads per rank on " + str(job.nodes)
                   + " nodes for a total of " + str(job.total_ranks)
                   + " ranks and " + str(job.total_threads)
                   + " threads...\"\n\n")

    if machine == 'peregrine':
        job.script += "cmd \"module purge\"\n"
        job.script += (
          "cmd \"module use /nopt/nrel/ecom/ecp/base/modules/gcc-6.2.0\"\n"
        )
        job.script += "cmd \"module load gcc/6.2.0\"\n"
        job.script += "cmd \"module load python\"\n"

        if job.compiler == 'gnu':
            job.script += "cmd \"module load openmpi\"\n\n"
            job.script += ("cmd \"export OMP_NUM_THREADS="
                           + str(job.threads_per_rank) + "\"\n\n")
            job.script += ("cmd \"" + job.pre_args
                           + "mpirun -np "
                           + str(job.total_ranks)
                           + " --map-by ppr:"
                           + str(job.ranks_per_node)
                           + ":node:pe="
                           + str(job.threads_per_rank)
                           + " -bind-to core -x OMP_NUM_THREADS "
                           + str(job.executable) + " "
                           + str(os.path.basename(job.input_file)) + " "
                           + job.post_args + "\"\n")
        elif job.compiler == 'intel':
            job.script += "cmd \"module load intel-parallel-studio\"\n\n"
            job.script += "MY_TMP_DIR=/scratch/${USER}/.tmp\n"
            job.script += "NODE_LIST=${MY_TMP_DIR}/node_list.${PBS_JOBID}\n"
            job.script += "cmd \"mkdir -p ${MY_TMP_DIR}\"\n"
            job.script += "cmd \"cat ${PBS_NODEFILE} > ${NODE_LIST}\"\n"
            job.script += "#cmd \"export I_MPI_DEBUG=5\"\n"
            job.script += "cmd \"export I_MPI_FABRIC_LIST=ofa,dapl\"\n"
            job.script += "cmd \"export I_MPI_FABRICS=shm:ofa\"\n"
            job.script += "cmd \"export I_MPI_FALLBACK=0\"\n"
            job.script += "cmd \"export I_MPI_PIN=1\"\n"
            job.script += "cmd \"export I_MPI_PIN_DOMAIN=omp\"\n"
            job.script += (
              "cmd \"export KMP_AFFINITY=compact,granularity=core\"\n"
            )
            job.script += ("cmd \"export OMP_NUM_THREADS="
                           + str(job.threads_per_rank) + "\"\n\n")
            job.script += ("cmd \"" + job.pre_args
                           + "mpirun -n "
                           + str(job.total_ranks)
                           + " -genvall -f ${NODE_LIST} -ppn "
                           + str(job.ranks_per_node) + " "
                           + str(job.executable) + " "
                           + str(os.path.basename(job.input_file)) + " "
                           + job.post_args + "\"\n")

    elif machine == 'cori':
        job.script += ("cmd \"export OMP_NUM_THREADS="
                       + str(job.threads_per_rank) + "\"\n")
        job.script += "cmd \"export OMP_PLACES=threads\"\n"
        job.script += "cmd \"export OMP_PROC_BIND=spread\"\n"

        if job.cpu_type == 'knl':
            job.script += (
              "cmd \"module swap craype-haswell craype-mic-knl || true\"\n"
            )

        if job.cpu_type == 'knl' and job.nodes > 156:
            my_exe = "/tmp/pelec.ex"
            job.script += ("cmd \"sbcast -f -F2 -t 300 --compress=lz4 "
                           + str(job.executable) + " " + my_exe + "\"\n")
        else:
            my_exe = job.executable

        job.script += ("\ncmd \"" + job.pre_args
                       + "srun -n " + str(job.total_ranks)
                       + " -c " + str(job.cores_per_rank)
                       + " --cpu_bind=" + str(job.cpu_bind) + " "
                       + my_exe + " "
                       + str(os.path.basename(job.input_file))
                       + " " + job.post_args + "\"\n")

    # Write job script to file
    job.script_file = os.path.join(job.path, job.name + '.sh')
    job_script_file_handle = open(job.script_file, 'w')
    job_script_file_handle.write(job.script)
    job_script_file_handle.close()

    # Make the job script executable
    st = os.stat(job.script_file)
    os.chmod(job.script_file, st.st_mode | stat.S_IEXEC)


# ========================================================================
#
# Function for copying files to job working directory
#
# ========================================================================


def copy_files(job_files_to_copy, job_path):
    for myfile in job_files_to_copy:
        print("   Copying file %s" % myfile)
        shutil.copy(myfile, job_path)


# ========================================================================
#
# Function for submitting the job to the machine scheduler
#
# ========================================================================


def submit_job_script(machine, job, job_set):
    # Save current working directory
    mycwd = os.getcwd()
    # print("   Changing to directory " + job.path)
    os.chdir(job.path)

    if machine == 'peregrine':
        batch = 'qsub '
    elif machine == 'cori':
        batch = 'sbatch '
        # Use real test option for Slurm submission
        # if job_set.test_run == True:
        #     batch = batch + "--test-only "

    print("   Submitting job...")
    command = batch + os.path.basename(job.script_file)
    if job_set.test_run is False:
        try:
            output = subprocess.check_output(
                command, stderr=subprocess.STDOUT, shell=True
            )
            print("   " + batch + "output: " + output)
        except subprocess.CalledProcessError as err:
            print("   " + batch + "error: " + output)
            print(err.output)
    else:
        print("   TEST RUN. Real run would use the command:")
        print("     " + command)

    # Switch back to previous working directory
    os.chdir(mycwd)


# ========================================================================
#
# Function for printing some job info before submitting
#
# ========================================================================


def print_job_info(job_number, job):
    print("%s: %s" % (job_number, job.name))
    print("   Executable: %s" % job.executable)
    print("   Input file: %s" % job.input_file)
    print("   Queue: %s" % job.queue)
    print("   CPU type: %s" % job.cpu_type)
    print("   Compiler: %s" % job.compiler)
    print("   Nodes: %s" % job.nodes)
    print("   Minutes: %s" % job.minutes)
    print("   Pre args: %s" % job.pre_args)
    print("   Post args: %s" % job.post_args)


# ========================================================================
#
# Function for printing job set info before submitting
#
# ========================================================================


def print_job_set_info(job_set):
    print("Name: %s" % job_set.name)
    print("Project allocation: %s" % job_set.project_allocation)
    print("Email: %s" % job_set.email)
    print("Notes: %s" % job_set.notes)
    if job_set.test_run is True:
        print("Performing test job submission")


# ========================================================================
#
# Function for populating job parameters according to machine type
#
# ========================================================================


def calculate_job_parameters(machine, job):
    if machine == 'peregrine':
        job.walltime = job.minutes * 60
        # Peregrine Haswell CPU logic
        job.ranks_per_node = 4
        job.cores_per_node = 24
        job.hyperthreads = 2
        if job.cpu_type != 'haswell':
            print("Only use haswell cpu_type on Peregrine")
            exit(-1)
    elif machine == 'cori':
        job.walltime = job.minutes
        # Cori CPU logic
        if job.cpu_type == 'knl':
            job.ranks_per_node = 32
            job.cores_per_node = 64
            job.hyperthreads = 4
            job.knl_core_specialization = 4
        elif job.cpu_type == 'haswell':
            job.ranks_per_node = 8
            job.cores_per_node = 32
            job.hyperthreads = 2
        else:
            print("The cpu_type is not recognized on Cori")

        if job.ranks_per_node <= job.cores_per_node:
            job.cpu_bind = 'cores'
        else:
            job.cpu_bind = 'threads'

    job.total_ranks = job.nodes * job.ranks_per_node
    job.cores_per_rank = (job.hyperthreads * job.cores_per_node
                          / job.ranks_per_node)
    # Don't use hyperthreading on haswell, but use two hyperthreads on KNL
    job.hypercores_per_thread = 2
    job.threads_per_rank = job.cores_per_rank / job.hypercores_per_thread
    job.total_threads = job.threads_per_rank * job.total_ranks


# ========================================================================
#
# Function for creating single instance of a job class
#
# ========================================================================


def create_job(job_number, pele_job, pele_job_set):
    job = Job(
      pele_job_set['name'] + "-" + str(job_number),  # name
      pele_job['queue'],           # queue
      pele_job['cpu_type'],        # cpu_type
      pele_job['compiler'],        # compiler
      pele_job['executable'],      # executable
      pele_job['input_file'],      # input file
      pele_job['files_to_copy'],   # files to copy
      pele_job['nodes'],           # number of nodes
      pele_job['minutes'],         # number of job minutes
      pele_job['pre_args'],        # arguments before mpirun
      pele_job['post_args'],       # arguments after application
      0,   # walltime
      0,   # ranks_per_node
      0,   # cores_per_node
      0,   # hyperthreads
      "",  # knl_core_specialization
      "",  # cpu_bind
      0,   # total_ranks
      0,   # cores_per_rank
      0,   # hypercores_per_thread
      0,   # threads_per_rank
      0,   # total_threads
      "",  # path
      "")  # script

    if job.pre_args is None:
        job.pre_args = ''

    if job.post_args is None:
        job.post_args = ''

    # Add input file into files to copy
    job.files_to_copy.append(job.input_file)

    return job


# ========================================================================
#
# Function for creating single instance of a job_set class
#
# ========================================================================


def create_job_set(pele_job_set, job_set_path):
    job_set = JobSet(
      pele_job_set['name'],       # name
      False,                      # test_run
      pele_job_set['email'],      # email
      pele_job_set['mail_type'],  # mail_type
      pele_job_set['project_allocation'],  # project_allocation
      pele_job_set['notes'],      # notes
      job_set_path                # path
    )

    return job_set


# ========================================================================
#
# Main code to load job list and loop over jobs
#
# ========================================================================


def main():
    parser = argparse.ArgumentParser(
        description='Job Scholar: Job submission backed by best practices.'
    )
    parser.add_argument('--test', dest='test_run', action='store_true',
                        help='perform a test job submission')
    parser.add_argument('job_set_file', type=argparse.FileType('r'),
                        help='file containing list of jobs in YAML format')
    parser.set_defaults(test_run=False)
    args = parser.parse_args()

    # Find the machine name or exit if machine is unsupported
    machine = find_machine_name()
    print("Machine detected as %s" % machine)

    # Load the job list file
    master_job_set = yaml.load(args.job_set_file)
    pele_job_set = master_job_set['pele_job_set']
    pele_job_list = pele_job_set['pele_job_list']

    # Create main directory for this set of jobs
    job_set_path = create_job_set_directory(pele_job_set['name'])

    # Create the instance of the job_set class
    job_set = create_job_set(pele_job_set, job_set_path)

    # Copy yaml file used to create jobs into job set directory
    print("Copying file %s" % args.job_set_file.name)
    shutil.copy(args.job_set_file.name, job_set.path)

    if args.test_run is True:
        job_set.test_run = True

    # Print out the information on this job set before submitting
    print_job_set_info(job_set)

    # Main loop over jobs in list
    print("Submitting jobs...")
    job_counter = 1
    for pele_job in pele_job_list:
        # Create the instance of the job class
        job = create_job(job_counter, pele_job, pele_job_set)
        # Calculate some job parameters based on machine
        calculate_job_parameters(machine, job)
        # Print out the information on this job before submitting
        print_job_info(job_counter, job)
        # Check that some necessary files exist in the right place
        # before submitting
        check_file_existence(job.executable, job.input_file, job.files_to_copy)
        # Create this job's working directory
        job.path = create_job_directory(job_set.path, job.name)
        # Copy necessary files for the job listed by the user to the
        # job's working directory
        copy_files(job.files_to_copy, job.path)
        # Write the job script to be submitted
        write_job_script(machine, job, job_set)
        # Submit the job script for this job
        submit_job_script(machine, job, job_set)

        job_counter += 1


if __name__ == "__main__":
    main()
