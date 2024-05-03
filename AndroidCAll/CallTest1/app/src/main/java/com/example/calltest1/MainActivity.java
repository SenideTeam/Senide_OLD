package com.example.calltest1;

import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.telephony.PhoneStateListener;
import android.telephony.TelephonyManager;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.Manifest;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

public class MainActivity extends AppCompatActivity {
    private static final int REQUEST_CALL_PHONE = 1;
    private long startTime; // Tiempo de inicio de la llamada
    private boolean callEnded = false; // Para verificar si la llamada ha terminado

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        TelephonyManager telephonyManager = (TelephonyManager) getSystemService(TELEPHONY_SERVICE);
        telephonyManager.listen(new PhoneStateListener() {
            @Override
            public void onCallStateChanged(int state, String incomingNumber) {
                super.onCallStateChanged(state, incomingNumber);
                if (state == TelephonyManager.CALL_STATE_OFFHOOK) {
                    startTime = System.currentTimeMillis(); // Registrar el tiempo de inicio
                }
                if (state == TelephonyManager.CALL_STATE_IDLE && !callEnded) {
                    long endTime = System.currentTimeMillis();
                    long elapsedTime = endTime - startTime;
                    if (elapsedTime < 15000) { // Menos de 15 segundos
                        Intent webIntent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://www.google.com"));
                        startActivity(webIntent);
                    }
                    callEnded = true;
                } else {
                    callEnded = false;
                }
            }
        }, PhoneStateListener.LISTEN_CALL_STATE);

        setupImageView(findViewById(R.id.imageView1), "684263667"); // Número específico para imageView1
        setupImageView(findViewById(R.id.imageView2), "662204776"); // Número general para otras imágenes
        setupImageView(findViewById(R.id.imageView3), "123456789");
        setupImageView(findViewById(R.id.imageView4), "123456789");

        Button btnCerrar = findViewById(R.id.btnCerrar);
        btnCerrar.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finishAffinity(); // Cierra la aplicación
            }
        });
    }

    private void setupImageView(ImageView imageView, String phoneNumber) {
        imageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent callIntent = new Intent(Intent.ACTION_CALL);
                callIntent.setData(Uri.parse("tel:" + phoneNumber));
                if (ActivityCompat.checkSelfPermission(MainActivity.this, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                    startActivity(callIntent);
                } else {
                    ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.CALL_PHONE}, REQUEST_CALL_PHONE);
                }
            }
        });
    }
}
