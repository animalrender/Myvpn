package co.asiven.vixentvpn.trial.ui

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import co.asiven.vixentvpn.trial.R
import co.asiven.vixentvpn.trial.data.PingState
import co.asiven.vixentvpn.trial.data.Server
import co.asiven.vixentvpn.trial.databinding.ItemServerBinding

/**
 * Flat, scrollable list of every server the backend returned — free **and** paid — with the
 * original attributes (type, price, usage, location) rendered as labels, exactly what the
 * trial build is supposed to expose instead of hiding paid rows behind a purchase gate.
 */
class ServerAdapter(
    private val onSelect: (Server) -> Unit,
    private val onPing: (Server) -> Unit,
    private val onDetails: (Server) -> Unit,
) : RecyclerView.Adapter<ServerAdapter.Holder>() {

    private val items = mutableListOf<Server>()
    private var selectedKey: String? = null
    private var runningKey: String? = null

    fun submit(servers: List<Server>, selected: String?) {
        items.clear()
        items.addAll(servers)
        selectedKey = selected
        notifyDataSetChanged()
    }

    fun setSelected(key: String?) {
        val old = selectedKey
        selectedKey = key
        items.indexOfFirst { it.key == old }.takeIf { it >= 0 }?.let { notifyItemChanged(it) }
        items.indexOfFirst { it.key == key }.takeIf { it >= 0 }?.let { notifyItemChanged(it) }
    }

    fun setConnectedKey(key: String?) {
        val old = runningKey
        runningKey = key
        items.indexOfFirst { it.key == old }.takeIf { it >= 0 }?.let { notifyItemChanged(it) }
        items.indexOfFirst { it.key == key }.takeIf { it >= 0 }?.let { notifyItemChanged(it) }
    }

    fun updatePing(server: Server) {
        val index = items.indexOfFirst { it.key == server.key }
        if (index >= 0) notifyItemChanged(index)
    }

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

            val usageSummary = server.usage?.summary().orEmpty()
            binding.usageText.text = usageSummary.ifBlank { context.getString(R.string.badge_no_usage) }

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
            binding.rowCard.setCardBackgroundColor(
                ContextCompat.getColor(
                    context,
                    when {
                        isConnected -> R.color.primary_dark
                        isSelected -> R.color.surface_alt
                        else -> R.color.surface
                    },
                ),
            )
            binding.connectHint.text = when {
                isConnected -> "متصل"
                isSelected -> "انتخاب‌شده"
                else -> ""
            }
            binding.connectHint.setTextColor(ContextCompat.getColor(context, R.color.good))

            binding.root.setOnClickListener { onSelect(server) }
            binding.pingButton.setOnClickListener { onPing(server) }
            binding.detailsButton.setOnClickListener { onDetails(server) }
            binding.root.setOnLongClickListener {
                onDetails(server)
                true
            }
        }
    }
}
