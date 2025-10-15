#!/usr/bin/env python3
"""
Test script for MCP Protocol Server
"""

import asyncio
import json
import websockets
import requests
import sys


async def test_mcp_websocket():
    """Test MCP server via WebSocket"""
    print("Testing MCP WebSocket connection...")
    
    uri = "ws://localhost:8080/mcp"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ WebSocket connection established")
            
            # Test initialize
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            await websocket.send(json.dumps(init_message))
            print("✓ Sent initialize message")
            
            response = await websocket.recv()
            result = json.loads(response)
            print(f"✓ Received response: {json.dumps(result, indent=2)}")
            
            # Test tools/list
            tools_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            await websocket.send(json.dumps(tools_message))
            print("✓ Sent tools/list message")
            
            response = await websocket.recv()
            result = json.loads(response)
            print(f"✓ Received tools list: {len(result.get('result', {}).get('tools', []))} tools")
            
            # Test tools/call - health check
            call_message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "health_check",
                    "arguments": {}
                }
            }
            
            await websocket.send(json.dumps(call_message))
            print("✓ Sent tools/call message")
            
            response = await websocket.recv()
            result = json.loads(response)
            print(f"✓ Received tool result: {json.dumps(result, indent=2)}")
            
            # Test git_status tool
            git_message = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "git_status",
                    "arguments": {}
                }
            }
            
            await websocket.send(json.dumps(git_message))
            print("✓ Sent git_status test")
            
            response = await websocket.recv()
            result = json.loads(response)
            print(f"✓ Received git_status result")
            
            print("\n✓ All MCP WebSocket tests passed!")
            
    except Exception as e:
        print(f"✗ WebSocket test failed: {e}")
        return False
    
    return True


def test_mcp_http():
    """Test MCP server via HTTP"""
    print("\nTesting MCP HTTP endpoint...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8080/health")
        if response.status_code == 200:
            print("✓ Health endpoint working")
            print(f"✓ Health response: {response.json()}")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
        
        # Test MCP over HTTP
        mcp_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = requests.post(
            "http://localhost:8080/mcp/http",
            json=mcp_message,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ MCP HTTP endpoint working")
            print(f"✓ MCP HTTP response: {json.dumps(result, indent=2)}")
        else:
            print(f"✗ MCP HTTP endpoint failed: {response.status_code}")
            return False
        
        print("\n✓ All MCP HTTP tests passed!")
        
    except Exception as e:
        print(f"✗ HTTP test failed: {e}")
        return False
    
    return True


async def main():
    """Run all tests"""
    print("🚀 Testing AI SRE MCP Protocol Server")
    print("=" * 50)
    
    # Test HTTP first
    http_success = test_mcp_http()
    
    # Test WebSocket
    ws_success = await test_mcp_websocket()
    
    print("\n" + "=" * 50)
    if http_success and ws_success:
        print("🎉 All tests passed! MCP server is working correctly.")
        print("\n📋 N8N Configuration:")
        print("   - Connection Type: WebSocket")
        print("   - URL: ws://ai-sre.ai.svc.cluster.local:8080/mcp")
        print("   - Protocol: MCP (Model Context Protocol)")
        return 0
    else:
        print("❌ Some tests failed. Please check the server logs.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
