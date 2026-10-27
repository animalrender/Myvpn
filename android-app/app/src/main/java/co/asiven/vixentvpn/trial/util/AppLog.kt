package co.asiven.vixentvpn.trial.util

import android.content.Context
import android.util.Log
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Tiny in-app log: keeps the last [MAX_LINES] lines in memory and mirrors them to
 * filesDir/mvpn-trial.log so a trial run can be debugged without adb.
 */
object AppLog {
    private const val TAG = "MvpnTrial"
    private const val MAX_LINES = 800
    private val lines = ArrayDeque<String>()
    private val stamp = SimpleDateFormat("HH:mm:ss", Locale.US)

    @Volatile
    private var logFile: File? = null

    fun attach(context: Context) {
        if (logFile == null) {
            val file = File(context.filesDir, "mvpn-trial.log")
            if (file.length() > 512 * 1024) file.delete()
            logFile = file
        }
    }

    fun d(message: String) {
        Log.d(TAG, message)
        append("D", message)
    }

    fun i(message: String) {
        Log.i(TAG, message)
        append("I", message)
    }

    fun w(message: String) {
        Log.w(TAG, message)
        append("W", message)
    }

    fun e(message: String, t: Throwable? = null) {
        Log.e(TAG, message, t)
        append("E", if (t == null) message else "$message — ${t.javaClass.simpleName}: ${t.message}")
    }

    private fun append(level: String, message: String) {
        val line = "${stamp.format(Date())} $level $message"
        synchronized(lines) {
            lines.addLast(line)
            while (lines.size > MAX_LINES) lines.removeFirst()
        }
        try {
            logFile?.appendText(line + "\n")
        } catch (_: Throwable) {
            // never let logging break the app
        }
    }

    fun dump(): String = synchronized(lines) { lines.joinToString("\n") }

    fun clear() {
        synchronized(lines) { lines.clear() }
        logFile?.delete()
    }
}
