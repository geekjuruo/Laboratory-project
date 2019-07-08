package com.example.thu_4over6_vpn;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.util.Log;

import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.Enumeration;
import java.net.InetAddress;


// class NetChecker
// 检查手机网络连接状态，获取ipv6地址类
public class NetChecker {

    /**
     * 检查手机wifi连接状态
     * @param context
     * @return
     */
    private static boolean isWIFIConnected(Context context) {
        if (context != null) {
            ConnectivityManager mConnectivityManager = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
            NetworkInfo mWiFiNetworkInfo = mConnectivityManager.getNetworkInfo(ConnectivityManager.TYPE_WIFI);
            if (mWiFiNetworkInfo != null && mWiFiNetworkInfo.isConnected()) {
                return true;
            }
            else {
                //Log.e("Net State", "无 Wifi 连接，请设置 wifi 连接");
            }
        }
        return false;
    }

    /**
     * 检查手机蜂窝网络状态连接
     * @param context
     * @return
     */
    private static  boolean isMOBILEConnected(Context context) {
        if (context != null) {
            ConnectivityManager mConnectivityManager = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
            NetworkInfo mPhoneNetworkInfo = mConnectivityManager.getNetworkInfo(ConnectivityManager.TYPE_MOBILE);
            if (mPhoneNetworkInfo != null && mPhoneNetworkInfo.isConnected()) {
                return true;
            }
            else {
                // Log.e("Net State", "无数字信号连接，请设置网络连接");
            }
        }
        return false;
    }

    /**
     * 检查手机网络连接状态
     * @param context
     * @return
     */
    static boolean checkNet(Context context) {
        // 判断连接的方式为wifi连接还是手机网络连接
        boolean wifiConnectedState = isWIFIConnected(context);
        boolean mobileConnectedState = isMOBILEConnected(context);

        // 二者之一需要连接成功
        return wifiConnectedState || mobileConnectedState;
    }

    /**
     * 获取 IPV6 地址
     * @param context
     * @return
     */
    static String getIpv6Address(Context context) {
        // 保证wifi连接成功----支持蜂窝流量？？ipv6 不支持蜂窝流量
        if(! isWIFIConnected(context)) {
            return null;
        }
        try {
            for(Enumeration<NetworkInterface> en = NetworkInterface.getNetworkInterfaces(); en.hasMoreElements(); ) {
                NetworkInterface networkInterface = en.nextElement();
                for (Enumeration<InetAddress> enumAddress = networkInterface.getInetAddresses(); enumAddress.hasMoreElements(); ) {
                    InetAddress inetAddress = enumAddress.nextElement();
                    if (!inetAddress.isLoopbackAddress() && !inetAddress.isLinkLocalAddress()) {
                        return inetAddress.getHostAddress();
                    }
                }
            }
        } catch(SocketException socketException) {
            Log.e("Net State", socketException.toString());
        }
        return null;
    }
}

