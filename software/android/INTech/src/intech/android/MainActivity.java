package intech.android;

import intech.android.wifi.SocketServerManager;
import intech.android.wifi.WifiChangeTask;

import org.opencv.android.BaseLoaderCallback;
import org.opencv.android.LoaderCallbackInterface;
import org.opencv.android.OpenCVLoader;

import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.preference.PreferenceManager;
import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.RadioButton;
import android.widget.TextView;
import android.widget.ToggleButton;

public class MainActivity extends Activity {

	public static int MESSAGE_UPDATE_SERVER_STATUS = 1;
	public static int MESSAGE_START_CAMERA = 2;
	public static int MESSAGE_DISPLAY_RESULT = 3;
	private final String TAG = "INTech";

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

		// Affichage de l'écran principal
		setContentView(R.layout.activity_main);
		PreferenceManager.setDefaultValues(this, R.xml.pref_general, false);

		// Callback en cas de demande d'analyse par socket
		Handler socketRequestHandler = new Handler() {
			@Override
			public void handleMessage(Message message) {
				if (message.what == MESSAGE_START_CAMERA) {
					String color = (String) message.obj;
					int id = (color.equals("r")) ? R.id.radioRed
							: R.id.radioBlue;
					RadioButton button = (RadioButton) findViewById(id);
					button.setChecked(true);
					TextView results = (TextView) findViewById(R.id.textResultsView);
					results.setVisibility(View.INVISIBLE);
					startCameraPreview(true);
				}
				else if (message.what == MESSAGE_UPDATE_SERVER_STATUS) {
					TextView status = (TextView) findViewById(R.id.textServerStatus);
					status.setText((String) message.obj);
				}
				else if (message.what == MESSAGE_DISPLAY_RESULT) {
					TextView results = (TextView) findViewById(R.id.textResultsView);
					results.setText((String) message.obj);
					results.setVisibility(View.VISIBLE);
				}

			}
		};

		// Lancement du serveur en écoute des demandes
		SocketServerManager.getInstance().setMessageOutHandler(
				socketRequestHandler);
	}

	@Override
	protected void onResume() {
		super.onResume();

		// Chargement asynchrone d'OpenCV
		if (!OpenCVLoader.initAsync(OpenCVLoader.OPENCV_VERSION_2_4_2, this,
				loadOpenCVCallBack)) {
			Log.e("INTech", "Cannot connect to OpenCV Manager");
		}
	}

	private BaseLoaderCallback loadOpenCVCallBack = new BaseLoaderCallback(this) {
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

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		getMenuInflater().inflate(R.menu.activity_main, menu);
		return true;
	}

	public void toggleWifi(View v) {
		// Récupération de l'état du wifi
		ToggleButton button = (ToggleButton) findViewById(R.id.toggleWifiButton);
		boolean wifiStatus = button.isChecked();

		// Change l'état du wifi
		WifiChangeTask task = new WifiChangeTask(wifiStatus,
				(WifiManager) getSystemService(Context.WIFI_SERVICE),
				new ProgressDialog(MainActivity.this));
		task.execute();
	}

	public void displaySettings(MenuItem item) {
		Intent intent = new Intent(this, SettingsActivity.class);
		startActivity(intent);
	}
	
	public void displayHistory(MenuItem item) {
		Intent intent = new Intent(this, HistoryActivity.class);
		startActivity(intent);
	}

	public void displayCameraPreview(View view) {
		startCameraPreview(false);
	}

	public void startCameraPreview(boolean socketMode) {
		Intent intent = new Intent(this, CameraPreviewActivity.class);
		intent.putExtra("socket_mode", socketMode);
		startActivity(intent);
	}

}