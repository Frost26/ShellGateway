#!/usr/bin/env python3
"""
Quick performance test for the enhanced Linux shell server
"""

import asyncio
import time
from linux_shell_server.main import ShellExecutor

async def test_performance():
    """Test the performance improvements"""
    print("Testing enhanced Linux shell server performance...")
    
    executor = ShellExecutor()
    
    # Test 1: Basic command
    print("\n1. Testing basic command...")
    start = time.time()
    result = await executor.execute_command("echo 'Hello World'")
    duration = time.time() - start
    print(f"   Duration: {duration:.3f}s")
    print(f"   Error: {result['error']}")
    print(f"   Exit code: {result['exit_code']}")
    
    # Test 2: Cached command (should be faster on second run)
    print("\n2. Testing command caching...")
    start = time.time()
    result1 = await executor.execute_command("pwd")
    duration1 = time.time() - start
    
    start = time.time()
    result2 = await executor.execute_command("pwd")  # Should be cached
    duration2 = time.time() - start
    
    print(f"   First run: {duration1:.3f}s")
    print(f"   Second run: {duration2:.3f}s")
    print(f"   Cached: {'[Result from cache]' in result2['output']}")
    
    # Test 3: Timeout handling (short timeout for demo)
    print("\n3. Testing timeout handling...")
    try:
        # This should timeout quickly
        executor._determine_timeout = lambda cmd: 1  # Override timeout to 1 second
        start = time.time()
        result = await executor.execute_command("sleep 3")
        duration = time.time() - start
        print(f"   Duration: {duration:.3f}s")
        print(f"   Result: Command should have timed out")
    except Exception as e:
        duration = time.time() - start
        print(f"   Duration: {duration:.3f}s")
        print(f"   Timeout handled correctly: {type(e).__name__}")
    
    # Test 4: Directory operations
    print("\n4. Testing async directory operations...")
    start = time.time()
    result = await executor.change_directory("/tmp")
    duration = time.time() - start
    print(f"   Duration: {duration:.3f}s")
    print(f"   Success: {not result['error']}")
    print(f"   Current dir: {executor.current_directory}")
    
    print("\n✅ Performance tests completed!")

if __name__ == "__main__":
    asyncio.run(test_performance())
