import os
import sys
import zipfile
from types import SimpleNamespace
import pytest

# Ensure repo root on sys.path so top-level imports work
here = os.path.dirname(os.path.dirname(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import utils.general_UI as gen


class DummyUpload:
    def __init__(self, name, data: bytes):
        self.name = name
        self._data = data

    def getvalue(self):
        return self._data


@pytest.fixture(autouse=True)
def streamlit_fixture(monkeypatch):
    import streamlit as st
    # clear state and provide defaults
    st.session_state.clear()
    st.session_state['availableLayerFiles'] = ['a', 'b', 'c']
    # track messages
    monkeypatch.setattr(st, 'error', lambda *a, **k: None)
    monkeypatch.setattr(st, 'warning', lambda *a, **k: None)
    monkeypatch.setattr(st, 'markdown', lambda *a, **k: None)
    monkeypatch.setattr(st, 'file_uploader', lambda *a, **k: None)
    monkeypatch.setattr(st, 'toast', lambda *a, **k: None)
    yield


def test_local_css_reads_and_calls_markdown(tmp_path, monkeypatch):
    css_file = tmp_path / 'style.css'
    css_file.write_text('body { color: red; }')

    calls = {}
    import streamlit as st
    monkeypatch.setattr(st, 'markdown', lambda txt, **k: calls.setdefault('sent', txt))

    gen.local_css(str(css_file))
    assert 'body { color: red; }' in calls['sent']


def test_upload_file_none_returns_none(monkeypatch):
    import streamlit as st
    monkeypatch.setattr(st, 'file_uploader', lambda *a, **k: None)
    # no uploader -> None
    res = gen.upload_file('desc', [], '', '')
    assert res is None


def test_upload_file_illegal_chars(monkeypatch):
    import streamlit as st
    data = b'good\nbadXline'
    monkeypatch.setattr(st, 'file_uploader', lambda *a, **k: DummyUpload('f.txt', data))
    errors = []
    monkeypatch.setattr(st, 'error', lambda msg: errors.append(msg))

    res = gen.upload_file('desc', ['X'], '', '')
    assert res is False
    assert errors and 'Illegal characters' in errors[0]


def test_upload_file_pattern_mismatch(monkeypatch):
    import streamlit as st
    # give content where second line doesn't match pattern r'^\d+$'
    data = b'header\n123\nabc'
    monkeypatch.setattr(st, 'file_uploader', lambda *a, **k: DummyUpload('p.txt', data))
    errors = []
    monkeypatch.setattr(st, 'error', lambda msg: errors.append(msg))

    res = gen.upload_file('desc', [], r'^\d+$', '')
    assert res is False
    assert errors and 'File content does not meet the required pattern' in errors[0]


def test_upload_file_filename_too_long(monkeypatch):
    import streamlit as st
    name = 'a' * 60 + '.txt'
    monkeypatch.setattr(st, 'file_uploader', lambda *a, **k: DummyUpload(name, b'header\n123'))
    errors = []
    monkeypatch.setattr(st, 'error', lambda msg: errors.append(msg))

    res = gen.upload_file('desc', [], r'^\w+$', '')
    assert res is False
    assert errors and 'Filename is too long' in errors[0]


def test_upload_file_devpar_verify_failures(monkeypatch):
    import streamlit as st
    data = b'header\n123'
    monkeypatch.setattr(st, 'file_uploader', lambda *a, **k: DummyUpload('dev.txt', data))

    # simulate verify_devpar_file returning 1 -> error
    monkeypatch.setattr(gen, 'utils_devpar', SimpleNamespace(verify_devpar_file=lambda d, t, a, s: (1, 'wrong')))
    errors = []
    monkeypatch.setattr(st, 'error', lambda m: errors.append(m))

    res = gen.upload_file('desc', [], r'^\w+$', check_devpar='simss')
    assert res is False
    assert errors

    # simulate verify returns 2 and missing files list -> warning and return uploaded_file
    monkeypatch.setattr(gen, 'utils_devpar', SimpleNamespace(verify_devpar_file=lambda d, t, a, s: (2, ['nk1', 'spec1'])))
    warnings = []
    monkeypatch.setattr(st, 'warning', lambda m: warnings.append(m))

    out = gen.upload_file('desc', [], r'^\w+$', check_devpar='zimt')
    assert isinstance(out, DummyUpload)
    assert warnings


def test_prepare_results_download_basic_and_calc(monkeypatch, tmp_path):
    # Setup a fake session folder with files referenced by session_state
    session = tmp_path / 'session'
    session.mkdir()
    sims = tmp_path / 'Simulations'
    sims.mkdir()

    import streamlit as st
    # populate state
    st.session_state.update({
        'varFile': 'a.txt',
        'logFile': 'b.txt',
        'traps_bulk': ['t1.txt'],
        'traps_int': ['t2.txt'],
        'LayersFiles': ['L1.txt'],
        'genProfile': 'none',
        'opticsFiles': [],
        'zimt_devpar_file': 'dev.txt',
        'tJFile': 'tj.txt',
        'tVGFile': 'tvg.txt'
    })

    # create those files
    for fname in ['a.txt', 'b.txt', 't1.txt', 't2.txt', 'L1.txt', 'dev.txt', 'tj.txt', 'tvg.txt']:
        (session / fname).write_text(fname)

    # patch create_summary_and_cite
    called = {}
    monkeypatch.setattr(gen.utils_sum, 'create_summary_and_cite', lambda folder, flag: called.update({'flag': flag}))

    # ensure operations happen in tmp_path as prepare_results_download writes the zip into the cwd
    monkeypatch.chdir(tmp_path)
    # call prepare_results_download for zimt and CV exp_type
    gen.prepare_results_download(str(session), 'ID1', 'zimt', 'CV')

    # archive should be in Simulations
    zipname = tmp_path / 'Simulations' / 'simulation_results_ID1.zip'
    assert zipname.exists()
    assert called.get('flag') is False

    # Now test genProfile == 'calc' copies Data_nk/Data_spectrum files and calls summary True
    st.session_state['genProfile'] = 'calc'
    # prepare subdirs and files
    dn = session / 'Data_nk'
    ds = session / 'Data_spectrum'
    dn.mkdir(); ds.mkdir()
    (dn / 'nk1.txt').write_text('nk'); (ds / 'sp1.txt').write_text('sp')
    # include these in opticsFiles
    st.session_state['opticsFiles'] = ['Data_nk/nk1.txt', 'Data_spectrum/sp1.txt']

    gen.prepare_results_download(str(session), 'ID2', 'zimt', 'IMPS')
    assert (tmp_path / 'Simulations' / 'simulation_results_ID2.zip').exists()
    assert called.get('flag') is True


def test_prepare_results_download_invalid_inputs(monkeypatch, tmp_path):
    session = tmp_path / 'session'
    session.mkdir()
    import streamlit as st
    errors = []
    monkeypatch.setattr(st, 'error', lambda m: errors.append(m))

    gen.prepare_results_download(str(session), 'ID', 'wrong', 'CV')
    assert errors and 'Wrong simulation type' in errors[0]

    errors.clear()
    gen.prepare_results_download(str(session), 'ID', 'zimt', 'WRONG')
    assert errors and 'Wrong experiment type' in errors[0]


def test_exchangeDevPar_invokes_run(monkeypatch, tmp_path):
    # simulate subprocess.run
    class R:
        def __init__(self, rc):
            self.returncode = rc

    monkeypatch.setattr(gen, 'run', lambda *a, **k: R(7))
    rc = gen.exchangeDevPar(str(tmp_path), 'src.txt', 'tgt.txt')
    assert rc == 7


def test_create_zip_creates_archive(tmp_path):
    session = tmp_path / 'session'
    session.mkdir()

    # create files and layers with duplicates
    (session / 'A.txt').write_text('a')
    (session / 'B.txt').write_text('b')
    layers = [['par', 'l0', 'A.txt'], ['par', 'l1', 'B.txt'], ['par', 'l2', 'A.txt']]

    zipfile_path = gen.create_zip(str(session), layers)
    assert os.path.isfile(zipfile_path)
    # inspect contents
    with zipfile.ZipFile(zipfile_path) as z:
        names = z.namelist()
    assert 'Device_parameters/A.txt' in names and 'Device_parameters/B.txt' in names


def test_safe_index_behaviour():
    options = ['a', 'b', '../c', '/path/d']
    assert gen.safe_index('a', options) == 0
    assert gen.safe_index('../c', options) == 2
    assert gen.safe_index('/path/d', options) == 3
    # basename match
    assert gen.safe_index('d', options) == 3
    # not found -> default
    assert gen.safe_index('x', options, default=9) == 9


def test_save_parameters_writes_and_exchange_and_toast(monkeypatch, tmp_path):
    session = tmp_path / 'session'
    session.mkdir()
    # set available layer files
    import streamlit as st
    st.session_state['availableLayerFiles'] = ['one.txt']

    called = {}
    monkeypatch.setattr(gen.utils_devpar_UI, 'write_pars_txt', lambda *a, **k: called.setdefault('written', True))

    # exchangeDevPar should be called when exchange_target set; simulate raising and not raising
    monkeypatch.setattr(gen, 'exchangeDevPar', lambda *a, **k: 0)

    # track toast called
    toasts = []
    monkeypatch.setattr(st, 'toast', lambda *a, **k: toasts.append(True))

    # Call with exchange_target
    gen.save_parameters({'a':1}, [['par','l','one.txt']], str(session), 'setup.txt', exchange_target='other.txt', show_toast=True)
    assert called.get('written', False)
    assert toasts

    # Simulate exchange throwing
    monkeypatch.setattr(gen, 'exchangeDevPar', lambda *a, **k: (_ for _ in ()).throw(Exception('boom')))
    # Should swallow exception
    gen.save_parameters({'a':1}, [['par','l','one.txt']], str(session), 'setup.txt', exchange_target='other.txt', show_toast=False)


def test_format_func():
    assert gen.format_func('/path/to/foo.txt') == 'foo.txt'


def test_prepare_results_calls_and_resets(monkeypatch):
    called = {}
    monkeypatch.setattr(gen, 'prepare_results_download', lambda *a, **k: called.setdefault('prep', True))

    import streamlit as st
    st.session_state['runSimulation'] = True

    gen.prepare_results('/some', 'ID', 'zimt', 'CV')
    assert called.get('prep', False)
    assert st.session_state['runSimulation'] is False
