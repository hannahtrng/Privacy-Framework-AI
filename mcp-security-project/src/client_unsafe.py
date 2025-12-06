import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# --- Define the Sensitive Data ---
# This simulates the PII and secret key the LLM agent generated from a user prompt.
SENSITIVE_USER_ID = "SSN-999-00-1234" # Critical PII
SECRET_KEY = "SECURE-A1B2-C3D4"       # Required Authorization Key

# --- Client Logic ---
async def run_client():
    print("[CLIENT-UNSAFE]: Preparing unsafe call to external [TOOL]...")

    # 1. Set up server parameters
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "server.py"],
    )

    # 2. Connect to the server via stdio
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 3. Initialize the connection
            await session.initialize()

            # 4. Get the tools available from the server
            tools_list = await session.list_tools()
            print(f"Client recognized tool: {tools_list.tools[0].name}")

            # 5. Create and execute the Tool Call
            print(f"CLIENT: Sending sensitive payload: {SENSITIVE_USER_ID}")
            
            try:
                result = await session.call_tool(
                    name="sensitive_data_lookup",
                    arguments={
                        "user_id": SENSITIVE_USER_ID,
                        "private_key": SECRET_KEY,
                    }
                )
                
                # 6. Process the result
                print("--- CLIENT RECEIVED RESULT ---")
                for content in result.content:
                    if content.type == "text":
                        print(f"Result: {content.text}")
            except Exception as e:
                print(f"CLIENT ERROR: {e}")
            

if __name__ == "__main__":
    asyncio.run(run_client())