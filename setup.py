from setuptools import find_packages,setup
from typing import List

HYPHEN_E_DOT = "-e ."
def get_requirements(file_path:str)->List[str]:
    '''
    This function will return the list of requirements

    '''
    req_list = []
    with open(file_path) as file_obj:
        req_list = file_obj.readlines()
        req_list = [req.replace("\n", "") for req in req_list]
        if HYPHEN_E_DOT in req_list:
            req_list.remove(HYPHEN_E_DOT)

    return req_list

setup(
name= "Video_KYC",
version= "0.0.1",
author= "Umrav Singh",
author_email= "umravsinghnbd@gmail.com",
packages= find_packages(),
install_requires = get_requirements("requirements.txt")
)