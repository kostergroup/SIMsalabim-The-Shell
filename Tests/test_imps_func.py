import os
import sys
import pytest

# Ensure repo root on sys.path so top-level imports work
here = os.path.dirname(os.path.dirname(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import utils.imps_func as imps_func


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
    (tmp_path / 'Statistics').mkdir()
    monkeypatch.chdir(tmp_path)
    yield


def make_imps_par_obj():
    return {
        'fmin': 10.0,
        'fmax': 1e5,
        'fstep': 10.0,
        'V0': 0.1,
        'fracG': 0.2,
        'G_frac': 0.5,
        'tVGFile': 'x.tVG',
        'tJFile': 'x.tJ'
    }


def test_run_IMPS_tvg_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(imps_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: make_imps_par_obj())
    monkeypatch.setattr(imps_func.imps_exp, 'run_IMPS_simu', lambda *a, **k: (1, 'tvG boom'))

    import streamlit as st
    errors = []
    monkeypatch.setattr(st, 'error', lambda msg: errors.append(msg))

    session = tmp_path / 'session'
    session.mkdir()

    imps_func.run_IMPS('devX', str(session), {'devX': {}}, ['L1'], 'IMPS-ID', {}, 'imps_pars.txt')

    assert errors and 'tvG boom' in errors[0]
    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'IMPS-ID IMPS FAILED' in log


@pytest.mark.parametrize('code', [0, 95])
def test_run_IMPS_success(monkeypatch, tmp_path, code):
    imps_obj = make_imps_par_obj()
    monkeypatch.setattr(imps_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: imps_obj)
    monkeypatch.setattr(imps_func.imps_exp, 'run_IMPS_simu', lambda *a, **k: (code, 'ok'))

    stored = {}
    def store_file_names(dev_par, backend, zimt_device_parameters, layers):
        stored['args'] = (dev_par, backend, zimt_device_parameters, layers)

    monkeypatch.setattr(imps_func.utils_devpar_UI, 'store_file_names', store_file_names)

    import streamlit as st
    successes = []
    monkeypatch.setattr(st, 'success', lambda msg: successes.append(msg))

    session = tmp_path / 'session'
    session.mkdir()

    # create a preexisting file so the removal branch is used
    existing = session / 'imps_pars.txt'
    existing.write_text('foo=1')

    imps_func.run_IMPS('devA', str(session), {'devA': {}}, ['Lx'], 'ID-SUCCESS', {}, 'imps_pars.txt')

    assert successes
    assert st.session_state['simulation_results'] == 'IMPS'
    assert st.session_state['expObject'] == imps_obj
    assert st.session_state['IMPSPars'] == 'imps_pars.txt'
    assert st.session_state['freqYFile'] == 'freqY.dat'
    assert st.session_state['runSimulation'] is True

    assert stored['args'][1] == 'zimt' and stored['args'][2] == 'devA'

    written = (session / 'imps_pars.txt').read_text()
    for k, v in imps_obj.items():
        assert f"{k} = {v}" in written

    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'ID-SUCCESS IMPS SUCCESS' in log


def test_run_IMPS_removes_existing_file(monkeypatch, tmp_path):
    """Verify that an existing parameter file is removed during a successful run.

    We patch the imps_func module's os.remove (not the global os) so the removal is observed
    and confined to the module under test.
    """
    monkeypatch.setattr(imps_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: make_imps_par_obj())
    monkeypatch.setattr(imps_func.imps_exp, 'run_IMPS_simu', lambda *a, **k: (0, 'ok'))
    monkeypatch.setattr(imps_func.utils_devpar_UI, 'store_file_names', lambda *a, **k: None)

    import streamlit as st
    monkeypatch.setattr(st, 'success', lambda msg: None)

    session = tmp_path / 'session'
    session.mkdir()
    existing_file = session / 'imps_pars.txt'
    existing_file.write_text('foo=1')

    removed = []
    # Patch the os.remove used by the module under test
    monkeypatch.setattr(imps_func.os, 'remove', lambda path: removed.append(path))

    imps_func.run_IMPS('devA', str(session), {'devA': {}}, ['Lx'], 'ID-SUCCESS', {}, 'imps_pars.txt')

    # Assert the old file was removed (path should match the session file path)
    assert removed and str(existing_file) in removed

def test_run_IMPS_other_error(monkeypatch, tmp_path):
    monkeypatch.setattr(imps_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: make_imps_par_obj())
    monkeypatch.setattr(imps_func.imps_exp, 'run_IMPS_simu', lambda *a, **k: (3, 'boom-other'))

    import streamlit as st
    errors = []
    monkeypatch.setattr(st, 'error', lambda msg: errors.append(msg))

    session = tmp_path / 'session'
    session.mkdir()

    imps_func.run_IMPS('devB', str(session), {'devB': {}}, [], 'ID-ERROR', {}, 'imps_out.txt')

    assert errors and 'boom-other' in errors[0]
    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'ID-ERROR IMPS ERROR' in log
