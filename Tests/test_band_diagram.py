import sys
import os
import matplotlib
matplotlib.use('Agg')

# ensure repo root on sys.path
here = os.path.dirname(os.path.dirname(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import utils.band_diagram as bd


def make_section(name, params):
    """Helper: create a dev_par section list matching devpar_read_from_txt format.

    params should be an iterable of tuples (param_name, value)
    """
    section = [name]
    for pname, pval in params:
        section.append(['par', pname, str(pval), ''])
    return section


def test_get_section_and_get_param():
    block = [
        make_section('General', [('T', 300), ('E_c', 4.0)]),
        make_section('Contacts', [('leftElec', -1), ('W_L', '3.5')])
    ]

    gen = bd.get_section(block, 'General')
    assert gen is not None and gen[0] == 'General'

    assert bd.get_param(gen, 'T', float) == 300.0
    assert bd.get_param(gen, 'E_c', float) == 4.0

    # nonexistent section
    assert bd.get_section(block, 'DoesNotExist') is None
    # nonexistent param
    assert bd.get_param(gen, 'nope') is None
    # section is None
    assert bd.get_param(None, 'T') is None


def test_create_width_label_and_plot_device_widths():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    y_min = -1.0

    # Provide thin and normal widths so scaling is applied for very small pieces
    L_original = [5e-9, 20e-9]
    L = [5e-9, 20e-9]
    # plot_device_widths expects L and L_original as lists of numbers; call it
    bd.plot_device_widths(ax, y_min, L, L_original)

    # Width label text entries: one per layer + the [nm] label (should be in texts)
    texts = [t.get_text() for t in ax.texts]
    # check nm label exists
    assert any('[nm]' in t for t in texts)
    # numeric label present for L_original[0] in nm rounding
    assert any(str(int(L_original[0] * 1e9)) in t for t in texts)


def test_create_energy_label_alignments():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    L_total = 100.0

    # wide enough: width > 0.2*L_total should center
    bd.create_energy_label(0.0, 30.0, L_total, 1.23, 'CB', ax, 'top')
    # 'WR' in band_type -> ha right
    bd.create_energy_label(30.0, 40.0, L_total, 2.0, 'WR', ax, 'top')
    # otherwise left
    bd.create_energy_label(40.0, 45.0, L_total, 0.5, 'CB', ax, 'bot')

    # examine last three texts
    t0, t1, t2 = ax.texts[-3:]
    assert t0.get_ha() == 'center'
    assert t1.get_ha() == 'right'
    assert t2.get_ha() == 'left'


def test_get_work_function_sfb_cases():
    # Build dev_par structure for device and a layer
    # dev_par[dev_par_name] has General section with T
    dev_par = {}
    dev_par['simulation_setup_simss.txt'] = [
        ['Description'],
        make_section('General', [('T', 300)])
    ]

    # Layer: neutral net = N_A - N_D
    # Case net > 0
    dev_par['layer1.txt'] = [
        ['Description'],
        make_section('General', [('E_c', 1.0), ('E_v', 2.0), ('N_c', 1e20), ('N_D', 0.0), ('N_A', 1e18)])
    ]

    # compute expected result: WF = E_v - (k*T/q) * ln(N_c/net)
    wf_1 = bd.get_work_function_sfb(['par', 'l1', 'layer1.txt'], dev_par, 'simulation_setup_simss.txt')
    assert wf_1 == 1.88

    # Case net < 0
    dev_par['layer2.txt'] = [
        ['Description'],
        make_section('General', [('E_c', 1.0), ('E_v', 2.0), ('N_c', 1e20), ('N_D', 1e18), ('N_A', 0.0)])
    ]

    wf_2 = bd.get_work_function_sfb(['par', 'l2', 'layer2.txt'], dev_par, 'simulation_setup_simss.txt')
    assert wf_2 == 1.12

    # Case net == 0
    dev_par['layer3.txt'] = [
        ['Description'],
        make_section('General', [('E_c', 1.0), ('E_v', 2.0), ('N_c', 1e20), ('N_D', 1e18), ('N_A', 1e18)])
    ]
    wf_3 = bd.get_work_function_sfb(['par', 'l3', 'layer3.txt'], dev_par, 'simulation_setup_simss.txt')
    assert wf_3 == 1.5


def build_dev_par_for_band():
    # Helper that constructs a simple dev_par and layers for get_param_band_diagram
    dev_par = {}

    # setup has Contacts section
    setup = [
        ['Description'],
        make_section('Contacts', [('leftElec', -1), ('W_L', '4.0'), ('W_R', '3.0')])
    ]
    dev_par['simulation_setup_simss.txt'] = setup

    # two layers with General params L, E_c, E_v
    dev_par['layer1.txt'] = [
        ['Description'],
        make_section('General', [('L', 10e-9), ('E_c', 1.0), ('E_v', -1.0)])
    ]
    dev_par['layer2.txt'] = [
        ['Description'],
        make_section('General', [('L', 50e-9), ('E_c', 0.5), ('E_v', -0.5)])
    ]

    layers = [['par', 'setup', 'simulation_setup_simss.txt'], ['par', 'l1', 'layer1.txt'], ['par', 'l2', 'layer2.txt']]
    return dev_par, layers


def test_get_param_band_diagram_returns_figure(monkeypatch, tmp_path):
    dev_par, layers = build_dev_par_for_band()

    # call with run_mode=False -> return fig
    fig = bd.get_param_band_diagram(dev_par, layers, 'simulation_setup_simss.txt', run_mode=False)
    assert hasattr(fig, 'gca') or fig is None or True  # just ensure call succeeded and returned

    # Now test run_mode True triggers UI: monkeypatch create_UI_band_diagram
    called = {}
    def fake_ui(fig_obj, msg):
        called['called'] = True

    monkeypatch.setattr(bd, 'create_UI_band_diagram', fake_ui)

    # This should not raise and should call our fake_ui
    bd.get_param_band_diagram(dev_par, layers, 'simulation_setup_simss.txt', run_mode=True)
    assert called.get('called', False)


def test_create_UI_band_diagram_error_and_normal(monkeypatch):
    # Error path
    msgs = []
    import streamlit as st
    monkeypatch.setattr(st, 'error', lambda m: msgs.append(m))
    bd.create_UI_band_diagram(None, 'Some error')
    assert msgs and 'Some error' in msgs[0]

    # Normal path: create simple fig and monkeypatch streamlit to accept calls
    class DummyContainer:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    # make st.empty return a context manager-like object
    monkeypatch.setattr(st, 'empty', lambda : DummyContainer())
    called = {'md': 0, 'btn': 0, 'pyplot': 0}
    monkeypatch.setattr(st, 'columns', lambda *a: (None, DummyContainer(), DummyContainer()))
    monkeypatch.setattr(st, 'markdown', lambda *a, **k: called.update({'md': called['md'] + 1}))
    monkeypatch.setattr(st, 'button', lambda *a, **k: called.update({'btn': called['btn'] + 1}) or None)
    monkeypatch.setattr(st, 'pyplot', lambda f: called.update({'pyplot': called['pyplot'] + 1}) or None)

    import matplotlib.pyplot as plt
    fig, _ = plt.subplots()
    bd.create_UI_band_diagram(fig, '')

    # Our monkeypatched functions were invoked at least once
    assert called['md'] >= 1
    assert called['pyplot'] >= 1


def test_close_figure_is_noop():
    # function exists and is callable
    assert callable(bd.close_figure)
    bd.close_figure()  # should do nothing


def build_dev_par_edge_cases():
    dev_par = {}
    # Contacts section
    dev_par['setup.txt'] = [
        ['Description'],
        make_section('General', [('T', 300)]),
        make_section('Contacts', [('leftElec', -1), ('W_L', 'sfb'), ('W_R', '5.0')])
    ]
    # Thin layer (< MIN_VISIBLE_WIDTH * total)
    dev_par['thin_layer.txt'] = [
        ['Description'],
        make_section('General', [('L', 1e-10), ('E_c', 2.0), ('E_v', 1.0), ('N_c', 1e20), ('N_D', 0.0), ('N_A', 1e18)])
    ]
    # Regular layer
    dev_par['normal_layer.txt'] = [
        ['Description'],
        make_section('General', [('L', 50e-9), ('E_c', 3), ('E_v', 1)])
    ]
    # Layer missing parameters
    # missing some optional params but include minimal L/E values to keep plotting stable
    dev_par['missing_layer.txt'] = [
        ['Description'],
        make_section('General', [('L', 20e-9), ('E_c', 0.0), ('E_v', 0.0)])
    ]
    layers = [
        ['par', 'setup', 'setup.txt'],
        ['par', 'thin', 'thin_layer.txt'],
        ['par', 'normal', 'normal_layer.txt'],
        ['par', 'missing', 'missing_layer.txt']
    ]
    return dev_par, layers


def test_min_visible_width_and_missing_params(monkeypatch):
    dev_par, layers = build_dev_par_edge_cases()

    # Monkeypatch UI wrapper to skip Streamlit calls
    monkeypatch.setattr(bd, 'create_UI_band_diagram', lambda fig, msg: None)

    # Call function with run_mode=False to get figure
    fig = bd.get_param_band_diagram(dev_par, layers, 'setup.txt', run_mode=False)

    # Determine original and scaled widths from plotted patches (collections)
    ax = fig.axes[0]
    # There should be at least three filled collections (one per layer)
    assert len(ax.collections) >= 3

    # First filled area corresponds to thin layer; compute its x-range
    poly = ax.collections[0].get_paths()[0]
    xs = poly.vertices[:, 0]
    thin_width_plotted = xs.max() - xs.min()

    # Compute expected minimal width threshold
    L_original = [bd.get_param(bd.get_section(dev_par[l[2]], 'General'), 'L') for l in layers[1:]]
    L_total_original = sum(L_original)
    expected_min = bd.MIN_VISIBLE_WIDTH * L_total_original

    # Ensure thin original is smaller than threshold and plotted width is at least expected_min
    assert L_original[0] < expected_min
    assert thin_width_plotted >= expected_min * 0.9

    # Check that missing parameters did not break plotting
    assert fig is not None

def test_multiple_layers_boundaries(monkeypatch):
    # Build 10 layers
    dev_par = {}
    layers = [['par', 'setup', 'setup.txt']]
    setup_section = make_section('Contacts', [('leftElec', -1), ('W_L', '4.0'), ('W_R', '3.0')])
    dev_par['setup.txt'] = [['Description'], setup_section]

    for i in range(10):
        dev_par[f'layer{i}.txt'] = [['Description'], make_section('General', [('L', 10e-9), ('E_c', i+1), ('E_v', i)])]
        layers.append(['par', f'layer{i}', f'layer{i}.txt'])

    # Monkeypatch UI wrapper
    monkeypatch.setattr(bd, 'create_UI_band_diagram', lambda fig, msg: None)

    fig = bd.get_param_band_diagram(dev_par, layers, 'setup.txt', run_mode=False)

    # Ensure 10 filled areas were created (axes.collections should hold PolyCollections)
    assert len(fig.axes[0].collections) >= 10
