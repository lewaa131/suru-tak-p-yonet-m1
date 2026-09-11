package org.surutakip.reminders;

import android.Manifest;
import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;
import android.util.Log;
import org.json.JSONArray;
import org.json.JSONObject;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

/** One persisted alarm for the next batch; no continuously running Python service. */
public class ReminderReceiver extends BroadcastReceiver {
    private static final String CHANNEL = "pregnancy_reminders";
    private static final String ACTION = "org.surutakip.reminders.CHECK";
    private static final String TEST = "org.surutakip.reminders.TEST";

    private static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences("pregnancy_reminders", Context.MODE_PRIVATE);
    }

    private static NotificationManager manager(Context c) {
        return (NotificationManager)c.getSystemService(Context.NOTIFICATION_SERVICE);
    }

    private static void channel(Context c) {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel channel = new NotificationChannel(CHANNEL,
                "Gebelik ve kuru dönem", NotificationManager.IMPORTANCE_DEFAULT);
            channel.setDescription("Kuruya ayırma ve tahmini doğum hatırlatmaları");
            manager(c).createNotificationChannel(channel);
        }
    }

    public static boolean notificationsEnabled(Context c) {
        channel(c);
        if (Build.VERSION.SDK_INT >= 33 && c.checkSelfPermission(
                Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) return false;
        if (Build.VERSION.SDK_INT >= 24 && !manager(c).areNotificationsEnabled()) return false;
        return Build.VERSION.SDK_INT < 26 || manager(c).getNotificationChannel(CHANNEL)
            .getImportance() != NotificationManager.IMPORTANCE_NONE;
    }

    public static void openSettings(Context c) {
        Intent intent;
        if (Build.VERSION.SDK_INT >= 26) {
            intent = new Intent(Settings.ACTION_CHANNEL_NOTIFICATION_SETTINGS);
            intent.putExtra(Settings.EXTRA_APP_PACKAGE, c.getPackageName());
            intent.putExtra(Settings.EXTRA_CHANNEL_ID, CHANNEL);
        } else {
            intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                Uri.parse("package:" + c.getPackageName()));
        }
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        c.startActivity(intent);
    }

    private static PendingIntent alarmIntent(Context c, String action) {
        Intent intent = new Intent(c, ReminderReceiver.class).setAction(action);
        return PendingIntent.getBroadcast(c, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    private static AlarmManager alarms(Context c) {
        return (AlarmManager)c.getSystemService(Context.ALARM_SERVICE);
    }

    private static String today() {
        return new SimpleDateFormat("yyyy-MM-dd", Locale.US).format(new Date());
    }

    private static long atTime(JSONObject event) throws Exception {
        String day = event.getString("day");
        String[] time = event.optString("time", "09:00").split(":");
        SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd", Locale.US);
        format.setLenient(false);
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(format.parse(day));
        calendar.set(Calendar.HOUR_OF_DAY, Integer.parseInt(time[0]));
        calendar.set(Calendar.MINUTE, Integer.parseInt(time[1]));
        calendar.set(Calendar.SECOND, 0);
        calendar.set(Calendar.MILLISECOND, 0);
        return calendar.getTimeInMillis();
    }

    public static synchronized void replacePlan(Context context, String json) throws Exception {
        Context c = context.getApplicationContext();
        JSONArray next = new JSONArray(json);
        JSONArray previous = new JSONArray(prefs(c).getString("plan", "[]"));
        Set<String> active = new HashSet<>();
        for (int i = 0; i < next.length(); i++) active.add(next.getJSONObject(i).getString("key"));
        Set<String> delivered = new HashSet<>(prefs(c).getStringSet("delivered", new HashSet<String>()));
        delivered.retainAll(active);
        if (!prefs(c).edit().putString("plan", json).putStringSet("delivered", delivered).commit())
            throw new IllegalStateException("Hatırlatmalar kaydedilemedi.");
        // Remove visible notifications as well as future alarms for deleted/changed records.
        for (int i = 0; i < previous.length(); i++) {
            String key = previous.getJSONObject(i).getString("key");
            if (!active.contains(key)) manager(c).cancel(key, 1);
        }
        scheduleNext(c);
    }

    private static boolean expired(JSONObject event, String day) {
        String until = event.optString("until", "");
        return !until.isEmpty() && day.compareTo(until) >= 0;
    }

    private static void scheduleNext(Context c) throws Exception {
        PendingIntent pending = alarmIntent(c, ACTION);
        alarms(c).cancel(pending);
        if (!notificationsEnabled(c)) return;
        JSONArray plan = new JSONArray(prefs(c).getString("plan", "[]"));
        Set<String> delivered = prefs(c).getStringSet("delivered", new HashSet<String>());
        long next = Long.MAX_VALUE;
        long now = System.currentTimeMillis();
        String day = today();
        for (int i = 0; i < plan.length(); i++) {
            JSONObject event = plan.getJSONObject(i);
            if (delivered.contains(event.getString("key")) || expired(event, day)) continue;
            next = Math.min(next, Math.max(now + 1000, atTime(event)));
        }
        if (next != Long.MAX_VALUE)
            alarms(c).setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, next, pending);
    }

    private static void notify(Context c, String key, String title, String body) {
        channel(c);
        Notification.Builder builder = Build.VERSION.SDK_INT >= 26
            ? new Notification.Builder(c, CHANNEL) : new Notification.Builder(c);
        Intent launch = c.getPackageManager().getLaunchIntentForPackage(c.getPackageName());
        if (launch != null) {
            launch.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            builder.setContentIntent(PendingIntent.getActivity(c, 0, launch,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE));
        }
        builder.setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title).setContentText(body)
            .setStyle(new Notification.BigTextStyle().bigText(body))
            .setAutoCancel(true).setOnlyAlertOnce(true)
            .setCategory(Notification.CATEGORY_REMINDER)
            .setVisibility(Notification.VISIBILITY_PRIVATE);
        manager(c).notify(key, 1, builder.build());
    }

    private static synchronized void deliver(Context c) throws Exception {
        if (!notificationsEnabled(c)) { scheduleNext(c); return; }
        JSONArray plan = new JSONArray(prefs(c).getString("plan", "[]"));
        Set<String> delivered = new HashSet<>(prefs(c).getStringSet("delivered", new HashSet<String>()));
        String day = today();
        long now = System.currentTimeMillis();
        for (int i = 0; i < plan.length(); i++) {
            JSONObject event = plan.getJSONObject(i);
            String key = event.getString("key");
            if (delivered.contains(key) || expired(event, day) || atTime(event) > now) continue;
            String title = event.getString("title");
            String body = event.getString("body");
            if (event.getString("kind").equals("birth") && day.compareTo(event.getString("day")) > 0) {
                title = "Tahmini doğum tarihi geçti";
                body = event.getString("identity") + " — Hayvanını kontrol et. Doğum olduysa gebelik kaydını kapat.";
            }
            notify(c, key, title, body);
            delivered.add(key);
        }
        if (!prefs(c).edit().putStringSet("delivered", delivered).commit())
            throw new IllegalStateException("Bildirim geçmişi kaydedilemedi.");
        scheduleNext(c);
    }

    public static synchronized void scheduleTest(Context c) {
        if (!notificationsEnabled(c)) throw new IllegalStateException("Bildirim izni kapalı.");
        manager(c).cancel("test", 1);
        alarms(c).setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,
            System.currentTimeMillis() + 60000, alarmIntent(c, TEST));
    }

    @Override public void onReceive(Context context, Intent intent) {
        try {
            synchronized (ReminderReceiver.class) {
                if (TEST.equals(intent.getAction())) {
                    if (notificationsEnabled(context)) notify(context, "test", "Hatırlatmalar hazır",
                        "Sürüm arka plan bildirimini gönderdi.");
                } else {
                    // Reads the persisted plan without starting Python, including after reboot.
                    deliver(context);
                }
            }
        } catch (Exception error) {
            Log.e("SurumReminders", "Hatırlatma işlenemedi", error);
        }
    }
}
