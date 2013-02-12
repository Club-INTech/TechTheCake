package intech.android.camera;

import java.util.List;

import android.content.Context;
import android.hardware.Camera;
import android.hardware.Camera.Parameters;
import android.hardware.Camera.Size;
import android.util.Log;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

public class CameraPreviewSurfaceView extends SurfaceView implements
		SurfaceHolder.Callback {

	private final String TAG = "INTech";
	private SurfaceHolder mHolder;
	private Camera mCamera;
	private boolean isPreviewRunning = false;

	public CameraPreviewSurfaceView(Context context) {
		super(context);
		// Install a SurfaceHolder.Callback so we get notified when the
		// underlying surface is created and destroyed.
		mHolder = getHolder();
		mHolder.addCallback(this);
		// deprecated setting, but required on Android versions prior to 3.0
		mHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);
	}

	public void surfaceCreated(SurfaceHolder holder) {
		try {
			// This case can actually happen if the user opens and closes the
			// camera too frequently.
			// The problem is that we cannot really prevent this from happening
			// as the user can easily
			// get into a chain of activites and tries to escape using the back
			// button.
			// The most sensible solution would be to quit the entire EPostcard
			// flow once the picture is sent.
			mCamera = Camera.open();
		} catch (Exception e) {
			return;
		}

		Parameters parameters = mCamera.getParameters();

		parameters.setRotation(90);
		Camera.Size previewSize = parameters.getSupportedPreviewSizes().get(0);
		parameters.setPreviewSize(previewSize.width, previewSize.height);
		Log.d(TAG, "Taille de la preview: w = " + previewSize.width + ", h = "
				+ previewSize.height);

//		Camera.Size pictureSize = parameters.getSupportedPictureSizes().get(0);
		parameters.setPictureSize(640, 480);

		mCamera.setParameters(parameters);
		mCamera.setDisplayOrientation(90);

		try {
			mCamera.setPreviewDisplay(holder);
			mCamera.startPreview();
			mCamera.autoFocus(null);
		} catch (Throwable ignored) {
			Log.e(TAG, "set preview error.", ignored);
		}
	}

	public void surfaceChanged(SurfaceHolder holder, int format, int width,
			int height) {
		if (isPreviewRunning) {
			mCamera.stopPreview();
		}
		try {
			mCamera.startPreview();
		} catch (Exception e) {
			Log.d(TAG, "Cannot start preview", e);
		}
		isPreviewRunning = true;
	}

	public void surfaceDestroyed(SurfaceHolder arg0) {
		if (isPreviewRunning && mCamera != null) {
			if (mCamera != null) {
				mCamera.stopPreview();
				mCamera.release();
				mCamera = null;
			}
			isPreviewRunning = false;
		}
	}

	public void takePicture(Camera.PictureCallback callback) {
		mCamera.takePicture(null, null, callback);
	}

}