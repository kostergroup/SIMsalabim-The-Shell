import os
import pytest
import sys

# Ensure the repository root (project workspace) is on sys.path so top-level modules like `utils` can be found
here = os.path.dirname(os.path.dirname(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import utils.CV_func as cv_func


class DummyToast:
    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(autouse=True)
def isolate_session_state(monkeypatch, tmp_path):
    # Ensure a fresh streamlit session_state and harmless toast context
    import streamlit as st
    st.session_state.clear()
    monkeypatch.setattr(st, "toast", lambda *a, **k: DummyToast())
    # Run tests inside a temporary repo-like root so writes go to a fresh 'Statistics'
    repo_root = tmp_path
    stats = repo_root / "Statistics"
    stats.mkdir()
    # Patch file paths used in the module (it writes to 'Statistics/log_file.txt')
    monkeypatch.chdir(repo_root)
    yield


def make_cv_par_obj():
    # Minimal set of keys expected by run_CV
    return {
        "freq": 1.0,
        "Vmin": -0.5,
        "Vmax": 0.5,
        "delV": 0.01,
        "Vstep": 0.1,
        "G_frac": 0.5,
        "tVGFile": "test.tVG",
        "tJFile": "test.tJ",
    }


def test_run_CV_tvg_failure(monkeypatch, tmp_path):
    # Simulate CV_exp.run_CV_simu returning result==1 (failed tVG creation)
    called = {}

    def fake_read_exp_parameters(CV_par, dev_par, keys, extract):
        called['read'] = (CV_par, dev_par, tuple(keys), tuple(extract))
        return make_cv_par_obj()

    monkeypatch.setattr(cv_func.utils_devpar_UI, 'read_exp_parameters', fake_read_exp_parameters)

    def fake_run_CV_simu(*args, **kwargs):
        return 1, "tVG generation failed"

    monkeypatch.setattr(cv_func.CV_exp, 'run_CV_simu', fake_run_CV_simu)

    # Spy on streamlit error call
    import streamlit as st
    errors = []
    monkeypatch.setattr(st, 'error', lambda msg: errors.append(msg))

    session = tmp_path / "session"
    session.mkdir()

    # Call function
    res = cv_func.run_CV("devA", str(session), {'devA': {}}, ['L1', 'L2'], 'id123', {}, 'CVPars.txt')

    # Should have recorded a streamlit error and produced a log entry
    assert errors and "tVG generation failed" in errors[0]

    log = (tmp_path / "Statistics" / "log_file.txt").read_text()
    assert 'id123 CV FAILED' in log


@pytest.mark.parametrize("result_code", [0, 95])
def test_run_CV_success_creates_files_and_sets_state(monkeypatch, tmp_path, result_code):
    cv_obj = make_cv_par_obj()

    def fake_read_exp_parameters(CV_par, dev_par, keys, extract):
        return cv_obj

    monkeypatch.setattr(cv_func.utils_devpar_UI, 'read_exp_parameters', fake_read_exp_parameters)

    # Return successful result code
    monkeypatch.setattr(cv_func.CV_exp, 'run_CV_simu', lambda *a, **k: (result_code, 'ok'))

    stored = {}

    def fake_store_file_names(dev_par, backend, zimt_device_parameters, layers):
        stored['args'] = (dev_par, backend, zimt_device_parameters, layers)

    monkeypatch.setattr(cv_func.utils_devpar_UI, 'store_file_names', fake_store_file_names)

    # Track streamlit success messages
    import streamlit as st
    successes = []
    monkeypatch.setattr(st, 'success', lambda msg: successes.append(msg))

    session = tmp_path / "session"
    session.mkdir()

    # Create an existing CVPars file; function should remove it and create new one
    cv_pars_file = session / 'CV_backup.txt'
    cv_pars_file.write_text('old=1')

    # Run CV
    res = cv_func.run_CV("devA", str(session), {'devA': {}}, ['L1', 'L2'], 'ID123', {}, 'CV_backup.txt')

    # Success path should call streamlit.success
    assert successes, "expected a success message"

    # Session state checks
    assert st.session_state['simulation_results'] == 'CV'
    assert st.session_state['expObject'] == cv_obj
    assert st.session_state['CVPars'] == 'CV_backup.txt'
    assert st.session_state['CapVolFile'] == 'CapVol.dat'
    assert st.session_state['runSimulation'] is True

    # store_file_names should have been called with expected args
    assert stored['args'][1] == 'zimt' and stored['args'][2] == 'devA'

    # The CV parameters file should exist and contain the cv_obj keys
    written = (session / 'CV_backup.txt').read_text()
    for key in cv_obj:
        assert f"{key} = {cv_obj[key]}" in written

    # Log file should record success
    log = (tmp_path / "Statistics" / "log_file.txt").read_text()
    assert 'ID123 CV SUCCESS' in log


def test_run_CV_removes_existing_file(monkeypatch, tmp_path):
    """Ensure that when a CV parameters file already exists it gets removed in the success path."""
    cv_obj = make_cv_par_obj()
    monkeypatch.setattr(cv_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: cv_obj)
    monkeypatch.setattr(cv_func.CV_exp, 'run_CV_simu', lambda *a, **k: (0, 'ok'))

    import streamlit as st
    monkeypatch.setattr(st, 'success', lambda msg: None)

    session = tmp_path / "session"
    session.mkdir()

    cv_pars_file = session / 'CV_backup.txt'
    cv_pars_file.write_text('old=1')

    removed = []
    # Patch the os.remove used inside the module under test
    monkeypatch.setattr(cv_func.os, 'remove', lambda path: removed.append(path))
    # Prevent internals from trying to read real device parameter structure
    monkeypatch.setattr(cv_func.utils_devpar_UI, 'store_file_names', lambda *a, **k: None)

    cv_func.run_CV("devA", str(session), {'devA': {}}, ['L1', 'L2'], 'ID-REMOVE', {}, 'CV_backup.txt')

    assert removed and str(cv_pars_file) in removed


def test_run_CV_other_error_logs(monkeypatch, tmp_path):
    # Simulate some non-1, non-0/95 error
    monkeypatch.setattr(cv_func.utils_devpar_UI, 'read_exp_parameters', lambda *a, **k: make_cv_par_obj())
    monkeypatch.setattr(cv_func.CV_exp, 'run_CV_simu', lambda *a, **k: (2, 'Sim failed'))

    import streamlit as st
    errors = []
    monkeypatch.setattr(st, 'error', lambda msg: errors.append(msg))

    session = tmp_path / "session"
    session.mkdir()

    cv_func.run_CV("devB", str(session), {'devB': {}}, ['L1'], 'ID-ERROR', {}, 'CVPars.txt')

    # Should have recorded an error and log should show ERROR
    assert errors and 'Sim failed' in errors[0]
    log = (tmp_path / "Statistics" / "log_file.txt").read_text()
    assert 'ID-ERROR CV ERROR' in log
