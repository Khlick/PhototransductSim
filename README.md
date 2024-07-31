# PhototransductSim

PhototransductSim is an application designed to simulate phototransduction in rod and cone photoreceptors. It allows users to manipulate model parameters and visualize the resulting changes in photoreceptor responses. Results from the model may be exported by graph, or as comma-delimited values (CSV).

## Motivation

This application was developed to provide researchers and students with a powerful tool to study and understand the mechanisms of phototransduction. By simulating various scenarios and parameters, users can gain insights into the behavior of photoreceptors under different conditions.

## Installation

Install the included binaries for your operating system from the most recent release.

## Usage

Once in the application:
1. Select either a default model or set parameter values for your own in the Model Parameters section.
2. Click on the robot icon to run the simulation.
3. View the results in the axes provided.
4. To save your model parameters, you may export them to a JSON file.
5. Following the format of the saved model parameters JSON file, you may also import your own model parameters.
6. To perform a sweep of a parameter, you may enter multiple values for any one parameter, separated by commas.
7. When you run the simulation again, the sweep of responses will be shown in the axes. Toggle the axes legend to get color legends.

## Development

Developers may contribute in multiple ways:
1. Fork the GitHub repo.
2. Set up your Python environment (written with intended target of 3.10 and higher) and install packages from the requirements.txt.
3. On your active Python environment, run the application with:

```plain
python src\main\app\application.py
```
in your terminal (assuming python points to your python executable).

### Modifying the Transduction Model

To modify the transduction model, developers will need to:
1. Update the model information in the `src/main/model/phototransduction.py` file. Specifically, modify the `param` attribute, the ODE in `diff_eq`, and the pre- and post-solution processing in the `simulate_once` method.
2. Update the UI parameters that correspond to the model by editing the `src/main/data/model_inputs.yaml` according to the new model parameters.

The current model comes with the default parameter values for mouse rod and cone photoreceptors. Developers may remove these from the data folder or replace them with accurate model parameters for the updated model. 

Note: In the future, the default model parameters will be moved to a module which will be parsed to populate the default models in the UI. Feel free to jump on that task and submit a PR ;)

## Attributions

PhototransductSim utilizes the brilliant minds of many open-source developers, and we are so grateful for the following authors.

### Fonts

This project makes use of the Playwrite HR and Playfair Display fonts provided under the Open Font License (OFL), and FontAwesome Free icons under the CC BY 4.0 License.

#### Playwrite HR
- **Font Name**: Playwrite HR
- **Author**: Dalton Maag
- **License**: Open Font License (OFL)
- **Source**: [Google Fonts](https://fonts.google.com/specimen/Playwrite+HR)

#### Playfair Display
- **Font Name**: Playfair Display
- **Author**: Claus Eggers Sørensen
- **License**: Open Font License (OFL)
- **Source**: [Google Fonts](https://fonts.google.com/specimen/Playfair+Display)

#### FontAwesome 6.6.0 (Free)
- **Icon Library**: FontAwesome Free
- **Version**: 6.6.0
- **Author**: Fonticons, Inc.
- **License**: CC BY 4.0 License
- **Source**: [FontAwesome](https://fontawesome.com)

### Scientific Contributions

- Abtout, Annia, and Jürgen Reingruber. "Analysis of calcium dynamics for dim-light responses in rod and cone photoreceptors." bioRxiv (2022): 2022-03.
- Reingruber, Jürgen, et al. "A kinetic analysis of mouse rod and cone photoreceptor responses." The Journal of Physiology 598.17 (2020): 3747-3763.
- Abtout, A., Fain, G. and Reingruber, J. (2021), Analysis of waveform and amplitude of mouse rod and cone flash responses. J Physiol, 599: 3295-3312. https://doi.org/10.1113/JP281225
- Abtout, Annia, and Jürgen Reingruber. "Analysis of dim-light responses in rod and cone photoreceptors with altered calcium kinetics." Journal of Mathematical Biology 87.5 (2023): 69.

## Reporting Issues

To report any issues or bugs, please follow these steps:
1. Go to the [GitHub Issues](https://github.com/Khlick/PhototransductSim/issues) page for this project.
2. Click on "New Issue" and fill out the provided template with details about the issue you're experiencing.
3. Submit the issue, and the development team will address it as soon as possible.

---

## Acknowledgments

PhototransductSim utilizes the brilliant minds of many open-source developers, and we are so grateful for the following authors and contributors:

### Fonts

- **Playwrite HR** by Dalton Maag (Open Font License)
- **Playfair Display** by Claus Eggers Sørensen (Open Font License)
- **FontAwesome Free** by Fonticons, Inc. (CC BY 4.0 License)

### Python Packages

- **NumPy** (BSD License)
- **Matplotlib** (BSD-like License)
- **SciPy** (BSD License)
- **PyQt6** (GPL v3 / Riverbank Commercial License)
- **ReportLab** (BSD License)
- **scikit-learn** (BSD License)
- **PyInstaller** (GPL v2)

### Scientific Contributions

This software includes portions of code and algorithms based on the following papers:

1. Reingruber, Jürgen, et al. "A kinetic analysis of mouse rod and cone photoreceptor responses." The Journal of physiology 598.17 (2020): 3747-3763.

2. Abtout, A., Fain, G. and Reingruber, J. (2021), "Analysis of waveform and amplitude of mouse rod and cone flash responses." J Physiol, 599: 3295-3312. [DOI: 10.1113/JP281225](https://doi.org/10.1113/JP281225)

3. Abtout, Annia, and Jürgen Reingruber. "Analysis of dim-light responses in rod and cone photoreceptors with altered calcium kinetics." Journal of Mathematical Biology 87.5 (2023): 69.
