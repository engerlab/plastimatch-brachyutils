from pydantic import BaseModel, ConfigDict, Field
from fastapi import FastAPI
from pathlib import Path
from typing import List, ClassVar

import subprocess


app = FastAPI()

class Register_Inputs(BaseModel):
    r"""
    ### Purpose:
    - This class defines the inputs required for the Elastix registration API.
    ### Attributes:
    - `fixed_image`: str := Path to the fixed image.
    - `moving_image`: str := Path to the moving image.
    - `parameter_map`: list[dict | str] := list of parameter maps for the transformations.
        For strings, we get the default maps from sitk, which are any combination of:
        "translation", "affine", "bspline", "groupwise", "rigid".
        If a dictionary is provided, it can contain the key "default_parameter_map" to specify
        which default map to use. If "default_parameter_map" matched a name of a default map,
        we would load the default map, then override the remaining provided keys and values.
        If the dictionary does not specify "default_parameter_map", we create a parameter map from scratch.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    global_params: Dict[str, str]
    stage_params_list: List[Dict[str, str]]

    def __init__(self, **data):
        super().__init__(**data)
        dir_temp_data = Path(__file__).parent.joinpath("temp_data")
        for key, value in self.global_params.items():
            if "temp_data/registration/" in value:
                value = value.split("temp_data/registration/")[-1]
            value = dir_temp_data.joinpath(value)
            self.global_params[key] = value

@app.post("/plastimatch_register")
def register_api(
    all_registration_inputs: Inputs_register
    ) -> None:
    r"""
    ### Purpose:
        - To run image registration using plastimatch.
    
    ### Inputs:
        - all_registration_inputs: an instance of Inputs_register containing the input parameters for the registration.
    """
    print(f"static image: {all_registration_inputs.global_params['fixed']}")
    print(f"moving image: {all_registration_inputs.global_params['moving']}")
    print(f"output image: {all_registration_inputs.global_params['image_out']}")
    print(f"output vf: {all_registration_inputs.global_params['vf_out']}")
    register(all_registration_inputs.global_params, all_registration_inputs.stage_params_list)

def register(
  global_params: Dict[str, str],
  stage_params_list: List[Dict[str, str]]
  ) -> Dict[str, float]:
  """
  ### Purpose:
    - To register two images using the plastimatch register command. The input to the command is a 
    text file called parm.txt. This text file has [Global] commands and [Stage] commands.
    While the variables for the global commands stay the same throughout many stages of the registration,
    the stage commands can be different for each stage. For the full list of these variables
    look at https://plastimatch.org/registration_command_file_reference.html.
    Here is an example of the parm.txt file:
      [GLOBAL]
      fixed=t5.mha
      moving=t0.mha
      image_out=warped.mha
      vf_out=deformation.nrrd

      [STAGE]
      xform=bspline
      grid_spac=50 50 50

      [STAGE]
      grid_spac=20 20 20

  ### Inputs:
    - global_params: dict := a dictionary containing the global parameters for the registration.
    The possible global parameters are:
      - fixed: str := the path to the fixed image.
      - moving: str := the path to the moving image.
      - fixed_roi: str := the path to the fixed region of interest.
      - moving_roi: str := the path to the moving region of interest.
      - fixed_landmarks: str := the path to the fixed landmarks.
      - moving_landmarks: str := the path to the moving landmarks.
      - warped_landmarks: str := the path to the warped landmarks.
      - xform_in: str := the path to the input transformation.
      - xform_out: str := the path to the output transformation.
      - vf_out: str := the path to the output vector field.
      - img_out: str := the path to the output image.
      - img_out_fmt: str := the format of the output image.
      - img_out_type: str := the type of the output image.
      - resample_when_linear: bool := whether to resample when linear.
      - logfile: str := the path to the log file.
    - stage_params_list: List[Dict[str, str]] := a list of dictionaries containing the stage parameters for the registration.
    please look at the plastimatch documentation for the full list of possible stage parameters.
  ### Outputs:
    - registration_summary: Dict[str, float] := a dictionary containing the registration summary.
    The possible keys are:
      - pth_registered_data: str := the path to the registered data.
      - log_file: str := the path to the log file.
  """
  
  # here are the possible global parameters for the registration
  # some are optional, some are mandatory, we loop through them 
  # and create the command
  global_param_possible_key_list = [
    "fixed", "moving", "fixed_roi",
    "moving_roi", "fixed_landmarks",
    "moving_landmarks","warped_landmarks",
    "xform_in", "xform_out", "vf_out",
    "image_out", "img_out_fmt", "img_out_type",
    "resample_when_linear", "logfile"
  ]
  final_global_params = defaultdict(str)
  # loop through the global parameters and create the command
  for key in global_params:
    if key in global_param_possible_key_list:
      final_global_params[key] = global_params[key]

  # make sure the required global parameters are present
  if "fixed" not in final_global_params:
    raise ValueError("The fixed image is required.")
  if "moving" not in final_global_params:
    raise ValueError("The moving image is required.")
  if "image_out" not in final_global_params:
    raise ValueError("The output image is required.")
  
  # here are the possible stage parameters for the registration
  # some are optional, some are mandatory, we loop through them
  # and create the command
  stage_param_possible_key_list = [
  "fixed_landmarks", "moving_landmarks", "warped_landmarks", "xform_out",
  "xform", "vf_out", "img_out", "img_out_fmt", "img_out_type",
  "resample_when_linear", "background_max", "convergence_tol", "default_value", 
  "demons_acceleration", "demons_filter_width", "demons_homogenization", "demons_std", 
  "demons_gradient_type", "demons_smooth_update_field", "demons_std_update_field",
  "demons_smooth_deformation_field", "demons_std_deformation_field", "demons_step_length",
  "grad_tol", "grid_spac", "gridsearch_min_overlap", "histoeq", "landmark_stiffness",
  "lbfgsb_mmax", "mattes_fixed_minVal", "mattes_fixed_maxVal", "mattes_moving_minVal",
  "mattes_moving_maxVal", "max_its", "max_step", "metric", "mi_histogram_bins", "min_its",
  "min_step", "num_hist_levels_equal", "num_matching_points", "num_samples", "num_samples_pct",
  "num_substages","optim", "optim_subtype", "pgtol", "regularization", "diffusion_penalty", 
  "curvature_penalty", "linear_elastic_multiplier", "third_order_penalty", 
  "total_displacement_penalty", "lame_coefficient_1", "lame_coefficient_2", "res",
  "res_mm", "res_mm_fixed", "res_mm_moving", "res_vox", "res_vox_fixed",
  "res_vox_moving", "rsg_grad_tol", "ss", "ss_fixed", "ss_moving",
  "threading", "thresh_mean_intensity", "translation_scale_factor",
  ]
  # loop through the stage parameters and create the command for each stage
  final_stage_params_list = []
  for stage_params in stage_params_list:
    final_stage_params = defaultdict(str)
    for key in stage_params:
      if key in stage_param_possible_key_list:
        final_stage_params[key] = stage_params[key]
    final_stage_params_list.append(final_stage_params) 

  # create the parm.txt file in the same directory as image_out
  out_dir = Path(final_global_params["image_out"]).parent
  out_dir.mkdir(parents=True, exist_ok=True)
  
  parm_txt_path = out_dir.joinpath("parm.txt")
  param_txt = "[Global]\n"
  for key in final_global_params:
    param_txt += f"{key}={final_global_params[key]}\n"
  param_txt += "\n"
  for stage in final_stage_params_list:
    param_txt += "[Stage]\n"
    for key in stage:
      param_txt += f"{key}={stage[key]}\n"
    param_txt += "\n"

  with open(parm_txt_path, "w") as f:
    f.write(param_txt)
  
  command = ["plastimatch", "register", str(parm_txt_path)]
  try:
    registration_summary = subprocess.run(command, capture_output = True, check = True)
  except Exception as e:
    print(e)


class Inputs_convert(BaseModel):
    r"""
    ### Purpose:
        - To define the input parameters for running the convert command of plastimatch.
    
    ### Attributes:
        - options: a dictionary containing the options for the convert command.
        - input_file: the input file for the convert command.
    """
    pth_input: Path | str = None
    pth_output: Path | str = None
    # these attributes will be filled from the options
    xf: Path | str = None

    def __init__(self, **data):
        dir_temp_data = Path(__file__).parent.joinpath("temp_data")
        for key, value in data.items():
            if isinstance(value, str):
                if "temp_data/registration/" in value:
                    value = value.split("temp_data/registration/")[-1]
                value = dir_temp_data.joinpath(value)
            data[key] = value
        super().__init__(**data)

@app.post("/plastimatch_convert")
def convert_api(
    all_convert_inputs: Inputs_convert
    ) -> None:
    r"""
    ### Purpose:
        - To run the convert command of plastimatch.
    ### Inputs:
        - all_convert_inputs: an instance of Inputs_convert containing the input parameters for the convert command.    
    """
    from plastimatch import convert
    convert(
        input=all_convert_inputs.pth_input,
        output_img=all_convert_inputs.pth_output,
        xf=all_convert_inputs.xf
    )

def convert(
    pth_input: Path | str,
    pth_output: Path | str,
    xf: Path | str = None
    ) -> None:
    """
    ### Purpose:
        - To convert an image using plastimatch.
    ### Inputs:
        - pth_input: Path | str := the path to the input image.
        - pth_output: Path | str := the path to the output image.
        - xf: Path | str := the path to the transformation file.
    """
    # Call the plastimatch convert command
    command = ["plastimatch", "convert", str(pth_input), str(pth_output)]
    if xf:
        command += ["--xf", str(xf)]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running plastimatch convert: {e}")

def test_register_api():
    pth_static = "../temp_data/static.nrrd"
    pth_moving = "../temp_data/moving.nrrd"
    pth_output = "../temp_data/registered.nrrd"
    vf_out = "../temp_data/vf.nrrd"

    global_params = {
        "fixed" : f"{pth_static}",
        "moving" : f"{pth_moving}",
        "image_out" : f"{pth_output}",
        "vf_out" : f"{vf_out}",
    }

    stage_params_list = [
        {
            "xform": "bspline"
        }
    ]
    inputs = Inputs_register(global_params=global_params, stage_params_list=stage_params_list)
    register_api(inputs)

def test_convert_api():
    pth_input = "../temp_data/moving.nrrd"
    pth_output = "../temp_data/warped.nrrd"
    xf = "../temp_data/vf.nrrd"
    inputs = Inputs_convert(pth_input=pth_input, pth_output=pth_output, xf=xf)
    convert_api(inputs)

if __name__ == "__main__":
    # test_register_api()
    test_convert_api()