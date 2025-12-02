"""
E2B Sandbox Manager - Isolated Research Execution Environment
Prevents system crashes by running research in secure sandboxes
"""
import asyncio
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from e2b import Sandbox

logger = logging.getLogger(__name__)

@dataclass
class SandboxResult:
    success: bool
    output: str
    error: Optional[str]
    execution_time: float
    memory_used: int
    exit_code: int

class E2BSandboxManager:
    """
    Manages E2B sandboxes for safe code execution
    Prevents research crashes by isolating heavy operations
    """
    
    def __init__(self, api_key: Optional[str] = None, max_sandboxes: int = 5):
        """
        Initialize E2B Sandbox Manager
        
        Args:
            api_key: E2B API key (or from env)
            max_sandboxes: Maximum concurrent sandboxes
        """
        self.api_key = api_key
        self.max_sandboxes = max_sandboxes
        self._active_sandboxes: Dict[str, Sandbox] = {}
        self._semaphore = asyncio.Semaphore(max_sandboxes)
        
    async def execute_research_query(
        self,
        code: str,
        timeout: int = 300,
        language: str = "python",
        env_vars: Optional[Dict[str, str]] = None
    ) -> SandboxResult:
        """
        Execute research code in isolated E2B sandbox
        
        Args:
            code: Code to execute
            timeout: Max execution time (seconds)
            language: Programming language
            env_vars: Environment variables
            
        Returns:
            SandboxResult with output and metadata
        """
        async with self._semaphore:
            sandbox_id = f"research_{asyncio.current_task().get_name()}"
            
            try:
                # Create sandbox
                sandbox = await self._create_sandbox(
                    sandbox_id, language, env_vars
                )
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    self._run_code(sandbox, code),
                    timeout=timeout
                )
                
                return result
                
            except asyncio.TimeoutError:
                logger.error(f"Sandbox {sandbox_id} timed out after {timeout}s")
                return SandboxResult(
                    success=False,
                    output="",
                    error=f"Execution timeout after {timeout}s",
                    execution_time=timeout,
                    memory_used=0,
                    exit_code=-1
                )
                
            except Exception as e:
                logger.error(f"Sandbox {sandbox_id} failed: {e}")
                return SandboxResult(
                    success=False,
                    output="",
                    error=str(e),
                    execution_time=0,
                    memory_used=0,
                    exit_code=-1
                )
                
            finally:
                # Always cleanup
                await self._cleanup_sandbox(sandbox_id)
    
    async def _create_sandbox(
        self,
        sandbox_id: str,
        language: str,
        env_vars: Optional[Dict[str, str]]
    ) -> Sandbox:
        """Create new E2B sandbox"""
        sandbox = await Sandbox.create(
            api_key=self.api_key,
            metadata={"id": sandbox_id, "language": language}
        )
        
        # Set environment variables
        if env_vars:
            for key, value in env_vars.items():
                await sandbox.process.start(f"export {key}={value}")
        
        self._active_sandboxes[sandbox_id] = sandbox
        logger.info(f"Created sandbox {sandbox_id}")
        return sandbox
    
    async def _run_code(self, sandbox: Sandbox, code: str) -> SandboxResult:
        """Execute code in sandbox"""
        import time
        start_time = time.time()
        
        try:
            # Execute code
            process = await sandbox.process.start(
                cmd=f"python -c '{code}'",
                on_stdout=lambda data: logger.debug(f"stdout: {data}"),
                on_stderr=lambda data: logger.warning(f"stderr: {data}")
            )
            
            # Wait for completion
            exit_code = await process.wait()
            
            # Get resource usage
            memory_used = await self._get_memory_usage(sandbox)
            
            execution_time = time.time() - start_time
            
            return SandboxResult(
                success=exit_code == 0,
                output=process.stdout or "",
                error=process.stderr if exit_code != 0 else None,
                execution_time=execution_time,
                memory_used=memory_used,
                exit_code=exit_code
            )
            
        except Exception as e:
            return SandboxResult(
                success=False,
                output="",
                error=str(e),
                execution_time=time.time() - start_time,
                memory_used=0,
                exit_code=-1
            )
    
    async def _get_memory_usage(self, sandbox: Sandbox) -> int:
        """Get sandbox memory usage in bytes"""
        try:
            result = await sandbox.process.start(
                "ps aux | awk '{sum+=$6} END {print sum}'"
            )
            return int(result.stdout.strip()) * 1024  # KB to bytes
        except Exception:
            return 0
    
    async def _cleanup_sandbox(self, sandbox_id: str):
        """Cleanup sandbox resources"""
        if sandbox_id in self._active_sandboxes:
            try:
                sandbox = self._active_sandboxes[sandbox_id]
                await sandbox.kill()
                del self._active_sandboxes[sandbox_id]
                logger.info(f"Cleaned up sandbox {sandbox_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup {sandbox_id}: {e}")
    
    async def cleanup_all(self):
        """Cleanup all active sandboxes"""
        logger.info(f"Cleaning up {len(self._active_sandboxes)} sandboxes")
        for sandbox_id in list(self._active_sandboxes.keys()):
            await self._cleanup_sandbox(sandbox_id)


# Integration with crash analysis engine
class SafeResearchExecutor:
    """
    Wrapper for crash-prone research operations
    Uses E2B sandboxes to prevent system crashes
    """
    
    def __init__(self, sandbox_manager: E2BSandboxManager):
        self.sandbox_manager = sandbox_manager
    
    async def safe_event_log_analysis(self) -> Dict[str, Any]:
        """Execute event log analysis safely in sandbox"""
        code = """
import subprocess
import json

result = subprocess.run(
    ['powershell', '-Command',
     'Get-WinEvent -FilterHashtable @{LogName=\"System\"; Level=1,2,3} -MaxEvents 100 | ConvertTo-Json'],
    capture_output=True, text=True, timeout=30
)
print(result.stdout)
"""
        
        result = await self.sandbox_manager.execute_research_query(
            code=code,
            timeout=60,
            language="python"
        )
        
        if result.success:
            return {"status": "success", "data": result.output}
        else:
            return {"status": "error", "error": result.error}
    
    async def safe_memory_analysis(self) -> Dict[str, Any]:
        """Execute memory analysis safely"""
        code = """
import psutil

mem = psutil.virtual_memory()
print(f"Memory: {mem.percent}% used, {mem.available / 1024**3:.2f} GB available")

# Top 10 memory consumers
processes = []
for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
    try:
        if proc.info['memory_percent'] > 1:
            processes.append(proc.info)
    except:
        pass

processes.sort(key=lambda x: x['memory_percent'], reverse=True)
for p in processes[:10]:
    print(f"{p['name']}: {p['memory_percent']:.2f}%")
"""
        
        result = await self.sandbox_manager.execute_research_query(
            code=code,
            timeout=30
        )
        
        return {
            "success": result.success,
            "output": result.output,
            "memory_used": result.memory_used,
            "execution_time": result.execution_time
        }


# Global singleton
_sandbox_manager: Optional[E2BSandboxManager] = None

def get_sandbox_manager(api_key: Optional[str] = None) -> E2BSandboxManager:
    """Get global E2B sandbox manager"""
    global _sandbox_manager
    if _sandbox_manager is None:
        _sandbox_manager = E2BSandboxManager(api_key=api_key)
    return _sandbox_manager


async def init_e2b_sandboxes(api_key: Optional[str] = None):
    """Initialize E2B sandbox system"""
    manager = get_sandbox_manager(api_key)
    logger.info("✅ E2B Sandbox Manager initialized")
    return manager


async def shutdown_e2b_sandboxes():
    """Shutdown all E2B sandboxes"""
    manager = get_sandbox_manager()
    await manager.cleanup_all()
    logger.info("🛑 E2B Sandbox Manager shutdown complete")
