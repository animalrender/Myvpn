package co.asiven.vixentvpn.trial.ui

import android.Manifest
import android.content.BroadcastReceiver
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.content.res.ColorStateList
import android.net.VpnService
import android.os.Build
import android.os.Bundle
import android.view.View
import android.widget.EditText
import android.widget.PopupMenu
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.widget.doAfterTextChanged
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
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.button.MaterialButton
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

    /** Key of the server the tunnel is currently running on (null when disconnected). */
    private var connectedKey: String? = null
    private var busy = false
    private var filterMode = FilterMode.ALL

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
            if (tunnelRunning) {
                // The service is the owner of the live server; adopt its key when this instance
                // does not know it yet (screen re-created, permission dialog round-trip).
                if (connectedKey.isNullOrBlank()) connectedKey = prefs.connectedKey.ifBlank { null }
            } else {
                connectedKey = null
            }
            val text = intent.getStringExtra(VpnTunnelService.EXTRA_TEXT).orEmpty()
            binding.statusText.text = text
            // The label is owned by updateHero(): it also distinguishes "disconnect" from
            // "switch to the selected server".
            paintStatusDot()
            adapter.setConnectedKey(if (tunnelRunning) connectedKey else null)
            updateHero()
            updateSummary()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        window.decorView.layoutDirection = View.LAYOUT_DIRECTION_RTL
        AppLog.attach(applicationContext)
        prefs = Prefs(applicationContext)
        api = ApiClient(applicationContext, prefs)
        XrayCore.init(applicationContext)

        adapter = ServerAdapter(
            onSelect = { selectServer(it) },
            onPing = { pingSingle(it) },
            onDetails = { showServerSheet(it) },
            onCopyLink = { copyShareLink(it) },
        )
        binding.serverList.layoutManager = LinearLayoutManager(this)
        binding.serverList.adapter = adapter

        binding.fetchButton.setOnClickListener { refreshAll() }
        binding.pingAllButton.setOnClickListener { pingAll() }
        binding.connectButton.setOnClickListener { toggleConnection() }
        binding.menuButton.setOnClickListener { showOverflow(it) }
        binding.searchInput.doAfterTextChanged { applyFilter() }
        binding.filterChips.setOnCheckedChangeListener { _, checkedId ->
            filterMode = when (checkedId) {
                R.id.chipFree -> FilterMode.FREE
                R.id.chipPaid -> FilterMode.PAID
                R.id.chipReady -> FilterMode.READY
                else -> FilterMode.ALL
            }
            applyFilter()
        }

        // A tunnel may already be running (the service outlives this activity, and a link
        // intent can create a new instance), so the initial state comes from the prefs.
        tunnelRunning = prefs.tunnelRunning
        connectedKey = prefs.connectedKey.ifBlank { null }
        paintStatusDot()
        updateModeLabel()
        updateHero()
        updateSummary()
        loadCached()
        // When a selection was restored from the previous run, the status line must say so
        // instead of claiming that nothing is selected.
        selectedServer()?.let { binding.statusText.text = getString(R.string.status_selected, it.name) }
        askNotificationPermissionIfNeeded()
        if (servers.isEmpty()) refreshAll()
        handleIncoming(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleIncoming(intent)
    }

    /**
     * Accepts a config the way v2rayNG does: `ACTION_VIEW` on a `vless://`/`vmess://`/`trojan://`/
     * `ss://` link, or `ACTION_SEND` with the share text. Sharing a subscription link from a
     * browser or a messenger therefore lands directly in this client.
     */
    private fun handleIncoming(intent: Intent?) {
        if (intent == null) return
        val data = intent.data?.toString()
        val text = data ?: intent.getStringExtra(Intent.EXTRA_TEXT)
        if (text.isNullOrBlank()) return
        val single = text.trim().lines().firstOrNull { it.isNotBlank() }?.trim().orEmpty()
        if (single.isBlank()) return
        // A subscription URL is fetched, a single config is imported directly.
        if (single.startsWith("http://", true) || single.startsWith("https://", true)) {
            importSubscription(single)
            return
        }
        importRaw(single)
    }

    override fun onStart() {
        super.onStart()
        // The tunnel state can change while this screen is stopped (notification, another
        // activity instance, service restart), so the header is re-synced on every start.
        tunnelRunning = prefs.tunnelRunning
        connectedKey = prefs.connectedKey.ifBlank { null }
        paintStatusDot()
        updateHero()
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

    // ------------------------------------------------------------------- menu

    private fun showOverflow(anchor: View) {
        val popup = PopupMenu(this, anchor)
        menuInflater.inflate(R.menu.menu_main, popup.menu)
        popup.setOnMenuItemClickListener { item -> handleMenu(item.itemId) }
        popup.show()
    }

    private fun handleMenu(itemId: Int): Boolean = when (itemId) {
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
        R.id.action_self_test -> {
            showText(getString(R.string.dlg_self_test_title), api.selfTest())
            true
        }
        R.id.action_import_sub -> {
            promptSubscription()
            true
        }
        R.id.action_toggle_mode -> {
            toggleMode()
            true
        }
        else -> false
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
            applyFilter()
            updateHero()
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
                val reason = api.lastError.ifBlank { prefs.protocolsSource.ifBlank { "—" } }
                binding.statusText.text = getString(R.string.status_error, reason.lineSequence().first())
                paintStatusDot()
                showText(getString(R.string.dlg_fetch_failed_title), reason)
            } else {
                servers.clear()
                servers.addAll(result)
                if (servers.none { it.key == prefs.selectedKey }) {
                    prefs.selectedKey = servers.firstOrNull()?.key.orEmpty()
                }
                adapter.submit(servers, prefs.selectedKey)
                applyFilter()
                updateHero()
                binding.statusText.text = getString(R.string.status_selected, selectedServer()?.name.orEmpty())
                paintStatusDot()
                updateSummary()
            }
        }
    }

    private fun selectServer(server: Server) {
        prefs.selectedKey = server.key
        adapter.setSelected(server.key)
        binding.statusText.text = getString(R.string.status_selected, server.name)
        paintStatusDot()
        updateHero()
        AppLog.i("سرور انتخاب شد: ${server.name} (price=${server.price}, type=${server.typeHint})")
    }

    private fun selectedServer(): Server? = servers.firstOrNull { it.key == prefs.selectedKey }

    /**
     * Fallback for «اتصال» when no row was selected yet: the quickest row that answered the last
     * ping, else the quickest row at all, else the first readable row.
     */
    private fun pickBestOrNull(): Server? {
        val usable = servers.filterNot { it.isOpaquePayload }
        return usable.filter { it.pingState == PingState.OK && it.pingMs > 0 }.minByOrNull { it.pingMs }
            ?: usable.firstOrNull()
    }

    private fun applyFilter() {
        adapter.setFilter(binding.searchInput.text?.toString().orEmpty(), filterMode)
        // Re-applied on every list rebuild: the live server keeps its "connected" marker even
        // when the user filters or refreshes the list.
        adapter.setConnectedKey(if (tunnelRunning) connectedKey else null)
        updateSummary()
    }

    // ---------------------------------------------------------------- ping

    private fun pingSingle(server: Server) {
        if (server.isOpaquePayload) {
            toast(getString(R.string.msg_no_ping_opaque))
            return
        }
        server.pingState = PingState.RUNNING
        adapter.updatePing(server)
        updateHero()
        lifecycleScope.launch {
            val ms = withContext(Dispatchers.IO) { measure(server) }
            server.pingMs = ms
            server.pingState = if (ms > 0) PingState.OK else PingState.FAILED
            adapter.updatePing(server)
            updateHero()
            updateSummary()
        }
    }

    /** Bulk ping with bounded parallelism — the "ping all" action. */
    private fun pingAll() {
        if (servers.isEmpty()) {
            toast(getString(R.string.status_empty))
            return
        }
        val measurable = servers.filterNot { it.isOpaquePayload }
        if (measurable.isEmpty()) {
            toast(getString(R.string.msg_no_ping_opaque))
            return
        }
        pingJob?.cancel()
        setProgress(true)
        val targets = measurable
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
            // The fastest row that actually answered becomes the selection, so the next tap on
            // «اتصال» is enough — the app never asks the user to pick a server by hand.
            val fastest = targets
                .filter { it.pingState == PingState.OK && it.pingMs > 0 }
                .minByOrNull { it.pingMs }
            if (fastest != null && selectedServer()?.pingState != PingState.OK) {
                selectServer(fastest)
                toast(getString(R.string.toast_fastest_selected, fastest.name, fastest.pingMs))
            }
            updateHero()
            updateSummary()
            AppLog.i("پینگ همهٔ $total سرور انجام شد؛ سریع‌ترین: ${fastest?.name ?: "—"}")
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
        updateHero()
        toast(if (prefs.mode == Prefs.MODE_VPN) getString(R.string.mode_vpn) else getString(R.string.mode_proxy))
    }

    private fun updateModeLabel() {
        binding.modeText.setText(
            if (prefs.mode == Prefs.MODE_VPN) R.string.mode_vpn_short else R.string.mode_proxy_short,
        )
    }

    private fun toggleConnection() {
        if (tunnelRunning) {
            val target = selectedServer()
            // A different server is selected: pressing the button must move the tunnel to it
            // instead of silently dropping the connection (and instead of needing two taps).
            if (target != null && connectedKey != null && target.key != connectedKey) {
                connectTo(target)
                return
            }
            VpnTunnelService.stop(this)
            return
        }
        val server = selectedServer() ?: pickBestOrNull() ?: run {
            toast(getString(R.string.toast_select_first))
            return
        }
        connectTo(server)
    }

    private fun connectTo(server: Server) {
        if (server.isOpaquePayload) {
            showText(getString(R.string.dlg_opaque_title), getString(R.string.dlg_opaque_body))
            return
        }
        selectServer(server)
        if (tunnelRunning) {
            val same = connectedKey == server.key
            VpnTunnelService.stop(this)
            if (same) {
                toast(getString(R.string.status_disconnected))
                return
            }
            // Give the old service a moment to release the TUN device, then start on the new one.
            binding.statusText.text = getString(R.string.status_connecting)
            binding.root.postDelayed({ launchTunnel(server) }, RECONNECT_DELAY_MS)
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
        connectedKey = server.key
        prefs.connectedKey = server.key
        runCatching { VpnTunnelService.start(this, server, prefs.mode) }
            .onFailure {
                AppLog.e("شروع سرویس تونل ناموفق", it)
                binding.statusText.text = getString(R.string.status_error, it.message.orEmpty())
            }
    }

    // ---------------------------------------------------------------- ui helpers

    private fun updateHero() {
        val running = tunnelRunning
        val server = selectedServer()
        val shown = server
        if (shown == null) {
            if (!running) binding.statusText.setText(R.string.status_idle)
            binding.selectedNameText.setText(R.string.hero_no_server)
            binding.selectedMetaText.setText(R.string.hero_no_server_hint)
            // While a tunnel is up but the selected row is not in the current list (a link
            // intent re-created the screen, a filter hides it), the button must still advertise
            // the switch instead of pretending that pressing it only disconnects.
            binding.connectButton.setText(
                when {
                    !running -> R.string.btn_connect
                    connectedKey != null -> R.string.btn_connect_selected
                    else -> R.string.btn_disconnect
                },
            )
            AppLog.d(
                "hero(no row): running=$running connected=${connectedKey ?: "-"} " +
                    "pressed=${binding.connectButton.text}",
            )
            return
        }
        binding.connectButton.setText(
            when {
                !running -> R.string.btn_connect
                connectedKey != null && connectedKey != shown.key -> R.string.btn_connect_selected
                else -> R.string.btn_disconnect
            },
        )
        AppLog.d(
            "hero: running=$running connected=${connectedKey ?: "-"} shown=${shown.key} " +
                "pressed=${binding.connectButton.text}",
        )

        binding.selectedNameText.text = "${shown.displayFlag}  ${shown.name}"
        val price = when {
            shown.price == null -> getString(R.string.badge_unknown_price)
            shown.isFree -> getString(R.string.badge_free)
            else -> getString(R.string.badge_paid, shown.price)
        }
        val ping = when {
            shown.pingState == PingState.OK -> getString(R.string.ping_ms, shown.pingMs)
            shown.pingState == PingState.RUNNING -> "…"
            shown.pingState == PingState.FAILED -> getString(R.string.ping_timeout)
            else -> null
        }
        val type = when (shown.typeHint.lowercase()) {
            "enc" -> getString(R.string.type_opaque)
            "" -> getString(R.string.type_unknown)
            else -> shown.typeHint
        }
        // Only the labels that actually carry a value, so the hero never shows stray dashes.
        binding.selectedMetaText.text = listOfNotNull(
            type, price, shown.flag.takeIf { it.isNotBlank() }, ping,
        ).joinToString(" · ")
        binding.connectButton.setText(if (running) R.string.btn_disconnect else R.string.btn_connect)
    }

    private fun paintStatusDot() {
        val color = when {
            tunnelRunning -> R.color.good
            busy -> R.color.warn
            servers.isEmpty() -> R.color.text_dim
            else -> R.color.primary
        }
        binding.statusDot.backgroundTintList =
            ColorStateList.valueOf(ContextCompat.getColor(this, color))
    }


    private fun updateSummary() {
        val total = servers.size
        val visible = adapter.visibleCount()
        binding.emptyText.setText(R.string.empty_filter)
        if (total == 0) {
            binding.summaryText.setText(R.string.status_empty)
            binding.emptyText.setText(R.string.status_empty)
            binding.emptyText.visibility = View.VISIBLE
            return
        }
        val free = servers.count { it.isFree }
        val paid = total - free
        // Empty state of the list: the filter/search hid everything (or the backend sent nothing).
        binding.emptyText.visibility = if (visible == 0) View.VISIBLE else View.GONE
        binding.summaryText.text = getString(R.string.status_filtered, visible, total, free, paid)
    }

    private fun setProgress(visible: Boolean) {
        binding.progress.visibility = if (visible) View.VISIBLE else View.GONE
        binding.fetchButton.isEnabled = !visible
        binding.pingAllButton.isEnabled = !visible
        busy = visible
        paintStatusDot()
    }

    /** Bottom sheet with every action for one server (labels + connect/ping/copy). */
    private fun showServerSheet(server: Server) {
        val sheet = BottomSheetDialog(this)
        val view = layoutInflater.inflate(R.layout.dialog_server, null)
        sheet.setContentView(view)

        view.findViewById<TextView>(R.id.sheetFlag).text = server.displayFlag
        view.findViewById<TextView>(R.id.sheetName).text = server.name
        view.findViewById<TextView>(R.id.sheetType).text = when (server.typeHint.lowercase()) {
            "enc" -> getString(R.string.type_opaque)
            "" -> getString(R.string.type_unknown)
            else -> server.typeHint
        }
        val locationView = view.findViewById<TextView>(R.id.sheetLocation)
        if (server.flag.isBlank()) {
            locationView.visibility = View.GONE
        } else {
            locationView.text = server.flag
        }
        val priceView = view.findViewById<TextView>(R.id.sheetPrice)
        priceView.text = when {
            server.price == null -> getString(R.string.badge_unknown_price)
            server.isFree -> getString(R.string.badge_free)
            else -> getString(R.string.badge_paid, server.price)
        }
        priceView.setTextColor(
            ContextCompat.getColor(this, if (server.isFree) R.color.free else R.color.paid),
        )
        val pingView = view.findViewById<TextView>(R.id.sheetPing)
        pingView.text = when {
            server.pingState == PingState.OK -> getString(R.string.ping_ms, server.pingMs)
            server.pingState == PingState.RUNNING -> "…"
            server.pingState == PingState.FAILED -> getString(R.string.ping_timeout)
            else -> getString(R.string.ping_none)
        }
        view.findViewById<TextView>(R.id.sheetUsage).text =
            server.usage?.summary().orEmpty().ifBlank { getString(R.string.badge_no_usage) }
        if (server.isOpaquePayload) {
            val state = view.findViewById<TextView>(R.id.sheetState)
            state.setText(R.string.sheet_opaque)
            state.visibility = View.VISIBLE
        }

        view.findViewById<MaterialButton>(R.id.sheetConnect).setOnClickListener {
            sheet.dismiss()
            connectTo(server)
        }
        view.findViewById<MaterialButton>(R.id.sheetPingButton).setOnClickListener {
            sheet.dismiss()
            pingSingle(server)
        }
        view.findViewById<MaterialButton>(R.id.sheetCopyLink).setOnClickListener {
            sheet.dismiss()
            copyShareLink(server)
        }
        view.findViewById<MaterialButton>(R.id.sheetCopyJson).setOnClickListener {
            sheet.dismiss()
            copy(server.rawConfig.ifBlank { server.rawJson })
        }
        view.findViewById<MaterialButton>(R.id.sheetDetails).setOnClickListener {
            sheet.dismiss()
            showDetails(server)
        }
        sheet.show()
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
            appendLine("مقدار اتصال (value):")
            appendLine(server.rawConfig.take(2000).ifBlank { "—" })
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
     * Imports a whole subscription: fetches the URL, base64-decodes it when needed and adds every
     * recognised share link. This is the fully client-side path that always works, regardless of
     * what the vendor backend returns.
     */
    private fun promptSubscription() {
        val layout = layoutInflater.inflate(R.layout.dialog_input, null)
        val input = layout.findViewById<EditText>(R.id.input)
        input.hint = "https://…/sub"
        val dialog = AlertDialog.Builder(this)
            .setTitle(R.string.dlg_sub_title)
            .setView(layout)
            .setNegativeButton(R.string.btn_close, null)
            .setPositiveButton(R.string.btn_import, null)
            .create()
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                val url = input.text?.toString()?.trim().orEmpty()
                if (!url.startsWith("http")) {
                    input.error = getString(R.string.import_invalid_url)
                    return@setOnClickListener
                }
                dialog.dismiss()
                importSubscription(url)
            }
        }
        dialog.show()
    }

    private fun importSubscription(url: String) {
        setProgress(true)
        binding.statusText.text = getString(R.string.status_fetching)
        lifecycleScope.launch {
            val raw = withContext(Dispatchers.IO) {
                runCatching {
                    val connection = (java.net.URL(url).openConnection() as java.net.HttpURLConnection).apply {
                        connectTimeout = 20_000
                        readTimeout = 25_000
                        setRequestProperty("User-Agent", "v2rayNG/1.8.5")
                    }
                    connection.inputStream.bufferedReader().use { it.readText() }
                }.onFailure { AppLog.e("دریافت اشتراک ناموفق", it) }.getOrNull()
            }
            setProgress(false)
            if (raw.isNullOrBlank()) {
                binding.statusText.text = getString(R.string.status_error, getString(R.string.import_sub_failed))
                paintStatusDot()
                return@launch
            }
            val body = unwrapSubscription(raw)
            val links = body.lineSequence()
                .map { it.trim() }
                .filter { it.isNotEmpty() && listOf("vmess://", "vless://", "trojan://", "ss://", "socks://", "hysteria://", "hy2://").any { p -> it.startsWith(p, true) } }
                .toList()
            if (links.isEmpty()) {
                binding.statusText.text = getString(R.string.status_error, getString(R.string.import_sub_empty))
                paintStatusDot()
                return@launch
            }
            val added = links.mapIndexed { index, link -> ServerParser.fromRaw(link, servers.size + index) }
            servers.addAll(0, added)
            if (servers.none { it.key == prefs.selectedKey }) prefs.selectedKey = servers.first().key
            adapter.submit(servers, prefs.selectedKey)
            applyFilter()
            updateHero()
            binding.statusText.text = getString(R.string.import_sub_ok, added.size)
            paintStatusDot()
            AppLog.i("${added.size} سرور از اشتراک $url اضافه شد")
        }
    }

    /** Subscription payloads are usually base64 of a newline-separated link list. */
    private fun unwrapSubscription(raw: String): String {
        val trimmed = raw.trim()
        val looksLikeList = listOf("vmess://", "vless://", "trojan://", "ss://").any { trimmed.contains(it) }
        if (looksLikeList) return trimmed
        val decoded = runCatching {
            String(
                android.util.Base64.decode(
                    trimmed.replace("\n", "").replace("\r", ""),
                    android.util.Base64.DEFAULT,
                ),
                Charsets.UTF_8,
            )
        }.getOrNull()
        return decoded ?: trimmed
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
        if (text.startsWith("http://", true) || text.startsWith("https://", true)) {
            importSubscription(text.lines().first().trim())
            return
        }
        importRaw(text)
    }

    /** Adds one raw config (share link or Xray JSON) to the list and selects it. */
    private fun importRaw(text: String) {
        val looksLikeConfig = text.startsWith("{") ||
            listOf("vmess://", "vless://", "trojan://", "ss://", "socks://")
                .any { text.startsWith(it, ignoreCase = true) }
        if (!looksLikeConfig) {
            toast(getString(R.string.import_invalid))
            return
        }
        val server = ServerParser.fromRaw(text, servers.size)
        servers.add(0, server)
        prefs.selectedKey = server.key
        adapter.submit(servers, prefs.selectedKey)
        applyFilter()
        updateHero()
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
        private const val RECONNECT_DELAY_MS = 700L
    }
}
