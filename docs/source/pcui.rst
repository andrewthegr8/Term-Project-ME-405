PC User Interface
==============================

Overview
--------

The scripts ``Talker.py``, ``RomiDisplay.py``, and ``GoatedPlotter.py``
form a comprehensive **PC-side user interface** for interacting with the
Romi robot over a Bluetooth serial connection.

This interface uses **multiple threads** to handle real-time data
streaming, user input, and data analysis concurrently.

It consists of four primary components:

* A **serial RX thread** that continously reads and decodes telemetry
  packets from the robot, using a predefined binary packet format
  (:mod:`Talker`).
* A **serial TX thread** that sends control commands to the robot
  (:mod:`Talker`).
* A **Tkinter GUI** for real–time data monitioring and control of the robot
  (:mod:`RomiDisplay`). 
* A **data–analysis and plotting engine** triggered automatically after
  each data-logged run (:mod:`GoatedPlotter`).

Together these scripts let the user:

* Stream high-rate telemetry from the robot over a Bluetooth virtual COM
  port.
* Visualise predicted vs. actual wheel motion and robot pose in real
  time.
* Log experiments and automatically generate plots and CSV exports.

Component Details
-----------------

ost application: ``Talker.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The host script orchestrates the PC side of the telemetry system. :contentReference[oaicite:7]{index=7}

Serial configuration
^^^^^^^^^^^^^^^^^^^^

* Opens the Bluetooth COM port:

  .. code-block:: python

     ser = serial.Serial('COM13', 460800, timeout=1)

* Uses a shared ``serial_lock`` (a :class:`threading.Lock`) to ensure
  safe concurrent access from reader and writer threads.

Telemetry reader thread
^^^^^^^^^^^^^^^^^^^^^^^

The ``SerialReader`` function runs in its own daemon thread and is
responsible for decoding the robot's binary telemetry stream. :contentReference[oaicite:8]{index=8}

* **Framing**

  * Packets are framed with a two–byte sync word and a type byte:

    - Sync: ``0xAA 0x55``
    - Type: one byte just after the sync:

      * ``0x00`` – standard telemetry packet.
      * ``0xFF`` – handshake or special information.

  * ``SerialReader`` maintains a rolling ``bytearray`` buffer:

    - Searches for the sync sequence.
    - Discards preceding bytes if sync is not aligned.
    - Verifies that enough bytes are present for a full packet before
      attempting to unpack.

* **Payload format**

  * Telemetry payload is defined by:

    .. code-block:: python

       format = '<IIfffffffffffffffff'
       packet_length = struct.calcsize(format) + 3

  * This corresponds to:

    - 2× unsigned 32-bit integers (``I``)
    - 17× 32-bit floats (``f``)
    - Plus 3 bytes for sync and type.

  * The data fields are unpacked in order and distributed to queues:

    ==========  ===============================
    Index       Meaning
    ==========  ===============================
    0           ``time_L`` (uint32)
    1           ``time_R`` (uint32)
    2           ``pos_L`` (float)
    3           ``velo_L``
    4           ``velo_R``
    5           ``pos_R``
    6           ``cmd_L``
    7           ``cmd_R``
    8           ``Eul_head`` (Euler heading)
    9           ``yaw_rate``
    10          ``offset`` (line–follower offset)
    11          ``X_pos``
    12          ``Y_pos``
    13          ``p_v_R`` (predicted right velocity)
    14          ``p_v_L`` (predicted left velocity)
    15          ``p_head`` (predicted heading)
    16          ``velo_set`` (commanded speed)
    17          ``p_pos_L`` (predicted left position)
    18          ``p_pos_R`` (predicted right position)
    ==========  ===============================

* **Thread coordination**

  * Respects a global event ``read_stop``:

    - If set, the reader temporarily sleeps and skips serial I/O.
    - Used during firmware update so that the port is not actively read.

* **Data logging**

  * When the ``record_data`` event is set, each decoded sample is also
    appended to a shared ``recorded_data`` dictionary of lists keyed by
    the field names above.

Serial writer thread
^^^^^^^^^^^^^^^^^^^^

The ``SerialWriter`` function runs in a second daemon thread and is
responsible for sending commands to the robot. :contentReference[oaicite:9]{index=9}

* Watches a :class:`queue.Queue` named ``Ser_cmds``.
* When a command string is available, it:

  - Acquires ``serial_lock``.
  - Writes the command followed by ``"\r\n"`` to the serial port.
  - Calls ``ser.flush()``.

* Respects the ``write_stop`` event in the same way that the reader
  respects ``read_stop`` (for firmware update operations).

Tkinter GUI: ``RomiDisplay``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`RomiDisplay` is the main user–facing interface for monitoring
the robot and driving experiments. :contentReference[oaicite:10]{index=10}

Layout and displayed telemetry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The GUI window titled **“Live Romi Data”** displays a unified table
of:

* **Left motor**

  - Control signal (commanded duty, in %).
  - Predicted velocity vs. actual velocity (in/s).
  - Predicted displacement vs. actual displacement (in).

* **Right motor**

  - Control signal (commanded duty, in %).
  - Predicted vs. actual velocity (in/s).
  - Predicted vs. actual displacement (in).

* **Pose**

  - Predicted heading ``p_head`` vs. estimated Euler heading
    ``Eul_head`` (deg).
  - ``X`` and ``Y`` position (inches).
  - Line follower offset (in/s).
  - Yaw rate (deg/s).

All of these are backed by :class:`queue.Queue` instances created in
``Talker.py`` and passed into :class:`RomiDisplay` at construction time.
The display logic periodically calls ``update_display()`` via
``root.after(5, ...)``:

* Each queue is checked for new data.
* Numeric values are rounded to two decimal places.
* Relevant units conversions are applied (e.g. radians → degrees by
  multiplying with ~57.297). :contentReference[oaicite:11]{index=11}

Control widgets
^^^^^^^^^^^^^^^

The GUI also provides several controls:

* **Speed control**

  - An entry field for target speed (``SPD``).
  - An **“Update”** button that:

    * Optionally starts data recording (see below).
    * Enqueues the command string ``"$SPD<value>"`` into ``Ser_cmds``.

  - A **“STOP”** button that:

    * Sends ``"$SPD0"`` to the robot.
    * If data logging is enabled, triggers the plotting workflow.

* **Recording control**

  - A status label showing either *“Data Logging On”* or
    *“Data Logging Off”*.
  - A **“Record Data”** toggle button (``toggle_record``):

    * When turned on:

      - Sets ``record_enable``.
      - Clears all lists in the shared ``recorded_data`` dictionary.
      - Updates the status label.

    * When turned off:

      - Clears ``record_enable`` and updates the status label only.

  - Actual sample–by–sample logging is driven by the ``record_data``
    event inside :mod:`Talker`; :meth:`RomiDisplay.speed` starts
    logging for a run and :meth:`start_plotter` stops it.

* **Plotting**

  - A **“Plot”** button calls :meth:`start_plotter`, which:
    - Clears ``record_data`` (stops logging).
    - Sets the ``go_plot`` event to wake the plotting thread.

  - The :mod:`GoatedPlotter` module (imported but not included here)
    is expected to:

    * Wait until ``go_plot`` is set.
    * Consume the ``recorded_data`` dictionary.
    * Produce plots (via :mod:`matplotlib`) for analysis. :contentReference[oaicite:12]{index=12}

* **Firmware update**

  - The (unattached) **“Update Code”** button handler
    :meth:`update`:

    * Uses ``read_stop`` and ``write_stop`` events to temporarily halt
      serial I/O.
    * Runs an ``mpremote`` command such as:

      .. code-block:: bash

         mpremote connect COM9 cp -r ./src/. :

      to copy MicroPython source files from the local ``./src/`` folder
      to the robot. :contentReference[oaicite:13]{index=13}
    * Restarts a PuTTY session using the preconfigured *“Default
      Settings”* profile for interactive debugging.

Threading and Synchronisation
-----------------------------

The system uses standard :mod:`threading` primitives for coordination
between the GUI and background workers. :contentReference[oaicite:14]{index=14}

Events
~~~~~~

* ``record_data``

  - When set: :func:`SerialReader` logs each sample into
    ``recorded_data``.
  - When cleared: incoming data is still displayed live, but not written
    to the log.

* ``read_stop`` and ``write_stop``

  - When set: suspend serial reads / writes, respectively.
  - Used by :meth:`RomiDisplay.update` to safely perform firmware
    updates without racing the I/O threads.

* ``go_plot``

  - When set: plotting thread (``GoatedPlotter``) should generate
    plots from the current snapshot of ``recorded_data``.
  - Cleared before starting a new logging run.

Queues
~~~~~~

Each telemetry field has its own :class:`queue.Queue`, ensuring
thread–safe communication from ``SerialReader`` to :class:`RomiDisplay`:

* ``time_L``, ``time_R``
* ``pos_L``, ``pos_R``
* ``velo_L``, ``velo_R``
* ``cmd_L``, ``cmd_R``
* ``Eul_head``, ``yaw_rate``, ``offset``
* ``X_pos``, ``Y_pos``
* ``p_v_R``, ``p_v_L``, ``p_head``
* ``velo_set``, ``p_pos_L``, ``p_pos_R``

Commands from the GUI to the serial writer are funneled through the
``Ser_cmds`` queue.


    
    .. figure:: /images/pcui_gui.png
       :align: center
       :width: 600px

       The Tkinter GUI displaying real-time telemetry from the Romi robot.
    
    Type a speed command (inches per second) into the text box
    and click "Set Speed" to command the robot to move. Click "Stop"
    to halt the robot. Enable "Data Log" to record telemetry for later
    analysis. After stopping the robot, click "Plot Data" to generate
    plots and CSV exports from the recorded run.

    .. note::
        If data logging is enabled, the plotting engine
        (:mod:`GoatedPlotter`) will automatically run after
        clicking "Stop".

Plotting Engine: ``GoatedPlotter.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :func:`GoatedPlotter` function is the **central analysis tool** that
runs asynchronously in its own loop and is activated by the main GUI.

State machine
^^^^^^^^^^^^^

The function cycles between two states:

* **State 0 – idle:**  
  Waits until ``go_plot.is_set()`` becomes true.

* **State 1 – process & plot:**  
  Executes the entire data-analysis pipeline:
  - Input validation
  - Outlier cleaning
  - CSV export
  - Plot generation
  - Output image saving
  - Clearing data and returning to idle

Outlier cleaning
^^^^^^^^^^^^^^^^

A helper function :func:`clean_outliers` implements a **median absolute
deviation (MAD) filter**, replacing samples that deviate more than
``threshold × MAD`` with the average of their immediate neighbors.

.. note::
    The MAD filter is necessary becuase data corrupted during bluetooth
    transmission regularly produces very large or small values when the binary
    packet is decoded. These outliers would lead to illegible plots before this 
    filter was implemented.

CSV export
^^^^^^^^^^

At the beginning of state 1:

* A timestamped CSV file is created inside ``./test_data``.
* All data streams are saved as columns.
* Not all data streams are plotted, but **all** fields are still
  exported for offline research.

Timestamp normalization
^^^^^^^^^^^^^^^^^^^^^^^

Both ``time_L`` and ``time_R`` are converted from milliseconds to
seconds, and normalized so the first entry begins at ``t=0``.

.. note::
    Due to the controller configuration, there is very little difference
    between these data sets and for simplicity only ``time_L`` is used for
    plotting graphs that don't contain to wheel-specific data (eg, Heading).

Plot creation (2×2 grid)
^^^^^^^^^^^^^^^^^^^^^^^^

A figure is created which contains four subplots:

1. **Left Wheel Velocity + Command**
   - True vs. predicted velocity  
   - Command duty (%) on a twin y-axis

2. **Right Wheel Velocity + Command**
   - Same layout as the left wheel

3. **Velocity Setpoint vs Time with Checkpoints**
   - Setpoint trace over time
   - Vertical dashed lines marking inferred checkpoint times  
     (determined by matching X-position to path setpoints)
   - A textbox labeling the end time of the run

.. note::
    An earlier version of this scripts contained a subplot for heading
    vs. time, contianing both true and predicted values.

4. **XY Path with Reference Setpoints**
   - Actual trajectory (X,Y), mirrored across the +Y axis for plot
     convention
   - Red dots indicating path setpoints  
   - Equal axis scaling for geometric accuracy

Checkpoint detection
^^^^^^^^^^^^^^^^^^^^

The plotting script automatically derives the moment the robot reaches
each path setpoint:

* Iterates through target ``X_SP`` values.
* Finds the nearest future sample in measured ``X_pos``.
* Stores those times for annotation on the velocity-setpoint subplot.

This gives experimenters **automatic segmentation of runs** without
manual timestamp labeling.

.. warning::
    This function is experimental and can sometimes produce
    erronous results, espcially is Romi does not complete a complete run.

Saving outputs
^^^^^^^^^^^^^^

Two persistent artifacts are saved:

* **CSV file** in ``test_data/romi_data_<timestamp>.csv``
* **PNG figure** in ``plots/<timestamp>.png`` (high-resolution)
