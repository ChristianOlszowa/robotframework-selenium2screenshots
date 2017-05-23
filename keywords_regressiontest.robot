*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot
Resource  Selenium2Screenshots/keywords.robot
Library   regression_helper.RegressionHelper

*** Variables ***

${log_output_dir}  ${OUTPUT_DIR}

*** Keywords ***

Test vs reference
    [Arguments]  ${css_tag}  ${name}  ${ref_path}  ${update}=False
    ${ref_Image} =  run keyword if  '${update}' == 'True'  Create Reference Image  ${css_tag}  ${name}  ${ref_path}  ELSE  get ref shot path  ${name}  ${ref_path}
    Should look equal  ${ref_Image}  ${css_tag}  ${name}
    [Return]  ${ref_Image}

Create Reference Image
    [Arguments]  ${selector}  ${name}  ${ref_path}
    # Set Screenshot Directory  ${path}
    @{selectors} =  Create List  ${selector}
    ${new_reference_filename} =  Generate Reference Image Filename  ${name}
    ${croped_reference_filename} =  set ref shot path  ${new_reference_filename}  ${ref_path}
    log  ${croped_reference_filename}
    #ToDo Fix me, something else than 5 seks
    sleep  5s
    Capture and Crop Page Screenshot  ${croped_reference_filename}  @{selectors}
    [Return]  ${croped_reference_filename}

Should look equal
    [Arguments]  ${reference_path}  ${selector}  ${name}
    @{selectors} =  Create List  ${selector}
    ${current_filename} =  Generate Test Image Filename  ${name}
    Capture and Crop Page Screenshot  ${current_filename}  @{selectors}
    ${odir} =  get test shot path  ${log_output_dir}  ${current_filename}
    ${result} =  Should Look Like Reference  ${reference_path}  ${odir}  ${name}
    [Return]  ${result}
