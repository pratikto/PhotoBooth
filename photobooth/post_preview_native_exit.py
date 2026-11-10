"""Trusted launcher-only auxiliary drain; never financial/release authority."""
import threading
import time


def drain_native_app(app,*,timeout=.2):
    """Keep global owner until the original native file/probe threads exit.

    Manual Windows profile disables detector initialization. Original preview
    pool and v1 health worker have nonblocking close/no join handle respectively;
    retain their actual thread objects, including already retiring pools.
    """
    if type(timeout) not in (int,float) or not 0<=timeout<=5:raise ValueError('Bounded native drain required')
    if app is None:return True
    try:
        if not getattr(app,'_closed',False):app.on_stop()
        threads=set()
        for name in ('_game_jobs','_mock_jobs','_sandbox_jobs','_health_reports','_preview_preloader'):
            actor=getattr(app,name,None)
            if actor is None:continue
            actor.close()
            thread=getattr(actor,'_thread',None)
            if thread is not None:threads.add(thread)
            executor=getattr(actor,'_executor',None)
            if executor is not None:threads.update(executor._threads)
        # Original read-only health probes have no retained public thread
        # handle. Only this launcher owns these original native actors.
        threads.update(t for t in threading.enumerate()
                       if t.name=='meong-device-health' or t.name.startswith('meong-preview'))
        deadline=time.monotonic()+timeout
        for thread in threads:
            if thread is threading.current_thread():return False
            thread.join(max(0,deadline-time.monotonic()))
        controller=getattr(app,'_operator_controller',None)
        if controller is not None and controller._health_probe_lock.locked():return False
        return bool(app._closed) and all(not t.is_alive() for t in threads)
    except Exception:
        return False  # Static launcher hold; no private exception text or unsafe release.
