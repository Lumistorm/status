# Status

A lightweight library for progress bars, status messages, and runtime information.

**Status** provides simple, low-overhead utilities for monitoring tasks.

## Example

```python
from status import Progress
import time

for _ in Progress(range(100), description='Processing'):
    pass
```

Output:

```
Processing |████████████████████████████████| 100% | 100/100 | ETA 0s | 2.0 it/s
```
Processing: [██████████] 100.0% 100/100 it 0.0ms
```
