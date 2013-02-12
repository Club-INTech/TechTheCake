package intech.android;

import intech.android.camera.CameraPreviewSurfaceView;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.URI;
import java.text.SimpleDateFormat;
import java.util.Date;

import org.opencv.android.BaseLoaderCallback;
import org.opencv.android.LoaderCallbackInterface;
import org.opencv.android.OpenCVLoader;
import org.opencv.android.Utils;
import org.opencv.core.Mat;
import org.opencv.highgui.Highgui;
import org.opencv.imgproc.Imgproc;

import android.graphics.Bitmap;
import android.hardware.Camera;
import android.hardware.Camera.PictureCallback;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.app.Activity;
import android.content.Intent;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.provider.MediaStore.Files.FileColumns;

public class CameraPreviewActivity extends Activity {

	private final String TAG = "INTech";
	private CameraPreviewSurfaceView cameraPreview;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

		// Ecran toujours allumé
		getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

		// Affichage de l'écran principal
		setContentView(R.layout.activity_camera_preview);
		
		cameraPreview = new CameraPreviewSurfaceView(this);

		FrameLayout preview = (FrameLayout) findViewById(R.id.camera_preview);
		preview.addView(cameraPreview);

	}

	@Override
	protected void onResume() {
		super.onResume();

		Log.i("INTech", "Trying to load OpenCV library");
		if (!OpenCVLoader.initAsync(OpenCVLoader.OPENCV_VERSION_2_4_2, this,
				mOpenCVCallBack)) {
			Log.e("INTech", "Cannot connect to OpenCV Manager");
		}
	}

	@Override
	protected void onPause() {
		super.onPause();
		Log.d(TAG, "pause");
	}

	public void takePicture(View view) {
		cameraPreview.takePicture(mPicture);
	}

	private BaseLoaderCallback mOpenCVCallBack = new BaseLoaderCallback(this) {
		@Override
		public void onManagerConnected(int status) {
			switch (status) {
			case LoaderCallbackInterface.SUCCESS: {
				Log.i(TAG, "OpenCV loaded successfully");
				System.loadLibrary("native_analyze");
			}
				break;
			default: {
				super.onManagerConnected(status);
			}
				break;
			}
		}
	};

	private PictureCallback mPicture = new PictureCallback() {

		@Override
		public void onPictureTaken(byte[] data, Camera camera) {
			
			// Relance la preview
			camera.startPreview();
			File captureFile = getOutputMediaFile(FileColumns.MEDIA_TYPE_IMAGE);

			// Aucun fichier disponible
			if (captureFile == null) {
				Log.d(TAG,
						"Erreur dans la création du fichier, vérifier les droits en écriture");
				return;
			}

			Log.d(TAG,
					"Enregistrement de la capture dans "
							+ captureFile.getAbsolutePath());

			try {

				// Ecriture du fichier avec les données
				FileOutputStream outputStream = new FileOutputStream(
						captureFile);
				outputStream.write(data);
				outputStream.close();

				Intent intent = new Intent(CameraPreviewActivity.this, DisplayImageActivity.class);
				intent.putExtra("image_path", captureFile.getAbsolutePath());
				startActivity(intent);

			} catch (FileNotFoundException e) {
				Log.d(TAG, "File not found: " + e.getMessage());
			} catch (IOException e) {
				Log.d(TAG, "Error accessing file: " + e.getMessage());
			}
		}
	};

	/**
	 * Création d'un fichier pour stocker un média
	 * 
	 * @param type
	 * @return
	 */
	private File getOutputMediaFile(int type) {

		File mediaStorageDir = new File(
				Environment
						.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES),
				"INTech");

		// Create the storage directory if it does not exist
		if (!mediaStorageDir.exists()) {
			if (!mediaStorageDir.mkdirs()) {
				Log.d(TAG,
						"Echec de la création du répertoire contenant les captures");
				return null;
			}
		}

		// Create a media file name
		String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss")
				.format(new Date());
		File mediaFile;
		if (type == FileColumns.MEDIA_TYPE_IMAGE) {
			mediaFile = new File(mediaStorageDir.getPath() + File.separator
					+ "IMG_" + timeStamp + ".jpg");
		} else if (type == FileColumns.MEDIA_TYPE_VIDEO) {
			mediaFile = new File(mediaStorageDir.getPath() + File.separator
					+ "VID_" + timeStamp + ".mp4");
		} else {
			return null;
		}

		return mediaFile;
	}

}



