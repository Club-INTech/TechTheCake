package intech.android.camera;

import java.util.List;

import android.content.Context;
import android.hardware.Camera;
import android.hardware.Camera.AutoFocusCallback;
import android.hardware.Camera.Parameters;
import android.hardware.Camera.PictureCallback;
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
	private boolean autoPicture;
	private Camera.PictureCallback pictureReadyCallBack;

	public CameraPreviewSurfaceView(Context context) {
		super(context);
		// Install a SurfaceHolder.Callback so we get notified when the
		// underlying surface is created and destroyed.
		mHolder = getHolder();
		mHolder.addCallback(this);
		// deprecated setting, but required on Android versions prior to 3.0
		mHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);
	}
	
	public void setPictureReadyCallBack(Camera.PictureCallback callback) {
		pictureReadyCallBack = callback;
	}
	
	public void setTakePictureWhenFocusReady(boolean auto) {
		autoPicture = auto;
	}

	public void surfaceCreated(SurfaceHolder holder) {
		try {
			mCamera = Camera.open();
		} catch (Exception e) {
			Log.d(TAG, e.getMessage());
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
			mCamera.autoFocus(focusReadyCallback);
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

	public void takePicture() {
		mCamera.takePicture(null, null, pictureReadyCallBack);
	}
	
	private AutoFocusCallback focusReadyCallback = new AutoFocusCallback() {

		@Override
		public void onAutoFocus(boolean success, Camera camera) {
			if (autoPicture) {
				takePicture();
			}
		}
		
	};

}