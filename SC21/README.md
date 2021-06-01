# Scripts for SC21 conference

## Machine descriptions

Using [the SC Tech Program Author Kit](https://github.com/SC-Tech-Program/Author-Kit):

- [NREL Eagle compute node description](eagle-system.txt), more details at the [website](https://www.nrel.gov/hpc/eagle-system-configuration.html)
- [ORNL Summit compute node description](summit-system.txt), more details at the [website](https://docs.olcf.ornl.gov/systems/summit_user_guide.html#summit-documentation-resources)
- ANL Theta, more details at the [website](https://www.alcf.anl.gov/support-center/theta/theta-thetagpu-overview)

## Submission job set files for [job-scholar](../job-scholar)

The [submission script](submit-jobs.py), is used as `python3 submit-jobs.py FILENAME`, where `FILENAME` is one of the following: 

- [Strong scaling job set file for NREL Eagle](strong-scaling-eagle.yaml) (Figure 9, 10 in paper)
- [Strong scaling job set file for ORNL Summit](strong-scaling-summit.yaml) (Figure 9, 10, and 11 in paper)
- [Weak scaling  job set file for ORNL Summit](weak-scaling-summit.yaml) (Figure 12 in paper)

## Case specific files

- [Build script for ORNL Summit](summit-build-pelec.sh)
- [Input file for PMF case](inputs_ex) and [initial flow condition setup](PMF_CH4_1bar_300K_DRM_MixAvg.dat)
- [Input file for piston bowl case](inputs_ex_pb)
