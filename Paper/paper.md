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


date: 11 December 2025
bibliography: paper.bib
---

# Summary

The Shell is an interactive, browser-based interface for the open-source drift-diffusion simulator SIMsalabim[@koopmans2022simsalabim], available on [www.simsalabim-online.com](www.simsalabim-online.com). SIMsalabim and the drift-diffusion technique are widely used to study and describe charge transport in semiconductor devices. While SIMsalabim provides a powerful and extensive implementation of this model, it requires command-line execution and manual configuration of the input and output files. Even with the addition of pySIMsalabim[@pySIMsalabim], which greatly enhances the functionality of SIMsalabim with the addition of several experimental techniques and interfaces the software with Python, users must still rely on scripting or code editing. This poses a barrier for researchers who want to focus on the actual physical modelling without the need for scripting. This also reduces the approachability of the drift-diffusion model and the capabilities of SIMsalabim, while it can be a great tool to further understand device limitations and performance.

The Shell addresses this by offering an intuitive graphical interface built in Python on the Streamlit framework [@streamlit]. It allows users to easily configure devices, run multiple experiments for the same device such as current-voltage sweeps and impedance spectroscopy, and immediately have visualized outputs, through a clean button-based navigation system. It also supports uploading custom user-defined device configurations, importing experimental data to directly compare with simulations, and export complete data packages with all metadata ready for publication. Because everything runs directly on the browser, there is no installation required. For more advanced usage, The Shell can also be deployed on a local network, for complete control over scalability, resource allocation, and customization.

By making SIMsalabim easier and more convenient to use, The Shell lowers the barrier for modelling semiconductor devices without compromising on the physical model. It enables users to quickly build, explore, and interpret the internal dynamics of semiconductor devices and to relate them to macroscopic performance.

# Statement of need

The design and optimization of semiconductor devices such as solar cells, LEDs, photodetectors, and thin-film transistors depends more and more on detailed modelling of the charge transport, recombination, and extraction processes. Drift-diffusion simulations provide the tools to achieve this, connecting the internal physics to measurable behaviour. SIMsalabim is an established open-source drift-diffusion simulator, but its requirement for scripting and command line based workflow can hinder efficient use and broader adoption in the research community.

The Shell addresses this by providing a user-friendly interface that uses SIMsalabims capabilities, but now directly from the browser, reducing any time that would be needed for installation of setting up the software. It removes the need for scripting and combines it with the extended functionality available in pySIMsalabim. Model parameters can be set through simple input fields, running experiments requires minimal setup time, and interactive results are directly generated and visualized. This enables users to rapidly combine several experiments to obtain a comprehensive understanding of the device behaviour. The deployed instance of The Shell ([www.simsalabim-online.com](www.simsalabim-online.com)) has seen significant interaction since its launch, with users from over 40 countries and an average of 800 simulations per month.

With the drift-diffusion technique being a well-established and popular modelling technique, there exist several more software programs in the community, each with their own strengths and weaknesses. Some are freeware, or even open-source, others commercial. Some do not include ionic motion in their simulations, or are focussed more on conventional photovoltaics. Several that have a graphical user interface are: SETFOS[@SETFOS], Sentaurus Device[@SentaurusDevice], Scaps-1D[@burgelman2000modelling], and ASA[@ASA].

# Acknowledgements

Funded by the European Union; views and opinions expressed are however those of the authors only and do not necessarily reflect those of the European Union or CINEA; neither the European Union nor the granting authority can be held responsible for them. NEXUS project has received funding from Horizon Europe Research and Innovation Action programme under Grant Agreement nº 101075330.

# References
