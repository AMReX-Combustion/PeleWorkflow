#!/bin/bash -l

MYPWD=${PWD}
set -e

cmd() {
  echo "+ $@"
  eval "$@"
}

cmd "source /nopt/nrel/ecom/hpacf/env.sh"
cmd "module load gcc"
cmd "module load binutils"
cmd "module load git"
cmd "module load python"
cmd "module load cuda/10.2.89"

cmd "git clone --recursive https://github.com/AMReX-Combustion/PeleC.git"
cmd "cd ${MYPWD}/PeleC/Submodules/AMReX"
cat > patch.tmp << '_EOF'
diff --git a/Tools/GNUMake/comps/nvcc.mak b/Tools/GNUMake/comps/nvcc.mak
index 47b9a07..7075986 100644
--- a/Tools/GNUMake/comps/nvcc.mak
+++ b/Tools/GNUMake/comps/nvcc.mak
@@ -79,7 +79,7 @@ ifeq ($(lowercase_nvcc_host_comp),gnu)

   NVCC_CCBIN ?= g++

-  CXXFLAGS_FROM_HOST := -ccbin=$(NVCC_CCBIN) -Xcompiler='$(CXXFLAGS)' --std=$(CXXSTD)
+  CXXFLAGS_FROM_HOST := -ccbin=$(NVCC_CCBIN) -Xcompiler='$(CXXFLAGS)' --std=$(CXXSTD) -Xptxas --disable-optimizer-constants
   CFLAGS_FROM_HOST := $(CXXFLAGS_FROM_HOST)
   ifeq ($(USE_OMP),TRUE)
      LIBRARIES += -lgomp
_EOF
cmd "git apply patch.tmp && rm patch.tmp"
cmd "cd ${MYPWD}/PeleC/Exec/RegTests/PMF"
cmd "git checkout v0.2 && git submodule update"
cmd "nice make -j8 TPLrealclean"
cmd "nice make -j8 COMP=gnu USE_CUDA=FALSE USE_SUNDIALS_PP=TRUE TPL"
cmd "nice make -j8 realclean"
cmd "nice make -j8 COMP=gnu USE_MPI=TRUE USE_CUDA=FALSE USE_SUNDIALS_PP=TRUE TINY_PROFILE=TRUE Chemistry_Model=drm19"
