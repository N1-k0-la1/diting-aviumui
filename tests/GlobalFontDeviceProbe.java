package com.android.server.graphics.fonts;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.graphics.fonts.FontStyle;
import android.graphics.fonts.SystemFonts;
import android.graphics.text.TextRunShaper;
import android.graphics.text.PositionedGlyphs;
import android.os.LocaleList;
import android.os.SharedMemory;
import android.text.FontConfig;

import org.json.JSONObject;

import java.io.File;
import java.nio.ByteBuffer;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Exercises actual Android native shaping in a disposable shell process, without installing fonts. */
public final class GlobalFontDeviceProbe {
    private static String shape(Typeface face, String text) {
        Paint paint = new Paint(); paint.setTextSize(48); paint.setTypeface(face);
        PositionedGlyphs glyphs = TextRunShaper.shapeTextRun(text, 0, text.length(),
                0, text.length(), 0, 0, false, paint);
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < glyphs.glyphCount(); i++) {
            result.append(glyphs.getFont(i).getFile()).append(':').append(glyphs.getGlyphId(i)).append(';');
        }
        return result.toString();
    }
    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }

    private static Map<String, Typeface> build(FontConfig config) {
        return SystemFonts.buildSystemTypefaces(config, SystemFonts.buildSystemFallback(config));
    }

    private static Map<String, Typeface> build(FontConfig config, String selected) {
        return GlobalFontConfig.apply(build(config), selected, config.getAliases());
    }

    private static String render(Typeface face, String text) throws Exception {
        check(face != null, "Typeface missing");
        Bitmap bitmap = Bitmap.createBitmap(1000, 150, Bitmap.Config.ARGB_8888);
        bitmap.eraseColor(Color.WHITE);
        Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        paint.setColor(Color.BLACK);
        paint.setTextSize(48);
        paint.setTypeface(face);
        new Canvas(bitmap).drawText(text, 20, 100, paint);
        ByteBuffer pixels = ByteBuffer.allocate(bitmap.getByteCount());
        bitmap.copyPixelsToBuffer(pixels);
        byte[] hash = MessageDigest.getInstance("SHA-256").digest(pixels.array());
        bitmap.recycle();
        return java.util.HexFormat.of().formatHex(hash);
    }

    public static void main(String[] args) throws Exception {
        check(android.os.Process.myUid() == 2000 || android.os.Process.myUid() == 0,
                "Run only as shell/root in a disposable process");
        check(args.length == 1 && new File(args[0]).isFile(), "Supply a readable test font");
        FontConfig stock = SystemFonts.getSystemPreinstalledFontConfig();
        Map<String, Typeface> original = build(stock);
        String text = "全局字体测试 Abc 123";
        String before = render(original.get("sans-serif"), text);
        String emoji = render(original.get("sans-serif"), "😀🙂");
        String missing = render(original.get("sans-serif"), "中文汉字");
        String mono = render(original.get("monospace"), "ABC 0123");

        FontConfig.Font font = new FontConfig.Font(new File(args[0]), null, "GlobalFontProbe",
                new FontStyle(400, FontStyle.FONT_SLANT_UPRIGHT), 0, "", null, 0);
        FontConfig.FontFamily family = new FontConfig.FontFamily(Collections.singletonList(font),
                LocaleList.getEmptyLocaleList(), 0);
        List<FontConfig.NamedFamilyList> named = new ArrayList<>(stock.getNamedFamilyLists());
        named.add(new FontConfig.NamedFamilyList(Collections.singletonList(family),
                UserCustomFontStore.FAMILY, null));
        FontConfig input = new FontConfig(stock.getFontFamilies(), stock.getAliases(), named,
                stock.getLocaleFallbackCustomizations(), stock.getLastModifiedTimeMillis(),
                stock.getConfigVersion());
        String key = "{\"android.theme.customization.font\":\"com.android.theme.font.custom\"}";
        String selected = GlobalFontConfig.selectedFamily(key);
        check(UserCustomFontStore.FAMILY.equals(selected), "Custom selection mapping");
        Map<String, Typeface> applied = build(input, selected);
        String custom = render(applied.get(UserCustomFontStore.FAMILY), text);
        check(render(applied.get("diting-stock-sans-serif"), text).equals(before),
                "Stock preview family was not preserved");
        check(!before.equals(custom), "Test font must differ from stock");
        check(render(applied.get("sans-serif"), text).equals(custom), "sans-serif still uses stock font");
        check(render(applied.get("sans-serif-condensed"), text).equals(custom), "Condensed bypassed selection");
        if (applied.containsKey("google-sans")) {
            check(render(applied.get("google-sans"), text).equals(custom), "GMS family bypassed selection");
        }
        check(render(applied.get("sans-serif"), "😀🙂").equals(emoji), "Emoji fallback changed");
        // Deliberately use a Latin-only import to exercise missing-CJK fallback.
        // A glyph absent from BOTH fonts only compares different .notdef drawings.
        FontConfig.Font latin = new FontConfig.Font(new File("/system/fonts/Roboto-Regular.ttf"),
                null, "GlobalLatinFallbackProbe", new FontStyle(400, FontStyle.FONT_SLANT_UPRIGHT),
                0, "", null, 0);
        FontConfig.FontFamily latinFamily = new FontConfig.FontFamily(Collections.singletonList(latin),
                LocaleList.getEmptyLocaleList(), 0);
        List<FontConfig.NamedFamilyList> latinNamed = new ArrayList<>(stock.getNamedFamilyLists());
        latinNamed.add(new FontConfig.NamedFamilyList(Collections.singletonList(latinFamily),
                UserCustomFontStore.FAMILY, null));
        FontConfig latinInput = new FontConfig(stock.getFontFamilies(), stock.getAliases(), latinNamed,
                stock.getLocaleFallbackCustomizations(), stock.getLastModifiedTimeMillis(), stock.getConfigVersion());
        Map<String, Typeface> latinMap = build(latinInput, selected);
        check(render(latinMap.get("sans-serif"), "中文汉字").equals(missing), "CJK fallback changed: "
                + shape(original.get("sans-serif"), "中文汉字") + " -> " + shape(latinMap.get("sans-serif"), "中文汉字"));
        check(render(applied.get("monospace"), "ABC 0123").equals(mono), "Monospace changed");

        // Exercise the exact shared-memory transport used to give new app processes their map.
        Map<String, Typeface> received = new HashMap<>();
        try (SharedMemory memory = Typeface.serializeFontMap(applied)) {
            ByteBuffer buffer = memory.mapReadOnly();
            Typeface.deserializeFontMap(buffer, received);
            Typeface.setSystemFontMap(received); // This child process only, never system_server.
            check(render(Typeface.DEFAULT, text).equals(custom), "Typeface.DEFAULT not replaced");
            check(render(Typeface.SANS_SERIF, text).equals(custom), "Public SANS_SERIF not replaced");
            check(render(Typeface.create("sans-serif", Typeface.NORMAL), text).equals(custom),
                    "App-style family lookup not replaced");
            check(render(Typeface.create("sans-serif-medium", Typeface.NORMAL), text)
                    .equals(render(Typeface.create(Typeface.create(UserCustomFontStore.FAMILY,
                            Typeface.NORMAL), 500, false), text)),
                    "Weighted alias does not resolve to custom family");
            // Retain the mapping until process exit: native Typefaces reference its data.
        }
        check(GlobalFontConfig.apply(original, selected, stock.getAliases()) == original,
                "Missing custom font changed defaults");
        check(GlobalFontConfig.apply(original, null, stock.getAliases()) == original,
                "Default/reset must preserve stock input");
        Map<String, Typeface> rejected = new HashMap<>(original);
        rejected.put(UserCustomFontStore.FAMILY, original.get("serif"));
        List<FontConfig.Alias> rejectedAliases = new ArrayList<>(stock.getAliases());
        rejectedAliases.add(new FontConfig.Alias(UserCustomFontStore.FAMILY, "serif", 400));
        check(GlobalFontConfig.apply(rejected, selected, rejectedAliases) == rejected,
                "Missing/rejected custom font must preserve the original app default");
        check(GlobalFontConfig.selectedFamily("{invalid") == null, "Malformed theme accepted");
        check(GlobalFontConfig.selectedFamily("{}") == null, "Default theme changed fonts");
        check(GlobalFontConfig.selectedFamily("{\"android.theme.customization.font\":\"unknown\"}") == null,
                "Unknown overlay accepted");
        for (String[] preset : new String[][] {{"condensed", "sans-serif-condensed"},
                {"sourcesanspro", "source-sans-pro"}, {"notoserif", "serif"}}) {
            String choice = GlobalFontConfig.selectedFamily(
                    "{\"android.theme.customization.font\":\"com.android.theme.font." + preset[0] + "\"}");
            check(preset[1].equals(choice), "Preset mapping failed");
            Map<String, Typeface> map = build(stock, choice);
            check(render(map.get("sans-serif"), text).equals(render(original.get(choice), text)),
                    "Preset is not global: " + choice);
        }
        System.out.println(new JSONObject().put("passed", true).put("native_render_and_shaping", true)
                .put("app_default_and_weighted_aliases", true).put("shared_memory_roundtrip", true)
                .put("emoji_cjk_and_monospace_preserved", true).put("presets_and_restore", true)
                .put("system_font_state_modified", false).toString());
    }
}
