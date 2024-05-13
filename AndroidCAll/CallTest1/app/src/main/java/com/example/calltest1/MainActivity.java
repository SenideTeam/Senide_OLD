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
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import android.Manifest;

public class MainActivity extends AppCompatActivity {
    private static final int REQUEST_CALL_PHONE = 1;
    private static final int REQUEST_READ_PHONE_STATE = 2;
    private long startTime; // Tiempo de inicio de la llamada
    private boolean callEnded = true; // Para verificar si la llamada ha terminado
    private String currentUserId = ""; // Almacenar el ID del usuario actual

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.READ_PHONE_STATE) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_PHONE_STATE}, REQUEST_READ_PHONE_STATE);
        } else {
            initTelephonyManager();
        }

        setupImageView(findViewById(R.id.imageView1), "684263667", "1");//Gerson
        setupImageView(findViewById(R.id.imageView2), "662204776", "2");//Aritz
        setupImageView(findViewById(R.id.imageView3), "634431480", "3");//Telle
        setupImageView(findViewById(R.id.imageView4), "688826404", "4");//Gorka

        Button btnCerrar = findViewById(R.id.btnCerrar);
        btnCerrar.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finishAffinity(); // Cierra la aplicación
            }
        });
    }

    private void initTelephonyManager() {
        TelephonyManager telephonyManager = (TelephonyManager) getSystemService(TELEPHONY_SERVICE);
        telephonyManager.listen(new PhoneStateListener() {
            @Override
            public void onCallStateChanged(int state, String incomingNumber) {
                super.onCallStateChanged(state, incomingNumber);
                switch (state) {
                    case TelephonyManager.CALL_STATE_OFFHOOK:
                        startTime = System.currentTimeMillis();
                        callEnded = false;
                        break;
                    case TelephonyManager.CALL_STATE_IDLE:
                        if (!callEnded) {
                            long endTime = System.currentTimeMillis();
                            long elapsedTime = endTime - startTime;
                            if (elapsedTime < 15000) {
                                Intent webIntent = new Intent(Intent.ACTION_VIEW, Uri.parse("http://dirección?uid=" + currentUserId));
                                startActivity(webIntent);
                            }
                            callEnded = true;
                        }
                        break;
                }
            }
        }, PhoneStateListener.LISTEN_CALL_STATE);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_READ_PHONE_STATE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                initTelephonyManager();
            } else {
                Toast.makeText(this, "Permission denied to read phone state", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void setupImageView(ImageView imageView, String phoneNumber, String userId) {
        imageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                currentUserId = userId; // Establecer el ID del usuario actual
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
