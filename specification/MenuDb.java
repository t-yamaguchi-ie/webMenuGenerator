package com.impact.apanel.config;

import android.util.Log;

import com.impact.apanel.general.Common;
import com.impact.apanel.general.Constants;
import com.impact.apanel.general.Logger;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Objects;

/**
 * <h3> 【class】 </h3>
 * <h2> MenuDBクラス </h2>
 * <div class="description">
 *      <h3> 【Description】 </h3>
 *      MenuDBクラスは、menudb.datから設定情報を取得し、<br>
 *      内部データとして格納します。<br>
 * </div>
 *
 * <div class="special reference">
 *     <h3>【Developer Guides】</h3>
 *     -
 * </div>
 *
 * @author t.yamaguchi
 */
public class MenuDb {
    // menudbオフセット
    private static final int OFS_LONG = 4;
    private static final int OFS_CHAR = 1;

    // 属性情報
    /** 属性：未使用 */
    public static final int PROPERTY_NOT_USE = 0;
    /** 属性：通常メニュー */
    public static final int PROPERTY_NORMAL_MENU = 1;
    /** 属性：10〜17 飲み放題(1〜8) */
    public static final int PROPERTY_FREE_DRINK = 9;
    /** 属性：20〜17 食べ放題(1〜8) */
    public static final int PROPERTY_FREE_FOOD = 19;
    /** 属性：ランチ単品メニュー */
    public static final int PROPERTY_LUNCH_MENU = 3;

    /** フリーフラグ0、通常メニュー、放題メニュー、共に表示 */
    public static final int FREE_FLAG_0 = 0;
    /** フリーフラグ1、放題メニューのみ表示(通常のTOP画面)
     */
    public static final int FREE_FLAG_1 = 1;
    /** フリーフラグ2、放題メニューのみ表示(専用のTOP画面(飲み放題専用のTOP画面))*/
    public static final int FREE_FLAG_2 = 2;


    // ヘッダ情報Index
    /** ヘッダー情報プロトコル長 */
    public static final int HEADER_INFORMATION_TOP = 0;    // 先頭オフセット
    /** ヘッダ情報を含む全ファイルサイズ */
    public static final int HEADER_INFORMATION_FILE_SIZE = HEADER_INFORMATION_TOP;
    /** 使用される最大大分類数(10を指定) */
    public static final int HEADER_INFORMATION_LMENU_MAX = HEADER_INFORMATION_FILE_SIZE + OFS_LONG;
    /** 一つの大分類項目に表示可能な最大の中分類数(12を指定) */
    public static final int HEADER_INFORMATION_MMENU_MAX = HEADER_INFORMATION_LMENU_MAX + OFS_CHAR;
    /** フリーレイアウト小分類画面の１セル横サイズ */
    public static final int HEADER_INFORMATION_WIDTH = HEADER_INFORMATION_MMENU_MAX + OFS_CHAR;
    /** フリーレイアウト小分類画面の１セル縦サイズ */
    public static final int HEADER_INFORMATION_HEIGHT = HEADER_INFORMATION_WIDTH + OFS_CHAR;
    /** 全小分類項目数の合計 */
    public static final int HEADER_INFORMATION_SMENU_NUM = HEADER_INFORMATION_HEIGHT + OFS_CHAR;
    /** 全商品セル情報項目数の合計 */
    public static final int HEADER_INFORMATION_ITEM_CELL_NUM = HEADER_INFORMATION_SMENU_NUM + OFS_LONG;
    /** 全商品フレーム情報数の合計 */
    public static final int HEADER_INFORMATION_ITEM_FRM_NUM = HEADER_INFORMATION_ITEM_CELL_NUM + OFS_LONG;
    /** 全商品詳細情報数の合計 */
    public static final int HEADER_INFORMATION_ITEM_INFO_NUM = HEADER_INFORMATION_ITEM_FRM_NUM + OFS_LONG;
    /** 全階層コード、指示ナンバー情報数の合計 */
    public static final int HEADER_INFORMATION_SUB_CODE_INFO_NUM = HEADER_INFORMATION_ITEM_INFO_NUM + OFS_LONG;
    /** 全サブ小分類項目数の合計 */
    public static final int HEADER_INFORMATION_SUB_SMENU_NUM = HEADER_INFORMATION_SUB_CODE_INFO_NUM + OFS_LONG;
    /** 全サブ商品セル情報項目数の合計 */
    public static final int HEADER_INFORMATION_SUB_ITEM_CELL_NUM = HEADER_INFORMATION_SUB_SMENU_NUM + OFS_LONG;
    /** 全サブ商品フレーム情報数の合計 */
    public static final int HEADER_INFORMATION_SUB_ITEM_FRM_NUM = HEADER_INFORMATION_SUB_ITEM_CELL_NUM + OFS_LONG;
    /** ヘッダ情報サイズ */
    public static final int HEADER_INFORMATION_SIZE = HEADER_INFORMATION_SUB_ITEM_FRM_NUM + OFS_LONG;

    /** ヘッダ情報 */
    public class MenuHead {
        /** ヘッダ情報を含む全ファイルサイズ。単位はバイト。 */
        public long mFilesize;
        /** 10を指定します。使用される最大大分類数。*/
        public char mLmenuMax;
        /** 12を指定します。一つの大分類項目に表示可能な最大の中分類数。*/
        public char mMmenuMax;
        /** フリーレイアウト小分類画面の１セルサイズ dmy[0]:横サイズ、dmy[1]:縦サイズ */
        public int[] dmy = {20,20};
        /** 全小分類項目数の合計 */
        public long mSmenuNum;
        /** 全商品セル情報項目数の合計。 */
        public long mItemCellNum;
        /** 全商品フレーム情報数の合計。 */
        public long mItemFrmNum;
        /** 全商品詳細情報数の合計。 */
        public long mItemInfoNum;
        /** 全階層コード、指示ナンバー情報数の合計。 */
        public long mSubCodeInfoNum;
        /** 全サブ小分類項目数の合計。 */
        public long mSubSMenuNum;
        /** 全サブ商品セル情報項目数の合計。 */
        public long mSubItemCellNum;
        /** 全サブ商品フレーム情報数の合計。 */
        public long mSubItemFrmNum;
    }

    /** ヘッダ情報格納用 */
    private MenuHead mMenuHead = new MenuHead();

    /** 大分類情報格納用 */
    ArrayList<BaseInformationLm> mBaseInformationLmList = new ArrayList<BaseInformationLm>();

    /** 基本情報(大分類関連)Index */
    public static final int BASE_INFORMATION_LM = 4 + 1 + 1 + 2 + 4 + 4 + 4 + 4 + 4 + 4 + 4 + 4;
    /** 大分類スクリーン用会計確認ボタン画像ファイル名 */
    public static final int BASE_INFORMATION_LM_CK_ORDER_BTN_IMG = BASE_INFORMATION_LM + (16 + 4) * 2;
    /** 大分類スクリーン用案内ボタン画像ファイル名 */
    public static final int BASE_INFORMATION_LM_ANNAI_BTN_IMG = BASE_INFORMATION_LM + (16 + 4) * 4;
    /** 基本情報(小分類関連) Index */
    public static final int BASE_INFORMATION_SM = BASE_INFORMATION_LM + (16 + 4) * 5;
    /** 基本情報(下フレーム関連) Index */
    public static final int BASE_INFORMATION_BF = BASE_INFORMATION_SM + (16 + 4) * 5;
    /** 下フレーム背景画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_BACK_IMG = BASE_INFORMATION_BF;
    /** 初期下フレーム背景画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_ST_BK_IMG = BASE_INFORMATION_BF + (16 + 4) * 1;
    /** 下フレーム右ページボタン画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_R_PAGE_BTN_IMG = BASE_INFORMATION_BF + (16 + 4) * 2;
    /** 下フレーム左ページボタン画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_L_PAGE_BTN_IMG = BASE_INFORMATION_BF + (16 + 4) * 3;
    /** 下フレームTOPボタン画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_TOP_BTN_IMG = BASE_INFORMATION_BF + (16 + 4) * 4;
    /** 下フレーム店員呼び出しボタン画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_CALL_BTN_IMG = BASE_INFORMATION_BF + (16 + 4) * 5;
    /** 下フレーム店員呼び出し閉じるボタン画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_CALL_END_BTN_IMG = BASE_INFORMATION_BF + (16 + 4) * 6;
    /** 下フレーム戻るボタン（TOPボタン反転）画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_RVS_BTN_IMG = BASE_INFORMATION_BF + (16 + 4) * 7;
    /** 下フレーム注文内容確認ボタン画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_CHECK_BTN_IMG = BASE_INFORMATION_BF + (16 + 4) * 8;
    /** 下フレーム注文内容確認終了ボタン画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_CHECK_END_BTN_IMG = BASE_INFORMATION_BF + (16 + 4) * 9;
    /** 下フレームプラスボタン画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_UP_BTN_IMG = BASE_INFORMATION_BF + (16 + 4) * 10;
    /** 下フレームマイナスボタン画像ファイル名 */
    public static final int BASE_INFORMATION_LM_BF_DOWN_BTN_IMG = BASE_INFORMATION_BF + (16 + 4) * 11;

    /** 基本情報(注文画面関連) Index */
    public static final int BASE_INFORMATION_OF = BASE_INFORMATION_BF + (16 + 4) * 12;
    /** オーダーフレーム背景画像ファイル名 */
    public static final int BASE_INFORMATION_OF_BACK_IMG = BASE_INFORMATION_OF;
    /** オーダーフレーム上ページボタン画像ファイル名 */
    public static final int BASE_INFORMATION_OF_UPAGE_BTN_IMG = BASE_INFORMATION_OF + (16 + 4) * 1;
    /** オーダーフレーム下ページボタン画像ファイル名 */
    public static final int BASE_INFORMATION_OF_DPAGE_BTN_IMG = BASE_INFORMATION_OF + (16 + 4) * 2;
    /** オーダーフレーム注文ボタン画像ファイル名 */
    public static final int BASE_INFORMATION_OF_ORDER_BTN_IMG = BASE_INFORMATION_OF + (16 + 4) * 3;
    /** オーダーフレームプラスボタン画像ファイル名 */
    public static final int BASE_INFORMATION_OF_UP_BTN_IMG = BASE_INFORMATION_OF + (16 + 4) * 4;
    /** オーダーフレームマイナスボタン画像ファイル名 */
    public static final int BASE_INFORMATION_OF_DOWN_BTN_IMG = BASE_INFORMATION_OF + (16 + 4) * 5;
    /** 品切れ注文エラーリスト背景画像ファイル名 */
    public static final int BASE_INFORMATION_OS_BACK_IMG = BASE_INFORMATION_OF + (16 + 4) * 6;
    /** 品切れ注文エラーリスト確認OKボタン画像ファイル名 */
    public static final int BASE_INFORMATION_OS_OK_IMG = BASE_INFORMATION_OF + (16 + 4) * 7;

    /** 基本情報(会計確認関連) Index */
    public static final int BASE_INFORMATION_CO = BASE_INFORMATION_OF + (16 + 4) * 8;
    /** 会計確認背景画像ファイル名 */
    public static final int BASE_INFORMATION_CO_BACK_IMG = BASE_INFORMATION_CO;
    /** 会計確認上ページボタン画像ファイル名 */
    public static final int BASE_INFORMATION_CO_UPAGE_BTN_IMG = BASE_INFORMATION_CO + (16 + 4) * 1;
    /** 会計確認下ページボタン画像ファイル名 */
    public static final int BASE_INFORMATION_CO_DPAGE_BTN_IMG = BASE_INFORMATION_CO + (16 + 4) * 2;
    /** 会計確認確認OKボタン画像ファイル名 */
    public static final int BASE_INFORMATION_CO_OK_BTN_IMG = BASE_INFORMATION_CO + (16 + 4) * 3;
    /** 会計確認割り勘ボタン画像ファイル名 */
    public static final int BASE_INFORMATION_CO_DIVI_BTN_IMG = BASE_INFORMATION_CO + (16 + 4) * 4;
    /** 会計確認割り勘背景ボタン画像ファイル名 */
    public static final int BASE_INFORMATION_CO_DIVI_BACK_BTN_IMG = BASE_INFORMATION_CO + (16 + 4) * 5;
    /** 会計確認プラスボタン画像ファイル名 */
    public static final int BASE_INFORMATION_CO_UP_BTN_IMG = BASE_INFORMATION_CO + (16 + 4) * 6;
    /** 会計確認マイナスボタン画像ファイル名 */
    public static final int BASE_INFORMATION_CO_DOWN_BTN_IMG = BASE_INFORMATION_CO + (16 + 4) * 7;

    /** Info画面戻るボタン画像ファイル名 */
    public static final int BASE_INFORMATION_II = BASE_INFORMATION_CO + (16 + 4) * 8;

    /** 基本情報(etc) Index */
    public static final int BASE_INFORMATION_MS = BASE_INFORMATION_II + (16 + 4) * 1;
    /** メッセージ画面ようこそ画像ファイル名 */
    public static final int BASE_INFORMATION_MS_WELCOME_IMG = BASE_INFORMATION_MS;
    /** メッセージ画面注文しています画像ファイル名 */
    public static final int BASE_INFORMATION_MS_ORDER_NOW_IMG = BASE_INFORMATION_MS + (16 + 4) * 1;
    /** メッセージ画面注文を承りました画像ファイル名 */
    public static final int BASE_INFORMATION_MS_ORDER_OK_IMG = BASE_INFORMATION_MS + (16 + 4) * 2;
    /** メッセージ画面置き台に戻してください画像ファイル名 */
    public static final int BASE_INFORMATION_MS_OKIDAI_IMG = BASE_INFORMATION_MS + (16 + 4) * 3;
    /** メッセージ画面ご注文の受付は終了いたしました画像ファイル名 */
    public static final int BASE_INFORMATION_MS_ORDER_END_IMG = BASE_INFORMATION_MS + (16 + 4) * 4;
    /** メッセージ画面ご注文の受付は終了いたしました画面での注文内容確認ボタン画像ファイル名 */
    public static final int BASE_INFORMATION_MS_ORDER_END_CK_BTN_IMG = BASE_INFORMATION_MS + (16 + 4) * 5;
    /** メッセージ画面会計確認中です画像ファイル名 */
    public static final int BASE_INFORMATION_MS_CHECK_NOW_IMG = BASE_INFORMATION_MS + (16 + 4) * 6;
    /** メッセージ画面選択商品が30を超えました画像ファイル名 */
    public static final int BASE_INFORMATION_MS_ITEM_OVER_IMG = BASE_INFORMATION_MS + (16 + 4) * 7;
    /** メッセージ画面注文が受け付けられなかった可能性があります画像ファイル名 */
    public static final int BASE_INFORMATION_MS_ORDER_ERR_IMG = BASE_INFORMATION_MS + (16 + 4) * 8;
    /** メッセージ画面ただいま大変混み合っております画像ファイル名 */
    public static final int BASE_INFORMATION_MS_JAM_IMG = BASE_INFORMATION_MS + (16 + 4) * 9;
    /** メッセージ画面案内画像ファイル名 */
    public static final int BASE_INFORMATION_MS_ANNAI_IMG = BASE_INFORMATION_MS + (16 + 4) * 10;
    /** メッセージ画面飲み放題終了画像ファイル名 */
    public static final int BASE_INFORMATION_MS_FD_STOP_IMG = BASE_INFORMATION_MS + (16 + 4) * 11;
    /** メッセージ画面食べ放題終了画像ファイル名 */
    public static final int BASE_INFORMATION_MS_FF_STOP_IMG = BASE_INFORMATION_MS + (16 + 4) * 12;
    /** メッセージ画面時間帯メニュー終了画像ファイル名 */
    public static final int BASE_INFORMATION_MS_FL_STOP_IMG = BASE_INFORMATION_MS + (16 + 4) * 13;

    /** 大分類項目情報 Index */
    public static final int LMENU_INFORMATION = BASE_INFORMATION_MS + (16 + 4) * 14;    // 大分類項目の先頭オフセット

    /** 大分類項目情報サイズ */
    public static final int LMENU_INFORMATION_SIZE = 1 + 1 + 1 + 1 + + (16 + 4) * 5;

    /**
     * 大分類項目情報
     */
    public class BaseInformationLm {
        /** 属性、この項目を表示するか否かの設定(未使用：0、表示：１ */
        public char mProperty;
        /** 動的メニュー表示 */
        public char mFreeFlg;
        /** 大分類スクリーンボタンを選択した場合に、どの大分類項目フレームを選択するか、対応する大分類項目番号 */
        public char mScrToFrmNo;
        /** ダミー */
        public char mDmy;
        /** 大分類スクリーン用ボタン画像ファイル名 */
        public String mScrBtnImg;
        /** 大分類スクリーン用ボタン画像ファイル名のビットマップアドレス */
        public long mScrBtnImgAddr;
        /** 大分類フレーム用背景画像ファイル名 */
        public String mLmFrmBackImg;
        /** 大分類フレーム用背景画像ファイル名のビットマップアドレス */
        public long mLmFrmBackImgAddr;
        /** 大分類フレーム用ボタン画像（未選択）ファイル名 */
        public String mFrmOffBtnImg;
        /** 大分類フレーム用ボタン画像（未選択）ファイル名のビットマップアドレス */
        public long mFrmOffBtnImgAddr;
        /** 大分類フレーム用ボタン画像（選択）ファイル名 */
        public String mFrmOnBtnImg;
        /** 大分類フレーム用ボタン画像（選択）ファイル名のビットマップアドレス */
        public long mFrmOnBtnImgAddr;
        /** 中分類フレーム用背景画像ファイル名 */
        public String mMmFrmBackImg;
        /** 中分類フレーム用背景画像ファイル名のビットマップアドレス */
        public long mMmFrmBackImgAddr;
    }

    /** 中分類呼応目情報サイズ */
    public static final int MMENU_INFORMATION_SIZE = 1 + 3 + (16 + 4) * 2 + 4 + 4;

    /**
     * 中分類呼応目情報
     */
    public class BaseInformationMm {
        /** 属性、この項目を表示するか否かの設定(未使用：0、表示：１ */
        public char mProperty;
        /** ダミー */
        public char[] mDmy;
        /** 中分類フレーム用ボタン画像（未選択）ファイル名 */
        public String mBtnOnImg;
        /** 中分類フレーム用ボタン画像（未選択）ファイル名のビットマップアドレス */
        public long mBtnOnImgAddr;
        /** 中分類フレーム用ボタン画像（選択）ファイル名 */
        public String mBtnOffImg;
        /** 中分類フレーム用ボタン画像（選択）ファイル名のビットマップアドレス */
        public long mBtnOffImgAddr;
        /** 小分類項目数。商品ページのページ数 */
        public long mSMenuNum;
        /** 小分類ページの定義の格納アドレス（オフセット） */
        public long mSMenuAddr;

        public boolean isNormalMenu() {
            return this.mProperty == PROPERTY_NORMAL_MENU;
        }
    }

    /** 小分類項目情報、サブ小分類項目情報、店員呼び出し小分類項目情報サイズ */
    public static final int SMENU_INFORMATION_SIZE = 1 + 1 + 2 + 4 + 4 + 16 + 4 + 4;
    // 定数(ShowType)　※あくまでmenudbの表示タイプ。おすすめとは別※
    /** 表示タイプ 0:セル */
    public static final int SHOW_TYPE_0_CELL = 0;
    /** 表示タイプ 1:6毎写真フレーム */
    public static final int SHOW_TYPE_1_FIXING_06FRAME = 1;
    /** 表示タイプ 2:8毎写真フレーム */
    public static final int SHOW_TYPE_2_FIXING_08FRAME = 2;
    /** 表示タイプ 3:12毎写真フレーム */
    public static final int SHOW_TYPE_3_FIXING_12FRAME = 3;
    /** 表示タイプ 4:24毎写真フレーム */
    public static final int SHOW_TYPE_4_FIXING_24FRAME = 4;
    /** 表示タイプ 5:24毎写真フレーム（特殊サブ機能用） */
    public static final int SHOW_TYPE_5_FIXING_24FRAME = 5;
    /** 表示タイプ 6:フリーフレーム（おすすめ機能用） */
    public static final int SHOW_TYPE_6_FREEFRAME_OSUSUME = 6;

    // 背景色カラーテーブル
    /** 背景色、黒 */
    public static final char BACK_COLOR_BLACK = 1;
    /** 背景色、黒(RGB) */
    public static final int  BACK_COLOR_BLACK_RGB = 0xff000000;
    /** 背景色、灰 */
    public static final char BACK_COLOR_GRAY = 2;
    /** 背景色、灰(RGB) */
    public static final int  BACK_COLOR_GRAY_RGB  = 0xff808080;
    /** 背景色、薄灰 */
    public static final char BACK_COLOR_LGRAY = 3;
    /** 背景色、薄灰(RGB) */
    public static final int  BACK_COLOR_LGRAY_RGB = 0xffc0c0c0;
    /** 背景色、白 */
    public static final char BACK_COLOR_WHITE = 4;
    /** 背景色、白(RGB) */
    public static final int  BACK_COLOR_WHITE_RGB = 0xffffffff;
    /** 背景色、赤 */
    public static final char BACK_COLOR_RED = 5;
    /** 背景色、赤(RGB) */
    public static final int  BACK_COLOR_RED_RGB = 0xffbf0000;
    /** 背景色、桃 */
    public static final char BACK_COLOR_PINK = 6;
    /** 背景色、桃(RGB) */
    public static final int  BACK_COLOR_PINK_RGB = 0xffff7f7f;
    /** 背景色、緑 */
    public static final char BACK_COLOR_GREEN = 7;
    /** 背景色、緑(RGB) */
    public static final int  BACK_COLOR_GREEN_RGB = 0xff00bf00;
    /** 背景色、黄緑 */
    public static final char BACK_COLOR_LGREEN  = 8;
    /** 背景色、黄緑(RGB) */
    public static final int  BACK_COLOR_LGREEN_RGB = 0xff7fff7f;
    /** 背景色、黄*/
    public static final char BACK_COLOR_YELLOW = 9;
    /** 背景色、黄(RGB) */
    public static final int  BACK_COLOR_YELLOW_RGB = 0xffffff00;
    /** 背景色、薄黄 */
    public static final char BACK_COLOR_LYELLOW = 10;
    /** 背景色、薄黄(RGB) */
    public static final int  BACK_COLOR_LYELLOW_RGB = 0xffffff7f;
    /** 背景色、青 */
    public static final char BACK_COLOR_BLUE = 11;
    /** 背景色、青(RGB) */
    public static final int  BACK_COLOR_BLUE_RGB = 0xff0000bf;
    /** 背景色、薄青 */
    public static final char BACK_COLOR_LBLUE = 12;
    /** 背景色、薄青(RGB) */
    public static final int  BACK_COLOR_LBLUE_RGB = 0xff7f7fff;

    // フォントサイズテーブル
    /** フォントサイズ小 */
    public static final char MENU_FONT_SMALL = 0;
    /** フォントサイズ中 */
    public static final char MENU_FONT_MIDDLE = 1;
    /** フォントサイズ大 */
    public static final char MENU_FONT_LARGE = 2;
    /** フォントサイズ小太 */
    public static final char MENU_FONT_SMALL_BOLD = 3;
    /** フォントサイズ中太 */
    public static final char MENU_FONT_MIDDLE_BOLD = 4;
    /** フォントサイズ大太 */
    public static final char MENU_FONT_LARGE_BOLD = 5;
    /** フォントサイズ特大 */
    public static final char MENU_FONT_OVERSIZED = 6;
    /** フォントサイズ小（サイズ） */
    public static final int MENU_FONT_SMALL_SIZE = 11;
    /** フォントサイズ中（サイズ） */
    public static final int MENU_FONT_MIDDLE_SIZE = 15;
    /** フォントサイズ大（サイズ） */
    public static final int MENU_FONT_LARGE_SIZE = 17;
    /** フォントサイズ特大（サイズ） */
    public static final int MENU_FONT_OVERSIZED_SIZE = 25;
    /** 小分類タイプ１、小分類項目情報 */
    public static final int SMALL_MENU_TYPE1_SMALL = 1;
    /** 小分類タイプ２、サブ小分類項目情報 */
    public static final int SMALL_MENU_TYPE2_SUB = 2;
    /** 小分類タイプ３、店員呼び出し小分類項目情報 */
    public static final int SMALL_MENU_TYPE3_STUFF = 3;

    /**
     * 小分類項目情報、サブ小分類項目情報、店員呼び出し小分類項目情報
     */
    public class BaseInformationSm {
        /** 表示タイプ */
        public int mShowType;
        /** 広告の表示 0:表示無し 1:表示あり */
        public char mCmFlg;
        /** ダミー */
        public char[] mDmy;
        /** 商品ページに割り当てられている有効なセル数または有効なフレーム内商品数 */
        public long mItemNum;
        /** 背景色 */
        public long mBackColor;
        /** 商品ページの背景画像ファイル名 */
        public String mBackImg;
        /** 商品ページの背景画像ファイル名のビットマップアドレス */
        public long mBackImgAddr;
        /** 商品セル（フレーム）表示情報定義の格納アドレス（オフセット） */
        public long mItemAddr;
        /** プログラム付与情報、表示中の画面タイプ */
        public int mSmallType;
    }

    /** 商品セル表示情報、サブ商品セル表示情報サイズ */
    public static final int ITEM_CELL_INFORMATION_SIZE = 1 + 1 + 1 + 1 + 2 * 16 + 1 + 1 + 2 + 4 + 4 + 4;

    /**
     * 商品セル表示情報、サブ商品セル表示情報
     */
    public static class ItemCellInformation {
        /** 表示情報や処理の選択 */
        public char mProcess;
        /** 表示する横セル座標 */
        public char mCellX;
        /** 表示する縦セル座標 */
        public char mCellY;
        /** ダミー(Processが101,103の場合、位置調整文字の色が設定) */
        public char mDmy;
        /** 表示する文字 */
        public String mText;
        /** フォントの大きさ */
        public char mFontSize;
        /** テキスト枠指定 0:枠なし 1:枠あり */
        public char mTextFrame;
        /** ダミー(Processが101,103の場合、位置調整文字のオフセット座標が設定) */
        public byte[] mDmy2;
        /** ダミー */
        public long mDmy3;
        /** Processが6、7の場合、サブ商品の商品詳細情報の格納先アドレス（オフセット値）が設定される。
         *  Processが15、16の場合、ジャンプ先のサブ小分類情報の格納先アドレス（オフセット値）が設定される。
         *  (15、16はサブメニューリンク専用)*/
        public long mOption;
        /** 商品詳細情報の格納先アドレス（オフセット値） */
        public long mItemInfoAddr;
        /** おすすめのフリーレイアウト */
        public boolean isLiteFreeLayout = false;
    }

    /** 商品フレーム表示情報、店員呼び出しセル表示情報サイズ */
    public static final int ITEM_FRAME_INFORMATION_SIZE = 1 + 1 + 1 + 1 + 16 + 4 + 2 * 32 + 1 + 1
                                                        + 2 + 2 * 8 + 1 + 1 + 2 + 2 * 8 + 1 + 1
                                                        + 2 + 2 * 32 + 1 + 1 + 2 + 4;

    /**
     * 商品フレーム表示情報、店員呼び出しセル表示情報
     */
    public static class ItemFrameInformation {
        /** 表示情報や処理の選択 */
        public char mProcess;
        /** 表示する横セル座標 */
        public char mCellX;
        /** 表示する縦セル座標 */
        public char mCellY;
        /** ダミー */
        public char mDmy;
        /** 商品写真 */
        public String mItemImg;//char[16]
        /** 商品写真のビットマップアドレス */
        public long mItemImgAddr;
        /** 表示する商品名文字 */
        public String mNameText;//short[32]
        /** 商品名フォントの大きさ 0:小 1:中 2:大 3:小太字 4:中太字 5:大太字 */
        public char mNameFontSize;
        /** 商品名テキスト背景色 */
        public char mNameTextColor;
        /** ダミー */
        public char[] mDmy2;//[2]
        /** 表示する価格文字 */
        public String mPriceText;//short[8]
        /** 価格フォントの大きさ 0:小 1:中 2:大3:小太字 4:中太字 5:大太字 */
        public char mPriceFontSize;
        /** 価格テキスト背景色 */
        public char mPriceTextColor;
        /** ダミー */
        public char[] mDmy3;//[2]
        /** 表示する税込み価格文字 */
        public String mTaxPriceText;//short[8]
        /** 税込み価格フォントの大きさ 0:小 1:中 2:大3:小太字 4:中太字 5:大太字 */
        public char mTaxPriceFontSize;
        /** 税込み価格テキスト背景色 */
        public char mTaxPriceTextColor;
        /** ダミー */
        public char[] mDmy4;//[2]
        /** 表示する説明文字 */
        public String mInfoText;//short[32]
        /** 説明フォントの大きさ 0:小 1:中 2:大3:小太字 4:中太字 5:大太字 */
        public char mInfoFontSize;
        /** 説明テキスト背景色 */
        public char mInfoTextColor;
        /** ダミー */
        public char[] mDmy5;//[2]
        /** 商品詳細情報の格納先アドレス（オフセット値） */
        public long mItemInfoAddr;
    }

    /** 商品詳細情報サイズ */
    public static final int ITEM_INFORMATION_SIZE = 4 + 1 + 1 + 1 + 1 + 4 + 4 + 2 * 32 + 1 + 1 + 1 + 1 + 4 + 4 + 4 + 1 + 3 + 16 + 4 + 2 * 128;
    // 定数：処理(Process)
    /** 処理(Process) 0:文字無し（クリックで商品選択） */
    public static final char PROCESS_0_CHOICEITEM_NONCHAR = 0;
    /** 処理(Process) 1:文字表示（クリックで商品選択） */
    public static final char PROCESS_1_CHOICEITEM_EXISTCHAR = 1;
    /** 処理(Process) 2:インフォ表示（クリックでインフォ画面表示） */
    public static final char PROCESS_2_INFO_APPEAR = 2;
    /** 処理(Process) 3:文字表示（クリック反応無し） */
    public static final char PROCESS_3_CHAR_APPEAR = 3;
    /** 処理(Process) 4:品切れ画像表示位置（品切れでない時は、処理0:と同じ） */
    public static final char PROCESS_4_SOLDOUT_POINT = 4;
    /** 処理(Process) 5:動画インフォ表示（クリックで動画インフォ画面表示） */
    public static final char PROCESS_5_MOVIE_INFO = 5;
    /** 処理(Process) 6:サブ画面を表示せずに商品とサブ商品を同時選択する */
    public static final char PROCESS_6_CHOICEITEM_SUBSKIP = 6;
    /** 処理(Process) 7:品切れ画像表示位置（品切れでない時は、処理6:と同じ） */
    public static final char PROCESS_7_SOLDOUT_POINT = 7;
    /** 処理(Process) 10:商品を選択して完了する（サブ画面を全て抜けます） */
    public static final char PROCESS_10_CHOICEITEM_SUBALLCLEAR = 10;
    /** 処理(Process) 11:キャンセル（サブ画面を全て抜けます）*/
    public static final char PROCESS_11_CANCELL_SUBALLCLEAR = 11;
    /** 処理(Process) 12:戻る（サブ画面を一つ戻ります）*/
    public static final char PROCESS_12_RETURN_SUBONECLEAR = 12;
    /** 処理(Process) 13:商品を選択せずに次のサブ画面へ遷移 */
    public static final char PROCESS_13_NOTCHOICE_NEXTSUB = 13;
    /** 処理(Process) 14:現在のテンポラリリストで商品を決定する（サブ画面を全て抜けます） */
    public static final char PROCESS_14_CHOICETEMP_SUBALLCLEAR = 14;
    /** 処理(Process) 15:商品を選択せずサブ画面をジャンプする */
    public static final char PROCESS_15_NO_ITEM_CHOICE_SUB_JUMP = 15;
    /** 処理(Process) 16:商品を選択してサブ画面をジャンプする */
    public static final char PROCESS_16_ITEM_CHOICE_SUB_JUMP = 16;
    /** 処理(Process) 101: 位置調整文字表示(クリックで商品選択) （仕変0258） */
    public static final char PROCESS_101_POINTADUST_NONCHAR = 101;
    /** 処理(Process) 103: 位置調整文字表示(クリックで反応なし) （仕変0258） */
    public static final char PROCESS_103_POINTADUST_EXISTCHAR = 103;
    // 定数：メニュー属性
    /** 0:メインメニュー*/
    public static final char MENU_ATTRIBUTE_MAIN    = 0x00;
    /** 1:コメントメニュー*/
    public static final char MENU_ATTRIBUTE_COMMENT = 0x01;
    /** 2:サブメニュー*/
    public static final char MENU_ATTRIBUTE_SUB     = 0x02;
    /** 3:セットメニュー*/
    public static final char MENU_ATTRIBUTE_SET     = 0x03;
    // 定数：サブメニューフラグ
    /** サブメニューフラグ 0:サブ無し */
    public static final char SUBMENUFLAG_0_NONSUB = 0;
    /** サブメニューフラグ 1:サブ有りで親が単独で注文不可能な商品。<br>
     *                   サブ商品を注文した数だけ親商品がカウントされる。*/
    public static final char SUBMENUFLAG_1_SUBEXIST_PARENT_NOTSINGLE = 1;
    /** サブメニューフラグ 2:サブ有りで親が単独で注文可能な商品 */
    public static final char SUBMENUFLAG_2_SUBEXIST_PARENT_SINGLEOK = 2;
    /** サブメニューフラグ 3:サブ有りで親が単独で注文不可能な商品（三品系）。固定フレームのみ。<br>
     *                   　指定数サブを注文すると親商品が1になる。*/
    public static final char SUBMENUFLAG_3_SUBEXIST_CHOICEITEM = 3;
    /** サブメニューフラグ 4: 複数のサブ画面で商品を全て選択すると親商品が1になる。<br>
     *                     ファミレスサブ(サブのパターンが複数存在)。*/
    public static final char SUBMENUFLAG_4_SUBEXIST_FAMIRES = 4;
    /** サブメニューフラグ 5: 複数のサブ有りでsublink.csvを参照する。<br>
     *                     サブメニューリンク(サブのパターンが決め打ち)*/
    public static final char SUBMENUFLAG_5_SUBEXIST_SUBMENULINK = 5;
    /** サブメニューフラグ 6:サブ有りで親がダミーとなる商品 */
    public static final char SUBMENUFLAG_6_SUBEXIST_DUMYSUB = 6;
    /** サブメニューフラグ x: 未定義 */
    public static final char SUBMENUFLAG_X_UNKNOWN = 99;

    /**
     * 商品詳細情報
     */
    public class ItemInformation {
        /** 商品コード */
        public long mCode;
        /** フリーオーダーフラグ 0:非対応 1:対応 */
        public char mFreeFlg;
        /** 品切れフラグ 0:あり 1:品切れ */
        public char mSoldOutFlg;
        /** 注文可能な最小商品数 */
        public char mMinItemNum;
        /** ダミー */
        public char mDmy;
        /** 価格（表示用、税込み価格） */
        public long mPrice;
        /** 税抜き価格（管理用） */
        public long mNoTaxPrice;
        /** 税込み価格（管理用） */
        public long mTaxPrice;
        /** 商品名（管理用） */
        public String mName;
        /** メニュー属性（データ区分）0:メイン 1:コメント 2:サブ 3:セット */
        public char mMenuAtt;
        /** サブメニューフラグ */
        public char mSubMenuFlg;
        /** サブ商品セット数 */
        public char mSubItemSetNum;
        /** ダミー */
        public char mDmy1;
        /** サブメニュー情報の格納先アドレス */
        public long mSubMenuAddr;
        /** 指示ナンバー */
        public long mCmdNo;
        /** 同時にセットされる商品詳細情報のアドレス */
        public long mSetItemAddr;
        /** 商品詳細情報有無 0:なし 1:あり */
        public char mInfo;
        /** ダミー */
        public char[] mdmy2;
        /** 商品詳細情報用写真 */
        public String infoImg;
        /** 商品詳細情報用写真のビットマップアドレス */
        public long mInfoImgAddr;
        /** 商品詳細情報用コメント */
        public String mInfoComment;
    }

    /**
     * 階層コード、指示ナンバー情報（未使用）
     */
    public class SubcodeINFO {
        /** メイン商品コード */
        long MCode;
        /** サブ商品コード */
        long SCode;
        /** 階層コード */
        long LayCode;
        /** 指示ナンバー */
        long CmdNo;
    }

    /** 階層コード、指示ナンバーサイズ */
    public static final int SUBCODE_INFO_SIZE = 4 + 4 + 4 + 4;

    /** ログ出力用タグ */
    private static final String TAG = "MenuDb";
    /** Commonの宣言 */
    private Common mCommon = null;
    /** menuDbデータ */
    private byte[] mMenuData = null;

    /** コンソール */

    /**
     * コンストラクタ
     * @param common 共通クラス
     */
    public MenuDb(Common common) {
        mCommon = common;
        getMenuData();
    }

    /**
     * DATファイルからの抽出データを2バイト文字列に変換
     * @return 返還後のデータ
     */
    private byte[] menudb2bytesArray() {
        java.io.File file = new java.io.File(mCommon.mDatas + "menudb.dat");
        byte[] buffer = new byte[(int)file.length()];
        InputStream ios = null;
        try {
            ios = new FileInputStream(file);
            int readn = 0;
            try {
                readn = ios.read(buffer);
                if (readn == -1) {
                    Log.e(TAG, "Error of read menudb.dat");
                    readn = 0;
                }
            } catch (IOException ioe) {
                Log.e(TAG, "Exeption of read menudb.dat");
            }
            Log.d(TAG, "menudb.dat " + readn + " bytes read");
        } catch (FileNotFoundException ioe) {
            Log.e(TAG, "menudb.dat not found");

            // 明示的にnull返却
            return null;
        } finally {
            try {
                if (ios != null) {
                    ios.close();
                }
            } catch (IOException ioe) {
                Logger.e(ioe);
            }
        }
        return buffer;
    }

    /**
     * メニューデータ取得処理
     */
    private void getMenuData() {
        long start = System.currentTimeMillis();
        mMenuData = menudb2bytesArray();
        // menudb.datが取得できない内部異常対処処置
        if (mMenuData == null) {
            File menudb = new File(mCommon.mDatas + "menudb.dat");
            if (menudb.exists()) {
                Logger.e("menu read error! reset process.");
                android.os.Process.killProcess(android.os.Process.myPid()); // プロセスリスタート
            } else {
                Logger.e("menudb.dat not exists.");
                if (mCommon.mStartMode != Common.ACTIVE_MODE_NONE) {
                    Logger.e("internal error.");    // 既に運用起動しているがmenudbが無い
                    android.os.Process.killProcess(android.os.Process.myPid()); // プロセスリスタート
                } else {
                    mCommon.isSafeMode = true;
                    return;
                }
            }
        }
        long end = System.currentTimeMillis();
        Log.d(TAG, "read time " + (end - start) + "ms");

        // ヘッダ情報取得
        mMenuHead.mFilesize         = getLongData(HEADER_INFORMATION_FILE_SIZE);
        mMenuHead.mLmenuMax         = getCharData(HEADER_INFORMATION_LMENU_MAX);
        mMenuHead.mMmenuMax         = getCharData(HEADER_INFORMATION_MMENU_MAX);
        mMenuHead.dmy[0]            = getCharData(HEADER_INFORMATION_WIDTH);
        mMenuHead.dmy[1]            = getCharData(HEADER_INFORMATION_HEIGHT);
        mMenuHead.mSmenuNum         = getLongData(HEADER_INFORMATION_SMENU_NUM);
        mMenuHead.mItemCellNum      = getLongData(HEADER_INFORMATION_ITEM_CELL_NUM);
        mMenuHead.mItemFrmNum       = getLongData(HEADER_INFORMATION_ITEM_FRM_NUM);
        mMenuHead.mItemInfoNum      = getLongData(HEADER_INFORMATION_ITEM_INFO_NUM);
        mMenuHead.mSubCodeInfoNum   = getLongData(HEADER_INFORMATION_SUB_CODE_INFO_NUM);
        mMenuHead.mSubSMenuNum      = getLongData(HEADER_INFORMATION_SUB_SMENU_NUM);
        mMenuHead.mSubItemCellNum   = getLongData(HEADER_INFORMATION_SUB_ITEM_CELL_NUM);
        mMenuHead.mSubItemFrmNum = getLongData(HEADER_INFORMATION_SUB_ITEM_FRM_NUM);

        // 大項目データをキャッシュ (何故か Android11 だとリークするので)
        {
            mBaseInformationLmList.clear();
            int lmNum = getCharData(4);
            for (int i = 0; i < lmNum; i++) {
                BaseInformationLm data = getBaseInformationLm(LMENU_INFORMATION + LMENU_INFORMATION_SIZE * i);
                mBaseInformationLmList.add(data);
            }
        }
    }

    /**
     * menudbヘッダ情報を取得します。
     */
    public MenuHead getMenuHead() {
        return mMenuHead;
    }

    /**
     * 画像ファイルパス取得
     * @param offset オフセット
     * @return 画像ファイルパス
     */
    public String getImageFilePath(int offset) {
        String str = getFileName(offset);
        if ((str != null) && (str.length() != Constants.INIT_DATA.getInt())) {
            str = mCommon.mImages + str;
        } else {
            str = "";
        }
        return str;
    }

    /**
     * ファイル名取得
     * @param offset オフセット
     * @return ファイル名
     */
    public String getFileName(int offset) {
        if (offset > mMenuData.length) {
            return null;
        }
        byte[] b = new byte[17];
        b[16] = ' ';
        for (int i = 0; i < 16; i++) {
            b[i] = mMenuData[offset + i];
            if (b[i] == 0) {
                b[i] = ' ';
            }
        }
        String str = null;
        try {
            str = new String(b, "UTF-8");
        } catch (IOException ioe) {
            Logger.e(ioe);
        }
        str = str.trim();
        return str;
    }

    /**
     * Long型データ取得
     * @param offset オフセット
     * @return Long型データ
     */
    public long getLongData(int offset) {
        if (offset > mMenuData.length - 4) { // 範囲チェック
            return 0;
        }
        byte[] b = new byte[8];

        // 上位4バイトを符号に応じて設定
        if ((mMenuData[offset] & 0x80) != 0) { // 符号ビットが立っている場合
            for (int i = 0; i < 4; i++) {
                b[i] = (byte) 0xFF; // 符号拡張：負数の場合は0xFFで埋める
            }
        }

        // 下位4バイトをコピー
        for (int i = 0; i < 4; i++) {
            b[i + 4] = mMenuData[offset + i];
        }

        ByteBuffer buf = ByteBuffer.wrap(b);
        return buf.getLong();
    }

    /**
     * Char型データ取得
     * @param offset オフセット
     * @return Char型データ
     */
    public char getCharData(int offset) {
        if (offset > mMenuData.length) {
            return 0;
        }
        byte[] b = new byte[2];
        b[1] = mMenuData[offset];
        ByteBuffer buf = ByteBuffer.wrap(b);
        char value = buf.getChar();
        return value;
    }

    /**
     * 名称取得
     * @param offset オフセット
     * @param size   サイズ
     * @return 名称
     */
    public String getNameShortData(int offset, int size) {
        if (offset > mMenuData.length) {
            return "";
        }
        int idx;
        for (idx = 0; idx < size * 2; idx = idx + 2) {
            if (mMenuData[offset + idx] == 0x00 && mMenuData[offset + idx + 1] == 0x00) {
                break;
            }
        }
        String str = "";
        if (idx > 0) {
            byte[] b = new byte[idx];
            System.arraycopy(mMenuData, offset, b, 0, idx);
            str = new String(b, StandardCharsets.UTF_16);
            str = str.trim();
            if (str.isEmpty()) {
                str = "";
            }
        }
        return str;
    }

    /**
     * 大分類項目情報リスト取得
     * @return 大分類項目情報リスト
     */
    public ArrayList<BaseInformationLm> getBaseInformationLmList() {
        return mBaseInformationLmList;
    }

    /**
     * 大分類項目情報取得
     * @param offset オフセット
     * @return 大分類項目情報
     */
    private BaseInformationLm getBaseInformationLm(int offset) {
        BaseInformationLm data = new BaseInformationLm();
        data.mProperty = getCharData(offset);
        data.mFreeFlg = getCharData(offset + 1);
        data.mScrToFrmNo = getCharData(offset + 2);
        data.mScrBtnImg = getImageFilePath(offset + 4);
        data.mLmFrmBackImg = getImageFilePath(offset + 24);
        data.mFrmOffBtnImg = getImageFilePath(offset + 44);
        data.mFrmOnBtnImg = getImageFilePath(offset + 64);
        data.mMmFrmBackImg = getImageFilePath(offset + 84);
        return data;
    }

    /**
     * 中分類項目情報リスト取得
     * @param index 大分類ページ番号(基本的に1～10)
     * @return 中分類項目情報
     */
    public ArrayList<BaseInformationMm> getBaseInformationMmList(int index) {
        ArrayList<BaseInformationMm> list = new ArrayList<BaseInformationMm>();
        int lmNum = getCharData(4);
        int mmNum = getCharData(5);
        int offset = LMENU_INFORMATION + LMENU_INFORMATION_SIZE * lmNum + MMENU_INFORMATION_SIZE * mmNum * (index - 1);
        for (int i = 0; i < mmNum; i++) {
            BaseInformationMm data = getBaseInformationMm(offset + MMENU_INFORMATION_SIZE * i);
            list.add(data);
        }
        return list;
    }

    /**
     * 中分類項目情報取得
     * @param offset オフセット
     * @return 中分類項目情報
     */
    private BaseInformationMm getBaseInformationMm(int offset) {
        BaseInformationMm data = new BaseInformationMm();
        data.mProperty = getCharData(offset);
        data.mDmy = new char[3];
        data.mBtnOnImg = getImageFilePath(offset + 4);
        data.mBtnOffImg = getImageFilePath(offset + 24);
        data.mSMenuNum = getLongData(offset + 44);
        data.mSMenuAddr = getLongData(offset + 48);
        return data;
    }

//    /**
//     * 小分類項目情報、サブ小分類項目情報、店員呼び出し小分類項目情報リスト取得
//     * @param offset オフセット
//     * @param num 商品ページ数
//     * @return 小分類項目情報、サブ小分類項目情報、店員呼び出し小分類項目情報リスト
//     */
//    public ArrayList<BaseInformationSm> getBaseInformationSmList(int offset, int num) {
//        ArrayList<BaseInformationSm> baseInformationSm = new ArrayList<BaseInformationSm>();
//        for (int i = 1; i <= num; i++) {
//            BaseInformationSm data;
//            data = getBaseInformationSm(offset + SMENU_INFORMATION_SIZE * (i - 1));
//            baseInformationSm.add(data);
//        }
//        return baseInformationSm;
//    }

    /**
     * 小分類項目情報、サブ小分類項目情報、店員呼び出し小分類項目情報取得
     * @param offset オフセット
     * @param idx 商品ページ
     * @return 小分類項目情報、サブ小分類項目情報、店員呼び出し小分類項目情報
     */
    public BaseInformationSm getBaseInformationSm(int offset, int idx, int type) {
        return getBaseInformationSm(offset + SMENU_INFORMATION_SIZE * (idx - 1), type);
    }

    /**
     * 小分類項目情報、サブ小分類項目情報、店員呼び出し小分類項目情報取得
     * @param offset オフセット
     *
     * @return 小分類項目情報、サブ小分類項目情報、店員呼び出し小分類項目情報
     */
    public BaseInformationSm getBaseInformationSm(int offset, int type) {
        BaseInformationSm data = new BaseInformationSm();
        data.mShowType = getCharData(offset);
        data.mCmFlg = getCharData(offset + 1);
        data.mDmy = new char[2];
        data.mItemNum = getLongData(offset + 4);
        data.mBackColor = getLongData(offset + 8);
        data.mBackImg = getImageFilePath(offset + 12);
        data.mItemAddr = getLongData(offset + 32);
        data.mSmallType = type;
        return data;
    }

    /**
     * 商品セル表示情報、サブ商品セル表示情報リスト取得
     * @param offset オフセット
     * @param num 商品ページ数
     * @return 商品セル表示情報、サブ商品セル表示情報リスト
     */
    public ArrayList<ItemCellInformation> getItemCellInformationList(int offset, int num) {
        ArrayList<ItemCellInformation> itemCellInformation = new ArrayList<ItemCellInformation>();
        for (int i = 1; i <= num; i++) {
            ItemCellInformation data;
            data = getItemCellInformation(offset + ITEM_CELL_INFORMATION_SIZE * (i - 1));
            itemCellInformation.add(data);
        }
        return itemCellInformation;
    }

    /**
     * 商品フレーム表示情報、店員呼び出しセル表示情報リスト取得
     * @param offset オフセット
     * @param num 商品ページ数
     * @return 商品フレーム表示情報、店員呼び出しセル表示情報リスト
     */
    public ArrayList<ItemFrameInformation> getItemFrameInformationList(int offset, int num) {
        ArrayList<ItemFrameInformation> itemFrameInformation = new ArrayList<ItemFrameInformation>();
        for (int i = 1; i <= num; i++) {
            ItemFrameInformation data;
            data = getItemFrameInformation(offset + ITEM_FRAME_INFORMATION_SIZE * (i - 1));
            itemFrameInformation.add(data);
        }
        return itemFrameInformation;
    }

    /**
     * 商品フレーム表示情報、店員呼び出しセル表示情報取得
     * @param offset オフセット
     * @return 商品フレーム表示情報、店員呼び出しセル表示情報
     */
    private ItemFrameInformation getItemFrameInformation(int offset) {
        ItemFrameInformation data = new ItemFrameInformation();
        data.mProcess = getCharData(offset);
        data.mCellX = getCharData(offset + 1);
        data.mCellY = getCharData(offset + 2);
        data.mItemImg = getImageFilePath(offset + 4);
        data.mItemImgAddr = getLongData(offset + 20);
        data.mNameText = getNameShortData(offset + 24, 32);
        data.mNameFontSize  = getCharData(offset + 88);
        data.mNameTextColor = getCharData(offset + 89);
        data.mPriceText = getNameShortData(offset + 92, 8);
        data.mPriceFontSize = getCharData(offset + 100);
        data.mPriceTextColor = getCharData(offset + 101);
        data.mTaxPriceText = getNameShortData(offset + 104, 8);
        data.mTaxPriceFontSize = getCharData(offset + 112);
        data.mTaxPriceTextColor = getCharData(offset + 113);
        data.mInfoText = getNameShortData(offset + 116, 32);
        data.mInfoFontSize = getCharData(offset + 180);
        data.mInfoTextColor = getCharData(offset + 181);
        data.mItemInfoAddr = getLongData(offset + 184);
        return data;
    }

    /**
     * 商品セル表示情報、サブ商品セル表示情報取得
     * @param offset オフセット
     * @return 商品セル表示情報、サブ商品セル表示情報
     */
    private ItemCellInformation getItemCellInformation(int offset) {
        ItemCellInformation data = new ItemCellInformation();
        data.mProcess = getCharData(offset);
        data.mCellX = getCharData(offset + 1);
        data.mCellY = getCharData(offset + 2);
        data.mDmy   = getCharData(offset + 3);
        if ( (data.mText = getNameShortData(offset + 4, 14)) == null) {
            data.mText = "";
        }
        data.mFontSize = getCharData(offset + 36);
        data.mTextFrame = getCharData(offset + 37);
        data.mDmy2 = new byte[2];
        data.mDmy2[0] = (byte)getCharData(offset + 38);
        data.mDmy2[1] = (byte)getCharData(offset + 39);
        data.mOption = getLongData(offset + 44);
        data.mItemInfoAddr = getLongData(offset + 48);
        return data;
    }

    /**
     * 商品詳細情報取得
     * @param offset オフセット
     * @return 商品詳細情報
     */
    public ItemInformation getItemInformation(int offset) {
        ItemInformation data = new ItemInformation();
        data.mCode = getLongData(offset);
        data.mFreeFlg = getCharData(offset + 4);
        data.mSoldOutFlg = getCharData(offset + 5);
        data.mMinItemNum = getCharData(offset + 6);
        data.mDmy = 0;
        data.mNoTaxPrice = getLongData(offset + 8);
        data.mTaxPrice = getLongData(offset + 12);
        data.mPrice = data.mTaxPrice;   // 表示用は全て税込価格
        data.mName = getNameShortData(offset + 16, 32);
        data.mMenuAtt = getCharData(offset + 80);
        data.mSubMenuFlg = getCharData(offset + 81);
        data.mSubItemSetNum = getCharData(offset + 82);
        data.mDmy1 = 0;
        data.mSubMenuAddr = getLongData(offset + 84);
        data.mCmdNo = getLongData(offset + 88);
        data.mSetItemAddr = getLongData(offset + 92);
        data.mInfo = getCharData(offset + 93);
        data.mdmy2 = null;
        data.infoImg = getImageFilePath(offset + 96);
        data.mInfoImgAddr = getLongData(offset + 112);
        data.mInfoComment = getNameShortData(offset + 116, 128);
        return data;
    }

    /**
     * 商品詳細情報取得(商品コードより取得)
     * @param code 商品コード
     * @return 商品詳細情報取得
     */
    public ItemInformation getItemInformationFromCode(int code) {
        // アイテム情報を取得する
        HashMap<Integer, ItemInformation> itemInfoMasterData = null;
        if (mCommon.getFunction() != null && mCommon.getFunction().getFuncMenuMasterData() != null) {
            itemInfoMasterData = mCommon.getFunction().getFuncMenuMasterData().getItemInfoMasterData();
        }
        if (itemInfoMasterData != null) {
            ItemInformation itemInfo = itemInfoMasterData.get(code);
            if (itemInfo != null) {
                try {
                    itemInfo.mName = Objects.requireNonNull(mCommon.getOrderInfo()).setConvertLineBreaks(itemInfo.mName);
                } catch (Exception exception) {
                    Logger.e(exception);
                }
                return itemInfo;
            }
        }

        // アイテム情報が存在しない場合、MenuDBから情報を取得する
        // 商品詳細情報の先頭オフセットをヘッダ情報から算出
        long baseIdx =
                // 大分類先頭のオフセットアドレス
                LMENU_INFORMATION
                // 大分類サイズ×大分類数
                + LMENU_INFORMATION_SIZE * mMenuHead.mLmenuMax
                // 中分類サイズ×大分類数×中分類数
                + MMENU_INFORMATION_SIZE * mMenuHead.mLmenuMax * mMenuHead.mMmenuMax
                // 小分類サイズ×小分類数
                + SMENU_INFORMATION_SIZE * mMenuHead.mSmenuNum
                // セル情報サイズ×セル情報項目数
                + ITEM_CELL_INFORMATION_SIZE * mMenuHead.mItemCellNum
                // フレーム情報サイズ×全商品フレーム情報数
                + ITEM_FRAME_INFORMATION_SIZE * mMenuHead.mItemFrmNum;

        // 全商品詳細情報数分ループし、該当する商品コードを検索する
        ItemInformation data = null;
        for (int i = 0; i < mMenuHead.mItemInfoNum; i++) {
            // オフセットアドレス算出
            long idx = baseIdx + ITEM_INFORMATION_SIZE * i;

            // 商品詳細情報と商品コードが一致するか確認
            int itemCode = (int) getLongData((int)idx);
            if (code == itemCode) {
                data = getItemInformation((int)idx);
                break;
            }
        }
        if (data != null) {
            try {
                data.mName = Objects.requireNonNull(mCommon.getOrderInfo()).setConvertLineBreaks(data.mName);
            } catch (Exception exception) {
                Logger.e(exception);
            }
        }
        return data;
    }

    // TODO 仕様はいずれリファクタリング時にクラス化する

    /**
     * プロパティが飲み放題か食べ放題かを判定します。
     * @param property プロパティ
     * @return プロパティタイプ
     */
    public int getPropertyType(int property) {
        if (property == PROPERTY_NORMAL_MENU) {
            return PROPERTY_NORMAL_MENU;
        } else if (property == PROPERTY_LUNCH_MENU) {
            return PROPERTY_LUNCH_MENU;
        } else if (property >= 10 && property <= 17) {
            return PROPERTY_FREE_DRINK;
        } else if (property >= 20 && property <= 27) {
            return PROPERTY_FREE_FOOD;
        } else {
            return PROPERTY_NOT_USE;
        }
    }

    /**
     * プロパティを飲み食べ放題の放題メニュー番号(1〜8)に変換します。
     * @param property プロパティ
     * @return 放題メニュー番号
     */
    public int convertPropertyToMenu(int property) {
        if (property >= 10 && property <= 17) {
            return property - 9;
        } else if (property >= 20 && property <= 27) {
            return property - 19;
        } else {
            return PROPERTY_NOT_USE;    // 通常発生しない
        }
    }

}
