import os
import sys
import pytest

# ensure repo root on sys.path
here = os.path.dirname(os.path.dirname(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import utils.summary_and_citation as sac


@pytest.fixture(autouse=True)
def clear_state(monkeypatch):
    import streamlit as st
    st.session_state.clear()
    # provide required state keys used by create_summary_and_cite
    st.session_state['SIMsalabim_version'] = 'vX.Y'
    st.session_state['TheShell_version'] = 'vA.B'
    yield


def test_get_reference_lookup():
    # known reference
    refdict = {'nk1': 'Author, ref1'}
    assert sac.get_reference('nk1', refdict) == 'Author, ref1'
    # missing -> fallback
    assert sac.get_reference('does_not_exist', refdict) == '-No reference provided-'


def test_create_description_variants():
    assert sac.create_description('Transient JV').strip().startswith('Simulate a JV Transient')
    assert 'impedance spectroscopy' in sac.create_description('Impedance').lower()
    assert 'intensity modulated' in sac.create_description('IMPS').lower()
    assert sac.create_description('Steady State JV') == ''


def test_create_summary_and_cite_basic(tmp_path, monkeypatch):
    session = tmp_path / 'session'
    session.mkdir()
    # create some files
    (session / 'input.txt').write_text('in')
    (session / 'out.dat').write_text('out')

    import streamlit as st
    st.session_state['simulation_results'] = 'Steady State JV'

    sac.create_summary_and_cite(str(session), used_optics=False)

    fname = session / sac.summary_file_name
    assert fname.exists()
    text = fname.read_text()
    # Contains versions and source info
    assert 'SIMsalabim version: vX.Y' in text
    assert 'The Shell version: vA.B' in text
    # Should list included files
    assert '- input.txt' in text and '- out.dat' in text
    # Steady State program should set program name to SimSS
    assert 'SIMsalabim program: SimSS' in text
    # Citation includes SIMsalabim reference
    assert 'SIMsalabim:' in text and sac.SIMsalabim_cite.split(',')[0] in text


def test_create_summary_and_cite_with_optics_and_impedance(monkeypatch, tmp_path):
    session = tmp_path / 'session'
    session.mkdir()
    # normal files
    (session / 'readme.txt').write_text('r')

    # create Data_nk and Data_spectrum with files
    dn = session / 'Data_nk'
    ds = session / 'Data_spectrum'
    dn.mkdir(); ds.mkdir()
    (dn / 'nk_known.txt').write_text('nk')
    (dn / 'nk_unknown.txt').write_text('nk')
    (ds / 'sp_known.txt').write_text('sp')

    # monkeypatch reference dicts in the module
    monkeypatch.setattr(sac, 'nk_ref_dict', {'nk_known': 'Ref NK'})
    monkeypatch.setattr(sac, 'spectrum_ref_dict', {'sp_known': 'Ref SP'})

    import streamlit as st
    st.session_state['simulation_results'] = 'Impedance'
    # add expected expObject entries used by Impedance branch
    st.session_state['expObject'] = {'fmin': 1.0, 'fmax': 1e6, 'V0': 0.5, 'delV': 0.01, 'G_frac': 0.2}

    sac.create_summary_and_cite(str(session), used_optics=True)
    text = (session / sac.summary_file_name).read_text()

    # should include nk and spectrum file names
    assert 'nk_known.txt' in text
    assert 'nk_unknown.txt' in text
    assert 'sp_known.txt' in text

    # Impedance-specific lines
    assert 'Frequency range' in text and 'Applied Voltage' in text
    # Fourier decomposition citation must appear for impedance
    assert 'Fourier Decomposition' in text and sac.fourier_decomp_cite.split(',')[0] in text

    # references: nk_known and sp_known resolved; unknown should show '-No reference provided-'
    assert '* nk_known: Ref NK' in text
    assert '* sp_known: Ref SP' in text
    assert '-No reference provided-' in text


def test_create_summary_and_cite_transient_use_expdata(tmp_path):
    session = tmp_path / 'session'
    session.mkdir()
    (session / 'a.dat').write_text('x')

    import streamlit as st
    st.session_state['simulation_results'] = 'Transient JV'
    st.session_state['expObject'] = {
        'UseExpData': 1,
        'expJV_Vmin_Vmax': 'e1.txt',
        'expJV_Vmax_Vmin': 'e2.txt',
        'scan_speed': 0.001,
        'direction': 1,
        'G_frac': 0.1
    }

    sac.create_summary_and_cite(str(session), used_optics=False)
    text = (session / sac.summary_file_name).read_text()

    assert 'Experimental JV data used. Files' in text
    assert '- e1.txt' in text and '- e2.txt' in text
    assert 'Scan speed' in text and 'direction:' in text
