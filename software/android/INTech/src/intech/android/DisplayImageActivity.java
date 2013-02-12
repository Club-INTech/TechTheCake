package intech.android;

import org.opencv.android.Utils;
import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.Scalar;
import org.opencv.imgproc.Imgproc;

import android.net.Uri;
import android.os.Bundle;
import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.widget.ImageView;

public class DisplayImageActivity extends Activity {

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
		Utils.bitmapToMat(originalBitmap, image);

		// Lance l'analyse depuis le programme C++
		analyze(image.getNativeObjAddr(), mask.getNativeObjAddr(),
				contours.getNativeObjAddr());

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

	}

	public native void analyze(long srcAddr, long maskAddr, long contoursAddr);

}
