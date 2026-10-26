package co.asiven.vixentvpn.trial.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import co.asiven.vixentvpn.trial.R
import co.asiven.vixentvpn.trial.data.PingState
import co.asiven.vixentvpn.trial.data.Server
import co.asiven.vixentvpn.trial.databinding.ItemServerBinding

/** Filter chips above the list. */
enum class FilterMode { ALL, FREE, PAID, READY }

/**
 * Sort keys offered by the sort button. `ORIGINAL` keeps the order the backend sent, the others
 * are shared with the activity through [Prefs] so the choice survives a restart.
 */
enum class SortField { ORIGINAL, NAME, PING, PRICE, ID }

/**
 * Flat, scrollable list of every server the backend returned — free **and** paid — with the
 * original attributes (type, price, usage, location) rendered as labels, exactly what the
 * trial build is supposed to expose instead of hiding paid rows behind a purchase gate.
 *
 * Search and the filter chips are applied here so the activity only ever deals with the full
 * list; the visible subset is what gets drawn.
 *
 * Every row can also export itself as a v2ray share link (copied to the clipboard), so the same
 * server can be pasted into v2rayNG/nekobox and used outside this app.
 */
class ServerAdapter(
    private val onSelect: (Server) -> Unit,
    private val onPing: (Server) -> Unit,
    private val onDetails: (Server) -> Unit,
    private val onCopyLink: (Server) -> Unit,
) : RecyclerView.Adapter<ServerAdapter.Holder>() {

    private val all = mutableListOf<Server>()
    private val items = mutableListOf<Server>()
    private var selectedKey: String? = null
    private var runningKey: String? = null
    private var query: String = ""
    private var mode: FilterMode = FilterMode.ALL
    private var sortField: SortField = SortField.ORIGINAL
    private var sortAscending: Boolean = true

    fun submit(servers: List<Server>, selected: String?) {
        all.clear()
        all.addAll(servers)
        selectedKey = selected
        recompute()
    }

    /** Applies the sort key picked in the sort dialog. */
    fun setSort(field: SortField, ascending: Boolean) {
        sortField = field
        sortAscending = ascending
        recompute()
    }

    /** Applies the search box text and the selected chip. */
    fun setFilter(text: String, filter: FilterMode) {
        query = text.trim()
        mode = filter
        recompute()
    }

    fun visibleCount(): Int = items.size
    fun totalCount(): Int = all.size

    private fun recompute() {
        val needle = query.lowercase()
        items.clear()
        items.addAll(
            all.filter { server ->
                val matchesText = needle.isEmpty() ||
                    server.name.lowercase().contains(needle) ||
                    server.flag.lowercase().contains(needle) ||
                    server.typeHint.lowercase().contains(needle) ||
                    server.protocolId?.toString()?.contains(needle) == true ||
                    server.serverId?.toString()?.contains(needle) == true
                val matchesMode = when (mode) {
                    FilterMode.ALL -> true
                    FilterMode.FREE -> server.isFree
                    FilterMode.PAID -> !server.isFree
                    FilterMode.READY -> server.isDialable
                }
                matchesText && matchesMode
            },
        )
        items.sortWith(comparatorFor(sortField, sortAscending))
        notifyDataSetChanged()
    }

    /**
     * One comparator per sort key. Rows that never answered a ping always sink to the bottom
     * (in both directions), which is what makes the «بدون پینگ» bucket usable.
     */
    private fun comparatorFor(field: SortField, ascending: Boolean): Comparator<Server> {
        if (field == SortField.ORIGINAL) {
            return if (ascending) Comparator { a, b -> all.indexOf(a) - all.indexOf(b) }
            else Comparator { a, b -> all.indexOf(b) - all.indexOf(a) }
        }
        // Rows without a value for the current key (no ping yet, unknown price, no id) are pushed
        // to the bottom in *both* directions — otherwise flipping the arrow would surface exactly
        // the rows the user is not interested in.
        val missing: (Server) -> Int = when (field) {
            SortField.PING -> { server -> if (server.pingState == PingState.OK && server.pingMs > 0) 0 else 1 }
            SortField.PRICE -> { server -> if (server.price != null) 0 else 1 }
            SortField.ID -> { server -> if (server.protocolId != null) 0 else 1 }
            SortField.NAME, SortField.ORIGINAL -> { _ -> 0 }
        }
        val byValue: Comparator<Server> = when (field) {
            SortField.PING -> if (ascending) compareBy { it.pingMs } else compareByDescending { it.pingMs }
            SortField.PRICE -> if (ascending) compareBy { it.price ?: 0 } else compareByDescending { it.price ?: 0 }
            SortField.ID -> if (ascending) compareBy { it.protocolId ?: 0 } else compareByDescending { it.protocolId ?: 0 }
            SortField.NAME -> if (ascending) compareBy { it.sortableName.lowercase() }
                else compareByDescending { it.sortableName.lowercase() }
            SortField.ORIGINAL -> compareBy { 0 }
        }
        return compareBy { missing(it) }
            .then(byValue)
            // stable tie-break, so equal keys do not shuffle on every refresh
            .thenBy { it.sortableName.lowercase() }
    }

    fun setSelected(key: String?) {
        val old = selectedKey
        selectedKey = key
        refreshRow(old)
        refreshRow(key)
    }

    fun setConnectedKey(key: String?) {
        val old = runningKey
        runningKey = key
        refreshRow(old)
        refreshRow(key)
    }

    private fun refreshRow(key: String?) {
        if (key == null) return
        val index = items.indexOfFirst { it.key == key }
        if (index >= 0) notifyItemChanged(index)
    }

    fun updatePing(server: Server) = refreshRow(server.key)

    fun snapshot(): List<Server> = items.toList()

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): Holder {
        val binding = ItemServerBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return Holder(binding)
    }

    override fun getItemCount(): Int = items.size

    override fun onBindViewHolder(holder: Holder, position: Int) {
        holder.bind(items[position])
    }

    inner class Holder(private val binding: ItemServerBinding) : RecyclerView.ViewHolder(binding.root) {

        fun bind(server: Server) {
            val context = binding.root.context
            binding.flagText.text = server.displayFlag
            binding.nameText.text = server.name

            binding.typeBadge.text = when (server.typeHint.lowercase()) {
                "enc" -> context.getString(R.string.type_opaque)
                "" -> context.getString(R.string.type_unknown)
                else -> server.typeHint
            }

            binding.priceBadge.text = when {
                server.price == null -> context.getString(R.string.badge_unknown_price)
                server.price!! > 0 -> context.getString(R.string.badge_paid, server.price)
                else -> context.getString(R.string.badge_free)
            }
            binding.priceBadge.setTextColor(
                ContextCompat.getColor(context, if (server.isFree) R.color.free else R.color.paid),
            )

            if (server.flag.isBlank()) {
                binding.locationBadge.visibility = View.GONE
            } else {
                binding.locationBadge.text = server.flag
                binding.locationBadge.visibility = View.VISIBLE
            }

            binding.pingButton.isEnabled = server.isDialable
            binding.pingButton.alpha = if (server.isDialable) 1f else 0.4f

            val usageSummary = server.usage?.summary().orEmpty()
            binding.usageText.text = when {
                usageSummary.isNotBlank() -> usageSummary
                !server.isDialable -> context.getString(R.string.badge_unsupported)
                else -> context.getString(R.string.badge_no_usage)
            }

            when (server.pingState) {
                PingState.OK -> {
                    binding.pingText.text = context.getString(R.string.ping_ms, server.pingMs)
                    val color = when {
                        server.pingMs in 0..300 -> R.color.good
                        server.pingMs in 301..900 -> R.color.warn
                        else -> R.color.bad
                    }
                    binding.pingText.setTextColor(ContextCompat.getColor(context, color))
                }
                PingState.FAILED -> {
                    binding.pingText.text = context.getString(R.string.ping_timeout)
                    binding.pingText.setTextColor(ContextCompat.getColor(context, R.color.bad))
                }
                PingState.RUNNING -> {
                    binding.pingText.text = "…"
                    binding.pingText.setTextColor(ContextCompat.getColor(context, R.color.warn))
                }
                PingState.IDLE -> {
                    binding.pingText.text = context.getString(R.string.ping_none)
                    binding.pingText.setTextColor(ContextCompat.getColor(context, R.color.text_dim))
                }
            }

            val isSelected = server.key == selectedKey
            val isConnected = server.key == runningKey
            val background = when {
                isConnected -> R.color.primary_soft
                isSelected -> R.color.surface_alt
                else -> R.color.surface
            }
            val stroke = when {
                isConnected -> R.color.good
                isSelected -> R.color.primary
                else -> R.color.card_stroke
            }
            binding.rowCard.setCardBackgroundColor(ContextCompat.getColor(context, background))
            binding.rowCard.strokeColor = ContextCompat.getColor(context, stroke)
            binding.rowCard.strokeWidth =
                if (isSelected || isConnected) (1.5f * context.resources.displayMetrics.density).toInt()
                else (context.resources.displayMetrics.density).toInt()

            binding.connectHint.text = when {
                isConnected -> context.getString(R.string.status_connected_short)
                isSelected -> context.getString(R.string.status_selected_short)
                else -> ""
            }

            binding.root.setOnClickListener { onSelect(server) }
            binding.pingButton.setOnClickListener { onPing(server) }
            binding.detailsButton.setOnClickListener { onDetails(server) }
            binding.copyLinkButton.setOnClickListener { onCopyLink(server) }
            binding.root.setOnLongClickListener {
                onDetails(server)
                true
            }
            binding.connectHint.visibility = View.VISIBLE
        }
    }
}
