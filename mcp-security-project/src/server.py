import asyncio
import sys
import mcp.server.stdio
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import Field
import os

# --- 1. Create the Server ---
server = Server("sensitive-data-server")

# --- 2. Define the Tool using a decorator ---
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="sensitive_data_lookup",
            description="Looks up sensitive user information in a simulated internal database using a unique user ID and a cryptographic key for verification.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique, sensitive identifier of the user (e.g., account number or SSN)."
                    },
                    "private_key": {
                        "type": "string",
                        "description": "The secret cryptographic key required to authorize the data lookup."
                    }
                },
                "required": ["user_id", "private_key"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "sensitive_data_lookup":
        user_id = arguments.get("user_id")
        private_key = arguments.get("private_key")
        
        # USE STDERR FOR LOGGING (not stdout!)
        # --- Decide banner based on whether inputs look redacted ---
        protected = False
        if isinstance(user_id, str) and "SSN-***-**-****" in user_id:
            protected = True
        if private_key == "REDACTED":
            protected = True

        print(f"\n--- SERVER RECEIVED TOOL CALL ({'Protected' if protected else 'Unprotected'}) ---\n",
            file=sys.stderr, flush=True)
        print(f"Received User ID {'(CRITICAL EXPOSURE):' if not protected else ':'} {user_id}",
            file=sys.stderr, flush=True)
        print(f"Received Private Key: {private_key}", file=sys.stderr, flush=True)
        print(f"---------------------------------\n", file=sys.stderr, flush=True)
       
        # --- DEMO TOGGLE (make parsing forgiving) ---
        ACCEPT_REDACTED_IN_DEMO = os.getenv("ACCEPT_REDACTED_IN_DEMO", "").strip().lower() in ("1", "true", "yes", "on")

        # --- HAPPY CASE (DEMO): allow success when key was redacted ---
        if isinstance(private_key, str) and private_key.strip() == "REDACTED" and ACCEPT_REDACTED_IN_DEMO:
            return [TextContent(type="text", text="SUCCESS (demo): privacy-preserving lookup completed.")]

        # --- REAL HAPPY CASE ---
        if private_key == "SECURE-A1B2-C3D4":
            return [TextContent(type="text", text="SUCCESS")]

        # --- FAILURE (return text, DON'T raise) ---
        return [TextContent(type="text", text="Authorization failed: The private key provided was invalid.")]


# --- 3. Run the Server ---
async def main():
    print("Starting CAPEF Server (listening for tool calls on stdio)...", file=sys.stderr, flush=True)
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())