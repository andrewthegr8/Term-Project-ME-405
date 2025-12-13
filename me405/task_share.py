"""Task-safe queues and shared variables for cooperative multitasking.

This module provides :class:`Queue` and :class:`Share` classes that allow
tasks to exchange data safely in a MicroPython cooperative multitasking
environment. Transfers can be protected against corruption by interrupt
handlers or pre-emptive threads using simple critical sections.

This file is **adapted from** John R. Ridgely's original ``task_share.py``
module. The original work is:

    Copyright (c) 2017–2023 by J. R. Ridgely

and is released under the GNU General Public License, version 3 (GPLv3).
This adapted version keeps the original logic (plus your local additions such
as :meth:`Queue.view` and :meth:`Queue.many`) but replaces Doxygen-style
comments with Sphinx/ReadTheDocs-friendly docstrings so that the API can be
documented using ``autodoc``. The license and copyright remain the same as
in the original source.:contentReference[oaicite:1]{index=1}

It is intended for educational use, but its use is not limited thereto.
THE SOFTWARE IS PROVIDED “AS IS” WITHOUT WARRANTY OF ANY KIND; see the
full GPLv3 license text for details.
"""

import array
import gc
import pyb
import micropython


#: Global list of all queues and shares, used for diagnostics.
share_list = []

#: Human-readable names for the ``array`` type codes used by :class:`Queue`
#: and :class:`Share`.
type_code_strings = {
    "b": "int8",
    "B": "uint8",
    "h": "int16",
    "H": "uint16",
    "i": "int(?)",
    "I": "uint(?)",
    "l": "int32",
    "L": "uint32",
    "q": "int64",
    "Q": "uint64",
    "f": "float",
    "d": "double",
}


def show_all() -> str:
    """Return a diagnostic string describing all queues and shares.

    The returned string contains one line per :class:`Queue` or
    :class:`Share` instance currently registered in :data:`share_list`.
    """
    gen = (str(item) for item in share_list)
    return "\n".join(gen)


class BaseShare:
    """Base class for queues and shares which exchange data between tasks.

    This class is not used directly by user code; it implements behavior that
    is common to both :class:`Queue` and :class:`Share`, such as storing the
    type code and registering the object in :data:`share_list`.
    """

    def __init__(self, type_code: str, thread_protect: bool = True, name=None):
        """Initialize data shared between queues and shares.

        Args:
            type_code: Single-letter type code as used by :mod:`array`.
            thread_protect: If ``True``, operations will disable interrupts
                to avoid data corruption in pre-emptive environments.
            name: Optional human-readable name for diagnostics.
        """
        self._type_code = type_code
        self._thread_protect = thread_protect

        # Add this instance to the global diagnostics list
        share_list.append(self)


class Queue(BaseShare):
    """FIFO queue for transferring data between tasks.

    A :class:`Queue` buffers items of a single :mod:`array` type. Transfers
    can optionally be protected from interrupt-based corruption by disabling
    interrupts during put/get operations.

    Example:
        .. code-block:: python

            import task_share

            # Queue of unsigned 16-bit integers
            my_queue = task_share.Queue('H', 100, name="My Queue")

            # Producer task
            def producer():
                while True:
                    if not my_queue.full():
                        my_queue.put(some_data())
                    yield 0

            # Consumer task
            def consumer():
                while True:
                    if my_queue.any():
                        value = my_queue.get()
                        process(value)
                    yield 0
    """

    #: Counter used to give serial numbers to queues for diagnostics.
    ser_num = 0

    def __init__(
        self,
        type_code: str,
        size: int,
        thread_protect: bool = False,
        overwrite: bool = False,
        name=None,
    ):
        """Create a queue object to carry and buffer data between tasks.

        Args:
            type_code: One-letter :mod:`array` type code for queue contents
                (for example ``"h"`` for signed 16-bit integers).
            size: Maximum number of items the queue can hold.
            thread_protect: If ``True``, disable/restore interrupts during
                put/get operations to avoid data corruption.
            overwrite: If ``True``, allow new data to overwrite old data when
                the queue becomes full. If ``False``, callers must ensure the
                queue is not full before calling :meth:`put`.
            name: Optional short name used in diagnostics. If omitted, a
                default name of the form ``"QueueN"`` is generated.
        """
        super().__init__(type_code, thread_protect, name)

        self._size = size
        self._overwrite = overwrite
        self._name = str(name) if name is not None else f"Queue{Queue.ser_num}"
        Queue.ser_num += 1

        # Allocate storage for the queue
        try:
            self._buffer = array.array(type_code, range(size))
        except (MemoryError, ValueError):
            self._buffer = None
            raise

        # Initialize pointers and counters
        self.clear()

        # Tidy up memory after allocation
        gc.collect()

    @micropython.native
    def put(self, item, in_ISR: bool = False):
        """Put an item into the queue.

        If the queue is full and ``overwrite`` is ``False``, this method
        will busy-wait until space becomes available, unless called from an
        interrupt service routine (``in_ISR=True``), in which case it returns
        immediately.

        Args:
            item: Item to insert into the buffer.
            in_ISR: Set to ``True`` if called from an interrupt handler.
        """
        if self.full():
            if in_ISR:
                return

            if not self._overwrite:
                while self.full():
                    pass

        if self._thread_protect and not in_ISR:
            _irq_state = pyb.disable_irq()

        self._buffer[self._wr_idx] = item
        self._wr_idx += 1
        if self._wr_idx >= self._size:
            self._wr_idx = 0
        self._num_items += 1
        if self._num_items >= self._size:
            self._num_items = self._size
        if self._num_items > self._max_full:
            self._max_full = self._num_items

        if self._thread_protect and not in_ISR:
            pyb.enable_irq(_irq_state)

    @micropython.native
    def get(self, in_ISR: bool = False):
        """Read and remove the oldest item from the queue.

        This version has been adapted so that it **does not block** if the
        queue is empty; instead it raises :class:`ValueError`.

        Args:
            in_ISR: Set to ``True`` if called from an interrupt handler.

        Raises:
            ValueError: If the queue is empty when called.

        Returns:
            The oldest item from the buffer.
        """
        if self.empty():
            raise ValueError("You tried to get from an empty queue")

        if self._thread_protect and not in_ISR:
            irq_state = pyb.disable_irq()

        to_return = self._buffer[self._rd_idx]

        self._rd_idx += 1
        if self._rd_idx >= self._size:
            self._rd_idx = 0
        self._num_items -= 1
        if self._num_items < 0:
            self._num_items = 0

        if self._thread_protect and not in_ISR:
            pyb.enable_irq(irq_state)

        return to_return

    def view(self, in_ISR: bool = False):
        """Return the most recently written item without removing it.

        This is a local extension: it allows one to *peek* at the newest
        value in the queue while leaving the buffer unchanged.

        Args:
            in_ISR: Set to ``True`` if called from an interrupt handler.

        Raises:
            ValueError: If the queue is empty.

        Returns:
            The most recently enqueued item.
        """
        if self.empty():
            raise ValueError("You tried to view an empty queue")

        if self._thread_protect and not in_ISR:
            irq_state = pyb.disable_irq()

        item = self._buffer[self._wr_idx - 1]

        if self._thread_protect and not in_ISR:
            pyb.enable_irq(irq_state)

        return item

    @micropython.native
    def any(self) -> bool:
        """Return ``True`` if there is at least one item in the queue."""
        return self._num_items > 0

    @micropython.native
    def many(self) -> bool:
        """Return ``True`` if there is more than one item in the queue."""
        return self._num_items > 1

    @micropython.native
    def empty(self) -> bool:
        """Return ``True`` if the queue is empty."""
        return self._num_items <= 0

    @micropython.native
    def full(self) -> bool:
        """Return ``True`` if the queue is full."""
        return self._num_items >= self._size

    @micropython.native
    def num_in(self) -> int:
        """Return the number of items currently in the queue."""
        return self._num_items

    def clear(self):
        """Remove all contents from the queue and reset counters."""
        self._rd_idx = 0
        self._wr_idx = 0
        self._num_items = 0
        self._max_full = 0

    def __repr__(self) -> str:
        """Return a concise diagnostic representation of this queue."""
        return "{:<12s} Queue<{:s}> Max Full {:d}/{:d}".format(
            self._name,
            type_code_strings[self._type_code],
            self._max_full,
            self._size,
        )


class Share(BaseShare):
    """Single shared data item used to transfer values between tasks.

    A :class:`Share` holds one value of a given :mod:`array` type. Access can
    be protected by disabling interrupts for the duration of each put/get to
    avoid corruption in pre-emptive environments.

    Example:
        .. code-block:: python

            import task_share

            # Signed 16-bit shared value
            my_share = task_share.Share('h', name="My Share")

            # Writer
            my_share.put(42)

            # Reader
            value = my_share.get()
    """

    #: Counter used to give serial numbers to shares for diagnostics.
    ser_num = 0

    def __init__(self, type_code: str, thread_protect: bool = True, name=None):
        """Create a new shared data item.

        Args:
            type_code: Single-letter :mod:`array` type code for the stored
                value.
            thread_protect: If ``True``, protect access with interrupt
                disable/enable.
            name: Optional short name used in diagnostics.
        """
        super().__init__(type_code, thread_protect, name)

        self._buffer = array.array(type_code, [0])

        self._name = str(name) if name is not None else f"Share{Share.ser_num}"
        Share.ser_num += 1

    @micropython.native
    def put(self, data, in_ISR: bool = False):
        """Write an item of data into the share.

        Args:
            data: Value to be written.
            in_ISR: Set to ``True`` if called from an interrupt handler.
        """
        if self._thread_protect and not in_ISR:
            irq_state = pyb.disable_irq()

        self._buffer[0] = data

        if self._thread_protect and not in_ISR:
            pyb.enable_irq(irq_state)

    @micropython.native
    def get(self, in_ISR: bool = False):
        """Read the current value from the share.

        Args:
            in_ISR: Set to ``True`` if called from an interrupt handler.

        Returns:
            The current value stored in the share.
        """
        if self._thread_protect and not in_ISR:
            irq_state = pyb.disable_irq()

        to_return = self._buffer[0]

        if self._thread_protect and not in_ISR:
            pyb.enable_irq(irq_state)

        return to_return

    def __repr__(self) -> str:
        """Return a concise diagnostic representation of this share."""
        return "{:<12s} Share<{:s}>".format(
            self._name, type_code_strings[self._type_code]
        )