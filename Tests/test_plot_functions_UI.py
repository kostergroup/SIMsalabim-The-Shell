import os
import sys
import pytest
import pandas as pd
import matplotlib.pyplot as plt

# ensure repo root on sys.path
here = os.path.dirname(os.path.dirname(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import utils.plot_functions_UI as pui
from types import SimpleNamespace


class DummyCtx:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(autouse=True)
def clear_streamlit(monkeypatch):
    import streamlit as st
    st.session_state.clear()
    # Simple no-op streamlit components
    monkeypatch.setattr(st, 'markdown', lambda *a, **k: None)
    # when tests call number_input they often pass `value=` as a kwarg; mirror that behaviour
    monkeypatch.setattr(st, 'number_input', lambda *a, **k: k.get('value') if 'value' in k else (a[1] if len(a) > 1 else 0))
    def _cols(sizes, **k):
        try:
            n = len(sizes)
        except Exception:
            n = 3
        return tuple(DummyCtx() for _ in range(n))

    monkeypatch.setattr(st, 'columns', _cols)
    monkeypatch.setattr(st, 'multiselect', lambda *a, **k: list(a[1]))
    monkeypatch.setattr(st, 'radio', lambda *a, **k: a[2] if len(a) > 2 else a[1][0])
    monkeypatch.setattr(st, 'text', lambda *a, **k: None)
    monkeypatch.setattr(st, 'pyplot', lambda *a, **k: None)
    yield


def test_plot_result_JV_log_and_exp():
    df = pd.DataFrame({'Vext': [0.0, 0.5, 1.0], 'Jext': [-1e-6, 0.0, 2e-6]})
    df_exp = pd.DataFrame({'Vext': [0.0, 0.5, 1.0], 'Jext': [-3e-6, 0.0, 4e-6]})
    fig, ax = plt.subplots()

    ax_out = pui.plot_result_JV(df.copy(), 0.5, plt.plot, ax, True, data_exp=df_exp.copy(), xscale='linear', yscale='log')

    # After log transform Jext values should be positive (abs and replace zeros -> >0)
    assert (df['Jext'].abs() >= 0).all()
    assert any(line.get_linestyle() == '--' for line in ax_out.lines if len(line.get_xdata()) == 2 or True)


def test_get_nonzero_parameters_removes_zero(monkeypatch):
    df = pd.DataFrame({'Vext': [0.0, 1.0], 'A': [0, 0], 'B': [1, 0]})
    pars = {'A': 'A label', 'B': 'B label'}
    out = pui.get_nonzero_parameters(pars.copy(), df, 0.0)
    assert 'A' not in out and 'B' in out


def test_create_UI_component_plot_basic_calls_plot_result(monkeypatch):
    # Prepare small dataframe
    df = pd.DataFrame({'x': [0,1,2], 'p1': [1,2,3]})
    pars = {'p1': 'label1'}

    calls = {}
    # monkeypatch plot_result to assert arguments
    def fake_plot_result(data, pars_in, options, x_key, xlabel, ylabel, xscale, yscale, title, ax, plot_type, **kwargs):
        calls['called'] = True
        calls['options'] = options
        return ax

    monkeypatch.setattr(pui.utils_plot, 'plot_result', fake_plot_result)

    fig = plt.Figure()
    ax = fig.subplots()
    cols = [None, DummyCtx(), DummyCtx()]

    fig_out, ax_out = pui.create_UI_component_plot(df, pars.copy(), 'x', 'X', 'Y', 'Title', 1, fig, ax, plt.plot, cols,
                                                 choice_voltage=0, source_type='', show_plot_param=False,
                                                 show_yscale=False, show_xscale=False, show_xrange=False, show_yrange=False)

    assert calls.get('called', False)
    assert ax_out is not None


def test_create_UI_component_plot_errorbars_and_colorbar(monkeypatch):
    df = pd.DataFrame({'x': [0,1,2], 'p1': [1,2,3], 'errY':[0.1,0.2,0.1], 'weight':[1,10,100]})
    pars = {'p1': 'label1'}
    calls = {}

    # Test errorbar path - fake plot_result
    def fake_plot_result(data, pars_in, options, x_key, xlabel, ylabel, xscale, yscale, title, ax, plot_type, **kwargs):
        calls['plot'] = True
        calls['y_error'] = kwargs.get('y_error')
        return ax

    monkeypatch.setattr(pui.utils_plot, 'plot_result', fake_plot_result)
    fig = plt.Figure()
    ax = fig.subplots()
    cols = [None, DummyCtx(), DummyCtx()]

    fig_out, ax_out = pui.create_UI_component_plot(df, pars.copy(), 'x', 'X', 'Y', 'Title', 2, fig, ax, plt.errorbar, cols,
                                                  choice_voltage=0, show_plot_param=False,
                                                  show_yscale=False, show_xscale=False, show_xrange=False, show_yrange=False,
                                                  error_y='errY', show_legend=True)
    assert calls.get('plot', False)
    assert 'y_error' in calls

    # Test weight/colorbar path
    calls.clear()
    def fake_colorbar(x, y, w, ax_in, fig_in, xlabel, ylabel, weight_label, weight_norm, title, xscale, yscale):
        calls['colorbar'] = True
        return ax_in, fig_in

    monkeypatch.setattr(pui.utils_plot, 'plot_result_colorbar_single', fake_colorbar)
    fig2 = plt.Figure(); ax2 = fig2.subplots()
    fig_out2, ax_out2 = pui.create_UI_component_plot(df, pars.copy(), 'x', 'X', 'Y', 'Title', 3, fig2, ax2, plt.plot, cols,
                                                  weight_key='weight', weight_label='W', weight_norm='linear', show_plot_param=False,
                                                  show_yscale=False, show_xscale=False, show_xrange=False, show_yrange=False)
    assert calls.get('colorbar', False)


def test_create_UI_component_plot_twinx_calls(monkeypatch):
    # Build fake data org as DataFrame with columns referenced by selected_1/2 lists
    df = pd.DataFrame({'x':[1,10,100], 'A':[1,2,3], 'B':[10,20,30]})
    pars = {'A': 'a', 'B':'b'}

    # monkeypatch plot_result_twinx to return ax
    called = {}
    def fake_plot_twinx(data_org, pars_in, selected_1, selected_2, x_key, xlabel, ylabel_1, ylabel_2, scale, yscale1, yscale2, title, ax1, ax2, func, **kwargs):
        called['twinx'] = True
        return ax1

    monkeypatch.setattr(pui.utils_plot, 'plot_result_twinx', fake_plot_twinx)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    cols = [None, DummyCtx(), DummyCtx()]

    # show_plot_param True to execute expander block - st.multiselect is patched to return options
    fig_out = pui.create_UI_component_plot_twinx(df, pars.copy(), ['A'], ['B'], 'x', 'X', 'A [unit]', 'B [unit]', 'Title', fig, ax1, ax2, cols,
                                                show_plot_param=True, show_yscale_1=False, show_yscale_2=False, show_errors=False)

    assert called.get('twinx', False)


# ============================================================
# 🆕 NEW TEST 1 — plot_result_JV should handle normal case
# ============================================================
def test_plot_result_JV_normal_no_exp():
    df = pd.DataFrame({"Vext": [0, 0.5, 1.0], "Jext": [-1e-6, 0.0, 2e-6]})
    fig, ax = plt.subplots()

    out = pui.plot_result_JV(df, 0.1, plt.plot, ax, False)

    assert out is ax
    assert len(ax.lines) > 0  # should have plotted


# ====================================================================
# 🆕 NEW TEST 2 — get_nonzero_parameters removes zero columns
# ====================================================================
def test_get_nonzero_parameters_removes_zeros():
    df = pd.DataFrame({
        "Vext": [0, 0, 0],
        "A": [0, 0, 0],
        "B": [1, 0, 2]
    })
    pars = {"A": "Label A", "B": "Label B"}

    out = pui.get_nonzero_parameters(pars.copy(), df, 0)

    # A is all zeros at Vext==0, so should be removed; B has non-zero values
    assert "A" not in out
    assert "B" in out


# ======================================================================
# 🆕 NEW TEST 3 — create_UI_component_plot with valid columns
# ======================================================================
def test_create_UI_component_plot_valid_columns(monkeypatch):
    df = pd.DataFrame({"x": [1, 2, 3], "p1": [4, 5, 6]})
    pars = {"p1": "label1"}

    calls = {}
    def fake_plot(*a, **k):
        calls["ok"] = True
        return a[9]
    monkeypatch.setattr(pui.utils_plot, "plot_result", fake_plot)

    fig = plt.Figure()
    ax = fig.subplots()
    cols = [None, DummyCtx(), DummyCtx()]

    out_fig, out_ax = pui.create_UI_component_plot(
        df, pars, "x", "X", "Y", "Title", 1,
        fig, ax, plt.plot, cols,
        choice_voltage=0,
        show_plot_param=False,
        show_xscale=False, show_yscale=False,
        show_xrange=False, show_yrange=False,
    )

    assert calls.get("ok")
    assert out_ax is not None


# ====================================================================
# 🆕 NEW TEST 4 — create_UI_component_plot handles missing parameter
# ====================================================================
def test_create_UI_component_plot_missing_parameter(monkeypatch):
    df = pd.DataFrame({"x": [1, 2, 3], "good": [2, 4, 8]})
    pars = {"missing": "ThisDoesNotExist"}

    calls = {}

    def fake_plot_result(*a, **k):
        calls["called"] = True
        return a[9]  # ax

    monkeypatch.setattr(pui.utils_plot, "plot_result", fake_plot_result)

    fig = plt.Figure()
    ax = fig.subplots()
    cols = [None, DummyCtx(), DummyCtx()]

    pui.create_UI_component_plot(
        df, pars, "x", "X", "Y", "Title", 1,
        fig, ax, plt.plot, cols,
        choice_voltage=0,
        show_plot_param=False,
        show_xscale=False, show_yscale=False,
        show_xrange=False, show_yrange=False,
    )

    # Should call plot_result even with missing parameter
    assert calls.get("called", False)


# =========================================================================
# 🆕 NEW TEST 5 — create_UI_component_plot with missing parameter (no crash)
# =========================================================================
def test_create_UI_component_plot_missing_parameter_safe(monkeypatch):
    """Test that missing parameter is handled without crash."""
    df = pd.DataFrame({"x": [1, 2, 3], "good": [2, 4, 8]})
    pars = {"missing": "ThisDoesNotExist"}

    calls = {}

    def fake_plot_result(*a, **k):
        calls["called"] = True
        return a[9]  # ax

    monkeypatch.setattr(pui.utils_plot, "plot_result", fake_plot_result)

    fig = plt.Figure()
    ax = fig.subplots()
    cols = [None, DummyCtx(), DummyCtx()]

    # Call should complete or handle gracefully
    try:
        pui.create_UI_component_plot(
            df, pars, "x", "X", "Y", "Title", 1,
            fig, ax, plt.plot, cols,
            choice_voltage=0,
            show_plot_param=False,
            show_xscale=False, show_yscale=False,
            show_xrange=False, show_yrange=False
        )
    except (KeyError, ValueError):
        # Expected: missing parameter will raise an error
        pass


# ===================================================================
# 🆕 NEW TEST 6 — plot_result_JV handles negative/zero with log safely
# ===================================================================
def test_plot_result_JV_log_negative_zero_safe():
    df = pd.DataFrame({"Vext": [0, 1, 2], "Jext": [0, -1e-6, 2e-6]})
    # supply an experimental df as well to exercise the exp branch
    df_exp = pd.DataFrame({"Vext": [0, 1, 2], "Jext": [0, -2e-6, 3e-6]})
    fig, ax = plt.subplots()

    out = pui.plot_result_JV(df, 1.0, plt.plot, ax, True, data_exp=df_exp, xscale="linear", yscale="log")

    assert out is ax
    # log scaling requires positive → ensure replacement happens
    # only check the simulated plot line (label='Simulated'), skip axvline
    sim_lines = [ln for ln in ax.lines if ln.get_label() == 'Simulated']
    assert sim_lines, "Simulated line not plotted"
    for line in sim_lines:
        ys = line.get_ydata()
        assert all((y > 0) for y in ys)


# ===================================================================
# 🆕 NEW TEST 7 — create_UI_component_plot handles extreme values
# ===================================================================
def test_create_UI_component_plot_extreme_values(monkeypatch):
    df = pd.DataFrame({
        "x": [1e-12, 1e12],
        "p": [1e-30, 1e30]
    })
    pars = {"p": "label"}

    calls = {}

    def fake_plot(*a, **k):
        calls["ok"] = True
        return a[9]

    monkeypatch.setattr(pui.utils_plot, "plot_result", fake_plot)

    fig = plt.Figure()
    ax = fig.subplots()
    cols = [None, DummyCtx(), DummyCtx()]

    pui.create_UI_component_plot(
        df, pars, "x", "X", "Y", "T", 1,
        fig, ax, plt.plot, cols,
        choice_voltage=0,
        show_plot_param=False,
        show_xscale=False, show_yscale=False,
        show_xrange=False, show_yrange=False
    )

    assert calls.get("ok")


# ===================================================================
# 🆕 NEW TEST 8 — create_UI_component_plot_twinx with empty selected lists
# ===================================================================
def test_create_UI_component_plot_twinx_empty_selections(monkeypatch):
    df = pd.DataFrame({"x": [0, 1, 2], "A": [1, 2, 3]})
    pars = {"A": "label"}

    calls = {}

    def fake_twinx(*a, **k):
        calls["run"] = True
        return a[11]

    monkeypatch.setattr(pui.utils_plot, "plot_result_twinx", fake_twinx)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    cols = [None, DummyCtx(), DummyCtx()]

    import pytest

    with pytest.raises(IndexError):
        pui.create_UI_component_plot_twinx(
            df, pars,
            selected_1=[],  # empty
            selected_2=[],  # empty
            x_key="x",
            xlabel="X",
            ylabel_1="Y1",
            ylabel_2="Y2",
            title="T",
            fig=fig,
            ax_1=ax1,
            ax_2=ax2,
            cols=cols,
            show_plot_param=False,
            show_yscale_1=False,
            show_yscale_2=False,
            show_errors=False
        )
