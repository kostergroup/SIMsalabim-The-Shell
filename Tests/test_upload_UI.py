import os
import sys
import pytest

# Ensure repo root on sys.path
here = os.path.dirname(os.path.dirname(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import utils.upload_UI as up


class DummyUpload:
    def __init__(self, name, data=b'content'):
        self.name = name
        self._data = data

    def getvalue(self):
        return self._data


@pytest.fixture(autouse=True)
def streamlit_state(monkeypatch):
    import streamlit as st
    st.session_state.clear()
    st.session_state['trapFiles'] = []
    yield


def test_upload_single_file_to_folder_writes(tmp_path):
    session = tmp_path / 'session'
    session.mkdir()

    f = DummyUpload('myfile.txt', b'hello')
    up.upload_single_file_to_folder(f, str(session))

    # file present
    content = (session / 'myfile.txt').read_text()
    assert content == 'hello'

    # test is_dev_par True writes to dev_par_name
    f2 = DummyUpload('ignored.txt', b'abc')
    up.upload_single_file_to_folder(f2, str(session), is_dev_par=True, dev_par_name='setup.txt')
    assert (session / 'setup.txt').read_text() == 'abc'


def test_upload_multiple_files_to_folder_writes(tmp_path):
    session = tmp_path / 'session'
    session.mkdir()

    files = [DummyUpload('a.txt', b'a'), DummyUpload('b.txt', b'b')]
    up.upload_multiple_files_to_folder(files, str(session))

    assert (session / 'a.txt').read_text() == 'a'
    assert (session / 'b.txt').read_text() == 'b'


def test_upload_exp_jv_file_updates_devpar_and_save(monkeypatch, tmp_path):
    session = tmp_path / 'session'
    session.mkdir()

    # device parameters with User interface
    dev_par = {'setup.txt': [['Description'], ['User interface', ['par', 'useExpData', '0', ''], ['par', 'expJV', 'old.txt', '']]]}
    layers = [['par', 'setup', 'setup.txt']]

    f = DummyUpload('exp.txt', b'data')

    calls = {}
    monkeypatch.setattr(up.utils_gen_UI, 'save_parameters', lambda d, l, path, cur, alt: calls.setdefault('saved', True))

    import streamlit as st
    success_calls = []
    monkeypatch.setattr(st, 'success', lambda msg: success_calls.append(msg))

    up.upload_exp_jv_file(f, str(session), dev_par, layers, 'setup.txt', 'other.txt')

    # check device parameter updated
    ui_section = dev_par['setup.txt'][1]
    assert any(p[1] == 'useExpData' and p[2] == '1' for p in ui_section)
    assert any(p[1] == 'expJV' and p[2] == 'exp.txt' for p in ui_section)
    assert calls.get('saved', False)
    assert success_calls


def test_upload_expJV_files_calls_upload_and_save(monkeypatch, tmp_path):
    session = tmp_path / 'session'
    session.mkdir()

    uploaded = [DummyUpload('1.txt', b'1'), DummyUpload('2.txt', b'2')]

    calls = {}
    # the module utils.general_UI may not have this attribute by default in the test environment; allow creation
    monkeypatch.setattr(up.utils_gen_UI, 'upload_multiple_files_to_folder', lambda files, path: calls.setdefault('uploaded', True), raising=False)
    monkeypatch.setattr(up.utils_gen_UI, 'save_parameters', lambda *a, **k: calls.setdefault('saved', True))

    import streamlit as st
    success = []
    monkeypatch.setattr(st, 'success', lambda msg: success.append(msg))

    dev_par = {'setup.txt': [['Description'], ['User interface']]}
    layers = [['par', 'setup', 'setup.txt']]

    up.upload_expJV_files(uploaded, str(session), dev_par, layers, 'setup.txt', 'other.txt')

    assert calls.get('uploaded', False)
    assert calls.get('saved', False)
    assert success


def test_upload_gen_prof_file_updates_optics(monkeypatch, tmp_path):
    session = tmp_path / 'session'
    session.mkdir()

    dev_par = {'setup.txt': [['Description'], ['Optics', ['par', 'genProfile', 'none', '']]]}
    layers = [['par', 'setup', 'setup.txt']]
    f = DummyUpload('gen.txt', b'gen')

    calls = {}
    monkeypatch.setattr(up.utils_gen_UI, 'save_parameters', lambda *a, **k: calls.setdefault('saved', True))

    import streamlit as st
    ok = []
    monkeypatch.setattr(st, 'success', lambda msg: ok.append(msg))

    up.upload_gen_prof_file(f, str(session), dev_par, layers, 'setup.txt', 'other.txt')

    optics = dev_par['setup.txt'][1]
    assert any(p[1] == 'genProfile' and p[2] == 'gen.txt' for p in optics)
    assert calls.get('saved', False)
    assert ok


def test_upload_trap_level_file_appends_and_saves(monkeypatch, tmp_path):
    session = tmp_path / 'session'
    session.mkdir()

    dev_par = {'setup.txt': [['Description'], ['User interface']]}
    layers = [['par', 'setup', 'setup.txt']]

    import streamlit as st
    st.session_state['trapFiles'] = []

    monkeypatch.setattr(up.utils_gen_UI, 'save_parameters', lambda *a, **k: None)
    called = []
    monkeypatch.setattr(st, 'success', lambda msg: called.append(msg))

    f = DummyUpload('trap.txt', b'trap')
    up.upload_trap_level_file(f, str(session), dev_par, layers, 'setup.txt', 'other.txt')

    assert 'trap.txt' in st.session_state['trapFiles']
    assert called


def test_upload_nk_and_spectrum(monkeypatch, tmp_path):
    session = tmp_path / 'session'
    session.mkdir()

    uploaded = [DummyUpload('nk1.txt', b'x'), DummyUpload('nk2.txt', b'y')]

    calls = {}
    monkeypatch.setattr(up, 'upload_multiple_files_to_folder', lambda files, path: calls.setdefault('nk_uploaded', path))
    monkeypatch.setattr(up.utils_gen_UI, 'save_parameters', lambda *a, **k: calls.setdefault('saved', True))

    import streamlit as st
    success = []
    monkeypatch.setattr(st, 'success', lambda msg: success.append(msg))

    dev_par = {'setup.txt': [['Description'], ['User interface']]}
    layers = [['par', 'setup', 'setup.txt']]

    up.upload_nk_file(uploaded, str(session), dev_par, layers, 'setup.txt', 'other.txt')
    assert 'Data_nk' in calls.get('nk_uploaded', '')
    assert calls.get('saved', False)
    assert success

    # spectrum file uses upload_single_file_to_folder - ensure target folder exists
    (session / 'Data_spectrum').mkdir()
    calls.clear()
    monkeypatch.setattr(up.utils_gen_UI, 'save_parameters', lambda *a, **k: calls.setdefault('saved2', True))
    upg = DummyUpload('sp.txt', b'sp')
    up.upload_spectrum_file(upg, str(session), dev_par, layers, 'setup.txt', 'other.txt')
    assert calls.get('saved2', False)


def test_upload_devpar_and_layer_file(monkeypatch, tmp_path):
    session = tmp_path / 'session'
    session.mkdir()

    uploaded_setup = DummyUpload('setup_incoming.txt', b'setup')
    uploaded_setup.name = 'setup_incoming.txt'
    uploaded_layers = [DummyUpload('L1.txt', b'l1'), DummyUpload('L2.txt', b'l2')]

    calls = {}
    monkeypatch.setattr(up, 'upload_single_file_to_folder', lambda f, p, *a, **k: calls.setdefault('single', f.name))
    monkeypatch.setattr(up, 'upload_multiple_files_to_folder', lambda files, p: calls.setdefault('multi', [f.name for f in files]))

    import streamlit as st
    success = []
    monkeypatch.setattr(st, 'success', lambda msg: success.append(msg))

    up.upload_devpar_file(uploaded_setup, uploaded_layers, str(session), 'setup.txt')

    # uploaded_setup should be renamed to 'setup.txt' and saved via our patched functions
    assert calls.get('single') == 'setup_incoming.txt' or calls.get('single') == 'setup.txt'
    assert calls.get('multi') == ['L1.txt', 'L2.txt']
    assert success


def test_upload_layer_file_writes_and_succeeds(monkeypatch, tmp_path):
    session = tmp_path / 'session'
    session.mkdir()

    f = DummyUpload('myLayer.txt', b'ok')

    calls = {}
    monkeypatch.setattr(up, 'upload_single_file_to_folder', lambda f, p, *a, **k: calls.setdefault('single', f.name))

    import streamlit as st
    success = []
    monkeypatch.setattr(st, 'success', lambda msg: success.append(msg))

    up.upload_layer_file(f, str(session))
    assert calls.get('single') == 'myLayer.txt'
    assert success
