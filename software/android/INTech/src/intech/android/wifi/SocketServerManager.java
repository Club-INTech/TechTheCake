package intech.android.wifi;

import android.os.Handler;
import android.util.Log;

public final class SocketServerManager {
	
	private final String TAG = "INTech-SocketManager";
	private static volatile SocketServerManager instance = null;
	private Handler handler;
	private SocketServer server;
	
	public synchronized static SocketServerManager getInstance() {
		if (instance == null) {
			instance = new SocketServerManager();
		}
		return instance;
	}
	
	public void setMessageOutHandler(Handler mainActivityHandler) {
		this.handler = mainActivityHandler;
	}
	
	public Handler getMessageInHandler() {
		return server.getResponseHandler();
	}
	
	public void startListeningSocket() {
		server = new SocketServer(handler);
		server.execute();
	}
	
	public void stopListeningSocket() {
		if (server != null) {
			server.stop();
			Log.d(TAG, "fermeture de la socket");
		} else {
			Log.d(TAG, "aucune socket à fermer");
		}
	}

}
