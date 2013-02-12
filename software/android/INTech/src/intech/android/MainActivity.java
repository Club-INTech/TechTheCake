package intech.android;

import android.os.Bundle;
import android.app.Activity;
import android.content.Intent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;

public class MainActivity extends Activity {

	private static final int RESULT_SETTINGS = 1;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
	}
	
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		getMenuInflater().inflate(R.menu.activity_main, menu);
		return true;
	}
	
	public void displaySettings(MenuItem item) {
		Intent intent = new Intent(this, SettingsActivity.class);
		startActivityForResult(intent, RESULT_SETTINGS);
	}
	
	public void displayCameraPreview(View view) {
		Intent intent = new Intent(this, CameraPreviewActivity.class);
		startActivityForResult(intent, RESULT_SETTINGS);
	}
	
	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
		if (requestCode == RESULT_SETTINGS) {
			if (resultCode == RESULT_OK) {
				// startActivity(new Intent(Intent.ACTION_VIEW, data));
			}
		}
	}

}