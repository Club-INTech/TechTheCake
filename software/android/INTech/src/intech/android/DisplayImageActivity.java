package intech.android;

import intech.android.wifi.SocketServer;
import intech.android.wifi.SocketServerManager;

import org.opencv.android.Utils;
import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.Scalar;
import org.opencv.imgproc.Imgproc;

import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.preference.PreferenceManager;
import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.widget.ImageView;
import android.widget.RadioButton;

public class DisplayImageActivity extends Activity {

	private final String TAG = "INTech";

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_display_image);

		// Chargement de la photo
		Bundle bundle = getIntent().getExtras();
		Bitmap originalBitmap = BitmapFactory.decodeFile(bundle
				.getString("image_path"));

		// Affichage à l'écran
		ImageView imageView = (ImageView) findViewById(R.id.capture_view);
		imageView.setImageBitmap(originalBitmap);

		// Conversion au format OpenCV
		Mat image = new Mat();
		Mat mask = new Mat();
		Mat contours = new Mat();
		Mat results = new Mat();
		Utils.bitmapToMat(originalBitmap, image);

		SharedPreferences preferences = PreferenceManager
				.getDefaultSharedPreferences(this);

		// Chargement de la couleur de l'équipe
		loadColor(bundle.getChar("color"));

		// Chargement des paramètres pour la détection des balles
		int hMin = Integer.valueOf(preferences.getString("balls_h_min", "0"));
		int sMin = Integer.valueOf(preferences.getString("balls_s_min", "0"));
		int vMin = Integer.valueOf(preferences.getString("balls_v_min", "0"));
		int hMax = Integer.valueOf(preferences.getString("balls_h_max", "0"));
		int sMax = Integer.valueOf(preferences.getString("balls_s_max", "0"));
		int vMax = Integer.valueOf(preferences.getString("balls_v_max", "0"));
		Log.d(TAG, String.valueOf(hMin) + " " + String.valueOf(hMax));
		loadBallsParameters(hMin, sMin, vMin, hMax, sMax, vMax);

		// Chargement des paramètres pour la couleur des bougies
		int redColor = Integer.valueOf(preferences
				.getString("red_h_color", "0"));
		int blueColor = Integer.valueOf(preferences.getString("blue_h_color",
				"0"));
		int colorTolerance = Integer.valueOf(preferences.getString(
				"tolerance_color", "0"));
		int whiteTolerance = Integer.valueOf(preferences.getString(
				"white_tolerance_color", "0"));
		loadBallColorsParameters(redColor, blueColor, colorTolerance,
				whiteTolerance);

		// Chargement des paramètres pour le masque
		int maskErode = Integer.valueOf(preferences.getString(
				"mask_erode_size", "0"));
		int maskClosing = Integer.valueOf(preferences.getString(
				"mask_closing_size", "0"));
		loadMaskParameters(maskErode, maskClosing);

		// Chargement des paramètres sur la taille des balles
		int minBallSize = Integer.valueOf(preferences.getString(
				"min_ball_size", "0"));
		int maxBallSize = Integer.valueOf(preferences.getString(
				"max_ball_size", "0"));
		loadBallSizeParameters(minBallSize, maxBallSize);

		// Lance l'analyse depuis le programme C++
		analyze(image.getNativeObjAddr(), mask.getNativeObjAddr(),
				contours.getNativeObjAddr(), results.getNativeObjAddr());

		// Envoi si nécessaire dans la socket
		boolean socketMode = getIntent().getExtras().getBoolean("socket_mode");
		if (socketMode) {
			Handler handler = SocketServerManager.getInstance()
					.getMessageInHandler();
			Message response = handler.obtainMessage(
					SocketServer.MESSAGE_IMAGE_RESPONSE, getResults());
			handler.sendMessage(response);
			finish();
		}

		// Affichage du masque
		Bitmap maskBitmap = Bitmap.createBitmap(image.cols(), image.rows(),
				Bitmap.Config.ARGB_8888);
		Utils.matToBitmap(mask, maskBitmap);
		ImageView maskView = (ImageView) findViewById(R.id.mask_view);
		maskView.setImageBitmap(maskBitmap);

		// Affichage des contours
		Bitmap contoursBitmap = Bitmap.createBitmap(image.cols(), image.rows(),
				Bitmap.Config.ARGB_8888);
		Utils.matToBitmap(contours, contoursBitmap);
		ImageView contoursView = (ImageView) findViewById(R.id.contours_view);
		contoursView.setImageBitmap(contoursBitmap);

		// Affichage des résultats
		Bitmap resultsBitmap = Bitmap.createBitmap(image.cols(), image.rows(),
				Bitmap.Config.ARGB_8888);
		Utils.matToBitmap(results, resultsBitmap);
		ImageView resultsView = (ImageView) findViewById(R.id.results_view);
		resultsView.setImageBitmap(resultsBitmap);

	}

	public native void loadColor(char color);

	public native void loadBallsParameters(int hMin, int sMin, int vMin,
			int hMax, int sMax, int vMax);

	public native void loadBallColorsParameters(int red, int blue,
			int tolerance, int white);

	public native void loadMaskParameters(int maskErode, int maskClosing);

	public native void loadBallSizeParameters(int minBallSize, int maxBallSize);

	public native void analyze(long srcAddr, long maskAddr, long contoursAddr,
			long resultsAddr);

	public native String getResults();

}
