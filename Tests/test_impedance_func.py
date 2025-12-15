import os
import sys
import pytest

# Ensure repo root in sys.path so we can import top-level utils package
here = os.path.dirname(os.path.dirname(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import utils.impedance_func as imp_func


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
    repo_root = tmp_path
    (repo_root / 'Statistics').mkdir()
    monkeypatch.chdir(repo_root)
    yield


def make_impedance_par_obj():
    return {
        "fmin": 1.0,
        "fmax": 1e6,
        "fstep": 10.0,
        "V0": 0.0,
        "delV": 0.01,
        "G_frac": 0.5,
        "tVGFile": "imp.tVG",
        "tJFile": "imp.tJ",
    }


def test_run_Impedance_tvg_failure(monkeypatch, tmp_path):
    # Simulate tVG creation failing
    monkeypatch.setattr(imp_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: make_impedance_par_obj())
    monkeypatch.setattr(imp_func.imp_exp, 'run_impedance_simu', lambda *a, **k: (1, 'tVG failed'))

    import streamlit as st
    errors = []
    monkeypatch.setattr(st, 'error', lambda msg: errors.append(msg))

    session = tmp_path / 'session'
    session.mkdir()

    imp_func.run_Impedance('dev1', str(session), {'dev1': {}}, ['L1'], 'IMP1', {}, 'imp.txt')

    assert errors and 'tVG failed' in errors[0]
    # confirm log recorded the FAILED state
    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'IMP1 Impedance FAILED' in log


@pytest.mark.parametrize('code', [0, 95])
def test_run_Impedance_success(monkeypatch, tmp_path, code):
    imp_obj = make_impedance_par_obj()
    monkeypatch.setattr(imp_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: imp_obj)
    monkeypatch.setattr(imp_func.imp_exp, 'run_impedance_simu', lambda *a, **k: (code, 'ok'))

    stored = {}
    monkeypatch.setattr(imp_func.utils_devpar_UI, 'store_file_names', lambda *a, **k: stored.update({'called': True, 'args': a}))

    import streamlit as st
    successes = []
    monkeypatch.setattr(st, 'success', lambda msg: successes.append(msg))

    session = tmp_path / 'session'
    session.mkdir()

    # create existing file to ensure removal step is exercised
    existing = session / 'imp_pars.txt'
    existing.write_text('old=1')

    imp_func.run_Impedance('devA', str(session), {'devA': {}}, ['Lx'], 'ID-SUCC', {}, 'imp_pars.txt')

    assert successes
    assert st.session_state['simulation_results'] == 'Impedance'
    assert st.session_state['expObject'] == imp_obj
    assert st.session_state['impedancePars'] == 'imp_pars.txt'
    assert st.session_state['freqZFile'] == 'freqZ.dat'
    assert st.session_state['runSimulation'] is True
    assert stored.get('called', False)

    written = (session / 'imp_pars.txt').read_text()
    for k, v in imp_obj.items():
        assert f"{k} = {v}" in written

    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'ID-SUCC Impedance SUCCESS' in log


def test_run_Impedance_removes_existing_file(monkeypatch, tmp_path):
    monkeypatch.setattr(imp_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: make_impedance_par_obj())
    monkeypatch.setattr(imp_func.imp_exp, 'run_impedance_simu', lambda *a, **k: (0, 'ok'))
    monkeypatch.setattr(imp_func.utils_devpar_UI, 'store_file_names', lambda *a, **k: None)

    import streamlit as st
    monkeypatch.setattr(st, 'success', lambda msg: None)

    session = tmp_path / 'session'
    session.mkdir()
    existing_file = session / 'imp_pars.txt'
    existing_file.write_text('foo=1')

    removed = []
    monkeypatch.setattr(imp_func.os, 'remove', lambda path: removed.append(path))

    imp_func.run_Impedance('devA', str(session), {'devA': {}}, ['Lx'], 'ID-SUCC2', {}, 'imp_pars.txt')

    assert removed and str(existing_file) in removed


def test_run_Impedance_other_error(monkeypatch, tmp_path):
    monkeypatch.setattr(imp_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: make_impedance_par_obj())
    monkeypatch.setattr(imp_func.imp_exp, 'run_impedance_simu', lambda *a, **k: (2, 'crashed'))

    import streamlit as st
    errors = []
    monkeypatch.setattr(st, 'error', lambda msg: errors.append(msg))

    session = tmp_path / 'session'
    session.mkdir()

    imp_func.run_Impedance('devB', str(session), {'devB': {}}, [], 'ID-ERROR', {}, 'imp_out.txt')

    assert errors and 'crashed' in errors[0]
    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'ID-ERROR Impedance ERROR' in log
