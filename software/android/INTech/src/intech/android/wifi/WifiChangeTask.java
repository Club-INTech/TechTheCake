package intech.android.wifi;

import java.lang.reflect.Method;

import android.app.ProgressDialog;
import android.net.wifi.WifiConfiguration;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import android.util.Log;

public class WifiChangeTask extends AsyncTask<Void, Void, Void> {

	private final String TAG = "INTech-Wifi";
	private WifiManager wifiManager;
	private boolean mode;
	private ProgressDialog dialog;

	private static final int WIFI_AP_STATE_UNKNOWN = -1;
	private static final int WIFI_AP_STATE_DISABLING = 0;
	private static final int WIFI_AP_STATE_DISABLED = 1;
	private static final int WIFI_AP_STATE_ENABLING = 2;
	private static final int WIFI_AP_STATE_ENABLED = 3;
	private static final int WIFI_AP_STATE_FAILED = 4;

	public WifiChangeTask(boolean mode, WifiManager wifiManager,
			ProgressDialog dialog) {
		this.mode = mode;
		this.wifiManager = wifiManager;
		this.dialog = dialog;
	}

	@Override
	protected void onPreExecute() {
		super.onPreExecute();

		dialog.setTitle("Point d'accès Wifi");
		dialog.setMessage((mode ? "Activation en cours..."
				: "Désactivation en cours..."));
		dialog.show();
	}

	protected void onPostExecute(Void aVoid) {
		super.onPostExecute(aVoid);
		try {
			dialog.dismiss();
		} catch (IllegalArgumentException e) {
		}
	}

	@Override
	protected Void doInBackground(Void... params) {
		setWifiApEnabled(mode);
		return null;
	}

	private int setWifiApEnabled(boolean enabled) {

		if (enabled && wifiManager.getConnectionInfo() != null) {
			Log.d(TAG, "Désactivation du wifi");
			wifiManager.setWifiEnabled(false);
			try {
				Thread.sleep(1500);
			} catch (Exception e) {
			}
		}

		int state = WIFI_AP_STATE_UNKNOWN;
		try {
			wifiManager.setWifiEnabled(false);
			Method method1 = wifiManager.getClass().getMethod(
					"setWifiApEnabled", WifiConfiguration.class, boolean.class);
			method1.invoke(wifiManager, null, enabled);
			Method method2 = wifiManager.getClass().getMethod("getWifiApState");
			state = (Integer) method2.invoke(wifiManager);
		} catch (Exception e) {
			Log.e(TAG, e.getMessage());
		}

		if (!enabled) {
			int loopMax = 5;
			while (loopMax > 0) {
				try {
					Thread.sleep(500);
					loopMax--;
				} catch (Exception e) {
				}
			}
			wifiManager.setWifiEnabled(true);
		} else if (enabled) {
			int loopMax = 10;
			while (loopMax > 0) {
				try {
					Thread.sleep(500);
					loopMax--;
				} catch (Exception e) {
				}
			}
		}

		return state;
	}

	// private int getWifiAPState() {
	// int state = WIFI_AP_STATE_UNKNOWN;
	// try {
	// Method method2 = wifi.getClass().getMethod("getWifiApState");
	// state = (Integer) method2.invoke(wifi);
	// } catch (Exception e) {
	// }
	// Log.d("WifiAP", "getWifiAPState.state "
	// + ((state < 0 || state >= WIFI_STATE_TEXTSTATE.length) ? "UNKNOWN" :
	// WIFI_STATE_TEXTSTATE[state]));
	// return state;
	// }
}
