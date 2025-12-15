# Developer Guidelines - The Shell

Contributions of all kinds: code, documentation, testing, bug reports, and feature ideas to improve The Shell and expand its functionality are welcome. This document explains instructions on the development environment, coding conventions, and the workflow for contributing.

## 1. How to Contribute

You can contribute in many ways:

-   Fix bugs
-   Add features or new experiments
-   Improve documentation
-   Refactor code for clarity and speed
-   Improve UI
-   Report issues

Before working on large features, please open an issue to discuss your idea.

## 2. Project Structure

    SIMsalabim-The-Shell/
    |
    |-- SIMsalabim.py               # Main GUI entry point
    |-- menu.py                     # Sidebar navigation and page loading
    |
    |-- pages/                      # Simulation setup pages (JV, CE, etc.) + Wrapper for result pages
    |-- results_pages/              # Result visualization pages
    |
    |-- Tests/                       # Test suite for functional unit tests
    |
    |-- utils/                      # Helper functions, plotting, parsing, UI widgets
        |-- band_diagram.py         # Build up the band diagram upon saving
        |-- device_parameters_UI.py # Modifying, reading, and writing of the parameters to/from files
        |-- dialog.py               # Definitions of dialog windows
        |-- general_UI.py           # General functions
        |-- plot_def.py             # Plot parameters and style
        |-- plot_functions_UI.py    # Wrappers to plot data in different styles on the UI using pySIMsalabim plotting functions
        |-- ref_optics.py           # References for the standard nk/spectrum files
        |-- style.css               # CSS style modifications
        |-- summary_and_citation.py # Create and build the summary_and_citations file 
        |-- upload_IU.py            # Wrappers to upload different types of files
        |-- steady_state.py         # Helper functions to run a steady state JV experiments + read scParsFile
        |-- transient_JV_func.py    # Helper functions to run a transient JV experiment
        |-- impedance_func.py       # Helper functions to run an impedance spectroscopy experiment
        |-- imps_func.py            # Helper functions to run an IMPS experiment
        |-- CV_func.py              # Helper functions to run a CV experiment
    |
    |-- Resources/                  # NK files, templates, optical data
    |-- Simulations/                # Individual session storage and run folders
    |-- Figures/                    # Folder to store figures for display
    |-- Statistics                  # Files to keep track of (usage) statistics



## 3. General Guidelines

All functions in the project should include a clear and concise docstring that describes what the function does, the arguments it accepts, and the values it returns. Using descriptive names for functions and variables is strongly encouraged, as this greatly improves code readability and maintainability. Clear documentation and naming help both new and experienced developers understand the purpose and behavior of the code at a glance.

Per streamlit's design, pages can reload upon user interaction. To ensure that important configuration, parameters, or results persist across page reloads and navigation, all information that needs to be retained must be stored in session_state parameters (e.g. st.session_state['device_file'] = path).

The project follows a clear separation of elements to maintain clarity and modularity. All user interface code should reside in the pages/ and results_pages/ directories, while computational logic, file parsing, and input/output operations should be handled within the utils/ modules. Including comments throughout the code to explain functionality is important, especially for complex computations or workflows, to aid future developers in understanding and maintaining the code.

When creating a new page, a consistent structure must be followed to ensure readability and maintainability. Begin with page configuration, including imports, layout settings, and session state initialization. Next, define any utility functions specific to the page. Finally, implement the UI code, including Streamlit widgets, layouts, and user interaction logic. Following this structure keeps pages organized, making it easier to develop, debug, and extend the application over time.

## 4. Adding new experiments

Before adding a new experiment, the numerical implementation of the experiment’s physics must be implemented in the pySIMsalabim package or folder. Once that is ready, follow these steps:

0.  It is recommended to review implementations of existing experiments to understand the structure, session state usage, and UI setup.
1.  Create a new page under pages/ directory.
2.  Initialize session_state parameters.
3.  Add UI controls for the page, such as text inputs, buttons or checkboxes.
4.  Add UI display for experiment specific parameters.
5.  Create a wrapper function in utils/exp_func.py that calls the relevant computational routines from pySIMsalabim.
6.  Store output file names or paths in session state variables.
7.  Create a visualization page in results_pages/.
8.  Register the new experiment mode in menu.py so it appears in the sidebar navigation.
9.  Write test cases for all newly added functions and wrappers.

After implementing these steps, run the tests provided in the Tests/ folder. Make sure both SIMsalabim and pySIMsalabim are present in the current folder.
```
pytest Tests
```
These tests primarily cover the functionality defined in the utils/ modules, but additional testing of the UI workflow is strongly recommended to ensure the new experiment integrates correctly with the rest of the application.

## 5. Report issues

If you encounter issues or bugs using The Shell, please don't hesitate to open an issue or contact us. Also check the documentation of SIMsalabim, for details on the drift-diffusion model. Provide as much information as possible, including the exact configuration of your device, and steps to reproduce the bug or issue.


