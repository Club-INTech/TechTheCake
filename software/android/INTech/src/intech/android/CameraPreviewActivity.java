package intech.android;

import intech.android.camera.CameraPreviewSurfaceView;
import intech.android.wifi.SocketServerManager;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

import android.hardware.Camera;
import android.hardware.Camera.PictureCallback;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.widget.RadioButton;
import android.widget.TextView;
import android.preference.PreferenceManager;
import android.provider.MediaStore.Files.FileColumns;

public class CameraPreviewActivity extends Activity {

	private final String TAG = "INTech-CameraPreview";
	public static int MESSAGE_UPDATE_SERVER_STATUS = 1;
	public static int MESSAGE_TAKE_PICTURE = 2;
	private char color;
	private boolean openSocket;
	private boolean isFocused = false;
	private CameraPreviewSurfaceView cameraPreview;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		setContentView(R.layout.activity_camera_preview);
		getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
		
		SharedPreferences preferences = PreferenceManager
				.getDefaultSharedPreferences(this);
		
		// Indique la couleur à détecter
		color = getIntent().getExtras().getChar("color");
		
		// Indique si l'application doit ouvrir une socket
		openSocket = getIntent().getExtras().getBoolean("open_socket");
		
		if (openSocket) {
			Log.d(TAG, "Activation de la socket");
			SocketServerManager.getInstance().setMessageOutHandler(socketRequestHandler);
			SocketServerManager.getInstance().stopListeningSocket();
			SocketServerManager.getInstance().startListeningSocket();
		}
		
		// Récupération de la caméra
		int delayAutofocus = Integer.valueOf(preferences.getString("autofocus_delay", "3000"));
		cameraPreview = new CameraPreviewSurfaceView(this, delayAutofocus);
		cameraPreview.setPictureReadyCallBack(pictureReadyCallback);
		cameraPreview.setTakePictureWhenFocusReady(false);
		
		// Affichage de la caméra
		FrameLayout preview = (FrameLayout) findViewById(R.id.camera_preview);
		preview.addView(cameraPreview);
	}
	
	Handler socketRequestHandler = new Handler() {
		@Override
		public void handleMessage(Message message) {
			if (message.what == MESSAGE_TAKE_PICTURE) {
				if (message.obj == null) {
					Log.d(TAG, "Demande de prise de photo incorrecte");
					return;
				}
				
				// Enregistrement de la couleur demandée
				String request = (String) message.obj;
				color = request.charAt(0);
				Log.d(TAG, "Demande de prise de photo pour la couleur " + color);
				
				// Prise de la photo
				cameraPreview.takePicture();
			}
		}
	};

	public void takePicture(View view) {
		if (!isFocused) {
			cameraPreview.autoFocus();
			if (!openSocket) isFocused = true;
		} else {
			if (!openSocket) cameraPreview.takePicture();
		}
	}

	private PictureCallback pictureReadyCallback = new PictureCallback() {

		@Override
		public void onPictureTaken(byte[] data, Camera camera) {
			
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
				intent.putExtra("socket_mode", getIntent().getExtras().getBoolean("open_socket"));
				intent.putExtra("color", color);
				startActivityForResult(intent, 0);

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
	
	public void onActivityResult(int requestCode, int resultCode, Intent data) {
		finish();
	}

}



