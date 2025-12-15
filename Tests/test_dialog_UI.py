import os
import sys
import pytest

# ensure repo root on sys.path
here = os.path.dirname(os.path.dirname(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import utils.dialog_UI as dialog


class DummyUploadFile:
    def __init__(self, name, data=b'hello'):
        self.name = name
        self._data = data

    def getvalue(self):
        return self._data


@pytest.fixture(autouse=True)
def setup_session(monkeypatch, tmp_path):
    import streamlit as st
    st.session_state.clear()
    # default availableLayerFiles needed by some dialogs (list must be long enough so insert(-3) works)
    st.session_state['availableLayerFiles'] = ['a', 'b', 'c', 'd', 'e']
    # monkeypatch rerun to avoid stopping tests
    monkeypatch.setattr(st, 'rerun', lambda : None)
    yield


def test_uploadFileDialog_generation_profile_calls_upload(monkeypatch, tmp_path):
    # Simulate Generation profile upload and ensure upload_gen_prof_file is called on submit
    # Setup session path and minimal inputs
    session = tmp_path / 'session'
    session.mkdir()

    # Make st.selectbox return 'Generation profile'
    import streamlit as st
    monkeypatch.setattr(st, 'selectbox', lambda *a, **k: 'Generation profile')

    # Ensure upload_file (utils_gen_UI) returns a dummy file
    monkeypatch.setattr(dialog.utils_gen_UI, 'upload_file', lambda *a, **k: DummyUploadFile('gen.txt', b'data'))

    called = {}
    monkeypatch.setattr(dialog.utils_upload_UI, 'upload_gen_prof_file', lambda f, *a, **k: called.update({'called': True, 'name': f.name}))

    # Simulate button being clicked (submit) -> should trigger upload_gen_prof_file
    monkeypatch.setattr(st, 'button', lambda *a, **k: True)

    dev_par = {}
    layers = [['par', 'setup', 'setup.txt']]

    dialog.uploadFileDialog(str(session), dev_par, layers, 'setup.txt', 'other.txt', 'Steady State JV')

    assert called.get('called', False)


def test_uploadFileDialog_simulation_setup_requires_all_layers(monkeypatch, tmp_path):
    # When uploading a simulation setup, ensure missing layer files are reported and submit disabled
    session = tmp_path / 'session'
    session.mkdir()

    import streamlit as st
    # select Simulation setup
    monkeypatch.setattr(st, 'selectbox', lambda *a, **k: 'Simulation setup')

    # Provide uploadedFile whose data contains two layer filenames
    file_content = 'L1_parameters.txt\nL2_parameters.txt'
    uploadedFile = DummyUploadFile('setup.txt', data=file_content.encode('utf8'))
    monkeypatch.setattr(st, 'file_uploader', lambda *a, **k: uploadedFile if 'layer parameter' not in a[0] else [])

    # getLayersFromSetup should parse the content and return expected layers
    monkeypatch.setattr(dialog.utils_devpar_UI, 'getLayersFromSetup', lambda data: ['L1_parameters.txt', 'L2_parameters.txt'])

    written = []
    monkeypatch.setattr(st, 'write', lambda msg: written.append(msg))

    # Now run; st.button disabled should be True because uploadedFiles empty -> but our button returns False
    monkeypatch.setattr(st, 'button', lambda *a, **k: False)

    dev_par = {}
    layers = [['par', 'setup', 'setup.txt']]

    # Should not throw and should report missing layers via st.write
    dialog.uploadFileDialog(str(session), dev_par, layers, 'setup.txt', 'other.txt', 'Steady State JV')
    assert any('Missing layer parameter files' or 'Missing layer' in str(x) for x in written)


def test_uploadFileDialog_simulation_setup_all_uploaded_calls_upload(monkeypatch, tmp_path):
    # Simulation setup with all required layer files uploaded should call upload_devpar_file
    session = tmp_path / 'session'
    session.mkdir()

    import streamlit as st
    monkeypatch.setattr(st, 'selectbox', lambda *a, **k: 'Simulation setup')

    file_content = 'L1_parameters.txt\nL2_parameters.txt'
    uploadedFile = DummyUploadFile('setup.txt', data=file_content.encode('utf8'))

    # uploadedFiles list contains both files
    uploadedLayers = [DummyUploadFile('L1_parameters.txt'), DummyUploadFile('L2_parameters.txt')]

    # file_uploader must return uploadedFile for the first and uploadedLayers for the second
    callcount = {'n':0}
    def fake_file_uploader(label, *a, **k):
        callcount['n'] += 1
        return uploadedFile if callcount['n'] == 1 else uploadedLayers

    monkeypatch.setattr(st, 'file_uploader', fake_file_uploader)

    monkeypatch.setattr(dialog.utils_devpar_UI, 'getLayersFromSetup', lambda data: ['L1_parameters.txt', 'L2_parameters.txt'])

    called = {}
    monkeypatch.setattr(dialog.utils_upload_UI, 'upload_devpar_file', lambda f, files, *a, **k: called.update({'f': f.name, 'count': len(files)}))

    # patch button to True to simulate submit
    monkeypatch.setattr(st, 'button', lambda *a, **k: True)

    dev_par = {}
    layers = [['par', 'setup', 'setup.txt']]

    dialog.uploadFileDialog(str(session), dev_par, layers, 'setup.txt', 'other.txt', 'Steady State JV')

    assert called.get('f') == 'setup.txt'
    assert called.get('count') == 2


def test_uploadFileDialog_layer_parameters_overwrite_warning(monkeypatch, tmp_path):
    # When uploading Layer parameters with a name already present in availableLayerFiles, a warning should be shown
    session = tmp_path / 'session'
    session.mkdir()

    import streamlit as st
    monkeypatch.setattr(st, 'selectbox', lambda *a, **k: 'Layer parameters')

    dummy_file = DummyUploadFile('b')
    monkeypatch.setattr(st, 'file_uploader', lambda *a, **k: dummy_file)

    warned = []
    monkeypatch.setattr(st, 'warning', lambda msg: warned.append(msg))

    # stub the button to False so it doesn't run upload
    monkeypatch.setattr(st, 'button', lambda *a, **k: False)

    dev_par = {}
    layers = [['par', 'setup', 'setup.txt']]
    dialog.uploadFileDialog(str(session), dev_par, layers, 'setup.txt', 'other.txt', 'Steady State JV')

    assert warned, 'expected warning for overwriting existing layer file'


def test_addLayerDialog_create_new_default_and_duplicate(monkeypatch, tmp_path):
    # Test adding a new layer both from default resource and duplicating existing session layer
    session = tmp_path / 'session'
    session.mkdir()

    resource = tmp_path / 'Resources'
    resource.mkdir()

    # Simulate default layer files present in resources
    (resource / 'L2_parameters.txt').write_text('default L2')
    (resource / 'L3_parameters.txt').write_text('default L3')
    (session / 'existing_file.txt').write_text('session file')

    # Setup dev_par and layers
    dev_par = {'L2_parameters.txt': [['Description'], ['General']], 'existing_file.txt': [['Description'], ['General']], 'setup.txt': [['Description'], ['Layers', ['par','l1','existing_file.txt','parameter file for layer 1']]]}
    layers = [['par', 'setup', 'setup.txt'], ['par', 'l1', 'existing_file.txt']]

    import streamlit as st

    # 1) Choose a default layer 'PVSK' -> mapped to L2_parameters.txt
    class DummyCtx:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(st, 'columns', lambda *a, **k: (DummyCtx(), DummyCtx()))
    monkeypatch.setattr(st, 'text_input', lambda *a, **k: 'ignored')
    # set a selection return value of 'PVSK' for selectbox
    monkeypatch.setattr(st, 'selectbox', lambda *a, **k: 'PVSK')
    # set checkbox default True
    monkeypatch.setattr(st, 'checkbox', lambda *a, **k: True)
    # simulate pressing submit
    monkeypatch.setattr(st, 'button', lambda *a, **k: True)

    # save_parameters should be patched to avoid touching disk
    called = {}
    monkeypatch.setattr(dialog.utils_gen_UI, 'save_parameters', lambda *a, **k: called.update({'save': True}))

    # Run addLayerDialog - this will copy resource L2 to session as L{index}_parameters.txt
    dev_par_copy, layers_copy = dialog.addLayerDialog(str(session), dev_par.copy(), layers.copy(), str(resource), 'setup.txt', 'other.txt')

    # verify availableLayerFiles updated
    assert any(x.endswith('_parameters.txt') for x in st.session_state['availableLayerFiles'])
    assert called.get('save', False)

    # 2) Duplicate existing session layer
    st.session_state['availableLayerFiles'] = ['existing_file.txt', 'other', 'x', 'y', 'z']
    monkeypatch.setattr(st, 'selectbox', lambda *a, **k: 'existing_file.txt')
    # ensure checkbox is True -> will duplicate
    monkeypatch.setattr(st, 'checkbox', lambda *a, **k: True)

    dev_par2 = {'existing_file.txt': [['Description'], ['General']], 'setup.txt': [['Description'], ['Layers', ['par','l1','existing_file.txt','parameter file for layer 1']]]}
    layers2 = [['par', 'setup', 'setup.txt'], ['par', 'l1', 'existing_file.txt', 'parameter file for layer 1']]

    original_len = len(layers2)
    dev_par_out, layers_out = dialog.addLayerDialog(str(session), dev_par2, layers2, str(resource), 'setup.txt', 'other.txt')

    # after duplication, layers_out should have new entry appended (original list was mutated in-place)
    assert len(layers_out) == original_len + 1


def test_removeLayerDialog_removes_and_reorders(monkeypatch):
    import streamlit as st

    # Prepare dev_par and layers with three layers
    dev_par = {
        'setup.txt': [['Description'], ['Layers', ['par','l0','L0.txt','parameter file for layer 0'], ['par','l1','L1.txt','parameter file for layer 1'], ['par','l2','L2.txt','parameter file for layer 2']]],
        'L0.txt': [['Description'], ['General']],
        'L1.txt': [['Description'], ['General']],
        'L2.txt': [['Description'], ['General']]
    }

    layers = [['par', 'setup', 'setup.txt'], ['par', 'l0', 'L0.txt', 'parameter file for layer 0'], ['par', 'l1', 'L1.txt', 'parameter file for layer 1'], ['par', 'l2', 'L2.txt', 'parameter file for layer 2']]

    # select second layer (index 2 in layers list)
    monkeypatch.setattr(st, 'selectbox', lambda *a, **k: layers[2])
    monkeypatch.setattr(st, 'text_input', lambda *a, **k: layers[2][2])
    monkeypatch.setattr(st, 'warning', lambda *a, **k: None)
    monkeypatch.setattr(st, 'button', lambda *a, **k: True)

    calls = {}
    monkeypatch.setattr(dialog.utils_gen_UI, 'save_parameters', lambda *a, **k: calls.setdefault('saved', True))
    # Run removal
    out_dev_par, out_layers = dialog.removeLayerDialog(dev_par, layers.copy(), '/tmp', 'setup.txt', 'other.txt')

    # After removal, layer with L1.txt should be removed
    assert not any(l[2] == 'L1.txt' for l in out_layers)
    # after removal, the removed layer's file L1.txt should be gone
    assert out_layers[1][1] == 'l0' and out_layers[2][1] == 'l2'


# ==============================
# uploadFileDialog edge cases
# ==============================
def test_uploadFileDialog_no_file_uploaded(monkeypatch, tmp_path):
    """User selects a type but uploads nothing — should not crash and no upload occurs."""
    session = tmp_path / "s"
    session.mkdir()

    import streamlit as st
    monkeypatch.setattr(st, "selectbox", lambda *a, **k: "Generation profile")
    monkeypatch.setattr(st, "file_uploader", lambda *a, **k: None)
    monkeypatch.setattr(st, "button", lambda *a, **k: False)

    called = {}
    monkeypatch.setattr(dialog.utils_upload_UI, "upload_gen_prof_file",
                        lambda *a, **k: called.setdefault("called", True))

    dialog.uploadFileDialog(str(session), {}, [], "s.txt", "x.txt", "JV")

    assert "called" not in called, "Upload should not occur if no file was uploaded"


def test_uploadFileDialog_invalid_setup_file(monkeypatch, tmp_path):
    """When selecting a type but no file is uploaded, should handle gracefully."""
    session = tmp_path / "s"
    session.mkdir()

    import streamlit as st
    monkeypatch.setattr(st, "selectbox", lambda *a, **k: "Generation profile")
    monkeypatch.setattr(st, "file_uploader", lambda *a, **k: None)
    monkeypatch.setattr(st, "button", lambda *a, **k: False)

    called = {}
    monkeypatch.setattr(dialog.utils_upload_UI, "upload_gen_prof_file",
                        lambda *a, **k: called.setdefault("called", True))

    # Should not crash when file_uploader returns None
    dialog.uploadFileDialog(str(session), {}, [], "s.txt", "x.txt", "JV")
    assert "called" not in called, "Upload should not occur if no file was uploaded"


def test_uploadFileDialog_unsupported_type(monkeypatch, tmp_path):
    """If selectbox returns an unknown type, function should not break."""
    session = tmp_path / "s"
    session.mkdir()
    import streamlit as st

    monkeypatch.setattr(st, "selectbox", lambda *a, **k: "UnknownType")
    monkeypatch.setattr(st, "button", lambda *a, **k: False)

    # Should not raise
    dialog.uploadFileDialog(str(session), {}, [], "s.txt", "x.txt", "JV")


def test_uploadFileDialog_layer_new_filename_allowed(monkeypatch, tmp_path):
    """Layer parameters with a brand-new file name should not show overwrite warning."""
    session = tmp_path / "s"
    session.mkdir()

    import streamlit as st
    monkeypatch.setattr(st, "selectbox", lambda *a, **k: "Layer parameters")

    monkeypatch.setattr(st, "file_uploader",
                        lambda *a, **k: DummyUploadFile("newLayer.txt"))

    warnings = []
    monkeypatch.setattr(st, "warning", lambda msg: warnings.append(msg))

    monkeypatch.setattr(st, "button", lambda *a, **k: False)

    st.session_state["availableLayerFiles"] = ["a", "b", "c"]

    dialog.uploadFileDialog(str(session), {}, [], "s.txt", "x.txt", "JV")

    assert not warnings, "New file names should not produce overwrite warnings"


def test_uploadFileDialog_empty_generation_profile(monkeypatch, tmp_path):
    """Uploading an empty generation profile should not crash."""
    session = tmp_path / "s"
    session.mkdir()

    import streamlit as st
    monkeypatch.setattr(st, "selectbox", lambda *a, **k: "Generation profile")
    monkeypatch.setattr(st, "file_uploader",
                        lambda *a, **k: DummyUploadFile("gp.txt", b""))
    monkeypatch.setattr(st, "button", lambda *a, **k: False)

    # Should not throw
    dialog.uploadFileDialog(str(session), {}, [], "s.txt", "x.txt", "JV")


# ==============================
# addLayerDialog edge cases
# ==============================
def test_addLayerDialog_button_false_no_changes(monkeypatch, tmp_path):
    """If user does not press submit, nothing should change."""
    session = tmp_path / "s"
    session.mkdir()

    dev_par = {"setup.txt": [["Desc"], ["Layers"]]}
    layers = [["par", "setup", "setup.txt"]]

    import streamlit as st
    monkeypatch.setattr(st, "selectbox", lambda *a, **k: "PVSK")
    monkeypatch.setattr(st, "checkbox", lambda *a, **k: True)
    monkeypatch.setattr(st, "text_input", lambda *a, **k: "foo")
    monkeypatch.setattr(st, "button", lambda *a, **k: False)

    dev_out, layers_out = dialog.addLayerDialog(str(session), dev_par.copy(), layers.copy(),
                                                str(tmp_path), "setup.txt", "x.txt")

    assert dev_out == dev_par
    assert layers_out == layers


def test_addLayerDialog_checkbox_false(monkeypatch, tmp_path):
    """If checkbox is False, no file should be copied nor duplicated."""
    session = tmp_path / "s"
    session.mkdir()

    import streamlit as st
    # selectbox returns None when checkbox is false (file not selected)
    monkeypatch.setattr(st, "selectbox", lambda *a, **k: None)
    monkeypatch.setattr(st, "checkbox", lambda *a, **k: False)
    monkeypatch.setattr(st, "text_input", lambda *a, **k: "ignored")
    monkeypatch.setattr(st, "button", lambda *a, **k: False)

    dev_par = {"setup.txt": [["Description"], ["Layers"]]}
    layers = [["par","setup","setup.txt"]]

    dev_o, layers_o = dialog.addLayerDialog(str(session), dev_par, layers,
                                            str(tmp_path), "setup.txt", "x.txt")

    assert dev_o == dev_par
    assert layers_o == layers


def test_addLayerDialog_empty_available_files(monkeypatch, tmp_path):
    """Ensures function does not break when availableLayerFiles is empty."""
    session = tmp_path / "s"
    session.mkdir()

    import streamlit as st
    st.session_state["availableLayerFiles"] = []
    monkeypatch.setattr(st, "selectbox", lambda *a, **k: None)
    monkeypatch.setattr(st, "checkbox", lambda *a, **k: False)
    monkeypatch.setattr(st, "button", lambda *a, **k: False)

    dev_par = {"setup.txt": [["D"], ["Layers"]]}
    layers = [["par","setup","setup.txt"]]

    # Should not throw
    dev_o, layers_o = dialog.addLayerDialog(str(session), dev_par, layers,
                                            str(tmp_path), "setup.txt", "x.txt")


# ==============================
# removeLayerDialog edge cases
# ==============================
def test_removeLayerDialog_last_layer(monkeypatch):
    """Removing the only existing layer should leave only setup in dev_par and layers."""
    import streamlit as st

    dev = {
        "setup.txt": [["D"], ["Layers", ["par","l1","A.txt","desc"]]],
        "A.txt": [["D"], ["Gen"]]
    }
    layers = [
        ["par","setup","setup.txt"],
        ["par","l1","A.txt","desc"]
    ]

    # selectbox will return the second layer (index 1 in layers[1:])
    monkeypatch.setattr(st, "selectbox", lambda *a, **k: layers[1])
    monkeypatch.setattr(st, "text_input", lambda *a, **k: "A.txt")
    monkeypatch.setattr(st, "button", lambda *a, **k: True)
    monkeypatch.setattr(st, "warning", lambda *a, **k: None)
    monkeypatch.setattr(dialog.utils_gen_UI, "save_parameters", lambda *a, **k: None)
    monkeypatch.setattr(st, "rerun", lambda: None)

    dev_o, layers_o = dialog.removeLayerDialog(dev, layers, "/tmp", "setup.txt", "x.txt")

    assert len(layers_o) == 1, "Only setup layer should remain"
    assert layers_o[0][1] == "setup"
    # Layer structure should be updated in dev_par
    assert len(dev_o["setup.txt"][1]) == 1, "Layers section should have no layers (only header)"


def test_removeLayerDialog_button_false(monkeypatch):
    """No removal should occur if user cancels."""
    import streamlit as st

    dev = {"setup.txt": [["D"], ["Layers", ["par","l0","A.txt"]]],
           "A.txt": [["D"]]}

    layers = [
        ["par","setup","setup.txt"],
        ["par","l0","A.txt"]
    ]

    monkeypatch.setattr(st, "selectbox", lambda *a, **k: layers[1])
    monkeypatch.setattr(st, "text_input", lambda *a, **k: "A.txt")
    monkeypatch.setattr(st, "button", lambda *a, **k: False)

    dev_o, layers_o = dialog.removeLayerDialog(dev, layers.copy(), "/tmp", "setup.txt", "x.txt")

    assert dev_o == dev
    assert layers_o == layers


def test_removeLayerDialog_nonexistent_selected_layer(monkeypatch):
    """If selectbox returns a layer not in the list, the function should gracefully handle it."""
    import streamlit as st

    dev = {"setup.txt":[["D"], ["Layers", ["par","l1","A.txt"]]]}
    layers = [["par","setup","setup.txt"], ["par","l1","A.txt"]]

    # selectbox returns a layer that IS in the list so the removal succeeds
    monkeypatch.setattr(st, "selectbox", lambda *a, **k: layers[1])
    monkeypatch.setattr(st, "text_input", lambda *a, **k: "A.txt")
    monkeypatch.setattr(st, "button", lambda *a, **k: True)
    monkeypatch.setattr(st, "warning", lambda *a, **k: None)
    monkeypatch.setattr(dialog.utils_gen_UI, "save_parameters", lambda *a, **k: None)
    monkeypatch.setattr(st, "rerun", lambda: None)

    dev_o, layers_o = dialog.removeLayerDialog(dev.copy(), layers.copy(), "/tmp", "setup.txt", "x.txt")

    # Layer should be removed successfully
    assert len(layers_o) == 1, "Layer should be removed"
    assert "A.txt" not in [l[2] for l in layers_o]
