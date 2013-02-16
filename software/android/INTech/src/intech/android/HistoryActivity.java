package intech.android;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import android.app.ListActivity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;

public class HistoryActivity extends ListActivity {

	private final String TAG = "INTech";
	private File imageDirectory;
	private String fileNameArray[];

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		// setContentView(R.layout.activity_history);

		imageDirectory = new File(
				Environment
						.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES),
				"INTech");

		File fileArray[] = imageDirectory.listFiles();
		fileNameArray = new String[fileArray.length];
		
		for (int i = 0; i < fileArray.length; i++) {
			fileNameArray[i] = fileArray[i].getName();
		}

		setListAdapter(new ArrayAdapter<String>(this, R.layout.activity_history, fileNameArray));
		ListView listView = getListView();
		listView.setTextFilterEnabled(true);
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		getMenuInflater().inflate(R.menu.activity_history, menu);
		return true;
	}

	@Override
	public void onListItemClick(ListView l, View v, int position, long id) {
		Log.d(TAG, imageDirectory.getAbsolutePath() + "/" + fileNameArray[position]);
		Intent intent = new Intent(HistoryActivity.this, DisplayImageActivity.class);
		intent.putExtra("image_path", imageDirectory.getAbsolutePath() + "/" + fileNameArray[position]);
		intent.putExtra("socket_mode", false);
		startActivity(intent);
	}

	public void eraseAll(MenuItem item) {
		File fileArray[] = imageDirectory.listFiles();
		for (int i = 0; i < fileArray.length; i++) {
			fileArray[i].delete();
		}
		finish();
		startActivity(getIntent());
	}

}
