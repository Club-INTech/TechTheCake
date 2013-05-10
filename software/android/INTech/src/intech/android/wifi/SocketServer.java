package intech.android.wifi;

import intech.android.CameraPreviewActivity;
import intech.android.MainActivity;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;

import android.os.AsyncTask;
import android.os.Handler;
import android.os.Message;
import android.util.Log;

public class SocketServer extends AsyncTask<Void, Integer, Void> {

	public static int MESSAGE_CLOSE_SOCKET = 0;
	public static int MESSAGE_IMAGE_RESPONSE = 1;

	private final String TAG = "INTech-Socket";
	private int port = 8080;
	private Handler messageHandler;
	private ServerSocket server;
	private Socket socket;
	private boolean isServerEnabled = true;

	SocketServer(Handler messageHandler) {
		this.messageHandler = messageHandler;
	}

	public void stop() {
		Log.d(TAG, "Fermeture de la socket");
		isServerEnabled = false;
		try {
			server.close();

			// Affichage à l'écran des infos
			Message infoMessage = messageHandler.obtainMessage(
					MainActivity.MESSAGE_UPDATE_SERVER_STATUS, "Déconnecté");
			messageHandler.sendMessage(infoMessage);
		} catch (IOException e) {
			Log.w(TAG, "Erreur socket: " + e.getMessage());
		}
	}

	public Handler getResponseHandler() {
		return new Handler() {

			@Override
			public void handleMessage(Message message) {
				try {
					if (message.what == MESSAGE_CLOSE_SOCKET) {
						stop();
					} else if (message.what == MESSAGE_IMAGE_RESPONSE) {
						
						String results = (String) message.obj;
						Log.d(TAG, "Réponse: " + results);
						
						// Envoi du résultat sur la socket
						PrintWriter output = new PrintWriter(
								socket.getOutputStream(), true);
						output.println(results);
						
						// Affichage à l'écran des infos
//						Message infoMessage = messageHandler.obtainMessage(
//								CameraPreviewActivity.MESSAGE_DISPLAY_RESULT,
//								"Résultats: " + results);
//						messageHandler.sendMessage(infoMessage);
					}
				} catch (IOException e) {
					Log.w(TAG, "Erreur socket: " + e.getMessage());
				}
			}

		};
	}

	@Override
	protected Void doInBackground(Void... params) {
		Log.i(TAG, "Création du thread d'écoute");

		try {
			// Création du serveur
			server = new ServerSocket(port);

			// Traitement des demandes
			while (isServerEnabled) {
				socket = server.accept();
				handleClient();
			}
		} catch (UnknownHostException e) {
			Log.w(TAG, "Erreur socket: " + e.getMessage());
		} catch (IOException e) {
			Log.w(TAG, "Erreur socket: " + e.getMessage());
		}

		return null;
	}

	protected void handleClient() throws IOException {
		// Initialisation des entrées/sorties
		Log.i(TAG, "Client connecté");
		InputStreamReader reader = new InputStreamReader(
				socket.getInputStream());
		BufferedReader input = new BufferedReader(reader);

		// Lecture de la couleur du robot
		String request = input.readLine();
		char color = request.charAt(request.length() - 1);
		Log.i(TAG, "Couleur du robot: " + color);

		// Lancement de l'analyse dans le thread UI
		Message startMessage = messageHandler.obtainMessage(
				CameraPreviewActivity.MESSAGE_TAKE_PICTURE, String.valueOf(color));
		messageHandler.sendMessage(startMessage);
	}

}
