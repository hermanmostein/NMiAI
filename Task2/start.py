"""
Startup script for the Tripletex AI Accounting Agent.

Reads HOST and PORT from environment variables so that Railway's injected
$PORT value is resolved by Python rather than the shell, avoiding the
"'$PORT' is not a valid integer" error that occurs when uvicorn is invoked
directly without shell interpretation.
"""

import os
import uvicorn

host = os.environ.get("HOST", "0.0.0.0")
port = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    uvicorn.run("main:app", host=host, port=port)
