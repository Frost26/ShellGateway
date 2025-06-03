#!/usr/bin/env python3
"""
Simple performance test for the MCP Linux Shell Server
"""

import asyncio
import time
import sys
import os

print("🚀 Starting simple performance test...")

# Add the linux_shell_server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'linux_shell_server'))

try:
    from main import ShellExecutor
    print("✅ Successfully imported ShellExecutor")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

async def simple_test():
    """Simple test of basic functionality"""
    print("🧪 Testing basic command execution...")
    
    executor = ShellExecutor()
    
    # Test quick command
    start_time = time.time()
    result = await executor.execute_command("echo 'Hello, World!'")
    elapsed = time.time() - start_time
    
    print(f"✅ Echo command: {elapsed:.3f}s")
    print(f"   Exit code: {result['exit_code']}")
    print(f"   Has output: {'Hello' in result['output']}")
    
    # Test caching
    print("\n🧪 Testing caching...")
    cmd = "pwd"
    
    # First run
    start_time = time.time()
    result1 = await executor.execute_command(cmd)
    first_time = time.time() - start_time
    
    # Second run (should be cached)
    start_time = time.time()
    result2 = await executor.execute_command(cmd)
    second_time = time.time() - start_time
    
    print(f"✅ First run: {first_time:.3f}s")
    print(f"✅ Second run: {second_time:.3f}s")
    print(f"✅ Cache hit: {'[Result from cache]' in result2['output']}")
    
    print("\n🎉 Simple test completed successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(simple_test())
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
