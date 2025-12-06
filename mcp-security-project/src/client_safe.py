import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# --- Define the Sensitive Data ---
# This simulates the PII and secret key the LLM agent generated from a user prompt.
SENSITIVE_USER_ID = "SSN-999-00-1234" # Critical PII
SECRET_KEY = "SECURE-A1B2-C3D4"       # Required Authorization Key

# --- Client Logic ---
async def run_client():
    print("[CLIENT-SAFE]: Preparing to call [TOOL] with sensitive data")
    print(f"CLIENT: User ID contains: {SENSITIVE_USER_ID}")
    print(f"CLIENT: Private key: {SECRET_KEY}")
    print("="*70 + "\n")

    # CRITICAL CHANGE: Connect to proxy_server.py instead of server.py
    # The proxy will intercept, apply privacy protection, then forward to server.py
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "proxy_server.py"],  # ← Connect to PROXY, not server
    )

    # Connect to the proxy via stdio
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get the tools available from the proxy (which forwards from server)
            tools_list = await session.list_tools()
            print(f"CLIENT: Recognized tool: {tools_list.tools[0].name}")
            print(f"CLIENT: Tool description: {tools_list.tools[0].description}\n")

            # Create and execute the Tool Call
            print(f"CLIENT: Calling tool with UNPROTECTED sensitive data...")
            print(f"CLIENT: (CAPEF Proxy will intercept and protect)\n")
            
            try:
                result = await session.call_tool(
                    name="sensitive_data_lookup",
                    arguments={
                        "user_id": SENSITIVE_USER_ID,
                        "private_key": SECRET_KEY,
                    }
                )
                
                # Process the result
                print("\n" + "="*70)
                print("CLIENT: RECEIVED RESULT FROM PROXY")
                print("="*70)
                for content in result.content:
                    if content.type == "text":
                        print(f"Result: {content.text}")
                print("="*70 + "\n")
                
            except Exception as e:
                print("\n" + "="*70)
                print("CLIENT: REQUEST FAILED")
                print("="*70)
                print(f"Error: {e}")
                print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(run_client())