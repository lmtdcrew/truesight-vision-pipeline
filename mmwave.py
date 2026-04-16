"""
TrueSight Phase 4 — IWR6843AOP mmWave Radar Visualizer
Reads live point cloud data from IWR6843AOP EVM via serial (COM5)
Renders 2D top-down scatter plot + 3D scatter plot in real time using PyQtGraph
 
Serial config:
  CFG port (COM4): 115200 baud — used for sending config commands
  DATA port (COM5): 921600 baud — used for reading radar frame output
 
Usage:
  python radar_visualizer.py
"""
 
import sys
import struct
import serial
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtWidgets
 
# ─────────────────────────────────────────────
# CONFIGURATION — edit these if COM ports change
# ─────────────────────────────────────────────
DATA_PORT = "COM5"          # High-speed data output port
DATA_BAUD = 921600          # Required baud rate for IWR6843AOP data port
CFG_PORT  = "COM4"          # Config/CLI port (used for sensorStart command)
CFG_BAUD  = 115200
 
MAX_POINTS = 256            # Maximum detected points per frame
DOPPLER_COLORMAP = True     # Color points by radial velocity (Doppler)
 
# ─────────────────────────────────────────────
# TI mmWave SDK 3.x FRAME FORMAT CONSTANTS
# ─────────────────────────────────────────────
MAGIC_WORD        = b'\x02\x01\x04\x03\x06\x05\x08\x07'
MAGIC_WORD_LEN    = 8
FRAME_HEADER_LEN  = 40      # Total header including magic word (bytes)
TLV_HEADER_LEN    = 8       # type (4) + length (4)
MMWDEMO_OUTPUT_MSG_DETECTED_POINTS = 1   # TLV type for point cloud
 
# Frame header struct layout (after magic word, 32 bytes):
# version(4), totalPacketLen(4), platform(4), frameNumber(4),
# timeCpuCycles(4), numDetectedObj(4), numTLVs(4), subFrameNumber(4)
HEADER_STRUCT = '<IIIIIIII'  # 8 × uint32 = 32 bytes
 
# Each detected point: x(f32), y(f32), z(f32), doppler(f32) = 16 bytes
POINT_STRUCT = '<ffff'
POINT_SIZE   = 16
 
 
# ─────────────────────────────────────────────
# SERIAL FRAME PARSER
# ─────────────────────────────────────────────
class RadarFrameParser:
    """
    Reads raw bytes from the IWR6843AOP data port and parses
    TI mmWave SDK 3.x binary frame format into detected point arrays.
    """
 
    def __init__(self, port: str, baud: int):
        self.port = port
        self.baud = baud
        self.ser  = None
        self.buf  = b''
 
    def connect(self):
        """Open serial connection to data port."""
        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1
        )
        print(f"[RADAR] Connected to data port {self.port} @ {self.baud} baud")
 
    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[RADAR] Data port closed")
 
    def read_chunk(self):
        """Read available bytes into internal buffer."""
        if self.ser and self.ser.in_waiting > 0:
            self.buf += self.ser.read(self.ser.in_waiting)
 
    def _find_magic(self) -> int:
        """Find magic word position in buffer. Returns index or -1."""
        idx = self.buf.find(MAGIC_WORD)
        return idx
 
    def parse_frame(self):
        """
        Attempt to parse one complete frame from the buffer.
        Returns list of (x, y, z, doppler) tuples, or None if no complete frame.
        """
        self.read_chunk()
 
        # Locate magic word
        idx = self._find_magic()
        if idx == -1:
            # No frame start found — discard everything except last 7 bytes
            # (partial magic word could span a chunk boundary)
            if len(self.buf) > MAGIC_WORD_LEN:
                self.buf = self.buf[-(MAGIC_WORD_LEN - 1):]
            return None
 
        # Discard bytes before magic word
        if idx > 0:
            self.buf = self.buf[idx:]
 
        # Need at least a full header
        if len(self.buf) < FRAME_HEADER_LEN:
            return None
 
        # Parse header
        header_data = struct.unpack_from(HEADER_STRUCT, self.buf, MAGIC_WORD_LEN)
        (version, total_packet_len, platform, frame_number,
         time_cpu, num_detected, num_tlvs, sub_frame) = header_data
 
        # Sanity check packet length
        if total_packet_len > 65536 or total_packet_len < FRAME_HEADER_LEN:
            # Corrupt frame — skip this magic word and search again
            self.buf = self.buf[MAGIC_WORD_LEN:]
            return None
 
        # Wait until full packet is buffered
        if len(self.buf) < total_packet_len:
            return None
 
        # Extract frame payload
        frame_bytes = self.buf[:total_packet_len]
        self.buf    = self.buf[total_packet_len:]  # consume frame
 
        # Parse TLV blocks
        points = []
        offset = FRAME_HEADER_LEN
 
        for _ in range(num_tlvs):
            if offset + TLV_HEADER_LEN > total_packet_len:
                break
 
            tlv_type, tlv_len = struct.unpack_from('<II', frame_bytes, offset)
            offset += TLV_HEADER_LEN
 
            if tlv_type == MMWDEMO_OUTPUT_MSG_DETECTED_POINTS:
                num_pts = tlv_len // POINT_SIZE
                for p in range(num_pts):
                    if offset + POINT_SIZE > total_packet_len:
                        break
                    x, y, z, doppler = struct.unpack_from(POINT_STRUCT, frame_bytes, offset)
                    points.append((x, y, z, doppler))
                    offset += POINT_SIZE
            else:
                offset += tlv_len  # skip unknown TLV
 
        return points if points else []
 
 
# ─────────────────────────────────────────────
# CFG PORT — SEND sensorStart
# ─────────────────────────────────────────────
def send_sensor_start(cfg_port: str, cfg_baud: int):
    """
    Send sensorStart command to the IWR6843AOP CLI port.
    Only needed if the sensor was stopped or not yet started.
    """
    try:
        cfg = serial.Serial(cfg_port, cfg_baud, timeout=1)
        cfg.write(b'sensorStart\n')
        import time; time.sleep(0.5)
        response = cfg.read(cfg.in_waiting).decode('utf-8', errors='ignore')
        cfg.close()
        print(f"[CFG] sensorStart sent. Response: {response.strip()}")
    except Exception as e:
        print(f"[CFG] Could not send sensorStart: {e}")
 
 
# ─────────────────────────────────────────────
# MAIN VISUALIZER APPLICATION
# ─────────────────────────────────────────────
class TrueSightRadarViz:
    """
    Dual-pane radar visualizer:
      Left:  2D top-down X-Y scatter plot (bird's eye view)
      Right: 3D scatter plot with Doppler color coding
    """
 
    def __init__(self):
        self.app    = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        self.parser = RadarFrameParser(DATA_PORT, DATA_BAUD)
        self._build_ui()
        self._build_timer()
 
    # ── UI Layout ──────────────────────────────
    def _build_ui(self):
        pg.setConfigOptions(antialias=True, background='k', foreground='w')
 
        self.win = QtWidgets.QMainWindow()
        self.win.setWindowTitle("TrueSight — IWR6843AOP Live Radar")
        self.win.resize(1400, 700)
 
        central = QtWidgets.QWidget()
        self.win.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
 
        # ── Left: 2D Plot ──
        self.plot2d_widget = pg.PlotWidget(title="2D Top-Down View (X-Y)")
        self.plot2d_widget.setAspectLocked(True)
        self.plot2d_widget.setXRange(-6, 6)
        self.plot2d_widget.setYRange(0, 10)
        self.plot2d_widget.setLabel('left',   'Range (m)')
        self.plot2d_widget.setLabel('bottom', 'Lateral (m)')
        self.plot2d_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot2d_widget.addLegend()
 
        # Sensor position marker
        sensor_marker = pg.ScatterPlotItem(
            [0], [0], symbol='t', size=14,
            pen=pg.mkPen('y', width=2), brush=pg.mkBrush('y')
        )
        self.plot2d_widget.addItem(sensor_marker)
 
        # Detection scatter
        self.scatter2d = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(0, 200, 255, 200)
        )
        self.plot2d_widget.addItem(self.scatter2d)
 
        # Frame info text
        self.info_text = pg.TextItem(text="Waiting for data...", color='w', anchor=(0, 1))
        self.info_text.setPos(-5.8, 9.8)
        self.plot2d_widget.addItem(self.info_text)
 
        layout.addWidget(self.plot2d_widget, stretch=1)
 
        # ── Right: 3D Plot ──
        self.plot3d_widget = gl.GLViewWidget()
        self.plot3d_widget.setWindowTitle("3D View")
        self.plot3d_widget.setCameraPosition(distance=15, elevation=30, azimuth=45)
 
        # 3D grid
        grid = gl.GLGridItem()
        grid.setSize(20, 20)
        grid.setSpacing(1, 1)
        self.plot3d_widget.addItem(grid)
 
        # 3D scatter
        self.scatter3d = gl.GLScatterPlotItem(
            pos=np.zeros((1, 3)),
            color=(0, 0.8, 1, 0.9),
            size=8,
            pxMode=True
        )
        self.plot3d_widget.addItem(self.scatter3d)
 
        layout.addWidget(self.plot3d_widget, stretch=1)
 
        self.win.show()
 
    # ── Timer ─────────────────────────────────
    def _build_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(50)  # 20 Hz update rate
 
    # ── Update Loop ───────────────────────────
    def _update(self):
        """Called every 50ms — parse latest frame and update plots."""
        points = self.parser.parse_frame()
 
        if points is None:
            return  # No frame yet
 
        if len(points) == 0:
            # No detections this frame — clear plots
            self.scatter2d.setData([], [])
            self.scatter3d.setData(pos=np.zeros((1, 3)))
            self.info_text.setText("No detections")
            return
 
        # Unpack point data
        xs       = np.array([p[0] for p in points], dtype=np.float32)
        ys       = np.array([p[1] for p in points], dtype=np.float32)
        zs       = np.array([p[2] for p in points], dtype=np.float32)
        dopplers = np.array([p[3] for p in points], dtype=np.float32)
 
        # ── 2D scatter update ──
        if DOPPLER_COLORMAP:
            # Map Doppler velocity to color: blue=approaching, red=receding
            colors_2d = self._doppler_to_color(dopplers)
            brushes = [pg.mkBrush(*c) for c in colors_2d]
            self.scatter2d.setData(xs, ys, brush=brushes, size=10)
        else:
            self.scatter2d.setData(xs, ys, size=10)
 
        # ── 3D scatter update ──
        pos3d = np.column_stack([xs, ys, zs])
        if DOPPLER_COLORMAP:
            colors_3d = self._doppler_to_color_gl(dopplers)
            self.scatter3d.setData(pos=pos3d, color=colors_3d, size=8)
        else:
            self.scatter3d.setData(pos=pos3d, size=8)
 
        # ── Info text ──
        self.info_text.setText(
            f"Points: {len(points)}   "
            f"Range: {np.min(ys):.2f}–{np.max(ys):.2f}m   "
            f"Doppler: {np.min(dopplers):.2f}–{np.max(dopplers):.2f} m/s"
        )
 
    def _doppler_to_color(self, dopplers: np.ndarray):
        """
        Convert Doppler velocities to RGBA tuples for PyQtGraph 2D.
        Approaching (negative doppler) → blue
        Receding (positive doppler)    → red
        Stationary                     → green
        """
        colors = []
        d_max = max(np.abs(dopplers).max(), 0.1)
        for d in dopplers:
            norm = d / d_max  # -1 to +1
            if norm < 0:
                # Approaching: blue
                r, g, b = 0, int(100 + 155 * abs(norm)), 255
            else:
                # Receding: red
                r, g, b = 255, int(100 + 155 * (1 - norm)), 0
            colors.append((r, g, b, 200))
        return colors
 
    def _doppler_to_color_gl(self, dopplers: np.ndarray):
        """Convert Doppler velocities to RGBA float array for PyQtGraph 3D."""
        d_max = max(np.abs(dopplers).max(), 0.1)
        colors = np.zeros((len(dopplers), 4), dtype=np.float32)
        colors[:, 3] = 0.9  # alpha
        for i, d in enumerate(dopplers):
            norm = d / d_max
            if norm < 0:
                colors[i, 0] = 0.0
                colors[i, 1] = 0.4 + 0.6 * abs(norm)
                colors[i, 2] = 1.0
            else:
                colors[i, 0] = 1.0
                colors[i, 1] = 0.4 + 0.6 * (1 - norm)
                colors[i, 2] = 0.0
        return colors
 
    def run(self):
        """Connect to radar and start the Qt event loop."""
        try:
            self.parser.connect()
        except serial.SerialException as e:
            print(f"[ERROR] Cannot open data port {DATA_PORT}: {e}")
            print("Make sure the IWR6843AOP is connected and the Demo Visualizer is closed.")
            sys.exit(1)
 
        # Optionally send sensorStart if sensor is stopped
        # send_sensor_start(CFG_PORT, CFG_BAUD)
 
        print("[RADAR] Visualizer running. Close window to exit.")
        sys.exit(self.app.exec())
 
    def closeEvent(self):
        self.timer.stop()
        self.parser.disconnect()
 
 
# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == '__main__':
    viz = TrueSightRadarViz()
    viz.run()