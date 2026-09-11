package org.surutakip.mobile;

import android.app.Activity;
import android.graphics.Color;
import android.graphics.Insets;
import android.os.Build;
import android.view.View;
import android.view.Window;
import android.view.WindowInsets;
import android.view.WindowManager;

/** Resize the SDL surface itself, so every Kivy popup shares the safe area. */
public final class SafeArea {
    public static void install(final Activity activity) {
        activity.runOnUiThread(new Runnable() {
            @Override public void run() {
                final Window window = activity.getWindow();
                final View content = activity.findViewById(android.R.id.content);
                if (content == null) return;
                content.setBackgroundColor(Color.rgb(12, 82, 54));
                window.clearFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
                window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
                if (Build.VERSION.SDK_INT >= 30) window.setDecorFitsSystemWindows(false);
                else window.getDecorView().setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_LAYOUT_STABLE | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
                window.setStatusBarColor(Color.TRANSPARENT);
                window.setNavigationBarColor(Color.TRANSPARENT);
                if (Build.VERSION.SDK_INT >= 29) {
                    window.setStatusBarContrastEnforced(false);
                    window.setNavigationBarContrastEnforced(false);
                }
                if (Build.VERSION.SDK_INT >= 30 && window.getInsetsController() != null)
                    window.getInsetsController().setSystemBarsAppearance(0, 24);
                content.setOnApplyWindowInsetsListener(new View.OnApplyWindowInsetsListener() {
                    @Override public WindowInsets onApplyWindowInsets(View view, WindowInsets insets) {
                        int left, top, right, bottom;
                        if (Build.VERSION.SDK_INT >= 30) {
                            Insets safe = insets.getInsets(WindowInsets.Type.systemBars()
                                | WindowInsets.Type.displayCutout() | WindowInsets.Type.ime());
                            left = safe.left; top = safe.top; right = safe.right; bottom = safe.bottom;
                        } else {
                            left = insets.getSystemWindowInsetLeft();
                            top = insets.getSystemWindowInsetTop();
                            right = insets.getSystemWindowInsetRight();
                            bottom = insets.getSystemWindowInsetBottom();
                            if (Build.VERSION.SDK_INT >= 28 && insets.getDisplayCutout() != null) {
                                left = Math.max(left, insets.getDisplayCutout().getSafeInsetLeft());
                                top = Math.max(top, insets.getDisplayCutout().getSafeInsetTop());
                                right = Math.max(right, insets.getDisplayCutout().getSafeInsetRight());
                                bottom = Math.max(bottom, insets.getDisplayCutout().getSafeInsetBottom());
                            }
                        }
                        view.setPadding(left, top, right, bottom);
                        return Build.VERSION.SDK_INT >= 30 ? WindowInsets.CONSUMED : insets.consumeSystemWindowInsets();
                    }
                });
                content.requestApplyInsets();
            }
        });
    }
}
