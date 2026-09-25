package com.d3f4ul1.lungeswap;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.option.KeyBinding;
import net.minecraft.client.util.InputUtil;
import net.minecraft.item.ItemStack;
import net.minecraft.util.Identifier;

import org.lwjgl.glfw.GLFW;

import java.util.Locale;

/**
 * Client entrypoint.
 *
 * <p>Scan the hotbar by display name, select the spear, force an attack, revert one tick later.
 * Nothing here is server-side: the mod only drives your own client's hotbar and attack key.
 */
public class LungeSwapClient implements ClientModInitializer {

    public static final String MOD_ID = "lungeswap";

    /**
     * MAPPING: Yarn has no {@code KeyMapping} class and no {@code Category.register}; it is
     * {@code KeyBinding.Category.create(Identifier)}. Verified non-idempotent by disassembly: it
     * throws {@code IllegalArgumentException("Category '%s' is already registered.")} on a repeat
     * id, so it must be evaluated exactly once -- hence {@code static final}.
     *
     * <p>The label resolves via {@code Category.getLabel()} ->
     * {@code id.toTranslationKey("key.category")} = {@code key.category.<namespace>.<path>}, which
     * is why the lang key is {@code key.category.lungeswap.main}.
     */
    public static final KeyBinding.Category CATEGORY =
            KeyBinding.Category.create(Identifier.of(MOD_ID, "main"));

    private static KeyBinding swapKeyBinding;

    @Override
    public void onInitializeClient() {
        // Default key G. Its own category, so it does not show up mixed in with the Movement group.
        swapKeyBinding = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "key.lungeswap.swap",
                InputUtil.Type.KEYSYM,
                GLFW.GLFW_KEY_G,
                CATEGORY));

        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            if (client.player != null && swapKeyBinding != null) {
                // MAPPING: consumeClick() does not exist on 1.21.11; wasPressed() is the
                // consuming variant (its bytecode decrements timesPressed).
                while (swapKeyBinding.wasPressed()) {
                    triggerSwap(client);
                }
            }
            SwapManager.tick(client);
        });
    }

    private void triggerSwap(MinecraftClient mc) {
        int targetSlot = -1;

        for (int slot = 0; slot < 9; slot++) {
            ItemStack stack = mc.player.getInventory().getStack(slot);
            // Match on the localised display name. Crude, but it catches any spear regardless of
            // how the item is registered -- modded spears included.
            String name = stack.getName().getString().toLowerCase(Locale.ROOT);
            if (name.contains("spear") || name.contains("trident")) {
                targetSlot = slot;
                break;
            }
        }

        // MAPPING: `inventory.selectedSlot` is `private int selectedSlot` on 1.21.11; use the
        // accessor, which is public API and needs no widener.
        int currentSlot = mc.player.getInventory().getSelectedSlot();

        if (targetSlot != -1 && targetSlot != currentSlot) {
            SwapManager.startSwap(targetSlot, currentSlot);
        }
    }
}
