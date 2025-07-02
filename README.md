# ASESeminar-crewAI

### 1. Installation

Ensure you have Python >=3.10 <3.14 installed on your system. CrewAI uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, install CrewAI and the additional tools package:

```shell
pip install crewai
```

```shell
pip install 'crewai[tools]'
```

The command above installs the basic package and also adds extra components which require more dependencies to function.

### Troubleshooting Dependencies

If you encounter issues during installation or usage, here are some common solutions:

#### Common Issues

1. **ModuleNotFoundError: No module named 'tiktoken'**

   - Install tiktoken explicitly: `pip install 'crewai[embeddings]'`
   - If using embedchain or other tools: `pip install 'crewai[tools]'`

2. **Failed building wheel for tiktoken**

   - Ensure Rust compiler is installed (see installation steps above)
   - For Windows: Verify Visual C++ Build Tools are installed
   - Try upgrading pip: `pip install --upgrade pip`
   - If issues persist, use a pre-built wheel: `pip install tiktoken --prefer-binary`

### 2. Setting Up Your Crew with the YAML Configuration

```shell
crewai create crew oaicrew
```

This command creates a new project folder with the following structure:

```
oaicrew/
├── .gitignore
├── pyproject.toml
├── README.md
├── .env
└── src/
    └── oaicrew/        <--      (!)   Replace this folder with the oaicrew-folder from this repository
        ├── __init__.py
        ├── main.py
        ├── crew.py
        ├── tools/
        │   ├── custom_tool.py
        │   └── __init__.py
        └── config/
            ├── agents.yaml
            └── tasks.yaml
```

Replace the folder marked above with the folder

```bash
oaicrew
```

in this repository.

### 3. Running Your Crew

Before running your crew, make sure you have the following keys set as environment variables in your `.env` file:

- An [OpenAI API key](https://platform.openai.com/account/api-keys) (or other LLM API key): `OPENAI_API_KEY=sk-...`

Lock the dependencies and install them by using the CLI command but first, navigate to your project directory:

```shell
cd oaicrew
crewai install (Optional)
```

To run your crew, execute the following command in the root of the folder "oaicrew":

```bash
crewai run
```

### 4. Error "List index out of range msg_i" when using Ollama

In case you encounter this error, please apply the following following hotfix:
File: oaicrew/.venv/Lib/site-packages/litellm/litellm_core_utils/prompt-templates/factory.py
Change

```python
def ollama_pt(...
 if ollama_tool_calls:
        assistant_content_str += (
            f"Tool Calls: {json.dumps(ollama_tool_calls, indent=2)}"
        )
        msg_i += 1   #remove one indent here
)
```

to

```python
def ollama_pt(...
 if ollama_tool_calls:
        assistant_content_str += (
            f"Tool Calls: {json.dumps(ollama_tool_calls, indent=2)}"
        )
 msg_i += 1
)
```

See also:
https://community.crewai.com/t/list-index-out-of-range-msg-i/5612/8
