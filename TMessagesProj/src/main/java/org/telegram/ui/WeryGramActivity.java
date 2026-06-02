package org.telegram.ui;

import android.content.Context;
import android.content.SharedPreferences;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import org.telegram.messenger.R;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.ActionBar.Theme;
import org.telegram.ui.Cells.TextCheckCell;
import org.telegram.ui.Cells.TextInfoPrivacyCell;
import org.telegram.ui.Components.LayoutHelper;
import org.telegram.ui.Components.RecyclerListView;

public class WeryGramActivity extends BaseFragment {

    private RecyclerListView listView;
    private ListAdapter listAdapter;
    
    private int premiumRow;
    private int infoRow;
    private int rowCount;

    @Override
    public View createView(Context context) {
        // 1. Настраиваем верхнюю панель (Action Bar)
        actionBar.setBackButtonImage(R.drawable.ic_ab_back);
        actionBar.setAllowOverlayTitle(true);
        actionBar.setTitle("WeryGram"); // Название экрана наверху
        
        // Обрабатываем нажатие на стрелочку "Назад"
        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {
            @Override
            public void onItemClick(int id) {
                if (id == -1) {
                    finishFragment();
                }
            }
        });

        // 2. Создаем контейнер для экрана
        fragmentView = new FrameLayout(context);
        fragmentView.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundWhite));
        FrameLayout frameLayout = (FrameLayout) fragmentView;

        // Определяем порядок строк в меню
        rowCount = 0;
        premiumRow = rowCount++;
        infoRow = rowCount++;

        // 3. Создаем стандартный список Телеграма
        listView = new RecyclerListView(context);
        listView.setLayoutManager(new LinearLayoutManager(context, LinearLayoutManager.VERTICAL, false));
        listView.setAdapter(listAdapter = new ListAdapter(context));
        
        // 4. Обработка клика по переключателю
        listView.setOnItemClickListener((view, position) -> {
            if (position == premiumRow) {
                // Открываем настройки памяти (SharedPreferences)
                SharedPreferences preferences = context.getSharedPreferences("werygram_settings", Context.MODE_PRIVATE);
                boolean currentState = preferences.getBoolean("visual_premium", false);
                
                // Меняем значение на противоположное и сохраняем
                boolean newState = !currentState;
                preferences.edit().putBoolean("visual_premium", newState).apply();
                
                // Визуально переключаем тумблер на экране
                if (view instanceof TextCheckCell) {
                    ((TextCheckCell) view).setChecked(newState);
                }
            }
        });

        frameLayout.addView(listView, LayoutHelper.createFrame(LayoutHelper.MATCH_PARENT, LayoutHelper.MATCH_PARENT));
        return fragmentView;
    }

    // Кастомный адаптер, который собирает дизайн Телеграма по кусочкам
    private class ListAdapter extends RecyclerListView.SelectionAdapter {
        private Context mContext;

        public ListAdapter(Context context) {
            mContext = context;
        }

        @Override
        public boolean isEnabled(RecyclerView.ViewHolder holder) {
            // Кликабельной должна быть только строка с тумблером
            return holder.getAdapterPosition() == premiumRow;
        }

        @Override
        public RecyclerView.ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
            View view;
            if (viewType == 0) {
                // Создаем красивую строку Телеграма с готовым переключателем (Switch)
                view = new TextCheckCell(mContext);
                view.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundWhite));
            } else {
                // Создаем строку для маленького серого текста-подсказки снизу
                view = new TextInfoPrivacyCell(mContext);
            }
            return new RecyclerListView.Holder(view);
        }

        @Override
        public void onBindViewHolder(RecyclerView.ViewHolder holder, int position) {
            if (position == premiumRow) {
                TextCheckCell cell = (TextCheckCell) holder.itemView;
                // Читаем из памяти, включен ли тумблер сейчас
                SharedPreferences preferences = mContext.getSharedPreferences("werygram_settings", Context.MODE_PRIVATE);
                boolean enabled = preferences.getBoolean("visual_premium", false);
                
                // Устанавливаем текст тумблера и его состояние
                cell.setTextAndCheck("Визуальный Premium", enabled, true);
            } else if (position == infoRow) {
                TextInfoPrivacyCell cell = (TextInfoPrivacyCell) holder.itemView;
                // Твой кастомный текст описания функции
                cell.setText("Premium данная функция включает телеграм премиум визуально");
            }
        }

        @Override
        public int getItemCount() {
            return rowCount;
        }

        @Override
        public int getItemViewType(int position) {
            if (position == premiumRow) {
                return 0; // Тип для TextCheckCell
            } else if (position == infoRow) {
                return 1; // Тип для TextInfoPrivacyCell
            }
            return 0;
        }
    }
}
