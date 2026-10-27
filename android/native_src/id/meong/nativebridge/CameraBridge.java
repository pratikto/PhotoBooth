package id.meong.nativebridge;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.ImageFormat;
import android.hardware.camera2.*;
import android.media.Image;
import android.media.ImageReader;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.SystemClock;
import android.util.Size;
import android.view.Surface;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/** One Camera2 owner. Preview and full-resolution JPEG share one capture session. */
public final class CameraBridge {
    public static final class Frame {
        public final byte[] pixels;
        public final int width, height, rotation;
        public final long sequence, stamp;
        Frame(byte[] p, int w, int h, int r, long seq) {
            pixels=p; width=w; height=h; rotation=r; sequence=seq;
            stamp=SystemClock.elapsedRealtime();
        }
    }
    private final Activity activity;
    private final int facing;
    private HandlerThread thread;
    private Handler handler;
    private CameraDevice camera;
    private CameraCaptureSession session;
    private ImageReader preview, still;
    private volatile boolean closed=false, ready=false;
    private volatile Frame frame;
    private volatile byte[] jpeg;
    private volatile CountDownLatch shot;
    private final CountDownLatch opened=new CountDownLatch(1);
    private final CountDownLatch released=new CountDownLatch(1);
    private int sensorRotation, lens;
    private long sequence;

    public CameraBridge(Activity activity, int facing) {
        this.activity=activity; this.facing=facing;
    }
    private int rotation() {
        int display=activity.getWindowManager().getDefaultDisplay().getRotation()*90;
        // Android front sensor needs the opposite display compensation; no mirror.
        return (sensorRotation + (lens==CameraCharacteristics.LENS_FACING_FRONT ? display : -display)+360)%360;
    }
    public boolean openAndWait(int timeout) {
        if (activity.checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED) return false;
        thread=new HandlerThread("meong-camera2"); thread.start(); handler=new Handler(thread.getLooper());
        handler.post(() -> {
            try {
                CameraManager manager=(CameraManager)activity.getSystemService(Context.CAMERA_SERVICE);
                String selected=null;
                for (String id:manager.getCameraIdList()) {
                    CameraCharacteristics c=manager.getCameraCharacteristics(id);
                    if (c.get(CameraCharacteristics.LENS_FACING)==facing) { selected=id; break; }
                }
                if (selected==null) { opened.countDown(); return; }
                CameraCharacteristics c=manager.getCameraCharacteristics(selected);
                sensorRotation=c.get(CameraCharacteristics.SENSOR_ORIENTATION);
                lens=c.get(CameraCharacteristics.LENS_FACING);
                android.hardware.camera2.params.StreamConfigurationMap map=c.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP);
                Size chosen=null;
                for(Size s:map.getOutputSizes(ImageFormat.YUV_420_888)) {
                    if(s.getWidth()%2!=0 || s.getHeight()%2!=0) continue;
                    if((long)s.getWidth()*s.getHeight()<=1280*720 && (chosen==null || area(s)>area(chosen))) chosen=s;
                }
                if(chosen==null) throw new IllegalStateException();
                Size full=null;
                for(Size s:map.getOutputSizes(ImageFormat.JPEG)) if(full==null || area(s)>area(full)) full=s;
                if(full==null) throw new IllegalStateException();
                preview=ImageReader.newInstance(chosen.getWidth(),chosen.getHeight(),ImageFormat.YUV_420_888,2);
                still=ImageReader.newInstance(full.getWidth(),full.getHeight(),ImageFormat.JPEG,2);
                preview.setOnImageAvailableListener(reader -> {
                    Image image=null;
                    try {
                        image=reader.acquireLatestImage();
                        if(image!=null && !closed) frame=new Frame(nv21(image),image.getWidth(),image.getHeight(),rotation(),++sequence);
                    } catch(Exception e) { frame=null; }
                    finally { if(image!=null) image.close(); }
                },handler);
                still.setOnImageAvailableListener(reader -> {
                    Image image=null;
                    try {
                        image=reader.acquireLatestImage();
                        if(image!=null && !closed && shot!=null) {
                            ByteBuffer b=image.getPlanes()[0].getBuffer(); byte[] bytes=new byte[b.remaining()]; b.get(bytes); jpeg=bytes;
                        }
                    } finally { if(image!=null) image.close(); CountDownLatch latch=shot; if(latch!=null) latch.countDown(); }
                },handler);
                manager.openCamera(selected,new CameraDevice.StateCallback() {
                    public void onOpened(CameraDevice device) {
                        if(closed) { device.close(); opened.countDown(); return; }
                        camera=device;
                        try {
                            device.createCaptureSession(Arrays.asList(preview.getSurface(),still.getSurface()),new CameraCaptureSession.StateCallback() {
                                public void onConfigured(CameraCaptureSession s) {
                                    if(closed) { s.close(); opened.countDown(); return; }
                                    session=s;
                                    try {
                                        CaptureRequest.Builder b=device.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);
                                        b.addTarget(preview.getSurface());
                                        b.set(CaptureRequest.CONTROL_MODE,CaptureRequest.CONTROL_MODE_AUTO);
                                        s.setRepeatingRequest(b.build(),null,handler); ready=true;
                                    } catch(Exception e) { ready=false; }
                                    opened.countDown();
                                }
                                public void onConfigureFailed(CameraCaptureSession s) { opened.countDown(); }
                            },handler);
                        } catch(Exception e) { opened.countDown(); }
                    }
                    public void onDisconnected(CameraDevice d) { d.close(); ready=false; frame=null; opened.countDown(); releaseShot(); }
                    public void onError(CameraDevice d,int error) { d.close(); ready=false; frame=null; opened.countDown(); releaseShot(); }
                },handler);
            } catch(Exception e) { opened.countDown(); }
        });
        try { return opened.await(Math.min(timeout,10000),TimeUnit.MILLISECONDS) && ready && !closed; }
        catch(InterruptedException e) { Thread.currentThread().interrupt(); return false; }
    }
    private static long area(Size s) { return (long)s.getWidth()*s.getHeight(); }
    private static byte[] nv21(Image image) {
        int w=image.getWidth(), h=image.getHeight(); byte[] output=new byte[w*h*3/2];
        Image.Plane[] planes=image.getPlanes();
        for(int p=0;p<3;p++) {
            ByteBuffer b=planes[p].getBuffer(); int row=planes[p].getRowStride(),pixel=planes[p].getPixelStride();
            int width=p==0?w:w/2,height=p==0?h:h/2,origin=b.position();
            for(int y=0;y<height;y++) for(int x=0;x<width;x++) {
                int target=p==0?y*w+x:w*h+y*w+2*x+(p==1?1:0);
                output[target]=b.get(origin+y*row+x*pixel);
            }
        }
        return output;
    }
    public boolean isReady() { return ready && !closed; }
    public Frame latestFrame() {
        Frame f=frame; return isReady() && f!=null && SystemClock.elapsedRealtime()-f.stamp<1000?f:null;
    }
    private void releaseShot() { CountDownLatch latch=shot; if(latch!=null) latch.countDown(); }
    public synchronized byte[] captureJpeg(int timeout) {
        if(!isReady() || shot!=null) return null;
        jpeg=null; CountDownLatch latch=new CountDownLatch(1); shot=latch;
        handler.post(() -> {
            if(!isReady() || shot!=latch) { latch.countDown(); return; }
            try {
                CaptureRequest.Builder b=camera.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE);
                b.addTarget(still.getSurface());
                b.set(CaptureRequest.JPEG_ORIENTATION,rotation());
                b.set(CaptureRequest.JPEG_QUALITY,(byte)95);
                session.capture(b.build(),new CameraCaptureSession.CaptureCallback() {
                    public void onCaptureFailed(CameraCaptureSession s,CaptureRequest r,CaptureFailure f) { latch.countDown(); }
                },handler);
            } catch(Exception e) { latch.countDown(); }
        });
        try {
            boolean done=latch.await(Math.min(timeout,10000),TimeUnit.MILLISECONDS);
            if(!done) { ready=false; frame=null; } // A late JPEG must never satisfy a later shot.
            return done && isReady()?jpeg:null;
        } catch(InterruptedException e) { Thread.currentThread().interrupt(); return null; }
        finally { shot=null; jpeg=null; }
    }
    public void close() {
        closed=true; ready=false; frame=null; releaseShot(); opened.countDown();
        Handler h=handler;
        if(h!=null) h.post(() -> {
            try {
                if(session!=null) session.close();
                if(camera!=null) camera.close();
                if(preview!=null) preview.close();
                if(still!=null) still.close();
            } finally { released.countDown(); thread.quitSafely(); }
        });
        else released.countDown();
        if(Thread.currentThread()!=thread) {
            try { released.await(3000,TimeUnit.MILLISECONDS); }
            catch(InterruptedException e) { Thread.currentThread().interrupt(); }
        }
    }
    public boolean isClosed() { return released.getCount()==0; }
}
