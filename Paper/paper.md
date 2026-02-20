---
title: 'The Shell: A graphical user interface for drift-diffusion simulations with SIMsalabim'
tags:
  - GUI
  - drift-diffusion
  - solar cells
  - Python
authors:
  - name: Sander Heester
    orcid: 0000-0001-5954-895X
    affiliation: 1
  - name: Marten Koopmans
    orcid: 0000-0002-2328-155X
    affiliation: 1
  - name: L. Jan Anton Koster
    orcid: 0000-0002-6558-5295
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: 1
affiliations:
 - name: Zernike Institute for Advanced Materials, University of Groningen, Nijenborgh 3, 9747AG, Groningen, The Netherlands


date: 20 February 2026
bibliography: paper.bib
---

# Summary

The Shell is an interactive, browser-based interface for the open-source drift-diffusion simulator SIMsalabim[@koopmans2022simsalabim], available on [www.simsalabim-online.com](www.simsalabim-online.com). SIMsalabim and the drift-diffusion technique are widely used to study and describe charge transport in semiconductor devices. While SIMsalabim provides a powerful and extensive implementation of this model, it requires command-line execution and manual configuration of the input and output files. Even with the addition of pySIMsalabim[@pySIMsalabim], which greatly enhances the functionality of SIMsalabim with the addition of several experimental techniques and interfaces the software with Python, users must still rely on scripting or code editing. This poses a barrier for researchers who want to focus on the actual physical modelling without the need for scripting. This also reduces the approachability of the drift-diffusion model and the capabilities of SIMsalabim, while it can be a great tool to further understand device limitations and performance.

The Shell addresses this by offering an intuitive graphical interface built in Python on the Streamlit framework [@streamlit]. It allows users to easily configure devices, run multiple experiments for the same device such as current-voltage sweeps and impedance spectroscopy, and immediately have visualized outputs, through a clean button-based navigation system. It also supports uploading custom user-defined device configurations, importing experimental data to directly compare with simulations, and export complete data packages with all metadata ready for publication. Because everything runs directly on the browser, there is no installation required. For more advanced usage, The Shell can also be deployed on a local network, for complete control over scalability, resource allocation, and customization.

By making SIMsalabim easier and more convenient to use, The Shell lowers the barrier for modelling semiconductor devices without compromising on the physical model. It enables users to quickly build, explore, and interpret the internal dynamics of semiconductor devices and to relate them to macroscopic performance.

# Statement of need

The design and optimization of semiconductor devices such as solar cells, LEDs, photodetectors, and thin-film transistors depends more and more on detailed modelling of the charge transport, recombination, and extraction processes. Drift-diffusion simulations provide the tools to achieve this, connecting the internal physics to measurable behaviour. SIMsalabim is an established open-source drift-diffusion simulator, but its requirement for scripting and command line based workflow can hinder efficient use and broader adoption in the research community.

The Shell addresses this by providing a user-friendly interface that uses SIMsalabims capabilities, but now directly from the browser, reducing any time that would be needed for installation of setting up the software. It removes the need for scripting and combines it with the extended functionality available in pySIMsalabim. Model parameters can be set through simple input fields, running experiments requires minimal setup time, and interactive results are directly generated and visualized. This enables users to rapidly combine several experiments to obtain a comprehensive understanding of the device behaviour.

# State of the field

With the drift-diffusion technique being a well-established and popular modelling technique, there exist several more software programs in the community, each with their own strengths and weaknesses. Some are freeware, or even open-source, others commercial. Some do not include ionic motion in their simulations, or are focused more on conventional photovoltaics. Several that have a graphical user interface are: SETFOS[@SETFOS], Sentaurus Device[@SentaurusDevice], Scaps-1D[@burgelman2000modelling], and ASA[@ASA].

The Shell addresses the gap left by the other software programs by providing a user-friendly, open-source, browser-based user interface that combines many of their advantages and bundles them with the extensive implementation of the drift-diffusion model in SIMsalabim, further extended with the additional experiments in pySIMsalabim. Together this provides a user-friendly yet powerful application, serving both beginner as well as advanced or expert users. Additionally, its lack of installation or extensive setup fills the gap as being a low threshold option for any user wanting to do advanced simulations of various semiconductor devices. Unlike other tools that are tightly coupled with their respective simulation engines, The Shell has also been developed as a standalone layer. This design choice ensures that any part of the SIMsalabim software suite can be used independently, depending on the user's specific application, without the need or restriction for the entire software suite.

# Software design

The Shell is designed to focus on usability, modularity and scalability, while retaining the robustness of SIMsalabim. By building it on the Streamlit framework, it leverages the use of Python with the framework's interactive widgets as well as easy application setup and deployment. It creates an intuitive interface without the requirement for extensive UI design. This approach balances the need for development and maintenance with a clear and user-friendly experience. The decision to use a Python based framework rather than more common JavaScript for backend development in combination with HTML/CSS for the frontend, was based on ease of development and contribution as well as seamless integration with existing tools in the SIMsalabim software suite. In addition to this, Streamlit's ability to handle both frontend and backend logic also simplifies development and maintenance, complemented with reduced software size and program complexity.

The Shell exclusively focuses on the UI or web application aspect of the software, while the core physics and experimental implementations are obtained from its integration with pySIMsalabim. This separation enables independent development of the user-interface and any physical components. The UI is constructed modularly, facilitating easy addition of any new experiments or extension of visualized results. 

To maximize accessibility, The Shell a browser-based application. This removes the requirement for any type of installation on a local device, which would also bring additional complexity to the software. In addition to this, The Shell can be accessed from any location and any device, removing the dependency on the resources of individual devices. Being browser-based also enables easier scaling, as this will only depend on the server capabilities. However, it is also possible to deploy the entire web application locally, which enables additional customization and resource allocation. Its fully open source nature further supports transparency and user-guided customization, which none of the other tools in the field provide while also offering a graphical user interface.

# Research Impact Statement

The Shell has already demonstrated significant impact since its launch. The deployed instance of The Shell ([www.simsalabim-online.com](www.simsalabim-online.com)) has seen significant interaction since its launch, with users from over 40 countries worldwide and an average of over 750 simulations run per month. The Shell has proven to not only be a useful tool from a research perspective, but also demonstrated to be highly useful for educational purposes. As the software starts to gain traction, it has been cited in peer-reviewed publication.[@thiesbrummel2026ion] With the continuous development, improvements and extensions, its usage is expected to grow further. This is supported by the growing Slack community for the SIMsalabim project, including The Shell, which continues to see an increasing number of users and interactions. With this growing adoption and community, The Shell can become one of the communities standard tools for semiconductor modelling, not just for theoretical researchers, but for all working on semiconductor devices.

# AI Usage Disclosure

Generative AI tools were used to assist in the creation of unit tests for The Shell. Specifically GitHub Copilot in combination with Mistral Le Chat have been used to help automate the generation of test cases, to ensure the most complete coverage of the entire software. All generated content has been thoroughly reviewed and validated manually to ensure correctness, whether it made sense, and its effectiveness. No generative AI tools were used in the creation, documentation, or development of the main software and writing of this manuscript.

# Acknowledgements

Funded by the European Union; views and opinions expressed are however those of the authors only and do not necessarily reflect those of the European Union or CINEA; neither the European Union nor the granting authority can be held responsible for them. NEXUS project has received funding from Horizon Europe Research and Innovation Action programme under Grant Agreement nº 101075330.

# References
