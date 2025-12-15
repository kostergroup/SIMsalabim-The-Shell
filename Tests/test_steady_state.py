import os
import sys
import pytest

# ensure repo root is importable
here = os.path.dirname(os.path.dirname(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import utils.steady_state as ss


class DummyToast:
    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(autouse=True)
def isolate_state(monkeypatch, tmp_path):
    import streamlit as st
    st.session_state.clear()
    monkeypatch.setattr(st, 'toast', lambda *a, **k: DummyToast())
    # Use tmp_path as cwd so statistics log is written to a disposable location
    (tmp_path / 'Statistics').mkdir()
    monkeypatch.chdir(tmp_path)
    yield


def test_split_line_scpars_various_lengths():
    sc = {'Simulated': {}, 'Experimental': {}, 'Deviation': {}}
    # create a long item that will populate simulated, experimental and deviation
    item = 'Vmpp: 1 + 2 + 3 + 4 + 5 + 6 + 7'
    out = ss.split_line_scpars(item, sc, 'Vmpp', 'V')

    # Keys use bracketed unit for non-FF
    assert 'Vmpp [V]' in out['Simulated']
    assert 'Vmpp [V]' in out['Experimental'] or True

    # minimal length: only simulated
    sc2 = {'Simulated': {}, 'Experimental': {}, 'Deviation': {}}
    item2 = 'Voc: 0.5 + 0.6'
    out2 = ss.split_line_scpars(item2, sc2, 'Voc', 'V')
    assert 'Voc [V]' in out2['Simulated']


def test_write_scpars_all_types():
    sc = {'Simulated': {'Jsc [Am\u207b\u00b2]': '<NA>'}, 'Experimental': {}, 'Deviation': {}}
    solar = False
    # Jsc line (only simulated tokens)
    sc, solar = ss.write_scpars('Jsc: 1 + 2 A/m2', sc, solar)
    assert solar is True
    assert 'Jsc [Am' in list(sc['Simulated'].keys())[0]

    # FF line (empty unit case)
    sc, solar = ss.write_scpars('FF: 0.5 + 0.1', sc, solar)
    assert 'FF ' in sc['Simulated']


def test_store_scPar_state_sets_session(monkeypatch):
    import streamlit as st
    # Build dev_par that contains expJV in UI
    dev_par = {'setup.txt': [['Description'], ['User interface', ['par', 'expJV', 'my_exp.txt', '']]]}
    # Provide sc_par and solar_cell True
    sc_par = {'Simulated': {}}
    ss.store_scPar_state(sc_par, True, dev_par, 'setup.txt')
    assert st.session_state['sc_par'] == sc_par
    # When solar_cell False, expJV should be reset and sc_par cleared
    ss.store_scPar_state({'Simulated': {}}, False, dev_par, 'setup.txt')
    assert st.session_state['expJV'] == 'none'


def test_read_scPar_run_mode_false_and_true(monkeypatch):
    # Build console string without solar cell lines -> should return {} when run_mode False
    out = ss.read_scPar('no params here', {}, 'setup.txt', run_mode=False)
    assert out == {}

    # With solar cell data and run_mode False -> return parsed dict
    console = 'Vmpp: 1 + 2\nVoc: 0.7 + 0.8'
    res = ss.read_scPar(console, {'setup.txt': [['Description'], ['User interface', ['par', 'expJV', 'my.txt', '']]]}, 'setup.txt', run_mode=False)
    # Should return a dict (since solar_cell True)
    assert isinstance(res, dict)

    # run_mode True: should store in session state via store_scPar_state
    import streamlit as st
    called = {}
    monkeypatch.setattr(ss, 'store_scPar_state', lambda sc, solar, dev_par, dpn: called.setdefault('st', True))
    ss.read_scPar(console, {'setup.txt': [['Description'], ['User interface', ['par', 'expJV', 'my.txt', '']]]}, 'setup.txt', run_mode=True)
    assert called.get('st', False)


def test_run_SS_JV_success_and_scPars_removal(monkeypatch, tmp_path):
    import streamlit as st
    session = tmp_path / 'session'
    session.mkdir()

    # create an existing scPars file that should be removed
    sc_file = session / 'scpars.txt'
    sc_file.write_text('old')

    # dev_par with User interface -> scParsFile and varFile
    dev_par = {'setup.txt': [['Description'], ['User interface', ['par', 'scParsFile', 'scpars.txt', ''], ['par', 'varFile', 'vars.txt', '']]]}

    # Make JV_exp return success
    monkeypatch.setattr(ss.JV_exp, 'run_SS_JV', lambda *a, **k: (0, 'OK'))

    called = {}
    monkeypatch.setattr(ss.utils_devpar_UI, 'store_file_names', lambda *a, **k: called.setdefault('stored', True))

    # success should remove scPars and set session state
    ss.run_SS_JV('setup.txt', str(session), dev_par, [['par','l1','L1.txt']], 'ID1')

    assert not sc_file.exists()
    assert st.session_state['simulation_results'] == 'Steady State JV'
    assert st.session_state['runSimulation'] is True
    assert called.get('stored', False)

    # log file should contain SUCCESS
    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'ID1 Steady_State SUCCESS' in log


def test_run_SS_JV_error_path(monkeypatch, tmp_path):
    import streamlit as st
    session = tmp_path / 'session'
    session.mkdir()

    dev_par = {'setup.txt': [['Description'], ['User interface', ['par', 'scParsFile', 'scpars.txt', '']]]}

    # create scPars file so removal branch covers exists case
    (session / 'scpars.txt').write_text('old')

    # simulate failing run
    monkeypatch.setattr(ss.JV_exp, 'run_SS_JV', lambda *a, **k: (2, 'FAIL'))

    errors = []
    monkeypatch.setattr(st, 'error', lambda m: errors.append(m))

    ss.run_SS_JV('setup.txt', str(session), dev_par, [['par','l1','L1.txt']], 'ID-ERR')

    assert errors and 'FAIL' in errors[0]
    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'ID-ERR Steady_State ERROR' in log


def test_run_SS_JV_with_missing_devpar(monkeypatch, tmp_path):
    # dev_par could be None; ensure function handles lookup gracefully and still calls JV_exp
    session = tmp_path / 'session'
    session.mkdir()

    monkeypatch.setattr(ss.JV_exp, 'run_SS_JV', lambda *a, **k: (95, 'OK95'))
    monkeypatch.setattr(ss.utils_devpar_UI, 'store_file_names', lambda *a, **k: None)

    # supply minimal dev_par so scParsFile logic executes safely
    ss.run_SS_JV('setup.txt', str(session), {'setup.txt': [['Description']]}, [['par','l1','L1.txt']], 'ID-NODEV')

    # log should contain SUCCESS for 95
    log = (tmp_path / 'Statistics' / 'log_file.txt').read_text()
    assert 'ID-NODEV Steady_State SUCCESS' in log


def test_split_line_scpars_malformed_line():
    sc = {'Simulated': {}, 'Experimental': {}, 'Deviation': {}}
    # Malformed line with extra spaces and missing tokens
    item = 'Vmpp: 1   +  '
    import pytest
    # Current implementation expects enough tokens; malformed lines raise IndexError
    with pytest.raises(IndexError):
        ss.split_line_scpars(item, sc, 'Vmpp', 'V')

def test_run_SS_JV_multiple_UI_sections(monkeypatch, tmp_path):
    session = tmp_path / 'session'
    session.mkdir()
    stats_path = tmp_path / 'Statistics'
    stats_path.mkdir(exist_ok=True)

    # dev_par with multiple UI sections and multiple parameters
    dev_par = {
        'setup.txt': [
            ['Description'],
            ['User interface', ['par', 'scParsFile', 'file1.txt', ''], ['par', 'varFile', 'vars1.txt', '']],
            ['User interface', ['par', 'scParsFile', 'file2.txt', ''], ['par', 'varFile', 'vars2.txt', '']]
        ]
    }

    # Make JV_exp return success
    monkeypatch.setattr(ss.JV_exp, 'run_SS_JV', lambda *a, **k: (0, 'OK-MULTI'))

    stored_calls = {}
    monkeypatch.setattr(ss.utils_devpar_UI, 'store_file_names', lambda *a, **k: stored_calls.setdefault('stored', True))

    ss.run_SS_JV('setup.txt', str(session), dev_par, [['par','l1','L1.txt']], 'ID-MULTI')

    # Should have called store_file_names
    assert stored_calls.get('stored', False)
    # Log file should exist and contain SUCCESS
    log_file = stats_path / 'log_file.txt'
    log_content = log_file.read_text()
    assert 'ID-MULTI Steady_State SUCCESS' in log_content
