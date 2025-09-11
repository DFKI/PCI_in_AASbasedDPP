# Integration of Product Circularity Indicators into the Digital Product Passport based on the Asset Administration Shell
This repository is provided for a conference paper, as detailed below:
## Title of the paper: Integration of Product Circularity Indicators into the Digital Product Passport based on the Asset Administration Shell
## Conference:
ISM 2025 - International Conference on Industry of the Future and Smart Manufacturing, https://www.msc-les.org/ism2025/ 
## Abstract:
The Circular Economy (CE) is an economic model that shifts from a traditional linear approach to a circular one. It promotes sustainable product development by addressing environmental impacts throughout the entire product lifecycle -- from eco-design and production to end-of-life. In order to achieve this goal, it becomes an absolute necessity to measure circularity at different levels, specifically at the product level. Measurement of the product circularity would allow describing the current situation, evaluating possible future achievements, supporting decision-making tasks, and hence directing policy interventions towards required circularity steps. Despite its potential, measuring product circularity faces significant challenges and is a very complex task, including dealing with all parts of the production process and of the product lifecycle, and it often touches intangible measures and business practices that can hinder the achievement of truly sustainable outcomes. This highlights the need for transparent, accessible, and interoperable information through a Digital Product Passport (DPP), enabling relevant data to be extracted and applied across various stakeholders. This paper first introduces a generic approach for modeling a template DPP, grounded in the Industry 4.0 digitalization framework known as the Asset Administration Shell (AAS), designed to support CE objectives. Subsequently, the approach is extended to incorporate Circularity Indicators (CIs) at the product level as integral elements of the DPP. The proposed DPP model is then applied to an industrial use case to demonstrate its practical applicability and benefits.
## Authors:
Monireh Pourjafarian, Abdullah Farrukh, Mahdi Rezapour, Christiane Plociennik, Martin Ruskowski

## Installation

To use this project, you need to install the required dependencies.

```
pip install nicegui
```


## Running the Project

### Running BASYX
Launch the BASYX Services using the docker compose inside the subfolder [basyx](./basyx/)

<code>docker compose up -d</code>

### Using Python
Once NiceGUI is installed, you can run the project with:

```
python main.py
```

## Using Docker
1. Build docker image:
<code>docker build -t dace_dpp .</code>

2. Start docker container:
<code>docker run --network=host dace_dpp</code>

## Disclaimer
Our current approach does not directly interact with the production AAS but rather uses a copy inside a local BaSyx repository to showcase the use-case. The methods used can be applied to  production system also.