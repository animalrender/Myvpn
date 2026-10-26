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

    fun submit(servers: List<Server>, selected: String?) {
        all.clear()
        all.addAll(servers)
        selectedKey = selected
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
                    FilterMode.READY -> !server.isOpaquePayload
                }
                matchesText && matchesMode
            },
        )
        notifyDataSetChanged()
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

            binding.typeBadge.text = server.typeHint.ifBlank { "?" }

            binding.priceBadge.text = when {
                server.price == null -> context.getString(R.string.badge_unknown_price)
                server.price!! > 0 -> context.getString(R.string.badge_paid, server.price)
                else -> context.getString(R.string.badge_free)
            }
            binding.priceBadge.setTextColor(
                ContextCompat.getColor(context, if (server.isFree) R.color.free else R.color.paid),
            )

            binding.locationBadge.text = server.flag.ifBlank { "—" }

            binding.pingButton.isEnabled = !server.isOpaquePayload
            binding.pingButton.alpha = if (server.isOpaquePayload) 0.4f else 1f

            val usageSummary = server.usage?.summary().orEmpty()
            binding.usageText.text = when {
                usageSummary.isNotBlank() -> usageSummary
                server.isOpaquePayload -> context.getString(R.string.badge_encrypted_payload)
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
