"""Cooperative task scheduler for MicroPython.

This module implements a simple cooperative multitasking framework based on
generator functions. Each task is written as a generator that yields its
current state; a scheduler then resumes each task in turn according to a
chosen policy (round-robin or highest-priority-first).

This file is **adapted from** John R. Ridgely's original ``cotask.py``
cooperative scheduler. The original work is:

    Copyright (c) 2017–2023 by J. R. Ridgely

and is released under the GNU General Public License, version 3 (GPLv3).
The license and copyright remain the
same as in the original source.

It is intended for educational use, but its use is not limited thereto.
THE SOFTWARE IS PROVIDED “AS IS” WITHOUT WARRANTY OF ANY KIND; see the
full GPLv3 license text for details.
"""

import gc                      # Memory allocation garbage collector
import utime                   # MicroPython time library
import micropython             # Used for @micropython.native hints


class Task:
    """Cooperative multitasking task.

    Instances of :class:`Task` wrap a generator function which implements the
    task's behavior as a simple state machine. Each time the scheduler calls
    :meth:`schedule`, the underlying generator is advanced to its next
    ``yield`` and the current state value is recorded.

    Tasks can be run periodically based on a time period, or triggered
    explicitly via :meth:`go`. Basic profiling (run time and scheduling
    latency) and optional transition tracing are also supported.

    Example:
        .. code-block:: python

            import cotask

            def task1_fun():
                \"\"\"Simple two-state example task.\"\"\"
                state = 0
                while True:
                    if state == 0:
                        state = 1
                    else:
                        state = 0
                    yield state

            # In main, create this task and set it to run twice per second
            task1 = cotask.Task(
                task1_fun,
                name="Task 1",
                priority=1,
                period=500,      # ms
                profile=True,
                trace=True,
            )

            cotask.task_list.append(task1)

            while True:
                cotask.task_list.pri_sched()
    """

    def __init__(
        self,
        run_fun,
        name: str = "NoName",
        priority: int = 0,
        period=None,
        profile: bool = False,
        trace: bool = False,
        shares=(),
    ):
        """Initialize a :class:`Task` so it can be run by the scheduler.

        Args:
            run_fun: The function which implements the task's code. It must
                be a generator function which yields the current state
                value each time it runs.
            name: Human-readable task name (default ``"NoName"``).
            priority: Task priority; larger numbers mean higher priority.
            period: Period between runs in **milliseconds** (``int`` or
                ``float``). If ``None``, the task is not time-scheduled and
                is instead awakened by :meth:`go`.
            profile: If ``True``, enable run-time profiling of the task's
                execution time and scheduling latency.
            trace: If ``True``, record a list of state transitions along with
                timing information. This slows execution and allocates memory.
            shares: Optional list or tuple of share/queue objects used by
                this task. If provided, it is passed into ``run_fun``.
        """
        # Run the generator function to obtain the generator object itself
        if shares:
            self._run_gen = run_fun(shares)
        else:
            self._run_gen = run_fun()

        #: Short descriptive name for the task.
        self.name = name

        #: Priority (integer); larger means higher scheduling priority.
        self.priority = int(priority)

        #: Period between runs, in microseconds (internal representation).
        if period is not None:
            self.period = int(period * 1000)
            self._next_run = utime.ticks_us() + self.period
        else:
            self.period = period
            self._next_run = None

        # Profiling and trace configuration
        self._prof = profile
        self.reset_profile()
        self._prev_state = 0
        self._trace = trace
        self._tr_data = []
        self._prev_time = utime.ticks_us()

        #: Flag set to ``True`` when the task is ready to run.
        self.go_flag = False

    def schedule(self) -> bool:
        """Attempt to run this task once.

        If the task is not ready to run yet (see :meth:`ready`), this method
        returns ``False`` immediately. If the task *is* ready, it runs the
        generator up to the next ``yield``, updates profiling/trace data, and
        returns ``True``.

        Returns:
            bool: ``True`` if the task ran, ``False`` otherwise.
        """
        if self.ready():

            # Reset the go flag for the next run
            self.go_flag = False

            # If profiling, save the start time
            if self._prof:
                stime = utime.ticks_us()

            # Run the generator for one step
            curr_state = next(self._run_gen)

            # If profiling or tracing, save timing data
            if self._prof or self._trace:
                etime = utime.ticks_us()

            # If profiling, save timing data
            if self._prof:
                self._runs += 1
                runt = utime.ticks_diff(etime, stime)
                if self._runs > 2:
                    self._run_sum += runt
                    if runt > self._slowest:
                        self._slowest = runt

            # If transition tracing is on, record a transition; if not, ignore
            if self._trace:
                try:
                    if curr_state != self._prev_state:
                        self._tr_data.append(
                            (utime.ticks_diff(etime, self._prev_time),
                             curr_state)
                        )
                except MemoryError:
                    self._trace = False
                    gc.collect()

                self._prev_state = curr_state
                self._prev_time = etime

            return True

        else:
            return False

    @micropython.native
    def ready(self) -> bool:
        """Check whether this task is ready to run.

        If the task is periodic, this method checks the current time against
        the next scheduled run time and updates :attr:`go_flag` accordingly.
        If the task is not periodic, the flag is only set by :meth:`go`.

        Returns:
            bool: ``True`` if the task is ready to run.
        """
        # If this task uses a timer, check if it's time to run again
        if self.period is not None:
            late = utime.ticks_diff(utime.ticks_us(), self._next_run)
            if late > 0:
                self.go_flag = True
                self._next_run = utime.ticks_diff(self.period,
                                                  -self._next_run)

                # If keeping a latency profile, record the data
                if self._prof:
                    self._late_sum += late
                    if late > self._latest:
                        self._latest = late

        # If the task doesn't use a timer, rely on go_flag
        return self.go_flag

    def set_period(self, new_period):
        """Change the time period between task runs.

        Args:
            new_period: New period in milliseconds, or ``None`` if the task
                should only be triggered via :meth:`go`.
        """
        if new_period is None:
            self.period = None
        else:
            self.period = int(new_period) * 1000

    def reset_profile(self):
        """Reset the variables used for execution time profiling."""
        self._runs = 0
        self._run_sum = 0
        self._slowest = 0
        self._late_sum = 0
        self._latest = 0

    def get_trace(self) -> str:
        """Return a string containing the task's transition trace.

        The trace is a sequence of lines, each containing a time stamp and
        the state value to which the task transitioned.

        Returns:
            str: Multi-line description of the recorded transitions, or a
            short message if tracing was disabled.
        """
        tr_str = "Task " + self.name + ":"
        if self._trace:
            tr_str += "\n"
            last_state = 0
            total_time = 0.0
            for item in self._tr_data:
                total_time += item[0] / 1_000_000.0
                tr_str += "{: 12.6f}: {: 2d} -> {:d}\n".format(
                    total_time, last_state, item[1]
                )
                last_state = item[1]
        else:
            tr_str += " not traced"
        return tr_str

    def go(self):
        """Mark this task as ready to run.

        This method is typically called by an interrupt handler or another
        task that has produced data which this task should process soon.
        """
        self.go_flag = True

    def __repr__(self) -> str:
        """Return a diagnostic string describing this task.

        The string includes the task's name, priority, period, run count,
        and (if profiling is enabled and has run) average and worst-case
        execution time and latency.
        """
        rst = f"{self.name:<16s}{self.priority: 4d}"
        try:
            rst += f"{(self.period / 1000.0): 10.1f}"
        except TypeError:
            rst += "         -"
        rst += f"{self._runs: 8d}"

        if self._prof and self._runs > 0:
            avg_dur = (self._run_sum / self._runs) / 1000.0
            avg_late = (self._late_sum / self._runs) / 1000.0
            rst += f"{avg_dur: 10.3f}{(self._slowest / 1000.0): 10.3f}"
            if self.period is not None:
                rst += f"{avg_late: 10.3f}{(self._latest / 1000.0): 10.3f}"
        return rst


class TaskList:
    """List of tasks managed by the scheduler.

    The task list groups tasks by priority and provides two scheduling
    methods:

    * :meth:`rr_sched` – simple round-robin execution.
    * :meth:`pri_sched` – highest-priority-first execution.

    In normal use, a single global :data:`task_list` is created when this
    module is imported, and user code adds tasks to that list.
    """

    def __init__(self):
        """Create an empty task list."""
        #: List of priority groups. Each element is of the form
        #: ``[priority, index, task, task, ...]``.
        self.pri_list = []

    def append(self, task: Task):
        """Append a task to the task list.

        Tasks are stored in sub-lists grouped by priority; the outer list
        is kept sorted from highest to lowest priority.

        Args:
            task: :class:`Task` instance to append.
        """
        new_pri = task.priority
        for pri in self.pri_list:
            if pri[0] == new_pri:
                pri.append(task)
                break
        else:
            self.pri_list.append([new_pri, 2, task])

        self.pri_list.sort(key=lambda pri: pri[0], reverse=True)

    @micropython.native
    def rr_sched(self):
        """Run tasks in round-robin order, ignoring priorities."""
        for pri in self.pri_list:
            for task in pri[2:]:
                task.schedule()

    @micropython.native
    def pri_sched(self):
        """Run the highest-priority ready task.

        Within each priority level, tasks are scheduled in round-robin
        order. This method returns after the first task which actually runs.
        """
        for pri in self.pri_list:
            tries = 2
            length = len(pri)
            while tries < length:
                ran = pri[pri[1]].schedule()
                tries += 1
                pri[1] += 1
                if pri[1] >= length:
                    pri[1] = 2
                if ran:
                    return

    def __repr__(self) -> str:
        """Return diagnostic text showing all tasks in the list."""
        ret_str = (
            "TASK             PRI    PERIOD    RUNS   AVG DUR   MAX "
            "DUR  AVG LATE  MAX LATE\n"
        )
        for pri in self.pri_list:
            for task in pri[2:]:
                ret_str += str(task) + "\n"

        return ret_str


#: Global task list created on import; user code appends tasks here and
#: calls :meth:`TaskList.rr_sched` or :meth:`TaskList.pri_sched` from the
#: main loop.
task_list = TaskList()