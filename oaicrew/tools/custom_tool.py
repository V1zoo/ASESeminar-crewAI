import os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    directory: str = Field(..., description="directory to search in")
    query: str = Field(...,description="string to look for in the python files of the directory")

class MyCustomTool(BaseTool):
    name: str = "Search python files in a directory for a string"
    description: str = (
        "This tool returns a list of files that contain the given query in the given directory"
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, directory: str, query: str) -> str:
        # Implementation goes here
        if directory[-1] == "/":
            directory = directory[:-1]
        files_list = [
            f"{directory}/{(os.path.join(root, filename).replace(directory, '').lstrip(os.path.sep))}"
            for root, dirs, files in os.walk(directory)
            for filename in files
        ]
        result = []
        for file in files_list:
            if file.rfind(".py") != -1:
                with open(file,encoding="latin-1") as f:
                    if query in f.read():
                        result.append(file)
        files = "\n- ".join(result)
        return f"File paths: \n-{files}"
