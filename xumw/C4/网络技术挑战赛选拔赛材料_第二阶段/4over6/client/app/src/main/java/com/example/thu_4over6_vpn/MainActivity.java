package com.example.thu_4over6_vpn;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.content.Intent;
import android.net.VpnService;
import android.widget.Toast;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.util.Date;
import java.util.Timer;



import static com.example.thu_4over6_vpn.NetChecker.checkNet;
import static com.example.thu_4over6_vpn.NetChecker.getIpv6Address;

public class MainActivity extends AppCompatActivity {

    /**
     * A native method that is implemented by the 'native-lib' native library,
     * which is packaged with this application.
     */
    // Used to load the 'native-lib' library on application startup.
    static {
        System.loadLibrary("native-lib");
    }
    // JNI 后台函数
    public native String stringFromJNI();
    public native int startVpnFromJNI(String addr, int port);
    public native int quitVpnFromJNI();

    // =========================== 全局变量记录 =========================== //
    final private static String TAG = "THU_4over6_VPN Activity";

    public float KB = 1024;                    // 2 << 10
    public float MB = 1048576;                 // 2 << 20
    public float GB = 1073741824;              // 2 << 30

    private Thread IVIthread;           // native C thread
    private Thread BackGroundthread;    // background thread
    private IpInfo ip_packet;
    private PackageInfo packageInfo;
    private Date startTime;
    private int isStart = 0;            // VPN 是否开启了服务
    private long sendBytes, receiveBytes, sendPackets, receivePackets;
    String ipHandleName = "/data/data/com.example.thu_4over6_vpn/mypipe";
    String statsHandleName = "/data/data/com.example.thu_4over6_vpn/mypipe_stats";
    Intent serviceIntent;

    // 是否允许启动后台，首先满足存在 ipv6 地址
    private boolean allow = false;


    // UI 界面 点击【断开 VPN】以前
    private Button UI_stopButton;                   //【断开 VPN】按钮
    private TextView UI_time_info;
    private TextView UI_up_speed_info;
    private TextView UI_down_speed_info;
    private TextView UI_send_info;
    private TextView UI_receive_info;
    private TextView UI_ipv4_addr;
    private TextView UI_ipv6_addr;

    // UI 界面 点击【连接 VPN】以前
    private Button UI_startButton;                  //【连接 VPN】按钮
    private Button UI_quitButton;                   //【退出程序】按钮
    private TextView UI_label_server_ipv6_addr;     // 服务器ipv6地址标题栏
    private EditText UI_server_ipv6_addr;           // 服务器ipv6地址填写
    private TextView UI_label_server_port;          // 服务器端口标题栏
    private EditText UI_server_port;                // 服务器端口填写
    private TextView UI_label_local_ipv6_addr;      // 本地ipv6地址标题栏
    private EditText UI_local_ipv6_addr;            // 本地ipv6地址显示栏
    private ImageView UI_logo;                      // logo图片

    // =========================== 类定义 =========================== //

    class IpInfo{                   // ipv4 地址信息类
        public String ipAddress;
        public String route;
        public String DNS1,DNS2,DNS3;
        public String socket;
    }

    class PackageInfo{              // 数据包信息类
        public String time_duration;
        public String speed_info;
        public String up_speed;
        public String down_speed;
        public String send_info;
        public String receive_info;
        public String ipv4_addr;
        public String ipv6_addr;
    }


    //timer routine
    class MyTimeertask extends java.util.TimerTask {

        public void run(){
            File file = new File(statsHandleName);
            while (!file.exists()){             // 检查管道是否存在
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }

            // 读取流量信息管道
            try {
                FileInputStream fileInputStream = new FileInputStream(file);
                BufferedInputStream in = new BufferedInputStream(fileInputStream);
                byte buf[] = new byte[1024];
                int readLen = in.read(buf, 0, 1024);

                if (readLen > 0){
                    String ipStatInfo = new String(buf);
                    String piece[] = ipStatInfo.split(" ");
                    packageInfo.speed_info = "网速: 上传速度：" + piece[0] + " Bytes/s  ，下载速度： "+piece[2]+" Bytes/s";
                    packageInfo.up_speed = "网速: 上传速度：" + speed_to_MGB(piece[0]);
                    packageInfo.down_speed = "网速: 下载速度： " + speed_to_MGB(piece[2]);
                    sendBytes += Long.parseLong(piece[0]);
                    sendPackets += Long.parseLong(piece[1]);
                    receiveBytes += Long.parseLong(piece[2]);
                    receivePackets += Long.parseLong(piece[3]);
                    packageInfo.send_info = "总共发送数据包: " + size_to_MGB(sendBytes) + " / " + Long.toString(sendPackets) + " packets";
                    packageInfo.receive_info = "总共接收数据包: " + size_to_MGB(receiveBytes) + " / " + Long.toString(receivePackets) + " packets";
                    long time_dura = (new Date().getTime() - startTime.getTime()) / 1000;
                    long hour = time_dura / 3600;
                    long min = (time_dura % 3600) / 60;
                    long sec = time_dura % 60;
                    packageInfo.time_duration = "运行计时: " + hour + " h " + min + " m " + sec + " s";

                    // 刷新界面
                    Log.v(TAG, "update Package Info");
                    new Handler(Looper.getMainLooper()).post(new Runnable() {
                        @Override
                        public void run() {
                            UI_time_info.setText(packageInfo.time_duration);
                            UI_up_speed_info.setText(packageInfo.up_speed);
                            UI_down_speed_info.setText(packageInfo.down_speed);
                            UI_send_info.setText(packageInfo.send_info);
                            UI_receive_info.setText(packageInfo.receive_info);
                            UI_ipv4_addr.setText(packageInfo.ipv4_addr);
                            UI_ipv6_addr.setText(packageInfo.ipv6_addr);
                        }
                    });
                }
                in.close();
            }catch (Exception e){
                e.printStackTrace();
            }
        }
    }

    // 点击连接VPN后UI变化
    public void setUIStart() {
        try {
            UI_startButton.setVisibility(View.GONE);                        //【连接 VPN】按钮不可见
            UI_quitButton.setVisibility(View.GONE);                         //【退出程序】按钮不可见
            UI_label_server_port.setVisibility(View.GONE);                  // 服务器端口标题栏不可见
            UI_label_server_ipv6_addr.setVisibility(View.GONE);             // 服务器地址标题栏不可见
            UI_label_local_ipv6_addr.setVisibility(View.GONE);              // 当前本地地址标题栏不可见
            UI_server_port.setVisibility(View.GONE);                        // 服务器端口不可见
            UI_server_ipv6_addr.setVisibility(View.GONE);                   // 服务器地址不可见
            UI_local_ipv6_addr.setVisibility(View.GONE);                    // 本地地址不可见
            UI_logo.setVisibility(View.GONE);                               // logo不可见

            UI_stopButton.setVisibility(View.VISIBLE);                      //【断开 VPN】按钮可见
            UI_time_info.setVisibility(View.VISIBLE);
            UI_up_speed_info.setVisibility(View.VISIBLE);
            UI_down_speed_info.setVisibility(View.VISIBLE);
            UI_send_info.setVisibility(View.VISIBLE);
            UI_receive_info.setVisibility(View.VISIBLE);
            UI_ipv4_addr.setVisibility(View.VISIBLE);
            UI_ipv6_addr.setVisibility(View.VISIBLE);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // 点击断开VPN后UI变化
    public void setUIStop() {
        try {
            UI_startButton.setVisibility(View.VISIBLE);                     //【连接 VPN】按钮可见
            UI_quitButton.setVisibility(View.VISIBLE);                      //【退出程序】按钮可见
            UI_label_server_port.setVisibility(View.VISIBLE);               // 服务器端口标题栏可见
            UI_label_server_ipv6_addr.setVisibility(View.VISIBLE);          // 服务器地址标题栏可见
            UI_label_local_ipv6_addr.setVisibility(View.VISIBLE);           // 当前本地地址标题栏可见
            UI_server_port.setVisibility(View.VISIBLE);                     // 服务器端口可见
            UI_server_ipv6_addr.setVisibility(View.VISIBLE);                // 服务器地址可见
            UI_local_ipv6_addr.setVisibility(View.VISIBLE);                 // 本地地址可见
            UI_logo.setVisibility(View.VISIBLE);                            // logo可见

            UI_stopButton.setVisibility(View.GONE);                         //【断开 VPN】按钮可见
            UI_time_info.setVisibility(View.GONE);
            UI_up_speed_info.setVisibility(View.GONE);
            UI_down_speed_info.setVisibility(View.GONE);
            UI_send_info.setVisibility(View.GONE);
            UI_receive_info.setVisibility(View.GONE);
            UI_ipv4_addr.setVisibility(View.GONE);
            UI_ipv6_addr.setVisibility(View.GONE);

        }
        catch (Exception e) {
            e.printStackTrace();
        }
    }

    // 读取 IP 信息管道
    protected IpInfo getIpInfo(){
        File file = new File(ipHandleName);
        while (!file.exists()){
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        IpInfo my_ipInfo = null;
        try {
            FileInputStream fileInputStream = new FileInputStream(file);
            BufferedInputStream in = new BufferedInputStream(fileInputStream);
            byte buf[] = new byte[1024];
            int readLen = in.read(buf, 0, 1024);
            if (readLen > 0){
                String ipDataInfo = new String(buf);
                String piece[] = ipDataInfo.split(" ");
                my_ipInfo = new IpInfo();
                my_ipInfo.ipAddress = piece[0];
                my_ipInfo.route = piece[1];
                my_ipInfo.DNS1 = piece[2];
                my_ipInfo.DNS2 = piece[3];
                my_ipInfo.DNS3 = piece[4];
                my_ipInfo.socket = piece[5];
            }
            in.close();
        }catch (Exception e){
            System.out.println(e);
        }
        return my_ipInfo;
    }

    private Intent getServiceIntent() {

        if (serviceIntent == null) {
            Log.e(TAG, "getServiceIntent: New Intent");
            serviceIntent = new Intent(this, MyVpnService.class);
        }
        return serviceIntent;
    }

    // 打开 VPN Service 服务
    protected void onActivityResult(int request, int result, Intent data) {
        if (result == RESULT_OK) {
            getServiceIntent();

            // 传递数据给 MyVpnService
            serviceIntent.putExtra("ip", ip_packet.ipAddress);
            serviceIntent.putExtra("route", ip_packet.route);
            serviceIntent.putExtra("DNS1", ip_packet.DNS1);
            serviceIntent.putExtra("DNS2", ip_packet.DNS2);
            serviceIntent.putExtra("DNS3", ip_packet.DNS3);
            serviceIntent.putExtra("socket", ip_packet.socket);
            startService(serviceIntent);
        }
    }

    // 程序正常退出
    public void exit(){
        quitVpnFromJNI();
        System.exit(0);
    }

    // 网速大小转换
    public String speed_to_MGB(String bytes) {
        float bytes_ = Float.parseFloat(bytes);
        String speed = "";
        if(bytes_ < KB) {
            speed = Float.toString((float)(Math.round(bytes_ * 1000)) / 1000);
            speed += " B/s";
        } else if(bytes_ < MB) {
            bytes_ = bytes_ / KB;
            speed = Float.toString((float)(Math.round(bytes_ * 1000)) / 1000);
            speed += " KB/s";
        } else if(bytes_ < GB){
            bytes_ = bytes_ / MB;
            speed = Float.toString((float)(Math.round(bytes_ * 1000)) / 1000);
            speed += " MB/s";
        } else {
            bytes_ = bytes_ / GB;
            speed = Float.toString((float)(Math.round(bytes_ * 1000)) / 1000);
            speed += " GB/s";
        }
        return speed;
    }

    // 数据包大小转换
    public String size_to_MGB(long bytes) {
        float bytes_ = (float)bytes;
        String size = "";
        if(bytes_ < KB) {
            size = Float.toString((float)(Math.round(bytes_ * 1000)) / 1000);;
            size += " B";
        } else if(bytes_ < MB) {
            bytes_ = bytes_ / KB;
            size = Float.toString((float)(Math.round(bytes_ * 1000)) / 1000);;
            size += " KB";
        } else if(bytes_ < GB){
            bytes_ = bytes_ / MB;
            size = Float.toString((float)(Math.round(bytes_ * 1000)) / 1000);;
            size += " MB";
        } else {
            bytes_ = bytes_ / GB;
            size = Float.toString((float)(Math.round(bytes_ * 1000)) / 1000);;
            size += " GB";
        }
        return size;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        sendBytes = 0;
        receiveBytes = 0;
        sendPackets = 0;
        receivePackets = 0;

        // 绑定 UI 组件 初始界面
        UI_startButton = (Button) findViewById(R.id.start_service);
        UI_quitButton = (Button) findViewById(R.id.quit);
        UI_label_server_ipv6_addr = (TextView) findViewById(R.id.label_address);
        UI_server_ipv6_addr = (EditText) findViewById(R.id.address);
        UI_label_server_port = (TextView) findViewById(R.id.label_port);
        UI_server_port = (EditText) findViewById(R.id.port);
        UI_label_local_ipv6_addr = (TextView) findViewById(R.id.label_local_ipv6);
        UI_local_ipv6_addr = (EditText) findViewById(R.id.local_address);
        UI_logo = (ImageView)findViewById(R.id.item_logo);

        // 绑定 UI 组件 连接界面
        UI_stopButton = (Button) findViewById(R.id.stop_service);
        UI_time_info = (TextView) findViewById(R.id.time_duration);
        UI_up_speed_info = (TextView) findViewById(R.id.up_speed_info);
        UI_down_speed_info = (TextView) findViewById(R.id.down_speed_info);
        UI_send_info = (TextView) findViewById(R.id.send_info);
        UI_receive_info = (TextView) findViewById(R.id.receive_info);
        UI_ipv4_addr = (TextView) findViewById(R.id.ipv4_addr);
        UI_ipv6_addr = (TextView) findViewById(R.id.ipv6_addr);

        packageInfo = new PackageInfo();

        // 初始化界面
        setUIStop();


        //push button to start service
        UI_startButton.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {

                if(!allow) {    // 是否允许开启后台线程
                    Toast.makeText(getApplicationContext(), "无IPV6网络，请检查网络连接状态...", Toast.LENGTH_SHORT).show();
                }
                else {
                    // TODO Auto-generated method stub
                    packageInfo.ipv6_addr = getIpv6Address(getApplicationContext());
                    if (isStart == 0 && packageInfo.ipv6_addr != null) {
                        packageInfo.ipv6_addr = "ipv6 地址：" + packageInfo.ipv6_addr;
                        // 初始化界面
                        setUIStart();

                        //create C thread
                        IVIthread = new Thread() {
                            @Override
                            public void run() {
                                String server_address = UI_server_ipv6_addr.getText().toString();
                                int server_port = Integer.parseInt(UI_server_port.getText().toString());
                                startVpnFromJNI(server_address, server_port);
                            }
                        };
                        IVIthread.start();
                        //create Background thread
                        BackGroundthread = new Thread() {
                            @Override
                            public void run() {
                                //read for ip info
                                ip_packet = getIpInfo();
                                packageInfo.ipv4_addr = "ipv4 地址：" + ip_packet.ipAddress;
                                //create vpnService
                                Intent intent = VpnService.prepare(MainActivity.this);
                                if (intent != null) {
                                    startActivityForResult(intent, 0);
                                } else {
                                    onActivityResult(0, RESULT_OK, null);
                                }
                                //start timer for GUI refreshing
                                startTime = new Date();
                                Timer timer = new Timer();
                                timer.schedule(new MyTimeertask(), 500, 1000);      //500ms delay and 1s cycle
                            }
                        };
                        BackGroundthread.start();
                        //Set start flag
                        isStart = 1;
                    } else if (packageInfo.ipv6_addr == null) {
                        Log.d(TAG, "network unavailable!");
                    }
                }
            }
        });

        //push button to stop service
        UI_stopButton.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                // TODO Auto-generated method stub
                File file = new File(ipHandleName);
                try {
                    // 初始化界面
                    setUIStop();


                    FileOutputStream fileOutputStream = new FileOutputStream(file);
                    BufferedOutputStream out = new BufferedOutputStream(fileOutputStream);
                    byte goodbye[] = "999\n".getBytes();
                    //Notify the background C thread
                    out.write(goodbye, 0, goodbye.length);
                    out.flush();
                    out.close();
                    Log.e(TAG, "say good bye to JNI");
                    BackGroundthread.interrupt();
                    Log.e(TAG, "backgroudthread interrupt");
                    stopService(getServiceIntent());
                    Log.e(TAG, "stop service");
                    //Clear the start flag
                    isStart = 0;
                } catch (Exception e){
                    e.printStackTrace();
                }
            }
        });

        UI_quitButton.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                exit();         // 退出程序
            }
        });

        // 每2s检查是否有ipv6访问权限
        final Handler net_handler = new Handler();
        Runnable runnable=new Runnable() {
            @Override
            public void run() {
                // TODO Auto-generated method stub
                if (checkNet(getApplicationContext())) {
                    Log.d("Net", "网络已连接");
                    String iPv6_addr = getIpv6Address(getApplicationContext());
                    if (iPv6_addr != null) {
                        allow = true;
                        UI_local_ipv6_addr.setText(iPv6_addr);
                    } else {
                        allow = false;
                        Toast.makeText(getApplicationContext(), "无IPv6访问权限，请检查网络, 2s后重试...", Toast.LENGTH_SHORT).show();
                        UI_local_ipv6_addr.setText("无IPv6访问权限，请检查网络");
                    }
                }
                else {
                    Toast.makeText(getApplicationContext(), "无IPv6访问权限，请检查网络, 2s后重试...", Toast.LENGTH_SHORT).show();
                    allow = false;
                }
                //要做的事情
                net_handler.postDelayed(this, 2000);
            }
        };
        net_handler.postDelayed(runnable, 2000);//每两秒检查一次网络runnable.
    }
}
