"""Original SwarmBase instruments with a three-line diagnostic footer."""
from pathlib import Path
import math
import time
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.text import Text
from gui.simpleGUI import SimpleGUI
from comm.FlightDiagnostics import MODES, COLORS


HELP_FILE = Path(__file__).resolve().parents[1] / 'CONTROLS.md'


def quick_reference():
    """The quick-reference block of CONTROLS.md, shown by the H key."""
    try:
        text = HELP_FILE.read_text(encoding='utf-8')
        block = text.split('<!-- quick-reference -->')[1].split('<!-- /quick-reference -->')[0]
        return '\n'.join(l for l in block.strip().splitlines() if not l.startswith('```'))
    except (OSError, IndexError):
        return 'Help not found: %s' % HELP_FILE


def mode(value):
    return MODES.get(int(value), 'Unknown mode')


def action(params):
    if int(params[0]) != 1:
        return mode(params[0])
    parts = []
    for value, positive, negative in [(params[1], 'Forward', 'Back'),
                                      (params[2], 'Up', 'Down'),
                                      (params[4], 'Yaw+', 'Yaw-')]:
        if abs(value) > 1e-6:
            parts.append(positive if value > 0 else negative)
    return ' + '.join(parts) or 'Hold (sticks released)'


class ManualDashboard(SimpleGUI):
    def __init__(self, diagnostics, camera='nicla'):
        self.d = diagnostics
        self.closed = False
        super().__init__(camera, n=20)
        self.fig.canvas.manager.set_window_title('SwarmBase · ManualPlus')
        self.fig.canvas.mpl_connect('close_event', self.on_close)
        # Keep the original instruments and sliders at exactly their original
        # physical sizes; extend the canvas downward for the small status area.
        width, old_height = self.fig.get_size_inches()
        extra = .8
        self.original_positions = [ax.get_position().frozen() for ax in self.fig.axes]
        self.original_axes = list(self.fig.axes)
        self.fig.set_size_inches(width, old_height + extra, forward=True)
        for ax, pos in zip(self.original_axes, self.original_positions):
            ax.set_position([pos.x0, (pos.y0*old_height+extra)/(old_height+extra),
                             pos.width, pos.height*old_height/(old_height+extra)])
        font = None
        for path in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                     '/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc']:
            if Path(path).exists():
                font = font_manager.FontProperties(fname=path)
                break
        self.status_ax = self.fig.add_axes([.025, .02, .95, (extra-.1)/(old_height+extra)], facecolor='#21262d')
        self.status_ax.set_xticks([])
        self.status_ax.set_yticks([])
        for spine in self.status_ax.spines.values():
            spine.set_visible(False)
        self.status_lines = [self.status_ax.text(.025, y, '', transform=self.status_ax.transAxes,
                             va='center', color='#ecf2f8', fontsize=9, fontproperties=font)
                             for y in [.85, .5, .15]]
        # H toggles a quick-reference overlay read from CONTROLS.md
        self.help_ax = self.fig.add_axes([0, 0, 1, 1], facecolor='#0d1117')
        self.help_ax.set_zorder(10)
        self.help_ax.set_xticks([])
        self.help_ax.set_yticks([])
        self.help_ax.text(.03, .96, 'SwarmBase controls  ·  H to close  ·  full guide: CONTROLS.md',
                          va='top', color='#ecf2f8', fontsize=10, fontweight='bold')
        self.help_ax.text(.03, .88, quick_reference(), va='top', color='#c9d1d9',
                          fontsize=7.4, family='monospace', linespacing=1.6)
        self.help_ax.set_visible(False)
        # Text sizes are in points and would stay fixed; scale them with the window instead
        self.base_size = tuple(self.fig.get_size_inches())
        self.base_fonts = [(t, t.get_fontsize()) for t in self.fig.findobj(Text)]
        self.fig.canvas.mpl_connect('resize_event', self.on_resize)
        self.refresh(draw=False)

    def on_key_press(self, event):
        if event.key == 'ctrl+c':
            raise KeyboardInterrupt
        if event.key in ('h', 'H'):
            self.help_ax.set_visible(not self.help_ax.get_visible())
            self.fig.canvas.draw_idle()
            return
        super().on_key_press(event)

    def on_resize(self, event):
        width, height = self.fig.get_size_inches()
        scale = min(width / self.base_size[0], height / self.base_size[1])
        for text, size in self.base_fonts:
            text.set_fontsize(size * scale)

    def on_close(self, event):
        self.closed = True
        self.d.close()

    def refresh(self, draw=True):
        if self.closed:
            return
        d = self.d
        d.poll()
        if d.tx:
            p = d.tx['params']
            status = 'Mode: %s | Cmd: %s | Color: %s' % (mode(p[0]), action(p), COLORS.get(int(p[7]), 'Unknown'))
        else:
            status = 'No robot selected (1 → Enter)'
        telemetry = ('%.1fs ago' % (time.monotonic()-d.telemetry_at)) if d.telemetry_at else 'no data'
        self.status_lines[0].set_text(status + ' | Telemetry: ' + telemetry + ' (base)')
        ex = d.execution if d.same_robot() else None
        if ex:
            stale = (d.passive and d.fd is None) or time.monotonic()-d.exec_at > 3
            line = '%s%s  |  Motor cmd %.0f%% / %.0f%%  |  Servo cmd %.0f° / %.0f°' % (
                'Stale · ' if stale else 'Robot · ', mode(ex['beh'][0]),
                ex['out'][0]*100, ex['out'][1]*100, ex['out'][2], ex['out'][3])
        elif all(p in d.extra and time.monotonic()-d.extra_at[p] < 3 for p in (2, 3, 4)):
            att, out, health = d.extra[2], d.extra[3], d.extra[4]
            stale = False
            line = ('Wireless · motor %.0f%%/%.0f%% · servo %.0f°/%.0f° · pitch %+.0f° · IMU %.0f/s · cam %.0f fps · loop %.1f ms · up %.0fs' %
                    (out[0]*100, out[1]*100, out[2], out[3], math.degrees(att[0]), health[1], health[2], health[4], health[0]))
        else:
            line = 'Robot output: no data (connect robot USB to view; commanded values, not measured)'
        self.status_lines[1].set_text(line)
        self.status_lines[1].set_color('#faa356' if ex and stale else '#a2d2fb')
        self.status_lines[2].set_text('Log not saved: ' + d.log_error[:45] if d.log_error else
                                     '1→Enter select · B start/stop · s stop · F1–F4 color · H help | Auto-logged')
        if draw:
            self.fig.canvas.draw_idle()
            plt.pause(.001)

    def update(self, **gauges):
        if self.closed:
            return
        self.refresh(draw=False)
        super().update(**gauges)
