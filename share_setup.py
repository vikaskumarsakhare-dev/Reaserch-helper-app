# Lets other apps (Chrome, WhatsApp...) "Share" text into Research Sangrah.
# Run after `npx cap add android`. Keeps .bak copies so the workflow can undo it.
import os, shutil

MAN = "android/app/src/main/AndroidManifest.xml"
JAVA = "android/app/src/main/java/com/shodh/sangrah/MainActivity.java"

shutil.copy(MAN, MAN + ".bak")
shutil.copy(JAVA, JAVA + ".bak")

m = open(MAN, encoding="utf-8").read()
flt = (
    '            <intent-filter>\n'
    '                <action android:name="android.intent.action.SEND" />\n'
    '                <category android:name="android.intent.category.DEFAULT" />\n'
    '                <data android:mimeType="text/plain" />\n'
    '            </intent-filter>\n'
)
assert "</activity>" in m, "manifest has no activity"
m = m.replace("</activity>", flt + "        </activity>", 1)
open(MAN, "w", encoding="utf-8").write(m)

java = '''package com.shodh.sangrah;

import android.content.Intent;
import android.webkit.ValueCallback;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        String action = intent.getAction();
        String type = intent.getType();
        if (Intent.ACTION_SEND.equals(action) && type != null) {
            bridge.getActivity().setIntent(intent);
            bridge.eval("window.dispatchEvent(new Event('sendIntentReceived'))", new ValueCallback<String>() {
                @Override
                public void onReceiveValue(String s) {}
            });
        }
    }
}
'''
open(JAVA, "w", encoding="utf-8").write(java)
print("share setup done")
