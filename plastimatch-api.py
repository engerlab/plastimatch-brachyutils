from SimpleITK import (
    ReadImage, WriteImage, ElastixImageFilter,
    GetDefaultParameterMap, WriteParameterFile,
    ReadParameterFile, TransformixImageFilter,
    ParameterMap, sitkNearestNeighbor
    )
from pydantic import BaseModel, ConfigDict, Field
from fastapi import FastAPI
from pathlib import Path
from typing import List, ClassVar

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

    pth_fixed_image: str
    pth_moving_image: str
    parameter_maps: List[dict | str] = None
    pth_output_image: str = "registered_image.nrrd"

    _parameter_maps_sitk: List[ParameterMap] = []
    _valid_param_maps: ClassVar[List[str]] = ["translation", "affine", "bspline", "groupwise", "rigid"]

    def __init__(self, **data):
        super().__init__(**data)
        dir_temp_data = Path(__file__).parent.joinpath("temp_data")
        self.pth_fixed_image=  str(dir_temp_data.joinpath(self.pth_fixed_image))
        self.pth_moving_image= str(dir_temp_data.joinpath(self.pth_moving_image))
        self.pth_output_image= str(dir_temp_data.joinpath(self.pth_output_image))

        # process the parameter maps argument. For strings, we get the default maps.
        # if a dictionary where key matched a name of a default map, we would load the 
        # default map, then override the provided keys and values.
        # if the dictionary with non-matching key, we create a parameter map from scratch.
        if self.parameter_maps is not None:
            for param_map in self.parameter_maps:
                if isinstance(param_map, str):
                    if param_map not in self._valid_param_maps:
                        raise ValueError(f"Parameter map {param_map} is not recognized. \
                            valid options are: \n {self._valid_param_maps}")
                    self._parameter_maps_sitk.append(GetDefaultParameterMap(param_map))
                if isinstance(param_map, dict):
                    # see if they want to modify a default_parameter_map
                    default_param_map = param_map.pop("default_parameter_map", None)
                    if default_param_map in self._valid_param_maps:
                        param_sitk = GetDefaultParameterMap(default_param_map)
                    else:
                        param_sitk = ParameterMap()
                    for param, val in param_map.items():
                        param_sitk[param] = [val]
                    self._parameter_maps_sitk.append(param_sitk)

app = FastAPI()

@app.post("/elastix_register")
def elastix_register(elastix_inputs: Register_Inputs):
    r"""
    ### Purpose:
    - This function performs image registration using the Elastix library.
    ### Parameters:
    - `elastix_inputs`: An instance of `Register_Inputs` containing the necessary inputs.
    ### Returns:
    - The result of the registration process.
    """

    fixed_image = ReadImage(elastix_inputs.pth_fixed_image)
    moving_image = ReadImage(elastix_inputs.pth_moving_image)

    ela_img_filter = ElastixImageFilter()
    ela_img_filter.SetFixedImage(fixed_image)
    ela_img_filter.SetMovingImage(moving_image)

    if elastix_inputs._parameter_maps_sitk:
        for i, param_map in enumerate(elastix_inputs._parameter_maps_sitk):
            if i == 0:
                ela_img_filter.SetParameterMap(param_map)
            else:
                ela_img_filter.AddParameterMap(param_map)

    result = ela_img_filter.Execute()
    try:
        WriteImage(result, elastix_inputs.pth_output_image)
        transform_maps = ela_img_filter.GetTransformParameterMap()
        for i, transform_map in enumerate(transform_maps):
            WriteParameterFile(
                transform_map,
                str(
                    Path(elastix_inputs.pth_output_image).parent.joinpath(f"transform_parameter_{i}.txt"))
            )
        return {
            "status": "success",
            "message": "Image registration completed successfully.",
            "output_image_path": elastix_inputs.pth_output_image
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to write output image: {str(e)}"
        }

class Warp_Inputs(BaseModel):
    r"""
    ### Purpose:
    - This class defines the inputs required for the Elastix warping API.
    The warp operation applies a transformation to an input image.
    ### Attributes:
    """
    pth_input: str
    pth_output: str
    pth_transform_maps: List[str]   

    def __init__(self, **data):
        super().__init__(**data)
        dir_temp_data = Path(__file__).parent.joinpath("temp_data")
        self.pth_input = str(dir_temp_data.joinpath(self.pth_input))
        self.pth_output = str(dir_temp_data.joinpath(self.pth_output))
        self.pth_transform_maps = [
            str(dir_temp_data.joinpath(pth)) for pth in self.pth_transform_maps
            ]

@app.post("/elastix_warp")
def elastix_warp(warp_inputs: Warp_Inputs):
    r"""
    ### Purpose:
    - This function performs image warping using the Elastix library.
    ### Parameters:
    - `warp_inputs`: An instance of `Warp_Inputs` containing the necessary inputs.
    ### Returns:
    - The result of the warping process.
    """

    input_image = ReadImage(warp_inputs.pth_input)
    transform_map_list = []
    for transform_map_path in warp_inputs.pth_transform_maps:
        if not Path(transform_map_path).exists():
            return {
                "status": "error",
                "message": f"Transform map file {transform_map_path} does not exist."
            }
        transform_map_list.append(ReadParameterFile(transform_map_path))

    transformix_filter = TransformixImageFilter()
    transformix_filter.SetMovingImage(input_image)
    transformix_filter.SetTransformParameterMap(transform_map_list)

    result = transformix_filter.Execute()

    try:
        WriteImage(result, warp_inputs.pth_output)
        return {
            "status": "success",
            "message": "Image warping completed successfully.",
            "output_image_path": warp_inputs.pth_output
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to write output image: {str(e)}"
        }

def test_elastix_register():
    dict_param_map = [
        {
            "default_parameter_map": "translation",
            "Interpolator": "NearestNeighborInterpolator",
            # "ResampleInterpolator": "NearestNeighborInterpolator"
            }
        ]
    input_obj = Register_Inputs(
        pth_fixed_image="static.nrrd",
        pth_moving_image="moving.nrrd",
        # parameter_maps=["translation", "affine"]
        parameter_maps=dict_param_map
    )
    elastix_register(input_obj)

def test_elastix_warp():
    input_obj = Warp_Inputs(
        pth_input="us_case000000.nrrd",
        pth_output="warped_image.nrrd",
        pth_transform_maps=["transform_parameter_0.txt"]
    )
    elastix_warp(input_obj)

if __name__ == "__main__":
    test_elastix_register()
    # print("Elastix registration test completed successfully.")
    # test_elastix_warp()
    # print("Elastix warping test completed successfully.")
    