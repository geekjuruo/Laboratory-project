package com.example.thu_4over6_vpn;


import android.content.Intent;
import android.net.VpnService;
import android.os.ParcelFileDescriptor;
import android.util.Log;

import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileOutputStream;


public class MyVpnService extends VpnService {
    private static final String TAG = "THU_4over6_VPN Service";             // 输出 TAG
    private ParcelFileDescriptor mInterface;
    String ipHandleName = "/data/data/com.example.thu_4over6_vpn/mypipe";
    //Configure a builder for the interface.
    Builder builder = new Builder();

    // Services interface
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // 获取从前端传来的信息
        String ipAddress = intent.getStringExtra("ip");
        String route = intent.getStringExtra("route");
        String dns = intent.getStringExtra("DNS2");
        String socket = intent.getStringExtra("socket");
        try {
            protect(Integer.parseInt(socket));
        } catch (Exception e) {
            Log.e(TAG, "onStartCommand: no socket");
            e.printStackTrace();
        }

        //Set MTU equal 1000 to avoid incomplete packet from server
        mInterface = builder.setSession("MyVPNService")
                .addAddress(ipAddress, 24)
                .addDnsServer(dns)
                .addRoute(route, 0)
                .setMtu(1000)
                .establish();

        // 定期向管道文件写入前台的数据信息
        try{
            File file = new File(ipHandleName);
            FileOutputStream fileOutputStream = new FileOutputStream(file);
            BufferedOutputStream out = new BufferedOutputStream(fileOutputStream);

            //transfer int to byte[]
            int fd = mInterface.getFd();
            ByteArrayOutputStream boutput = new ByteArrayOutputStream();
            DataOutputStream doutput = new DataOutputStream(boutput);
            doutput.writeInt(fd);
            byte[] buf = boutput.toByteArray();

            //Pass the file descriptor to background
            out.write(buf, 0, buf.length);
            out.flush();
            out.close();
        } catch(Exception e){
            e.printStackTrace();
        }
        //Start the service
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        // TODO Auto-generated method stub
        super.onDestroy();
    }
}
