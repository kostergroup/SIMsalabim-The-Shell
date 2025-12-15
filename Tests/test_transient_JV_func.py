import os
import sys
import pytest

# Ensure the repo root is on sys.path so top-level 'utils' package can be imported
here = os.path.dirname(os.path.dirname(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import utils.transient_JV_func as transient_func


class DummyToast:
    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(autouse=True)
def isolate_session_state(monkeypatch, tmp_path):
    import streamlit as st
    st.session_state.clear()
    monkeypatch.setattr(st, "toast", lambda *a, **k: DummyToast())
    # create Statistics dir so the module can log without touching the repo
    repo_root = tmp_path
    (repo_root / "Statistics").mkdir()
    monkeypatch.chdir(repo_root)
    yield


def make_transient_par_obj(use_exp_data=0):
    return {
        'scan_speed': 1.0,
        'direction': 'F',
        'G_frac': 0.3,
        'UseExpData': use_exp_data,
        'Vmin': -1.0,
        'Vmax': 1.0,
        'steps': 10,
        'expJV_Vmin_Vmax': None,
        'expJV_Vmax_Vmin': None,
        'tVGFile': 'file.tVG'
    }


def test_run_Transient_JV_tvg_failure(monkeypatch, tmp_path):
    # Simulate tVG creation failure (result==1)
    monkeypatch.setattr(transient_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: make_transient_par_obj())
    monkeypatch.setattr(transient_func.transient_exp, 'Hysteresis_JV', lambda *a, **k: (1, 'tVG failed', {}))

    import streamlit as st
    errors = []
    monkeypatch.setattr(st, 'error', lambda msg: errors.append(msg))

    session = tmp_path / 'session'
    session.mkdir()

    transient_func.run_Transient_JV('devX', str(session), {'devX': {}}, ['L1'], 'ID-1', {}, 'hyst.txt')

    assert errors and 'tVG failed' in errors[0]
    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'ID-1 Transient FAILED' in log


@pytest.mark.parametrize('result_code', [0, 95])
def test_run_Transient_JV_success_sets_state_and_writes_file(monkeypatch, tmp_path, result_code):
    # Successful runs (0 and 95) should set session_state, write file, call store_file_names
    obj = make_transient_par_obj(use_exp_data=1)
    monkeypatch.setattr(transient_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: obj)

    output_vals = {'rms': 0.01, 'hyst_index': 7}
    monkeypatch.setattr(transient_func.transient_exp, 'Hysteresis_JV', lambda *a, **k: (result_code, 'ok', output_vals))

    called = {}
    def fake_store_file_names(dev_par, backend, zimt_device_parameters, layers):
        called['args'] = (dev_par, backend, zimt_device_parameters, layers)

    monkeypatch.setattr(transient_func.utils_devpar_UI, 'store_file_names', fake_store_file_names)

    import streamlit as st
    succ = []
    monkeypatch.setattr(st, 'success', lambda msg: succ.append(msg))

    session = tmp_path / 'session'
    session.mkdir()

    # Create an existing file to test removal and rewrite
    f = session / 'hyst_out.txt'
    f.write_text('old')

    transient_func.run_Transient_JV('devY', str(session), {'devY': {}}, ['L1','L2'], 'ID-SUCCESS', {}, 'hyst_out.txt')

    assert succ
    assert st.session_state['simulation_results'] == 'Transient JV'
    assert st.session_state['expObject'] == obj
    assert st.session_state['transientPars'] == 'hyst_out.txt'
    assert st.session_state['hystIndex'] == output_vals['hyst_index']
    assert st.session_state['hystRmsError'] == output_vals['rms']
    assert st.session_state['runSimulation'] is True
    assert called['args'][1] == 'zimt' and called['args'][2] == 'devY'

    # Ensure file contains keys
    content = (session / 'hyst_out.txt').read_text()
    for k, v in obj.items():
        assert f"{k} = {v}" in content

    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'ID-SUCCESS Transient SUCCESS' in log


def test_run_Transient_JV_removes_existing_file(monkeypatch, tmp_path):
    """Verify that an existing transient JV parameter file is removed during a successful run."""
    obj = make_transient_par_obj(use_exp_data=1)
    monkeypatch.setattr(transient_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: obj)
    monkeypatch.setattr(transient_func.transient_exp, 'Hysteresis_JV', lambda *a, **k: (0, 'ok', {'rms':0, 'hyst_index':1}))

    # Replace store_file_names so the test doesn't depend on the full device parameters shape
    monkeypatch.setattr(transient_func.utils_devpar_UI, 'store_file_names', lambda *a, **k: None)

    import streamlit as st
    monkeypatch.setattr(st, 'success', lambda msg: None)

    session = tmp_path / 'session'
    session.mkdir()
    existing = session / 'hyst_out.txt'
    existing.write_text('old')

    removed = []
    monkeypatch.setattr(transient_func.os, 'remove', lambda path: removed.append(path))

    transient_func.run_Transient_JV('devY', str(session), {'devY': {}}, ['L1','L2'], 'ID-REMOVE', {}, 'hyst_out.txt')

    assert removed and str(existing) in removed


def test_run_Transient_JV_other_error(monkeypatch, tmp_path):
    monkeypatch.setattr(transient_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: make_transient_par_obj())
    monkeypatch.setattr(transient_func.transient_exp, 'Hysteresis_JV', lambda *a, **k: (2, 'sim error', {}))

    import streamlit as st
    errors = []
    monkeypatch.setattr(st, 'error', lambda msg: errors.append(msg))

    session = tmp_path / 'session'
    session.mkdir()

    transient_func.run_Transient_JV('devZ', str(session), {'devZ': {}}, ['L1'], 'ID-ERROR', {}, 'hyst_pars.txt')

    assert errors and 'sim error' in errors[0]
    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'ID-ERROR Transient ERROR' in log
