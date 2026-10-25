package co.asiven.vixentvpn.trial.ui

import android.Manifest
import android.content.BroadcastReceiver
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.net.VpnService
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import co.asiven.vixentvpn.service.VpnTunnelService
import co.asiven.vixentvpn.trial.BuildConfig
import co.asiven.vixentvpn.trial.R
import co.asiven.vixentvpn.trial.core.ConfigBuilder
import co.asiven.vixentvpn.trial.core.XrayCore
import co.asiven.vixentvpn.trial.data.ApiClient
import co.asiven.vixentvpn.trial.data.PingState
import co.asiven.vixentvpn.trial.data.Prefs
import co.asiven.vixentvpn.trial.data.Server
import co.asiven.vixentvpn.trial.data.ServerParser
import co.asiven.vixentvpn.trial.databinding.ActivityMainBinding
import co.asiven.vixentvpn.trial.util.AppLog
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import org.json.JSONObject

/**
 * Single screen of the trial client:
 *   • one button that fetches **all** servers (free + paid) from `/api/protocols`
 *   • a scrollable list where each row shows the original attributes as labels
 *   • per-row ping and a bulk "ping all" action
 *   • selection + connect through the real Xray/hev stack
 * Every row can export its v2ray share link to the clipboard (v2rayNG compatible).
 * No ads, no sign-in, no price gate.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var prefs: Prefs
    private lateinit var api: ApiClient
    private lateinit var adapter: ServerAdapter

    private val servers = mutableListOf<Server>()
    private var pingJob: Job? = null
    private var pendingServer: Server? = null
    private var tunnelRunning = false
    private var busy = false

    private val vpnPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult(),
    ) { result ->
        val server = pendingServer
        pendingServer = null
        if (result.resultCode == RESULT_OK && server != null) {
            launchTunnel(server)
        } else {
            toast(getString(R.string.vpn_permission_needed))
        }
    }

    private val notificationPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { /* the tunnel still works without the notification; nothing to do */ }

    private val stateReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action != VpnTunnelService.ACTION_STATE) return
            tunnelRunning = intent.getBooleanExtra(VpnTunnelService.EXTRA_RUNNING, false)
            val text = intent.getStringExtra(VpnTunnelService.EXTRA_TEXT).orEmpty()
            binding.statusText.text = text
            binding.connectButton.setText(
                if (tunnelRunning) R.string.btn_disconnect else R.string.btn_connect,
            )
            adapter.setConnectedKey(if (tunnelRunning) prefs.selectedKey else null)
            updateSummary()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        window.decorView.layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL
        AppLog.attach(applicationContext)
        prefs = Prefs(applicationContext)
        api = ApiClient(applicationContext, prefs)
        XrayCore.init(applicationContext)

        adapter = ServerAdapter(
            onSelect = { selectServer(it) },
            onPing = { pingSingle(it) },
            onDetails = { showDetails(it) },
            onCopyLink = { copyShareLink(it) },
        )
        binding.serverList.layoutManager = LinearLayoutManager(this)
        binding.serverList.adapter = adapter

        binding.fetchButton.setOnClickListener { refreshAll() }
        binding.pingAllButton.setOnClickListener { pingAll() }
        binding.connectButton.setOnClickListener { toggleConnection() }
        binding.toolbar.setOnMenuItemClickListener { item ->
            when (item.itemId) {
                R.id.action_raw_json -> {
                    showText(getString(R.string.dlg_raw_title), prefs.protocolsCache.ifBlank { "—" })
                    true
                }
                R.id.action_logs -> {
                    showText(getString(R.string.dlg_log_title), AppLog.dump().ifBlank { "—" })
                    true
                }
                R.id.action_import_clipboard -> {
                    importFromClipboard()
                    true
                }
                R.id.action_toggle_mode -> {
                    toggleMode()
                    true
                }
                else -> false
            }
        }

        updateModeLabel()
        loadCached()
        askNotificationPermissionIfNeeded()
        if (servers.isEmpty()) refreshAll()
    }

    override fun onStart() {
        super.onStart()
        ContextCompat.registerReceiver(
            this,
            stateReceiver,
            IntentFilter(VpnTunnelService.ACTION_STATE),
            ContextCompat.RECEIVER_NOT_EXPORTED,
        )
    }

    override fun onStop() {
        super.onStop()
        runCatching { unregisterReceiver(stateReceiver) }
    }

    // ---------------------------------------------------------------- servers

    private fun loadCached() {
        val cached = prefs.protocolsCache
        if (cached.isBlank()) return
        val parsed = runCatching {
            ServerParser.parseList(JSONObject(cached))
        }.getOrElse {
            AppLog.w("خواندن کش سرورها ناموفق: ${it.message}")
            emptyList()
        }
        if (parsed.isNotEmpty()) {
            servers.clear()
            servers.addAll(parsed)
            adapter.submit(servers, prefs.selectedKey)
            updateSummary()
            AppLog.i("${parsed.size} سرور از کش بارگذاری شد")
        }
    }

    /** The single "fetch and refresh everything" action. */
    private fun refreshAll() {
        if (busy) return
        busy = true
        setProgress(true)
        binding.statusText.text = getString(R.string.status_fetching)
        lifecycleScope.launch {
            pingJob?.cancel()
            val result = withContext(Dispatchers.IO) {
                api.fetchToken()
                api.fetchSetting()
                api.fetchProtocols()
            }
            busy = false
            setProgress(false)
            if (result.isEmpty()) {
                binding.statusText.text = getString(R.string.status_error, "فهرست سرورها دریافت نشد — لاگ‌ها را ببینید")
            } else {
                servers.clear()
                servers.addAll(result)
                if (servers.none { it.key == prefs.selectedKey }) {
                    prefs.selectedKey = servers.firstOrNull()?.key.orEmpty()
                }
                adapter.submit(servers, prefs.selectedKey)
                binding.statusText.text = getString(R.string.status_selected, selectedServer()?.name.orEmpty())
                updateSummary()
            }
        }
    }

    private fun selectServer(server: Server) {
        prefs.selectedKey = server.key
        adapter.setSelected(server.key)
        binding.statusText.text = getString(R.string.status_selected, server.name)
        AppLog.i("سرور انتخاب شد: ${server.name} (price=${server.price}, type=${server.typeHint})")
    }

    private fun selectedServer(): Server? = servers.firstOrNull { it.key == prefs.selectedKey }

    // ---------------------------------------------------------------- ping

    private fun pingSingle(server: Server) {
        server.pingState = PingState.RUNNING
        adapter.updatePing(server)
        lifecycleScope.launch {
            val ms = withContext(Dispatchers.IO) { measure(server) }
            server.pingMs = ms
            server.pingState = if (ms > 0) PingState.OK else PingState.FAILED
            adapter.updatePing(server)
            updateSummary()
        }
    }

    /** Bulk ping with bounded parallelism — the "ping all" action. */
    private fun pingAll() {
        if (servers.isEmpty()) {
            toast(getString(R.string.status_empty))
            return
        }
        pingJob?.cancel()
        setProgress(true)
        val targets = servers.toList()
        targets.forEach { it.pingState = PingState.RUNNING }
        adapter.notifyDataSetChanged()
        val total = targets.size
        var done = 0
        pingJob = lifecycleScope.launch {
            val semaphore = Semaphore(PING_CONCURRENCY)
            coroutineScope {
                targets.map { server ->
                    async(Dispatchers.IO) {
                        semaphore.withPermit {
                            val ms = measure(server)
                            server.pingMs = ms
                            server.pingState = if (ms > 0) PingState.OK else PingState.FAILED
                        }
                        withContext(Dispatchers.Main) {
                            done++
                            binding.summaryText.text = getString(R.string.status_pinging, done, total)
                            adapter.updatePing(server)
                        }
                    }
                }.awaitAll()
            }
            setProgress(false)
            updateSummary()
            AppLog.i("پینگ همهٔ $total سرور انجام شد")
        }
    }

    private fun measure(server: Server): Long {
        val parsed = ConfigBuilder.parse(server)
        val outbound = parsed.outbound ?: run {
            AppLog.w("پینگ ${server.name} ممکن نیست: ${parsed.error}")
            return -1L
        }
        val url = prefs.testUrl.ifBlank { BuildConfig.TEST_URL }
        val ms = XrayCore.measureDelay(ConfigBuilder.pingConfig(outbound), url)
        AppLog.d("پینگ ${server.name}: $ms ms")
        return ms
    }

    // ---------------------------------------------------------------- tunnel

    private fun toggleMode() {
        prefs.mode = if (prefs.mode == Prefs.MODE_VPN) Prefs.MODE_PROXY else Prefs.MODE_VPN
        updateModeLabel()
        toast(if (prefs.mode == Prefs.MODE_VPN) getString(R.string.mode_vpn) else getString(R.string.mode_proxy))
    }

    private fun updateModeLabel() {
        binding.modeText.text = if (prefs.mode == Prefs.MODE_VPN) {
            getString(R.string.mode_vpn)
        } else {
            getString(R.string.mode_proxy)
        }
    }

    private fun toggleConnection() {
        if (tunnelRunning) {
            VpnTunnelService.stop(this)
            return
        }
        val server = selectedServer() ?: run {
            toast("اول یک سرور انتخاب کنید")
            return
        }
        binding.statusText.text = getString(R.string.status_connecting)
        if (prefs.mode == Prefs.MODE_VPN) {
            val permission = VpnService.prepare(this)
            if (permission != null) {
                pendingServer = server
                vpnPermissionLauncher.launch(permission)
                return
            }
        }
        launchTunnel(server)
    }

    private fun launchTunnel(server: Server) {
        runCatching { VpnTunnelService.start(this, server, prefs.mode) }
            .onFailure {
                AppLog.e("شروع سرویس تونل ناموفق", it)
                binding.statusText.text = getString(R.string.status_error, it.message.orEmpty())
            }
    }

    // ---------------------------------------------------------------- ui helpers

    private fun updateSummary() {
        if (servers.isEmpty()) {
            binding.summaryText.text = getString(R.string.status_empty)
            return
        }
        val free = servers.count { it.isFree }
        val paid = servers.size - free
        if (pingJob?.isActive == true) return
        binding.summaryText.text = getString(R.string.status_servers, servers.size, free, paid)
    }

    private fun setProgress(visible: Boolean) {
        binding.progress.visibility = if (visible) android.view.View.VISIBLE else android.view.View.GONE
        binding.fetchButton.isEnabled = !visible
        binding.pingAllButton.isEnabled = !visible
    }

    private fun showDetails(server: Server) {
        val usage = server.usage?.summary().orEmpty().ifBlank { "—" }
        val extras = if (server.extra.isEmpty()) "—" else
            server.extra.entries.joinToString("\n") { "• ${it.key} = ${it.value}" }
        val body = buildString {
            appendLine("نام: ${server.name}")
            appendLine("پرچم/موقعیت: ${server.flag.ifBlank { "—" }}")
            appendLine("نوع: ${server.typeHint}")
            appendLine("قیمت اصلی: ${server.price ?: "—"} ${if (server.isFree) "(رایگان)" else "(پولی)"}")
            appendLine("id: ${server.protocolId ?: "—"}   serverId: ${server.serverId ?: "—"}")
            appendLine("مصرف/سهمیه: $usage")
            appendLine("پینگ: ${if (server.pingMs > 0) "${server.pingMs} ms" else "—"}")
            appendLine()
            appendLine("فیلدهای دیگر پاسخ سرور:")
            appendLine(extras)
            appendLine()
            appendLine("JSON خام این سرور:")
            appendLine(server.rawJson.take(4000))
        }
        AlertDialog.Builder(this)
            .setTitle(R.string.dlg_details_title)
            .setMessage(body)
            .setPositiveButton(R.string.btn_close, null)
            .setNeutralButton(R.string.btn_copy) { _, _ -> copy(server.rawJson) }
            .show()
    }

    /**
     * Imports a server from the clipboard (`vmess://`, `vless://`, `trojan://`, `ss://` or a full
     * Xray JSON config). Useful when the backend hands out an encrypted blob: the tunnel stack is
     * identical, so any working config can still be used, pinged and shared.
     */
    private fun importFromClipboard() {
        val clipboard = getSystemService(ClipboardManager::class.java)
        val text = clipboard?.primaryClip?.takeIf { it.itemCount > 0 }
            ?.getItemAt(0)?.coerceToText(this)?.toString()?.trim().orEmpty()
        if (text.isBlank()) {
            toast(getString(R.string.import_empty))
            return
        }
        val looksLikeConfig = text.startsWith("{") ||
            listOf("vmess://", "vless://", "trojan://", "ss://", "socks://", "http://", "https://")
                .any { text.startsWith(it, ignoreCase = true) }
        if (!looksLikeConfig) {
            toast(getString(R.string.import_invalid))
            return
        }
        val server = ServerParser.fromRaw(text, servers.size)
        servers.add(0, server)
        prefs.selectedKey = server.key
        adapter.submit(servers, prefs.selectedKey)
        updateSummary()
        binding.statusText.text = getString(R.string.status_selected, server.name)
        toast(getString(R.string.import_ok, server.typeHint))
        AppLog.i("کانفیگ دستی اضافه شد: ${server.typeHint} (${text.length} کاراکتر)")
    }

    /** Copies this server as a v2ray share URI so it can be imported into any v2ray client. */
    private fun copyShareLink(server: Server) {
        val link = runCatching { ConfigBuilder.shareLink(server) }.getOrNull()
        if (link.isNullOrBlank()) {
            toast(getString(R.string.link_unavailable))
            AppLog.w("لینک اشتراک برای ${server.name} قابل ساخت نیست (نوع: ${server.typeHint})")
            return
        }
        copy(link)
        toast(getString(R.string.link_copied, server.name))
        AppLog.i("لینک v2ray برای ${server.name} کپی شد (${link.length} کاراکتر)")
    }

    private fun showText(title: String, text: String) {
        AlertDialog.Builder(this)
            .setTitle(title)
            .setMessage(text)
            .setPositiveButton(R.string.btn_close, null)
            .setNeutralButton(R.string.btn_copy) { _, _ -> copy(text) }
            .show()
    }

    private fun copy(text: String) {
        val clipboard = getSystemService(ClipboardManager::class.java)
        clipboard.setPrimaryClip(ClipData.newPlainText("mvpn-trial", text))
        toast(getString(R.string.dlg_copied))
    }

    private fun toast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun askNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) !=
            PackageManager.PERMISSION_GRANTED
        ) {
            notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    companion object {
        private const val PING_CONCURRENCY = 4
    }
}
