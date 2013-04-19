package intech.android.wifi;

import android.os.Handler;

public final class SocketServerManager {
	
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
		if (server != null) server.stop();
	}

}
