package id.meong.nativebridge;

import android.content.Context;
import android.graphics.Bitmap;
import com.google.mediapipe.framework.image.BitmapImageBuilder;
import com.google.mediapipe.framework.image.MPImage;
import com.google.mediapipe.tasks.core.BaseOptions;
import com.google.mediapipe.tasks.components.containers.Category;
import com.google.mediapipe.tasks.vision.core.RunningMode;
import com.google.mediapipe.tasks.vision.gesturerecognizer.GestureRecognizer;
import java.util.List;

/** Android binding of the same pinned Gesture Recognizer model used in v2. */
public final class PalmBridge {
    private final GestureRecognizer recognizer;
    public PalmBridge(Context context, String model) {
        GestureRecognizer.GestureRecognizerOptions options = GestureRecognizer.GestureRecognizerOptions.builder()
            .setBaseOptions(BaseOptions.builder().setModelAssetPath(model).build())
            .setRunningMode(RunningMode.IMAGE).setNumHands(1)
            .setMinHandDetectionConfidence(0.6f).setMinHandPresenceConfidence(0.6f)
            .setMinTrackingConfidence(0.6f).build();
        recognizer=GestureRecognizer.createFromOptions(context,options);
    }
    public float detect(byte[] rgb, int width, int height) {
        if(width<1 || height<1 || width>480 || height>360 || rgb.length!=width*height*3) throw new IllegalArgumentException();
        int[] pixels=new int[width*height];
        for(int i=0;i<pixels.length;i++) pixels[i]=0xff000000|((rgb[i*3]&255)<<16)|((rgb[i*3+1]&255)<<8)|(rgb[i*3+2]&255);
        Bitmap bitmap=Bitmap.createBitmap(pixels,width,height,Bitmap.Config.ARGB_8888);
        MPImage image=new BitmapImageBuilder(bitmap).build();
        try {
            float score=0;
            for(List<Category> hand:recognizer.recognize(image).gestures())
                for(Category category:hand) if("Open_Palm".equals(category.categoryName())) score=Math.max(score,category.score());
            return score;
        } finally { image.close(); bitmap.recycle(); }
    }
    public void close() { recognizer.close(); }
}
