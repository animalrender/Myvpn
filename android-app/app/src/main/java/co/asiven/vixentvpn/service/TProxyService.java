package co.asiven.vixentvpn.service;

/**
 * JNI binding for <b>hev-socks5-tunnel</b> — the same TUN→SOCKS5 engine the analysed APK
 * and v2rayNG stack on top of Xray.
 *
 * <p>The library is compiled with {@code -DPKGNAME=co/asiven/vixentvpn/service} and
 * {@code -DCLSNAME=TProxyService}; hev's {@code JNI_OnLoad} registers the natives on this
 * exact class, so the fully-qualified name and the method signatures below are part of the
 * ABI. Keep them in sync with {@code tools/build-hevtun.sh}.
 */
public final class TProxyService {

    static {
        System.loadLibrary("hev-socks5-tunnel");
    }

    private TProxyService() {
    }

    /**
     * Starts the tunnel thread.
     *
     * @param configPath absolute path of the hev YAML config
     * @param fd         the TUN file descriptor obtained from {@code VpnService.Builder.establish()}
     * @return true when the tunnel thread started
     */
    public static native boolean TProxyStartService(String configPath, int fd);

    public static native boolean TProxyStopService();

    public static native boolean TProxyIsRunning();

    /** @return {@code [tx_packets, tx_bytes, rx_packets, rx_bytes]} */
    public static native long[] TProxyGetStats();
}
