# Artifacts for SC21 conference

## Machine characterization

Results from the [the SC Tech Program Author Kit](https://github.com/SC-Tech-Program/Author-Kit):

- [NREL Eagle compute node description](eagle-system.txt), more details at the [website](https://www.nrel.gov/hpc/eagle-system-configuration.html)
- [ORNL Summit compute node description](summit-system.txt), more details at the [website](https://docs.olcf.ornl.gov/systems/summit_user_guide.html#summit-documentation-resources)
- Authors have not renewed access to ANL Theta and cannot perform introspection - More details at their [website](https://www.alcf.anl.gov/support-center/theta/theta-thetagpu-overview)

## Files for generation of test cases

- [Example build procedure for ORNL Summit](summit-build-pelec.sh)
- [Example build procedure for NREL Eagle](eagle-build-pelec.sh)
- [Example input file for PMF case](inputs_ex) and [initial flow condition setup](PMF_CH4_1bar_300K_DRM_MixAvg.dat)
- [Example input file for piston bowl case](inputs_ex_pb)

Figure 3 requires the PeleC branch [here](https://github.com/AMReX-Combustion/PeleC/tree/jrood/cuda_acc).

## Submission files for the [job-scholar](../job-scholar) job submission framework

The [submission script](submit-jobs.py), is used as `python submit-jobs.py FILENAME`, where `FILENAME` is one of the following: 

- [Example strong scaling job set file for NREL Eagle](strong-scaling-eagle.yaml) (Figure 9, 10 in paper)
- [Example strong scaling job set file for ORNL Summit](strong-scaling-summit.yaml) (Figure 9, 10, and 11 in paper)
- [Example weak scaling job set file for ORNL Summit](weak-scaling-summit.yaml) (Figure 12 in paper)

Job-scholar generates submission scripts for each listed job using best practices for each supported machine. Although we have not recreated every YAML file necessary to recreate the figures, we provide several examples which demonstrate the exercise.


