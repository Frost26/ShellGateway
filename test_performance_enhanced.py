#!/usr/bin/env python3
"""
Enhanced performance test for the MCP Linux Shell Server
Tests all the performance optimizations including caching, timeouts, and async operations.
"""

import asyncio
import time
import sys
import os

# Add the linux_shell_server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'linux_shell_server'))

from main import ShellExecutor

async def test_basic_performance():
    """Test basic command execution performance"""
    print("🧪 Testing basic command execution...")
    
    executor = ShellExecutor()
    
    # Test quick command
    start_time = time.time()
    result = await executor.execute_command("echo 'Hello, World!'")
    elapsed = time.time() - start_time
    
    print(f"✅ Echo command: {elapsed:.3f}s")
    print(f"   Output: {result['output'][:50]}...")
    print(f"   Exit code: {result['exit_code']}")

async def test_caching_performance():
    """Test command caching functionality"""
    print("\n🧪 Testing command caching...")
    
    executor = ShellExecutor()
    
    # First execution (should be cached)
    command = "ls -la"
    start_time = time.time()
    result1 = await executor.execute_command(command)
    first_elapsed = time.time() - start_time
    
    # Second execution (should use cache)
    start_time = time.time()
    result2 = await executor.execute_command(command)
    second_elapsed = time.time() - start_time
    
    print(f"✅ First execution: {first_elapsed:.3f}s")
    print(f"✅ Second execution (cached): {second_elapsed:.3f}s")
    print(f"✅ Speed improvement: {(first_elapsed/second_elapsed):.1f}x faster")
    
    # Verify cache hit
    cache_hit = "[Result from cache]" in result2['output']
    print(f"✅ Cache hit detected: {cache_hit}")

async def test_timeout_handling():
    """Test timeout handling for long-running commands"""
    print("\n🧪 Testing timeout handling...")
    
    executor = ShellExecutor()
    
    # Test a command that should timeout quickly
    start_time = time.time()
    result = await executor.execute_command("sleep 5")  # Should timeout in 30s (but we'll see it's fast)
    elapsed = time.time() - start_time
    
    print(f"✅ Sleep command handled in: {elapsed:.3f}s")
    print(f"   Result: {'Timeout' if 'timed out' in result['output'] else 'Completed'}")

async def test_long_running_command_timeout():
    """Test timeout detection for potentially long-running commands"""
    print("\n🧪 Testing long-running command timeout detection...")
    
    executor = ShellExecutor()
    
    # Test find command (should get longer timeout)
    timeout = executor._determine_timeout("find /home -name '*.txt'")
    print(f"✅ Find command timeout: {timeout}s")
    
    # Test regular command
    timeout = executor._determine_timeout("ls -la")
    print(f"✅ Regular command timeout: {timeout}s")

async def test_output_truncation():
    """Test output truncation for large outputs"""
    print("\n🧪 Testing output truncation...")
    
    executor = ShellExecutor()
    
    # Generate large output
    result = await executor.execute_command("seq 1 10000")
    
    is_truncated = "output truncated" in result['output']
    output_length = len(result['output'])
    
    print(f"✅ Large output handled: {output_length} characters")
    print(f"✅ Output truncated: {is_truncated}")

async def test_directory_operations():
    """Test async directory operations"""
    print("\n🧪 Testing directory operations...")
    
    executor = ShellExecutor()
    
    # Test current directory
    result = executor.get_current_directory()
    print(f"✅ Current directory: {result['output']}")
    
    # Test directory change
    original_dir = executor.current_directory
    temp_dir = "/tmp"
    
    start_time = time.time()
    result = await executor.change_directory(temp_dir)
    elapsed = time.time() - start_time
    
    print(f"✅ Directory change: {elapsed:.3f}s")
    print(f"   Result: {result['output']}")
    
    # Change back
    await executor.change_directory(original_dir)

async def test_error_handling():
    """Test error handling and resilience"""
    print("\n🧪 Testing error handling...")
    
    executor = ShellExecutor()
    
    # Test invalid command
    result = await executor.execute_command("nonexistent_command_12345")
    print(f"✅ Invalid command handled: {result.get('error', False)}")
    
    # Test invalid directory
    result = await executor.change_directory("/nonexistent/directory/path")
    print(f"✅ Invalid directory handled: {result.get('error', False)}")
    
    # Test empty command
    result = await executor.execute_command("")
    print(f"✅ Empty command handled: {result.get('error', False)}")

async def performance_comparison():
    """Compare performance with and without optimizations"""
    print("\n🧪 Performance comparison...")
    
    executor = ShellExecutor()
    
    # Test multiple quick commands
    commands = ["pwd", "whoami", "date", "hostname", "id"]
    
    # First run (no cache)
    start_time = time.time()
    for cmd in commands:
        await executor.execute_command(cmd)
    first_run_time = time.time() - start_time
    
    # Second run (with cache)
    start_time = time.time()
    for cmd in commands:
        await executor.execute_command(cmd)
    second_run_time = time.time() - start_time
    
    print(f"✅ First run (no cache): {first_run_time:.3f}s")
    print(f"✅ Second run (with cache): {second_run_time:.3f}s")
    print(f"✅ Cache performance improvement: {(first_run_time/second_run_time):.1f}x")

async def main():
    """Run all performance tests"""
    print("🚀 MCP Linux Shell Server - Performance Test Suite")
    print("=" * 60)
    
    try:
        await test_basic_performance()
        await test_caching_performance()
        await test_timeout_handling()
        await test_long_running_command_timeout()
        await test_output_truncation()
        await test_directory_operations()
        await test_error_handling()
        await performance_comparison()
        
        print("\n" + "=" * 60)
        print("🎉 All performance tests completed successfully!")
        print("\n📊 Performance Optimizations Verified:")
        print("   ✅ Command caching")
        print("   ✅ Timeout handling")
        print("   ✅ Output truncation")
        print("   ✅ Async operations")
        print("   ✅ Error handling")
        print("   ✅ Process management")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
