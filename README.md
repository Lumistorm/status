# Status

A lightweight library for progress bars, status messages, and runtime information.

**Status** provides simple, low-overhead utilities for monitoring tasks.

## Example

```python
from status import Progress
import time

for _ in Progress(range(100), description='Processing'):
    pass
